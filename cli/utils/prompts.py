"""
prompts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Prompt Template Utilities

Loads and formats prompt templates for refinement and scoring.

Location: cli/utils/prompts.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
from pathlib import Path
from typing import Dict


def load_refinement_prompt(raw_idea: str) -> str:
    """
    Load and format the refinement prompt template.
    
    Args:
        raw_idea: User's vague/broad business idea
        
    Returns:
        Formatted prompt string
    """
    template_path = Path(__file__).parent.parent.parent / "agents" / "refinement_agent" / "prompts" / "refinement_prompt.md"
    
    if not template_path.exists():
        # Fallback inline prompt
        return f"""You are a startup advisor. The user has this raw idea: "{raw_idea}"

Help them refine it into a clear, niche-ready business concept.

Return ONLY valid JSON with:
{{
  "refined_idea": {{
    "name": "Specific business name",
    "niche": "Target market",
    "value_proposition": "What problem it solves",
    "target_customer": "Who pays for this",
    "unique_angle": "What makes it different"
  }}
}}

Be specific, not generic. Focus on niches."""
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace placeholder
    return template.replace('"{raw_idea}"', f'"{raw_idea}"')


def load_scoring_prompt(refined_idea: Dict) -> str:
    """
    Load and format the scoring prompt template.
    
    Args:
        refined_idea: Dict with refined business concept
        
    Returns:
        Formatted prompt string
    """
    idea_text = f"""
Business: {refined_idea.get('name', 'Unknown')}
Niche: {refined_idea.get('niche', 'Not specified')}
Value Prop: {refined_idea.get('value_proposition', 'Not specified')}
Target Customer: {refined_idea.get('target_customer', 'Not specified')}
Unique Angle: {refined_idea.get('unique_angle', 'Not specified')}
"""
    
    return f"""You are a business analyst. Score this refined business idea:

{idea_text}

Return ONLY valid JSON with scores (0-10) for each criterion:

{{
  "market_size": 7,
  "entry_ease": 8,
  "personal_fit": 6,
  "scalability": 7,
  "speed_to_mvp": 8,
  "competition": 6,
  "resource_need": 7,
  "justification": "Brief reasoning for the scores"
}}

Be realistic and data-driven."""

