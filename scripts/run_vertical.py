#!/usr/bin/env python3
"""
run_vertical.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Script for Running Vertical Agent

Quick test script to evaluate business vertical ideas.

Usage:
    python scripts/run_vertical.py
    
Location: scripts/run_vertical.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.vertical_agent.vertical_agent import run_vertical_agent


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Example Business Verticals
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ideas = [
    {
        "name": "Golf Courses",
        "reach": 6,          # Reach: 1-10 (number of potential customers)
        "impact": 7,         # Impact: 1-10 (how much value it creates)
        "confidence": 8,     # Confidence: 1-10 (how sure we are)
        "effort": 4,         # Effort: 1-10 (how hard to build)
        "description": "Course management and booking system for golf clubs"
    },
    {
        "name": "Car Garages",
        "reach": 7,
        "impact": 8,
        "confidence": 7,
        "effort": 3,
        "description": "Booking, inventory, and customer management for auto repair shops"
    },
    {
        "name": "Hair Salons",
        "reach": 5,
        "impact": 6,
        "confidence": 9,
        "effort": 2,
        "description": "Appointment scheduling and client records for hair salons"
    },
    {
        "name": "Restaurants",
        "reach": 8,
        "impact": 7,
        "confidence": 6,
        "effort": 5,
        "description": "Table booking and waitlist management system"
    },
    {
        "name": "Fitness Studios",
        "reach": 6,
        "impact": 7,
        "confidence": 8,
        "effort": 3,
        "description": "Class scheduling and membership management"
    }
]


def main():
    """Run vertical evaluation and display results."""
    print("\n" + "="*70)
    print("🎯 VERTICAL AGENT - Business Opportunity Evaluation")
    print("="*70 + "\n")
    
    print(f"📊 Evaluating {len(ideas)} business verticals using RICE framework...\n")
    
    # Run the vertical agent
    result = run_vertical_agent(ideas, framework="RICE")
    
    # Display results
    print("\n" + "🏆 " + "="*66)
    print("   RECOMMENDATION")
    print("="*70 + "\n")
    
    print(result['summary'])
    
    print("\n" + "─"*70)
    print("\n📈 TOP CHOICE DETAILS:\n")
    top = result['top_choice']
    print(f"   Name:       {top['name']}")
    print(f"   RICE Score: {top['score']}")
    print(f"   Reach:      {top['reach']}/10")
    print(f"   Impact:     {top['impact']}/10")
    print(f"   Confidence: {top['confidence']}/10")
    print(f"   Effort:     {top['effort']}/10")
    if 'description' in top:
        print(f"   Details:    {top['description']}")
    
    print("\n" + "─"*70)
    print("\n📊 FULL RANKING:\n")
    for i, idea in enumerate(result['all_ranked'], start=1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {medal} {i}. {idea['name']:<20} Score: {idea['score']:>8.2f}")
    
    # Display proactive suggestions
    if 'proactive_notes' in result and result['proactive_notes']:
        print("\n" + "─"*70)
        print("\n🤖 PROACTIVE INSIGHTS:\n")
        for i, note in enumerate(result['proactive_notes'], start=1):
            # Wrap long lines
            lines = note.split('. ')
            if len(lines) > 1:
                print(f"   {i}. {lines[0]}.")
                for line in lines[1:]:
                    if line.strip():
                        print(f"      {line.strip()}{'.' if not line.endswith('.') else ''}")
            else:
                print(f"   {i}. {note}")
    
    print("\n" + "="*70)
    print("✅ Evaluation Complete!")
    print("="*70 + "\n")
    
    print("💡 Next Steps:")
    print("   1. Review the top recommendation")
    print("   2. Address any proactive insights above")
    print("   3. Feed this to Strategy Agent for detailed planning")
    print("   4. Or run with different verticals via YAML input\n")


if __name__ == "__main__":
    main()

