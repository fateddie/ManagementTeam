#!/usr/bin/env python3
"""
Test edge cases for Vertical Agent proactive suggestions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.vertical_agent.vertical_agent import run_vertical_agent


def test_low_confidence_high_effort():
    """Test vertical with multiple red flags."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Low Confidence + High Effort Vertical")
    print("="*70 + "\n")
    
    ideas = [
        {
            "name": "Enterprise Healthcare AI",
            "reach": 3,           # Limited reach
            "impact": 9,          # High impact
            "confidence": 4,      # Low confidence
            "effort": 9,          # Very high effort
            "description": "Complex AI-powered healthcare management system"
        },
        {
            "name": "Simple Pet App",
            "reach": 6,
            "impact": 6,
            "confidence": 8,
            "effort": 2,
            "description": "Basic pet care reminder app"
        }
    ]
    
    result = run_vertical_agent(ideas)
    
    print(f"Top Choice: {result['top_choice']['name']}")
    print(f"Score: {result['top_choice']['score']}\n")
    
    print("🤖 Proactive Insights:")
    for i, note in enumerate(result['proactive_notes'], start=1):
        print(f"   {i}. {note}\n")


def test_missing_data():
    """Test validation with missing fields."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Missing Data Validation")
    print("="*70 + "\n")
    
    ideas = [
        {
            "name": "Complete Vertical",
            "reach": 7,
            "impact": 8,
            "confidence": 7,
            "effort": 3
        },
        {
            "name": "Incomplete Vertical",
            "reach": 6,
            "impact": 7,
            # Missing confidence and effort
        }
    ]
    
    result = run_vertical_agent(ideas)
    
    if 'error' in result:
        print(f"❌ Validation Error: {result['error']}")
        print(f"   Missing: {', '.join(result['missing'])}")
        print(f"   Action: {result['action']}")
    else:
        print(f"✅ All data valid")


def test_close_competition():
    """Test with very close scores."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Close Competition Between Verticals")
    print("="*70 + "\n")
    
    ideas = [
        {"name": "Option A", "reach": 6, "impact": 7, "confidence": 8, "effort": 4},
        {"name": "Option B", "reach": 6, "impact": 7, "confidence": 8, "effort": 4.1},  # Nearly identical
        {"name": "Option C", "reach": 6, "impact": 7, "confidence": 8, "effort": 4.2},
    ]
    
    result = run_vertical_agent(ideas)
    
    print(f"Top Choice: {result['top_choice']['name']}")
    print(f"Scores: {[v['score'] for v in result['all_ranked']]}\n")
    
    print("🤖 Proactive Insights:")
    for i, note in enumerate(result['proactive_notes'], start=1):
        print(f"   {i}. {note}\n")


def test_clear_winner():
    """Test with one obviously superior option."""
    print("\n" + "="*70)
    print("🧪 TEST 4: Clear Winner Scenario")
    print("="*70 + "\n")
    
    ideas = [
        {"name": "Amazing Opportunity", "reach": 10, "impact": 10, "confidence": 9, "effort": 2},  # 450 score
        {"name": "Mediocre Option", "reach": 4, "impact": 5, "confidence": 6, "effort": 5},  # 24 score
    ]
    
    result = run_vertical_agent(ideas)
    
    print(f"Top Choice: {result['top_choice']['name']}")
    print(f"Score: {result['top_choice']['score']}")
    print(f"Runner-up: {result['all_ranked'][1]['name']}")
    print(f"Score: {result['all_ranked'][1]['score']}\n")
    
    print("🤖 Proactive Insights:")
    for i, note in enumerate(result['proactive_notes'], start=1):
        print(f"   {i}. {note}\n")


if __name__ == "__main__":
    test_low_confidence_high_effort()
    test_missing_data()
    test_close_competition()
    test_clear_winner()
    
    print("\n" + "="*70)
    print("✅ All Edge Case Tests Complete!")
    print("="*70 + "\n")

