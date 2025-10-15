"""
run_idea_to_project.py

Complete Idea-to-Project Workflow with Workshop Integration
Phase 2 - Orchestrator Integration

Purpose:
    Execute the complete pipeline from raw idea to project creation:
    1. RefinementAgent - Turn vague idea into clear concept
    2. IterativeWorkshopAgent - Evolve idea through 3-round methodology
    3. VerticalAgent - RICE scoring
    4. OpportunityRankingAgent - 7-criteria weighted scoring
    5. StrategicPlannerAgent - Final planning and project creation

Why This Script:
    - Provides single entry point for complete workflow
    - Enables testing of full integration
    - Shows workshop agent in context of complete pipeline
    - Validates data flow between all agents

Reasoning for Design:
    - Uses orchestrator's existing agent loading and sequencing
    - Workshop agent automatically runs at stage 1.5 (after refinement)
    - Maintains separation of concerns (orchestrator handles execution)
    - Enables easy testing and debugging of complete workflow

Usage:
    python scripts/run_idea_to_project.py "My raw business idea"
    python scripts/run_idea_to_project.py  # Interactive mode

Created: 2025-01-XX
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.refinement_agent.refinement_agent import RefinementAgent
from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
from core.base_agent import AgentContext, AgentOutput
from core.cache import Cache


def main():
    """
    Execute complete idea-to-project workflow.
    
    Why separate script:
    - Provides dedicated entry point for idea workflow
    - Allows custom configuration for idea processing
    - Enables workflow-specific logging and reporting
    - Simplifies testing and debugging
    """
    parser = argparse.ArgumentParser(
        description="Complete Idea-to-Project Workflow with Workshop Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/run_idea_to_project.py
  
  # Direct input
  python scripts/run_idea_to_project.py "AI-powered email assistant for entrepreneurs"
  
  # With custom output
  python scripts/run_idea_to_project.py "My idea" --output my_project

Workflow:
  1. Refinement - Vague idea → Clear concept
  2. Workshop - Clear concept → Evolved viable idea (NEW!)
  3. Vertical - RICE scoring
  4. Ranking - 7-criteria weighted scoring
  5. Planning - Project creation

The Workshop stage (NEW) uses:
  - Real-time market data from Perplexity
  - 3-round methodology (Assessment → Risk → Opportunity)
  - Expert MBA + founder persona
  - Chain-of-Thought reasoning for better analysis
        """
    )
    
    parser.add_argument(
        "idea",
        nargs="?",
        help="Raw business idea to process (or leave blank for interactive)"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="Output project name (default: auto-generated from idea)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🚀 IDEA-TO-PROJECT WORKFLOW")
    print("   with Iterative Workshop Integration")
    print("="*70 + "\n")
    
    # Get idea (from arg or interactive)
    if args.idea:
        raw_idea = args.idea
    else:
        print("💡 Enter your raw business idea:")
        raw_idea = input("> ").strip()
    
    if not raw_idea:
        print("❌ No idea provided")
        return
    
    print(f"\n📝 Processing: '{raw_idea}'\n")
    
    # Create session context
    # Why: AgentContext enables data sharing between agents
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    context = AgentContext(
        session_id=session_id,
        inputs={"raw_idea": raw_idea},
        cache=Cache() if Cache else None,
        shared_data={}
    )
    
    print("🔄 Workflow sequence:")
    print("   1. RefinementAgent - Turn vague idea into clear concept")
    print("   2. IterativeWorkshopAgent - Evolve idea through 3-round methodology (NEW!)")
    print("   3. [Future: VerticalAgent, OpportunityRankingAgent, StrategicPlannerAgent]")
    
    print("\n" + "="*70)
    print("⚙️  EXECUTING WORKFLOW")
    print("="*70 + "\n")
    
    # STEP 1: Refinement
    # Why: Workshop needs refined idea with clear problem, customer, value prop
    print("▶️  Step 1: RefinementAgent")
    refinement_agent = RefinementAgent()
    refinement_output = refinement_agent.execute(context)
    context.shared_data["RefinementAgent"] = refinement_output
    
    print(f"   ✅ Refined to: {refinement_output.data_for_next_agent.get('title', 'N/A')}")
    print(f"   Confidence: {refinement_output.confidence:.2f}\n")
    
    # STEP 2: Workshop (NEW!)
    # Why: Iteratively improve idea through risk mitigation and opportunity capture
    print("▶️  Step 2: IterativeWorkshopAgent (NEW!)")
    print("   🧠 Running 3-round iterative workshop...")
    print("      Round 1: Quick Assessment with real-time market data")
    print("      Round 2: Risk Mitigation with solution generation")
    print("      Round 3: Opportunity Capture with strategy optimization\n")
    
    workshop_agent = IterativeWorkshopAgent()
    workshop_output = workshop_agent.execute(context)
    context.shared_data["IterativeWorkshopAgent"] = workshop_output
    
    # Display workshop results
    workshop_data = workshop_output.data_for_next_agent
    
    print(f"   ✅ Workshop Complete!")
    print(f"   Original Viability: {workshop_data.get('workshop_history', {}).get('round_1', {}).get('initial_viability_score', 'N/A')}/50")
    print(f"   Final Viability: {workshop_data.get('viability_score', 'N/A')}/50")
    print(f"   Improvement: +{workshop_data.get('improvement', 'N/A')} points")
    print(f"   Recommendation: {workshop_data.get('recommendation', 'N/A')}")
    print(f"   Confidence: {workshop_output.confidence:.2f}\n")
    
    if 'evolved_idea' in workshop_data:
        evolved = workshop_data['evolved_idea']
        print(f"📊 Evolved Idea:")
        print(f"   Title: {evolved.get('title', 'N/A')}")
        print(f"   Target: {evolved.get('target_customer', 'N/A')}")
        print(f"   Value Prop: {evolved.get('value_proposition', 'N/A')[:80]}...")
    
    print("\n" + "="*70)
    print("✅ WORKFLOW COMPLETE")
    print("="*70 + "\n")
    
    print("📁 Results:")
    print("   - Refined idea + Workshop analysis available in memory")
    print("   - logs/workshop_agent.log - Workshop execution log")
    print("   - Ready for: VerticalAgent, OpportunityRankingAgent (future integration)")


if __name__ == "__main__":
    main()
