# Round 2: Risk Mitigation Prompt

**Why:** Addressing the biggest risk dramatically improves idea viability. This round generates multiple solutions, evaluates them objectively, and applies the best one to evolve the idea.

---

## Prompt Template

```
BIGGEST RISK IDENTIFIED:
{risk_description}
Probability: {probability}%
Impact: ${impact}
Score: {score}

CURRENT IDEA STATE:
{current_idea_json}

YOUR TASK: Generate 5+ solutions to address this risk, evaluate them, and recommend the best one.

REASONING APPROACH (Chain-of-Thought):
Think step-by-step:
1. First, deeply understand WHY this risk is critical
2. Then, brainstorm diverse solutions (conventional + creative)
3. Next, evaluate each solution objectively across multiple criteria
4. Consider tradeoffs: risk reduction vs cost vs time vs feasibility
5. Finally, recommend the best solution with clear reasoning

For each solution, explain WHY it works and what tradeoffs exist.

SOLUTION REQUIREMENTS:

For each solution, provide (WITH JUSTIFICATION FOR EVERY NUMBER):
1. Solution name (concise, actionable)
2. How it addresses the risk (specific mechanism)
3. Risk reduction percentage (0-100%) + JUSTIFY: Why this %? What evidence?
4. Implementation cost ($0-$X) + JUSTIFY: Show breakdown and assumptions
5. Time to implement (weeks) + JUSTIFY: Why this duration? What drives timeline?
6. Feasibility score (0-10) + JUSTIFY: Why this score? What makes it easy/hard?
7. Overall score (calculated) + SHOW CALCULATION: risk_reduction × feasibility / (cost + 1)
8. Tradeoff analysis: What do you gain vs sacrifice with this solution?

EVALUATION CRITERIA:
- Prioritize high risk reduction with low cost
- Consider feasibility and time constraints
- Favor solutions that can be tested quickly
- Look for creative, unconventional approaches

OUTPUT FORMAT: JSON (SHOW YOUR THINKING AT EACH STEP)
{{
  "thinking_process": {{
    "understanding_risk": "Step-by-step: Why is this risk critical? What makes it the biggest threat?",
    "solution_brainstorming": "Step-by-step: How did I generate these solutions? What approaches did I consider?",
    "evaluation_criteria": "Step-by-step: How did I evaluate each solution? What tradeoffs did I consider?",
    "selection_rationale": "Step-by-step: Why did I recommend this specific solution over the others?"
  }},
  "risk_being_addressed": {{
    "risk": "...",
    "probability": 0-100,
    "impact": $value,
    "score": calculated,
    "why_biggest_risk": "Explain step-by-step why this is the biggest threat to success"
  }},
  "solutions": [
    {{
      "name": "...",
      "description": "...",
      "risk_reduction": 0-100,
      "cost": $value,
      "time_weeks": number,
      "feasibility": 0-10,
      "score": calculated,
      "pros": ["...", "..."],
      "cons": ["...", "..."],
      "why_this_score": "Explain step-by-step: How did I calculate this score? What factors did I weigh?",
      "tradeoff_analysis": "What are the tradeoffs? What do you gain vs what do you sacrifice?"
    }},
    ...5+ solutions
  ],
  "solution_comparison": {{
    "why_not_highest_risk_reduction": "If recommended solution isn't highest risk reduction, explain why",
    "why_not_lowest_cost": "If recommended solution isn't lowest cost, explain why",
    "final_decision_logic": "Step-by-step: How did I weigh all factors to reach this decision?"
  }},
  "recommended_solution": {{
    "name": "...",
    "reasoning": "Detailed step-by-step explanation of why this is the best choice",
    "expected_outcome": "What will improve",
    "why_better_than_alternatives": "Specifically compare to other top solutions and explain why this wins"
  }},
  "evolved_idea": {{
    "title": "Updated if changed",
    "description": "Updated with mitigation",
    "target_customer": "Narrowed/focused if applicable",
    "value_proposition": "Enhanced if applicable",
    "changes_made": "Summary of what changed",
    "why_these_changes": "Step-by-step justification for each change made to the idea"
  }},
  "impact_assessment": {{
    "risk_score_before": "X (from Round 1)",
    "estimated_risk_score_after": "Y (after mitigation)",
    "reduction_calculation": "Show math: X - Y = reduction. Justify the new score.",
    "confidence_in_mitigation": "0-100% - How confident am I this mitigation will work? Why?"
  }}
}}
```
