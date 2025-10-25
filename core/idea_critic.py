"""
Idea Critic - AI-powered critique and grammar correction

Provides:
- Spelling/grammar correction for idea summaries
- Positive and negative feedback
- Quality analysis explanation
- Suggested improvements
"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    from src.utils.config_loader import get_env, load_env
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# HuggingFace for local grammar correction
try:
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available - grammar correction will use OpenAI only")


class IdeaCritic:
    """
    Analyzes and critiques business ideas with AI.

    Provides:
    - Grammar/spelling correction
    - Positive feedback (strengths)
    - Negative feedback (weaknesses/risks)
    - Quality score explanation
    - Actionable suggestions
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 800,
        use_local_grammar: bool = True
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        self.available = False
        self.grammar_pipeline = None
        self.use_local_grammar = use_local_grammar

        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            load_env()
            api_key = get_env("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.available = True
                    logger.info("✅ Idea Critic initialized with OpenAI")
                except Exception as e:
                    logger.warning(f"Failed to initialize IdeaCritic OpenAI: {e}")

        # Initialize local grammar correction (HuggingFace T5)
        if TRANSFORMERS_AVAILABLE and use_local_grammar:
            try:
                device = 0 if torch.cuda.is_available() else -1
                self.grammar_pipeline = pipeline(
                    "text2text-generation",
                    model="vennify/t5-base-grammar-correction",
                    device=device
                )
                logger.info("✅ T5 grammar correction initialized (local, $0 cost)")
            except Exception as e:
                logger.warning(f"Failed to initialize T5 grammar correction: {e}")
                self.grammar_pipeline = None

    def is_available(self) -> bool:
        """Check if AI critic is available."""
        return self.available and self.client is not None

    def _correct_grammar_local(self, text: str) -> str:
        """
        Local grammar correction using T5 (HuggingFace).

        Zero cost alternative to OpenAI grammar correction.
        Falls back to original text if T5 not available.

        Args:
            text: Text to correct

        Returns:
            Grammar-corrected text
        """
        if not self.grammar_pipeline or not text:
            return text

        try:
            # T5 works best with shorter texts
            if len(text) > 500:
                # Split into sentences and correct each
                sentences = text.split('. ')
                corrected = []
                for sentence in sentences:
                    if len(sentence) > 10:  # Skip very short fragments
                        result = self.grammar_pipeline(
                            sentence,
                            max_length=min(len(sentence) * 2, 512),
                            num_beams=3  # Faster than 5
                        )[0]['generated_text']
                        corrected.append(result)
                    else:
                        corrected.append(sentence)
                return '. '.join(corrected)
            else:
                # Correct short text directly
                result = self.grammar_pipeline(
                    text,
                    max_length=min(len(text) * 2, 512),
                    num_beams=3
                )[0]['generated_text']
                return result

        except Exception as e:
            logger.warning(f"Local grammar correction failed: {e}")
            return text  # Fallback to original

    def critique_idea(
        self,
        collected_data: Dict[str, Any],
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Provide comprehensive critique of an idea.

        Args:
            collected_data: Dictionary of field_name: value
            quality_score: Overall quality score (0.0-1.0)

        Returns:
            {
                "corrected_summary": {...},  # Grammar-corrected fields
                "strengths": [str],          # Positive feedback
                "weaknesses": [str],         # Negative feedback / risks
                "suggestions": [str],        # Actionable improvements
                "quality_explanation": str,  # What the score means
                "recommendation": str        # Proceed / Refine / Rethink
            }
        """
        if not self.is_available():
            return self._fallback_critique(collected_data, quality_score)

        try:
            # STEP 1: Apply local grammar correction (T5) - ZERO COST!
            corrected_summary = {}
            if self.grammar_pipeline:
                logger.info("🔧 Applying local T5 grammar correction...")
                for field, value in collected_data.items():
                    if isinstance(value, str) and value.strip():
                        corrected_summary[field] = self._correct_grammar_local(value)
                    else:
                        corrected_summary[field] = value
            else:
                # No local correction available, OpenAI will do it
                corrected_summary = collected_data.copy()

            # STEP 2: Build prompt with corrected text
            prompt = self._build_critique_prompt(corrected_summary, quality_score)

            # STEP 3: Get critique from OpenAI (no grammar correction needed!)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=15,
                response_format={"type": "json_object"}
            )

            critique = json.loads(response.choices[0].message.content)

            # Use our local T5-corrected summary (already done!)
            critique['corrected_summary'] = corrected_summary

            if self.grammar_pipeline:
                logger.info(f"✅ Idea critique generated (T5 grammar + GPT critique, score: {quality_score*100:.0f}%)")
            else:
                logger.info(f"✅ Idea critique generated (GPT only, score: {quality_score*100:.0f}%)")

            return critique

        except Exception as e:
            logger.error(f"AI critique failed: {e}")
            return self._fallback_critique(collected_data, quality_score)

    def _get_system_prompt(self) -> str:
        """System prompt for AI critic."""
        grammar_note = ""
        if self.grammar_pipeline:
            grammar_note = "\n\nNOTE: Grammar/spelling has already been corrected. Skip the corrected_summary field and focus on critique."

        return f"""You are an experienced startup advisor providing honest, constructive feedback on business ideas.

Your job: Analyze the idea and provide balanced critique.{grammar_note}

Response format (JSON):
{{
  "strengths": [
    "What's good about this idea (2-3 points)"
  ],
  "weaknesses": [
    "Potential risks or concerns (2-3 points)"
  ],
  "suggestions": [
    "Specific actionable improvements (2-3 points)"
  ],
  "quality_explanation": "Explain what the quality score means and why",
  "recommendation": "PROCEED / REFINE / RETHINK"
}}

Be encouraging but honest. Focus on actionable feedback."""

    def _build_critique_prompt(
        self,
        collected_data: Dict[str, Any],
        quality_score: float
    ) -> str:
        """Build critique prompt."""

        # Format the idea data
        idea_text = "\n".join([
            f"{key.replace('_', ' ').title()}: {value}"
            for key, value in collected_data.items()
            if value
        ])

        return f"""
Analyze this business idea:

{idea_text}

Quality Score: {quality_score*100:.0f}% ({self._score_to_label(quality_score)})

Provide:
1. Corrected version (fix spelling/grammar)
2. Strengths (what's promising)
3. Weaknesses (risks/concerns)
4. Suggestions (how to improve)
5. Explain what {quality_score*100:.0f}% means
6. Recommendation (PROCEED/REFINE/RETHINK)

Respond in JSON format as specified.
"""

    def _score_to_label(self, score: float) -> str:
        """Convert score to label."""
        if score >= 0.80:
            return "Excellent"
        elif score >= 0.70:
            return "Good"
        elif score >= 0.60:
            return "Acceptable"
        elif score >= 0.50:
            return "Needs Work"
        else:
            return "Incomplete"

    def _fallback_critique(
        self,
        collected_data: Dict[str, Any],
        quality_score: float
    ) -> Dict[str, Any]:
        """Fallback critique when AI unavailable."""

        strengths = []
        weaknesses = []
        suggestions = []

        # Basic analysis
        if 'core_idea' in collected_data:
            strengths.append("You have a clear problem you're trying to solve")

        if 'target_customer' in collected_data:
            strengths.append("You've identified a target customer segment")

        if quality_score < 0.70:
            weaknesses.append("Some fields need more detail and specificity")
            suggestions.append("Add more specific examples and numbers where possible")

        if quality_score < 0.60:
            weaknesses.append("Core idea could be more clearly defined")
            suggestions.append("Clarify exactly what problem you're solving and how")

        quality_explanation = f"Your idea scored {quality_score*100:.0f}% - "
        if quality_score >= 0.80:
            quality_explanation += "excellent quality with clear details"
            recommendation = "PROCEED"
        elif quality_score >= 0.60:
            quality_explanation += "acceptable quality, but could be more specific"
            recommendation = "REFINE"
        else:
            quality_explanation += "needs more detail to proceed confidently"
            recommendation = "RETHINK"

        return {
            "corrected_summary": collected_data,  # No corrections in fallback
            "strengths": strengths or ["You have the beginnings of an idea"],
            "weaknesses": weaknesses or ["More research needed"],
            "suggestions": suggestions or ["Add more specific details"],
            "quality_explanation": quality_explanation,
            "recommendation": recommendation
        }

    def format_critique_display(self, critique: Dict[str, Any]) -> str:
        """Format critique for console display."""
        lines = []

        lines.append("\n" + "="*70)
        lines.append("🔍 IDEA CRITIQUE & ANALYSIS")
        lines.append("="*70)

        # Corrected summary
        lines.append("\n📝 Corrected Summary (spelling/grammar fixed):")
        lines.append("-"*70)
        corrected = critique.get("corrected_summary", {})
        for field, value in corrected.items():
            lines.append(f"\n• {field.replace('_', ' ').title()}:")
            lines.append(f"  {value}")

        # Strengths
        lines.append("\n\n✅ Strengths:")
        lines.append("-"*70)
        for i, strength in enumerate(critique.get("strengths", []), 1):
            lines.append(f"{i}. {strength}")

        # Weaknesses
        lines.append("\n\n⚠️  Weaknesses / Risks:")
        lines.append("-"*70)
        for i, weakness in enumerate(critique.get("weaknesses", []), 1):
            lines.append(f"{i}. {weakness}")

        # Suggestions
        lines.append("\n\n💡 Suggestions for Improvement:")
        lines.append("-"*70)
        for i, suggestion in enumerate(critique.get("suggestions", []), 1):
            lines.append(f"{i}. {suggestion}")

        # Quality explanation
        lines.append("\n\n📊 Quality Score Explanation:")
        lines.append("-"*70)
        lines.append(critique.get("quality_explanation", ""))

        # Recommendation
        recommendation = critique.get("recommendation", "PROCEED")
        if recommendation == "PROCEED":
            emoji = "🟢"
            message = "Ready to proceed to research phase"
        elif recommendation == "REFINE":
            emoji = "🟡"
            message = "Consider refining before proceeding"
        else:
            emoji = "🔴"
            message = "Recommend rethinking core concept"

        lines.append(f"\n\n{emoji} Recommendation: {recommendation}")
        lines.append(f"   {message}")

        lines.append("\n" + "="*70)

        return "\n".join(lines)
