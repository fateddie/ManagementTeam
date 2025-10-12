#!/usr/bin/env python3
"""
run_refine_and_score.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Integrated Refinement + Scoring Pipeline

Takes a vague idea, refines it, then scores it automatically.

Usage:
    python scripts/run_refine_and_score.py "AI Call Catcher"
    
Location: scripts/run_refine_and_score.py
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
from cli.utils.scoring_prompts import score_idea


def main():
    """Integrated refinement and scoring pipeline."""
    parser = argparse.ArgumentParser(
        description="Refine and score a startup idea in one go",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Refine and score a vague idea
  python scripts/run_refine_and_score.py "AI Call Catcher"
  
  # Interactive mode
  python scripts/run_refine_and_score.py
  
  # Custom model
  python scripts/run_refine_and_score.py "AI Call Catcher" --model gpt-4

Workflow:
  1. Refine: Vague idea → Clear concept
  2. Score: Clear concept → Quantitative evaluation
  3. Save: Both refinement and scores saved
        """
    )
    
    parser.add_argument(
        "idea",
        nargs="?",
        help="The raw idea to refine and score"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔄 INTEGRATED REFINEMENT + SCORING PIPELINE")
    print("="*70 + "\n")
    
    # Get idea (from arg or interactive)
    if args.idea:
        raw_idea = args.idea
    else:
        raw_idea = input("💡 Enter your raw startup idea: ").strip()
    
    if not raw_idea:
        print("❌ No idea provided")
        return
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Refinement
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("="*70)
    print("🧠 STEP 1: Refining Idea")
    print("="*70 + "\n")
    
    refiner = RefinementAgent(model=args.model)
    refined = refiner.refine_idea(raw_idea)
    
    # Display refinement results
    if 'refined_idea' in refined:
        refined_concept = refined['refined_idea']
        
        print("📌 Refined Output:\n")
        for key, value in refined_concept.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Save refined idea
    refiner.save_refined_idea(refined)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Scoring
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print("\n" + "="*70)
    print("📊 STEP 2: Scoring Refined Idea")
    print("="*70 + "\n")
    
    scores = score_idea(refined.get('refined_idea', {}), model=args.model)
    
    # Display scores
    print("📈 Score Breakdown:\n")
    
    score_items = [k for k in scores.keys() if k not in ["Comments", "Verdict", "Overall_Score"]]
    for criterion in score_items:
        score_val = scores.get(criterion, 0)
        print(f"   {criterion.replace('_', ' ')}: {score_val}/10")
    
    if 'Overall_Score' in scores:
        print(f"\n   ━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"   🎯 Overall Score: {scores['Overall_Score']}/60")
        print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if 'Verdict' in scores:
        print(f"\n💡 Verdict: {scores['Verdict']}")
    
    # Show comments if available
    if 'Comments' in scores and scores['Comments']:
        print(f"\n💬 Detailed Comments:")
        for criterion, comment in scores['Comments'].items():
            if comment:
                print(f"   • {criterion}: {comment}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Save Everything
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Save scores
    Path("data/scores").mkdir(parents=True, exist_ok=True)
    
    combined_result = {
        "original_idea": raw_idea,
        "refined": refined,
        "scores": scores,
        "timestamp": refined.get('refined_at', '')
    }
    
    with open("data/scores/last_score.json", "w") as f:
        json.dump(combined_result, f, indent=2)
    
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETE")
    print("="*70 + "\n")
    
    print("📁 Results saved to:")
    print("   ✅ data/refined/refined_ideas.json (refinement)")
    print("   ✅ data/scores/last_score.json (scores + refinement)\n")
    
    print("🚀 Next Steps:")
    print("   1. Review the refined concept above")
    print("   2. Address clarifying questions if needed")
    print("   3. Feed to Vertical Agent for RICE scoring")
    print("   4. Or continue to Strategic Planner\n")


if __name__ == "__main__":
    main()

