#!/usr/bin/env python3
"""
run_strategic_planner.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Script for Running Strategic Planner Agent

Reads Vertical Agent output and makes strategic decision on which
project to build next.

Usage:
    python scripts/run_strategic_planner.py
    python scripts/run_strategic_planner.py --recommendation outputs/recommendation.md

Location: scripts/run_strategic_planner.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.strategic_planner.strategic_planner import StrategicPlannerAgent


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Strategic Planner Agent - Decides what to build next",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default paths (outputs/recommendation.md)
  python scripts/run_strategic_planner.py
  
  # Specify custom recommendation file
  python scripts/run_strategic_planner.py --recommendation outputs/my_recommendation.md
  
  # Use YAML scores directly
  python scripts/run_strategic_planner.py --scores outputs/vertical_scores.yaml

Typical Workflow:
  1. Run Vertical Agent:
     python scripts/run_vertical_agent.py inputs/ideas.json
     
  2. Run Strategic Planner:
     python scripts/run_strategic_planner.py
     
  3. Check decision:
     cat outputs/strategic_decision.yaml
        """
    )
    
    parser.add_argument(
        "-r", "--recommendation",
        default="outputs/recommendation.md",
        help="Path to Vertical Agent recommendation markdown"
    )
    
    parser.add_argument(
        "-s", "--scores",
        default="outputs/vertical_scores.yaml",
        help="Path to Vertical Agent scores YAML"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="outputs/strategic_decision.yaml",
        help="Where to save strategic decision"
    )
    
    parser.add_argument(
        "--no-invoke",
        action="store_true",
        help="Don't invoke Planning Agent automatically"
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip human approval (auto-approve)"
    )
    
    args = parser.parse_args()
    
    # Create agent
    agent = StrategicPlannerAgent(
        recommendation_path=args.recommendation,
        scores_path=args.scores,
        output_path=args.output,
        interactive=not args.non_interactive  # Interactive by default
    )
    
    # Run
    print("\n" + "="*70)
    print("🧠 STRATEGIC PLANNER AGENT")
    print("="*70 + "\n")
    
    result = agent.run()
    
    # Display result
    if hasattr(result, 'reasoning'):
        print(f"\n💡 Decision: {result.decision.upper()}")
        print(f"📝 Reasoning: {result.reasoning}\n")
    elif isinstance(result, dict):
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}\n")
        else:
            print(f"\n📊 Selected: {result.get('selected_vertical', 'N/A')}")
            print(f"💯 Score: {result.get('score', 0)}")
            print(f"🚦 Proceed: {'YES' if result.get('proceed') else 'NO'}")
            print(f"💡 Reasoning: {result.get('reasoning', 'N/A')}\n")
    
    print("="*70)
    print("✅ Strategic Planning Complete!")
    print("="*70 + "\n")
    
    print("📄 Output saved to:")
    print(f"   - {args.output}")
    print(f"   - logs/strategic_decisions/")


if __name__ == "__main__":
    main()

