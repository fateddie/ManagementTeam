"""
scoring_utils.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scoring Utilities for Business Vertical Evaluation

Simple RICE and ICE scoring frameworks.

Location: src/utils/scoring_utils.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, List


def calculate_rice(reach: float, impact: float, confidence: float, effort: float) -> float:
    """
    Calculate RICE score.
    
    RICE = (Reach × Impact × Confidence) / Effort
    
    Args:
        reach: Number of users/customers affected
        impact: Impact score (0-10)
        confidence: Confidence level (0-10) 
        effort: Person-months or complexity (1-10)
        
    Returns:
        RICE score (float)
    """
    return (reach * impact * confidence) / max(effort, 0.1)


def calculate_ice(impact: float, confidence: float, ease: float) -> float:
    """
    Calculate ICE score (simpler alternative to RICE).
    
    ICE = (Impact + Confidence + Ease) / 3
    
    Args:
        impact: Value created (0-10)
        confidence: Certainty (0-10)
        ease: Implementation ease (0-10, inverse of effort)
        
    Returns:
        ICE score (float)
    """
    return (impact + confidence + ease) / 3


def score_vertical(vertical_data: Dict, framework: str = "RICE") -> Dict:
    """
    Score a single vertical idea.
    
    Args:
        vertical_data: Dict with keys: name, reach, impact, confidence, effort
        framework: "RICE" or "ICE"
        
    Returns:
        vertical_data dict with added 'score' key
    """
    if framework.upper() == "ICE":
        # ICE scoring
        ease = 10 - vertical_data.get('effort', 5)  # Inverse of effort
        score = calculate_ice(
            impact=vertical_data['impact'],
            confidence=vertical_data['confidence'],
            ease=ease
        )
    else:
        # RICE scoring (default)
        score = calculate_rice(
            reach=vertical_data['reach'],
            impact=vertical_data['impact'],
            confidence=vertical_data['confidence'],
            effort=vertical_data['effort']
        )
    
    vertical_data['score'] = round(score, 2)
    vertical_data['framework'] = framework
    return vertical_data


def score_all_verticals(ideas: List[Dict], framework: str = "RICE") -> List[Dict]:
    """
    Score and rank multiple verticals.
    
    Args:
        ideas: List of vertical dicts
        framework: Scoring framework to use
        
    Returns:
        List of scored verticals, sorted by score (descending)
    """
    scored = [score_vertical(idea.copy(), framework) for idea in ideas]
    ranked = sorted(scored, key=lambda x: x['score'], reverse=True)
    return ranked


def get_recommendation(ranked: List[Dict]) -> Dict:
    """
    Generate recommendation from ranked verticals.
    
    Args:
        ranked: List of scored verticals (sorted)
        
    Returns:
        Dict with top_choice, alternatives, and summary
    """
    if not ranked:
        return {
            "top_choice": None,
            "alternatives": [],
            "summary": "⚠️ No verticals to evaluate"
        }
    
    top = ranked[0]
    alternatives = ranked[1:4]  # Top 3 alternatives
    
    return {
        "top_choice": top,
        "alternatives": alternatives,
        "all_ranked": ranked,
        "summary": f"🏆 Recommend pursuing: {top['name']} (score: {top['score']})"
    }
