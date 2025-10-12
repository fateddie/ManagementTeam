"""
score_utils.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Simple Weighted Scoring Utilities

Clean, simple scoring functions for Opportunity Ranking Agent.

Location: src/utils/score_utils.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Tuple


def weighted_score(idea: Dict, weights: Dict[str, int]) -> Tuple[int, Dict[str, int]]:
    """
    Calculate weighted score for a business idea.
    
    Args:
        idea: Dict with scoring criteria (0-10 values)
        weights: Dict with criterion weights
        
    Returns:
        Tuple of (total_score, breakdown_dict)
        
    Example:
        idea = {"market_size": 7, "entry_ease": 8, ...}
        weights = {"market_size": 5, "entry_ease": 4, ...}
        score, breakdown = weighted_score(idea, weights)
        # score = (7*5) + (8*4) + ... = total
    """
    breakdown = {}
    total = 0
    
    for criterion, weight in weights.items():
        value = idea.get(criterion, 0)
        score = int(value * weight)
        breakdown[criterion] = score
        total += score
    
    return total, breakdown

