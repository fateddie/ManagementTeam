"""
scoring_prompts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scoring Prompt Templates

AI-powered scoring for refined business ideas.

Location: cli/utils/scoring_prompts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
from typing import Dict
from openai import OpenAI


SCORE_PROMPT = """
You are a VC analyst scoring startup ideas.

Score this startup idea across 6 dimensions (0–10 scale):
- **Clarity**: How clear and well-defined is the concept?
- **Niche Focus**: How well-targeted is the market segment?
- **Market Size**: How large is the addressable market?
- **Pain Severity**: How acute is the customer's problem?
- **Differentiation**: How unique is the solution?
- **Monetization**: How clear is the revenue model?

Return a JSON object like:
{{
  "Clarity": 7,
  "Niche Focus": 9,
  "Market Size": 6,
  "Pain Severity": 8,
  "Differentiation": 7,
  "Monetization": 9,
  "Comments": {{
    "Clarity": "Well-written, but could be more concise",
    "Niche Focus": "Excellent - very specific target market",
    "Market Size": "Medium-sized niche, room to grow",
    "Pain Severity": "High pain point - missed calls = lost revenue",
    "Differentiation": "Good angle with salon-specific training",
    "Monetization": "Clear SaaS model with per-location pricing"
  }},
  "Verdict": "Worth pursuing if refined further",
  "Overall_Score": 46
}}

Calculate Overall_Score as the sum of all 6 dimensions.
"""


def score_idea(idea: Dict, model: str = 'gpt-4o-mini') -> Dict:
    """
    Score a refined business idea using AI.
    
    Args:
        idea: Refined idea dict
        model: OpenAI model to use
        
    Returns:
        Dict with scores and comments
    """
    prompt = SCORE_PROMPT + "\n\nIdea to Score:\n" + json.dumps(idea, indent=2)
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a VC analyst. Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up markdown code blocks
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        scores = json.loads(content)
        return scores
        
    except Exception as e:
        print(f"⚠️  AI scoring failed: {e}")
        # Return mock scores
        return {
            "Clarity": 7,
            "Niche Focus": 8,
            "Market Size": 6,
            "Pain Severity": 7,
            "Differentiation": 6,
            "Monetization": 7,
            "Overall_Score": 41,
            "Verdict": "Mock scores - AI unavailable",
            "Comments": {}
        }

