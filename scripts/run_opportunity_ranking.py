#!/usr/bin/env python3
"""
run_opportunity_ranking.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Script for Opportunity Ranking Agent

Usage:
    python scripts/run_opportunity_ranking.py
    python scripts/run_opportunity_ranking.py --input data/my_ideas.json
    
Location: scripts/run_opportunity_ranking.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.opportunity_ranking.opportunity_ranking_agent import OpportunityRankingAgent


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Opportunity Ranking Agent - Advanced Weighted Scoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default paths
  python scripts/run_opportunity_ranking.py
  
  # Custom input file
  python scripts/run_opportunity_ranking.py --input data/my_ideas.json
  
  # Custom weights
  python scripts/run_opportunity_ranking.py --weights config/my_weights.yaml
  
  # Full custom
  python scripts/run_opportunity_ranking.py \\
    --input data/opportunity/idea_blocks.json \\
    --weights config/weights/weight_config.yaml \\
    --output results/opportunity_report.md
        """
    )
    
    parser.add_argument(
        "--input",
        default="data/opportunity/idea_blocks.json",
        help="Path to idea blocks JSON file"
    )
    
    parser.add_argument(
        "--weights",
        default="config/weights/weight_config.yaml",
        help="Path to weight configuration YAML"
    )
    
    parser.add_argument(
        "--output",
        default="results/opportunity_report.md",
        help="Path to output markdown report"
    )
    
    args = parser.parse_args()
    
    # Create and run agent
    print("\n" + "="*70)
    print("📊 OPPORTUNITY RANKING AGENT")
    print("="*70 + "\n")
    
    agent = OpportunityRankingAgent(
        ideas_path=args.input,
        weights_path=args.weights,
        output_path=args.output
    )
    
    result = agent.run()
    
    # Display top result
    if hasattr(result, 'reasoning'):
        print(f"\n💡 {result.reasoning}\n")
    
    print("="*70)
    print("✅ Ranking Complete!")
    print("="*70 + "\n")
    
    print("📄 Outputs generated:")
    print(f"   - {args.output}")
    print(f"   - results/ranked_opportunities.json\n")


if __name__ == "__main__":
    main()

