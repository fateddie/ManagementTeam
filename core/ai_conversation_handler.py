"""
AI Conversation Handler

Intelligent conversation management using OpenAI for natural, context-aware
question-answer interactions during idea validation workflow.

WHY: Transforms script-based conversations into truly intelligent dialogue that:
- Understands meta-responses ("I want to refine my idea" vs actual answers)
- Generates contextual follow-ups based on actual content
- Detects contradictions and vague answers
- Adapts to user's conversation style

Features:
- GPT-4o-mini for cost-effective intelligence
- JSON-structured responses for reliable parsing
- Graceful error handling with fallback to script-based
- Conversation history tracking for coherence
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional OpenAI import (graceful degradation if not available)
try:
    from openai import OpenAI
    from src.utils.config_loader import get_env, load_env
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available - conversations will use script-based fallback")


class AIConversationHandler:
    """
    Manages AI-powered conversational interactions.

    Uses OpenAI to analyze user responses, detect meta-responses,
    suggest improvements, and generate contextual follow-ups.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 300,
        timeout: int = 10
    ):
        """
        Initialize AI conversation handler.

        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            temperature: Creativity level (0.7 = balanced)
            max_tokens: Max response length
            timeout: API timeout in seconds
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.conversation_history = []

        # Initialize OpenAI client
        self.client = None
        self.available = False

        if OPENAI_AVAILABLE:
            load_env()
            api_key = get_env("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.available = True
                    logger.info("✅ AI Conversation Handler initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI: {e}")
            else:
                logger.warning("OPENAI_API_KEY not found - using fallback mode")

    def is_available(self) -> bool:
        """Check if AI handler is available and working."""
        return self.available and self.client is not None

    def analyze_response(
        self,
        question: str,
        user_answer: str,
        field_name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze user's response using AI.

        Args:
            question: The question that was asked
            user_answer: User's response
            field_name: Field being collected
            context: Previous answers for coherence checking

        Returns:
            {
                "is_meta_response": bool,
                "quality_score": 0-100,
                "missing_elements": List[str],
                "suggested_follow_up": str,
                "acknowledgment": str,
                "coherence_check": {
                    "aligns_with_context": bool,
                    "contradictions": List[str]
                }
            }
        """
        if not self.is_available():
            return self._fallback_analysis(user_answer)

        try:
            # Build prompt for GPT
            prompt = self._build_analysis_prompt(
                question, user_answer, field_name, context
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            analysis = json.loads(response.choices[0].message.content)

            # Log for debugging
            logger.debug(f"AI Analysis for '{field_name}': quality={analysis.get('quality_score')}")

            # Track in conversation history
            self.conversation_history.append({
                "field": field_name,
                "question": question,
                "answer": user_answer,
                "analysis": analysis
            })

            return analysis

        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._fallback_analysis(user_answer)

    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analyzer."""
        return """You are a startup advisor analyzing user responses during idea validation.

Your job: Analyze each answer for quality, detect issues, and suggest improvements.

Response format (JSON):
{
  "is_meta_response": bool (true if asking for help vs answering),
  "quality_score": 0-100 (how specific and complete),
  "missing_elements": ["what's missing"],
  "suggested_follow_up": "next question to ask",
  "acknowledgment": "brief acknowledgment",
  "coherence_check": {
    "aligns_with_context": bool,
    "contradictions": []
  }
}

Be encouraging but honest. If answer is vague, suggest specific improvements."""

    def _build_analysis_prompt(
        self,
        question: str,
        user_answer: str,
        field_name: str,
        context: Dict[str, Any]
    ) -> str:
        """Build analysis prompt for GPT."""

        # Format context
        context_str = "\n".join([
            f"- {key}: {value}"
            for key, value in context.items()
            if value and key != field_name
        ])

        return f"""
Analyze this response:

Question asked: "{question}"
Field: {field_name}
User's answer: "{user_answer}"

Previous context:
{context_str if context_str else "(First question)"}

Evaluate:
1. Is this a meta-response (asking for help) or actual answer?
2. Quality score (0-100): How specific?
3. What's missing (if anything)?
4. Best follow-up question?
5. Does it contradict previous answers?

Respond in JSON format as specified.
"""

    def _fallback_analysis(self, user_answer: str) -> Dict[str, Any]:
        """
        Fallback analysis when AI unavailable.
        Uses simple heuristics.
        """
        # Simple checks
        is_meta = any(phrase in user_answer.lower() for phrase in [
            "i want to", "can you help", "i need help", "how do i"
        ])

        quality_score = min(100, len(user_answer) * 2)  # Rough: 50 chars = 100 score

        return {
            "is_meta_response": is_meta,
            "quality_score": quality_score,
            "missing_elements": [],
            "suggested_follow_up": "Could you tell me more about that?",
            "acknowledgment": "I see.",
            "coherence_check": {
                "aligns_with_context": True,
                "contradictions": []
            }
        }

    def clear_history(self):
        """Clear conversation history (for new workflow)."""
        self.conversation_history = []
        logger.debug("Conversation history cleared")
