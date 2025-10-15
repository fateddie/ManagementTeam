"""
show_workshop_reasoning.py

Display complete workshop reasoning with all justifications
Shows step-by-step thinking and calculations for transparency

Usage:
    python scripts/show_workshop_reasoning.py "Your idea"
    
Why this script:
    - Makes AI reasoning completely visible
    - Shows all calculations and justifications
    - Enables users to verify and challenge assumptions
    - Demonstrates evidence-based decision making
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.refinement_agent.refinement_agent import RefinementAgent
from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
from core.base_agent import AgentContext
import json


def print_section(title):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subsection(title):
    """Print formatted subsection header."""
    print("\n" + "-"*70)
    print(f"  {title}")
    print("-"*70)


def display_thinking_process(thinking):
    """Display the AI's thinking process."""
    if not thinking:
        return
        
    print("\n🧠 AI THINKING PROCESS:")
    for key, value in thinking.items():
        print(f"\n  {key.replace('_', ' ').title()}:")
        print(f"  {value}")


def display_risk_with_justification(risk, index):
    """Display a risk with complete justification."""
    print(f"\n{index}. {risk.get('risk', 'N/A')}")
    print(f"   Probability: {risk.get('probability', 'N/A')}%")
    if 'probability_justification' in risk:
        print(f"   ├─ Justification: {risk['probability_justification']}")
    
    print(f"\n   Impact: ${risk.get('impact', 0):,}")
    if 'impact_justification' in risk:
        print(f"   ├─ Justification: {risk['impact_justification']}")
    
    print(f"\n   Risk Score: {risk.get('score', 0):,}")
    if 'score_calculation' in risk:
        print(f"   ├─ Calculation: {risk['score_calculation']}")
    
    if 'reasoning' in risk:
        print(f"\n   Why This Risk Matters:")
        print(f"   └─ {risk['reasoning']}")
    
    if 'how_identified' in risk:
        print(f"\n   How Identified:")
        print(f"   └─ {risk['how_identified']}")


def display_solution_with_justification(solution, index):
    """Display a solution with complete justification."""
    print(f"\n{index}. {solution.get('name', 'N/A')}")
    print(f"   {solution.get('description', 'N/A')}")
    
    print(f"\n   Risk Reduction: {solution.get('risk_reduction', 0)}%")
    if 'risk_reduction_justification' in solution:
        print(f"   ├─ Why: {solution['risk_reduction_justification']}")
    
    print(f"\n   Cost: ${solution.get('cost', 0):,}")
    if 'cost_justification' in solution:
        print(f"   ├─ Breakdown: {solution['cost_justification']}")
    
    print(f"\n   Time: {solution.get('time_weeks', 0)} weeks")
    if 'time_justification' in solution:
        print(f"   ├─ Why: {solution['time_justification']}")
    
    print(f"\n   Feasibility: {solution.get('feasibility', 0)}/10")
    print(f"   Score: {solution.get('score', 0)}")
    if 'why_this_score' in solution:
        print(f"   ├─ Calculation: {solution['why_this_score']}")
    
    if 'tradeoff_analysis' in solution:
        print(f"\n   Tradeoffs:")
        print(f"   └─ {solution['tradeoff_analysis']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/show_workshop_reasoning.py \"Your idea\"")
        return
    
    idea = sys.argv[1]
    
    print_section("COMPLETE WORKSHOP REASONING ANALYSIS")
    print(f"\nIdea: {idea}\n")
    
    # Create context and run workflow
    context = AgentContext(
        session_id="reasoning_display",
        inputs={"raw_idea": idea},
        shared_data={}
    )
    
    # Refinement
    print("⏳ Running refinement...")
    ref_agent = RefinementAgent()
    ref_output = ref_agent.execute(context)
    context.shared_data["RefinementAgent"] = ref_output
    
    # Workshop
    print("⏳ Running 3-round workshop with full reasoning...")
    workshop_agent = IterativeWorkshopAgent()
    workshop_output = workshop_agent.execute(context)
    
    # Extract results
    workshop_data = workshop_output.data_for_next_agent
    history = workshop_data.get("workshop_history", {})
    
    # ==========================================
    # ROUND 1: QUICK ASSESSMENT
    # ==========================================
    print_section("ROUND 1: QUICK ASSESSMENT")
    
    round_1 = history.get("round_1", {})
    
    # Show thinking process
    if 'thinking_process' in round_1:
        display_thinking_process(round_1['thinking_process'])
    
    # Show risks with justifications
    print_subsection("TOP 3 RISKS (with full justification)")
    risks = round_1.get("risks", [])
    for i, risk in enumerate(risks[:3], 1):
        display_risk_with_justification(risk, i)
    
    # Show opportunities with justifications
    print_subsection("TOP 3 OPPORTUNITIES (with full justification)")
    opportunities = round_1.get("opportunities", [])
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"\n{i}. {opp.get('opportunity', 'N/A')}")
        print(f"   Potential Value: \${opp.get('potential_value', 0):,}")
        if 'value_justification' in opp:
            print(f"   ├─ Value Justification: {opp['value_justification']}")
        
        print(f"\n   Probability: {opp.get('probability', 0)}%")
        if 'probability_justification' in opp:
            print(f"   ├─ Probability Justification: {opp['probability_justification']}")
    
    # Show viability breakdown
    print_subsection("VIABILITY SCORE BREAKDOWN")
    if 'viability_breakdown' in round_1:
        breakdown = round_1['viability_breakdown']
        total = 0
        for dimension, data in breakdown.items():
            if isinstance(data, dict):
                score = data.get('score', 0)
                reasoning = data.get('reasoning', 'No reasoning provided')
                print(f"\n   {dimension.replace('_', ' ').title()}: {score}/10")
                print(f"   └─ Why: {reasoning}")
                total += score
            else:
                # Old format
                print(f"\n   {dimension.replace('_', ' ').title()}: {data}/10")
                total += data
        
        print(f"\n   TOTAL VIABILITY: {total}/50")
        if 'viability_calculation' in round_1:
            print(f"   └─ Calculation: {round_1['viability_calculation']}")
    
    # ==========================================
    # ROUND 2: RISK MITIGATION
    # ==========================================
    print_section("ROUND 2: RISK MITIGATION")
    
    round_2 = history.get("round_2", {})
    
    # Show thinking process
    if 'thinking_process' in round_2:
        display_thinking_process(round_2['thinking_process'])
    
    # Show risk being addressed
    if 'risk_being_addressed' in round_2:
        risk = round_2['risk_being_addressed']
        print(f"\n🎯 Addressing: {risk.get('risk', 'N/A')}")
        if 'why_biggest_risk' in risk:
            print(f"   └─ Why This Risk: {risk['why_biggest_risk']}")
    
    # Show solutions
    print_subsection("SOLUTIONS GENERATED (with justifications)")
    solutions = round_2.get("solutions", [])
    for i, solution in enumerate(solutions[:5], 1):
        display_solution_with_justification(solution, i)
    
    # Show recommended solution
    if 'recommended_solution' in round_2:
        rec = round_2['recommended_solution']
        print_subsection("RECOMMENDED SOLUTION")
        print(f"\n✅ {rec.get('name', 'N/A')}")
        print(f"\n   Reasoning: {rec.get('reasoning', 'N/A')}")
        if 'why_better_than_alternatives' in rec:
            print(f"\n   Why Better Than Alternatives:")
            print(f"   └─ {rec['why_better_than_alternatives']}")
    
    # Show solution comparison
    if 'solution_comparison' in round_2:
        comp = round_2['solution_comparison']
        print("\n   Decision Logic:")
        for key, value in comp.items():
            print(f"   └─ {key}: {value}")
    
    # ==========================================
    # FINAL RESULTS
    # ==========================================
    print_section("FINAL RESULTS")
    
    print(f"\n📊 Viability Transformation:")
    print(f"   Initial Score: {round_1.get('initial_viability_score', 'N/A')}/50")
    
    round_3 = history.get("round_3", {})
    print(f"   Final Score: {round_3.get('final_viability_score', 'N/A')}/50")
    print(f"   Improvement: {workshop_data.get('improvement', 'N/A')} points")
    
    if 'improvement_justification' in round_3:
        print(f"\n   Improvement Justification:")
        print(f"   └─ {round_3['improvement_justification']}")
    
    print(f"\n💡 Recommendation: {workshop_data.get('recommendation', 'N/A')}")
    if 'recommendation_justification' in round_3:
        print(f"   └─ Why: {round_3['recommendation_justification']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
