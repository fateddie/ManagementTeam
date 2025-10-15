"""
view_last_workshop_results.py

Display detailed workshop analysis from last session
Shows all 3 rounds with risks, opportunities, solutions, and strategies

Usage:
    python scripts/view_last_workshop_results.py
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("\n" + "="*70)
    print("📊 DETAILED WORKSHOP ANALYSIS - Last Session")
    print("="*70 + "\n")
    
    # Since we don't have persistent storage yet, let's run a fresh analysis
    # with the same idea to show the detailed output
    
    from agents.refinement_agent.refinement_agent import RefinementAgent
    from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
    from core.base_agent import AgentContext
    
    idea = "Personal assistant app with email management, calendar, life coaching, fitness coaching, and voice interaction"
    
    # Create context
    context = AgentContext(
        session_id="detailed_view_001",
        inputs={"raw_idea": idea},
        shared_data={}
    )
    
    # Step 1: Refinement
    print("Step 1: Refining idea...")
    refinement_agent = RefinementAgent()
    refinement_output = refinement_agent.execute(context)
    context.shared_data["RefinementAgent"] = refinement_output
    
    refined_data = refinement_output.data_for_next_agent
    
    print("\n" + "="*70)
    print("📋 REFINED IDEA")
    print("="*70)
    print(f"\nTitle: {refined_data.get('title', 'N/A')}")
    print(f"Description: {refined_data.get('description', 'N/A')}")
    print(f"Target Customer: {refined_data.get('target_customer', 'N/A')}")
    print(f"Value Proposition: {refined_data.get('value_proposition', 'N/A')}")
    print(f"Niche: {refined_data.get('niche', 'N/A')}")
    
    # Step 2: Workshop
    print("\n" + "="*70)
    print("🧠 WORKSHOP ANALYSIS")
    print("="*70)
    
    workshop_agent = IterativeWorkshopAgent()
    workshop_output = workshop_agent.execute(context)
    workshop_data = workshop_output.data_for_next_agent
    
    # Display Round 1 results
    print("\n" + "-"*70)
    print("ROUND 1: QUICK ASSESSMENT")
    print("-"*70)
    
    history = workshop_data.get("workshop_history", {})
    round_1 = history.get("round_1", {})
    
    print(f"\n🚨 TOP 3 RISKS:")
    for i, risk in enumerate(round_1.get("risks", []), 1):
        print(f"\n{i}. {risk.get('risk', 'N/A')}")
        print(f"   Probability: {risk.get('probability', 0)}%")
        print(f"   Impact: ${risk.get('impact', 0):,}")
        print(f"   Risk Score: {risk.get('score', 0)}")
        if 'reasoning' in risk:
            print(f"   Reasoning: {risk.get('reasoning', 'N/A')}")
    
    print(f"\n🚀 TOP 3 OPPORTUNITIES:")
    for i, opp in enumerate(round_1.get("opportunities", []), 1):
        print(f"\n{i}. {opp.get('opportunity', 'N/A')}")
        print(f"   Potential Value: ${opp.get('potential_value', 0):,}")
        print(f"   Probability: {opp.get('probability', 0)}%")
        if 'reasoning' in opp:
            print(f"   Reasoning: {opp.get('reasoning', 'N/A')}")
    
    print(f"\n📊 INITIAL VIABILITY SCORE: {round_1.get('initial_viability_score', 'N/A')}/50")
    if 'viability_breakdown' in round_1:
        breakdown = round_1['viability_breakdown']
        print(f"\n   Breakdown:")
        print(f"   - Market Attractiveness: {breakdown.get('market_attractiveness', 0)}/10")
        print(f"   - Competitive Position: {breakdown.get('competitive_position', 0)}/10")
        print(f"   - Differentiation: {breakdown.get('differentiation', 0)}/10")
        print(f"   - Unit Economics: {breakdown.get('unit_economics', 0)}/10")
        print(f"   - Technical Feasibility: {breakdown.get('technical_feasibility', 0)}/10")
    
    if 'key_insight' in round_1:
        print(f"\n💡 Key Insight: {round_1.get('key_insight', 'N/A')}")
    
    # Display Round 2 results
    print("\n" + "-"*70)
    print("ROUND 2: RISK MITIGATION")
    print("-"*70)
    
    round_2 = history.get("round_2", {})
    
    if 'risk_being_addressed' in round_2:
        risk = round_2['risk_being_addressed']
        print(f"\n🎯 Addressing Risk: {risk.get('risk', 'N/A')}")
        print(f"   Score: {risk.get('score', 0)}")
    
    print(f"\n💡 SOLUTIONS GENERATED:")
    for i, solution in enumerate(round_2.get("solutions", []), 1):
        print(f"\n{i}. {solution.get('name', 'N/A')}")
        print(f"   Description: {solution.get('description', 'N/A')}")
        print(f"   Risk Reduction: {solution.get('risk_reduction', 0)}%")
        print(f"   Cost: ${solution.get('cost', 0):,}")
        print(f"   Time: {solution.get('time_weeks', 0)} weeks")
        print(f"   Feasibility: {solution.get('feasibility', 0)}/10")
        print(f"   Score: {solution.get('score', 0)}")
    
    if 'recommended_solution' in round_2:
        rec = round_2['recommended_solution']
        print(f"\n✅ RECOMMENDED SOLUTION: {rec.get('name', 'N/A')}")
        print(f"   Reasoning: {rec.get('reasoning', 'N/A')}")
        print(f"   Expected Outcome: {rec.get('expected_outcome', 'N/A')}")
    
    # Display Round 3 results
    print("\n" + "-"*70)
    print("ROUND 3: OPPORTUNITY CAPTURE")
    print("-"*70)
    
    round_3 = history.get("round_3", {})
    
    if 'opportunity_being_captured' in round_3:
        opp = round_3['opportunity_being_captured']
        print(f"\n🎯 Capturing Opportunity: {opp.get('opportunity', 'N/A')}")
        print(f"   Potential Value: ${opp.get('potential_value', 0):,}")
    
    print(f"\n💡 STRATEGIES GENERATED:")
    for i, strategy in enumerate(round_3.get("strategies", []), 1):
        print(f"\n{i}. {strategy.get('name', 'N/A')}")
        print(f"   Description: {strategy.get('description', 'N/A')}")
        print(f"   Revenue Impact: {strategy.get('revenue_impact', 'N/A')}")
        print(f"   Cost: ${strategy.get('cost', 0):,}")
        print(f"   Time: {strategy.get('time_weeks', 0)} weeks")
        print(f"   ROI: {strategy.get('roi', 0):.1f}:1")
        print(f"   Score: {strategy.get('score', 0)}")
    
    if 'recommended_strategy' in round_3:
        rec = round_3['recommended_strategy']
        print(f"\n✅ RECOMMENDED STRATEGY: {rec.get('name', 'N/A')}")
        print(f"   Reasoning: {rec.get('reasoning', 'N/A')}")
        print(f"   Expected Outcome: {rec.get('expected_outcome', 'N/A')}")
    
    # Final Summary
    print("\n" + "="*70)
    print("🎯 FINAL RESULTS")
    print("="*70)
    
    print(f"\n📊 Viability Scores:")
    print(f"   Initial: {round_1.get('initial_viability_score', 'N/A')}/50")
    print(f"   Final: {round_3.get('final_viability_score', 'N/A')}/50")
    print(f"   Improvement: {round_3.get('viability_improvement', 'N/A')}")
    
    print(f"\n💡 Recommendation: {round_3.get('recommendation', workshop_data.get('recommendation', 'N/A'))}")
    
    print(f"\n📝 Evolved Idea:")
    evolved = round_3.get("final_idea", workshop_data.get("evolved_idea", {}))
    print(f"   Title: {evolved.get('title', 'N/A')}")
    print(f"   Target: {evolved.get('target_customer', 'N/A')}")
    print(f"   Value Prop: {evolved.get('value_proposition', 'N/A')}")
    if 'evolution_summary' in evolved:
        print(f"\n   Evolution Summary: {evolved.get('evolution_summary', 'N/A')}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
