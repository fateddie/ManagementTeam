#!/usr/bin/env python3
"""
run_vertical_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Wrapper for Vertical Agent with JSON Input

Accepts a JSON file containing business vertical ideas and runs
the Vertical Agent evaluation.

Usage:
    python scripts/run_vertical_agent.py inputs/verticals.json
    python scripts/run_vertical_agent.py inputs/verticals.json --framework ICE

Location: scripts/run_vertical_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import yaml
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.vertical_agent.vertical_agent import run_vertical_agent


def load_input_file(file_path: str):
    """
    Load verticals from JSON or YAML file.
    
    Args:
        file_path: Path to input file
        
    Returns:
        List of vertical dicts
    """
    path = Path(file_path)
    
    if not path.exists():
        print(f"❌ Error: File not found: {file_path}")
        sys.exit(1)
    
    # Determine file type
    if path.suffix.lower() == '.json':
        with open(path, 'r') as f:
            data = json.load(f)
    elif path.suffix.lower() in ['.yaml', '.yml']:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    else:
        print(f"❌ Error: Unsupported file type. Use .json, .yaml, or .yml")
        sys.exit(1)
    
    # Handle both formats:
    # {"verticals": [...]} or just [...]
    if isinstance(data, dict) and 'verticals' in data:
        return data['verticals']
    elif isinstance(data, list):
        return data
    else:
        print(f"❌ Error: Invalid file format. Expected list or dict with 'verticals' key")
        sys.exit(1)


def print_result(result: dict):
    """
    Pretty print the evaluation result.
    
    Args:
        result: Result dict from run_vertical_agent
    """
    print("\n" + "="*70)
    print("🎯 VERTICAL AGENT EVALUATION RESULT")
    print("="*70 + "\n")
    
    # Handle errors
    if "error" in result:
        print("❌ Error:", result["error"])
        if "missing" in result:
            print("\n   Missing data for:")
            for item in result["missing"]:
                print(f"   - {item}")
        if "action" in result:
            print(f"\n💡 Action: {result['action']}")
        print()
        return
    
    # Display summary
    print("🔍 Summary:")
    print(f"   {result.get('summary', 'No summary available')}\n")
    
    # Display top choice details
    if 'top_choice' in result and result['top_choice']:
        top = result['top_choice']
        print("─"*70)
        print("\n🏆 TOP CHOICE DETAILS:\n")
        print(f"   Name:       {top['name']}")
        print(f"   Score:      {top['score']}")
        print(f"   Reach:      {top['reach']}/10")
        print(f"   Impact:     {top['impact']}/10")
        print(f"   Confidence: {top['confidence']}/10")
        print(f"   Effort:     {top['effort']}/10")
        if 'description' in top:
            print(f"   Details:    {top['description']}")
    
    # Display proactive suggestions
    if "proactive_notes" in result and result["proactive_notes"]:
        print("\n" + "─"*70)
        print("\n🧠 PROACTIVE INSIGHTS:\n")
        for i, note in enumerate(result["proactive_notes"], start=1):
            # Wrap long lines
            lines = note.split('. ')
            if len(lines) > 1:
                print(f"   {i}. {lines[0]}.")
                for line in lines[1:]:
                    if line.strip():
                        print(f"      {line.strip()}{'.' if not line.endswith('.') else ''}")
            else:
                print(f"   {i}. {note}")
    
    # Display alternatives
    if 'alternatives' in result and result['alternatives']:
        print("\n" + "─"*70)
        print("\n🥈 ALTERNATIVE OPTIONS:\n")
        for i, alt in enumerate(result['alternatives'], start=1):
            print(f"   {i}. {alt['name']:<25} Score: {alt['score']}")
    
    print("\n" + "="*70)
    print("✅ Evaluation Complete!")
    print("="*70 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run the Vertical Agent with business idea evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate from JSON file
  python scripts/run_vertical_agent.py inputs/verticals.json
  
  # Evaluate from YAML file
  python scripts/run_vertical_agent.py inputs/verticals.yaml
  
  # Use ICE scoring instead of RICE
  python scripts/run_vertical_agent.py inputs/verticals.json --framework ICE
  
  # View verbose output
  python scripts/run_vertical_agent.py inputs/verticals.json --verbose
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Path to JSON or YAML file containing list of verticals"
    )
    
    parser.add_argument(
        "-f", "--framework",
        choices=["RICE", "ICE"],
        default="RICE",
        help="Scoring framework to use (default: RICE)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output including full ranking"
    )
    
    args = parser.parse_args()
    
    # Load input
    print(f"\n📂 Loading verticals from: {args.input_file}")
    ideas = load_input_file(args.input_file)
    print(f"✅ Loaded {len(ideas)} vertical ideas\n")
    
    # Run evaluation
    print(f"🔄 Evaluating using {args.framework} framework...")
    result = run_vertical_agent(ideas, framework=args.framework)
    
    # Display result
    print_result(result)
    
    # Show full ranking if verbose
    if args.verbose and 'all_ranked' in result:
        print("📊 FULL RANKING:\n")
        for i, vertical in enumerate(result['all_ranked'], start=1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {medal} {i}. {vertical['name']:<25} Score: {vertical['score']:>8.2f}")
        print()
    
    # Show where recommendation was saved
    output_file = Path("./outputs/recommendation.md")
    if output_file.exists():
        print(f"📄 Full recommendation saved to: {output_file}\n")


if __name__ == "__main__":
    main()

