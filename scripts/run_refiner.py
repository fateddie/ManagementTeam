#!/usr/bin/env python3
"""
run_refiner.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Script for Idea Refinement Agent

Refines vague business ideas into clear, scoreable concepts.

Usage:
    python scripts/run_refiner.py "AI Call Catcher"
    python scripts/run_refiner.py  # Interactive mode
    
Location: scripts/run_refiner.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.refinement_agent.refinement_agent import RefinementAgent


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Idea Refinement Agent - Turn vague ideas into clear concepts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (prompts for input)
  python scripts/run_refiner.py
  
  # Direct input
  python scripts/run_refiner.py "AI Call Catcher"
  
  # With custom output path
  python scripts/run_refiner.py "AI Call Catcher" --output data/my_refined.json

Workflow:
  1. Enter vague idea ("AI Call Catcher")
  2. Agent refines it ("AI Receptionist for Hair Salons")
  3. Saved to data/refined/refined_ideas.json
  4. Ready to score with Vertical Agent!
        """
    )
    
    parser.add_argument(
        "idea",
        nargs="?",
        help="Raw business idea to refine (or leave blank for interactive)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="data/refined/refined_ideas.json",
        help="Output JSON file path"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔄 IDEA REFINEMENT AGENT")
    print("="*70 + "\n")
    
    # Get idea (from arg or interactive)
    if args.idea:
        raw_idea = args.idea
    else:
        raw_idea = input("💡 Enter your raw startup idea: ").strip()
    
    if not raw_idea:
        print("❌ No idea provided")
        return
    
    # Create agent and run
    agent = RefinementAgent(model=args.model, output_path=args.output)
    refined = agent.run(raw_idea)
    
    # Display results
    print("\n" + "="*70)
    print("✅ REFINEMENT COMPLETE")
    print("="*70 + "\n")
    
    if 'refined_idea' in refined:
        idea_details = refined['refined_idea']
        
        print("📋 Refined Concept:\n")
        print(f"   Name: {idea_details.get('name', 'N/A')}")
        print(f"   Niche: {idea_details.get('niche', 'N/A')}")
        print(f"   Value Prop: {idea_details.get('value_proposition', 'N/A')}")
        print(f"   Target Customer: {idea_details.get('target_customer', 'N/A')}")
        print(f"   Unique Angle: {idea_details.get('unique_angle', 'N/A')}")
    
    if 'critique' in refined:
        print(f"\n💭 Critique:")
        print(f"   {refined['critique']}")
    
    if 'clarifying_questions' in refined and refined['clarifying_questions']:
        print(f"\n❓ Clarifying Questions:")
        for i, q in enumerate(refined['clarifying_questions'], 1):
            print(f"   {i}. {q}")
    
    if 'suggested_refinements' in refined and refined['suggested_refinements']:
        print(f"\n💡 Alternative Refinements:")
        for i, r in enumerate(refined['suggested_refinements'], 1):
            print(f"   {i}. {r}")
    
    if 'next_steps' in refined and refined['next_steps']:
        print(f"\n🚀 Suggested Next Steps:")
        for i, step in enumerate(refined['next_steps'], 1):
            print(f"   {i}. {step}")
    
    print("\n" + "="*70)
    print(f"💾 Saved to: {args.output}")
    print("="*70 + "\n")
    
    print("💡 Next: Score this refined idea")
    print(f"   python scripts/run_vertical_agent.py --from-refined\n")


if __name__ == "__main__":
    main()

