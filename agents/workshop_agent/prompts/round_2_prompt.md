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

REASONING APPROACH (Two-Step Process):

STEP 1 - WRITE YOUR BRAINSTORMING IN PLAIN ENGLISH:

Talk through your thinking naturally:
- "This risk is critical because [specific example from real company]..."
- "Looking at how Startup X solved this, they did Y and it cost $Z..."
- "Solution 1 could work because [specific mechanism]... but it would cost $X because we'd need to [specific breakdown]..."
- "I'm comparing Solution A (high cost, high certainty) vs Solution B (low cost, uncertain)..."
- "The tradeoff here is: we save $10K but risk taking 3 months longer because..."

Example: "Okay, the biggest risk is competing with Google Calendar. They have 1B users and it's free. Looking at how Motion.ai survived, they charge $30/month and focus on AI scheduling - not trying to beat Google at calendar, but adding AI on top. Superhuman did similar with email - they don't compete with Gmail, they enhance it. So one solution is 'Don't compete with Google - enhance their product'. This would cost maybe $20K for integration development (2 months × $10K/month). Risk reduction would be high (80%) because we're not fighting Google, we're riding with them..."

Write 2-3 paragraphs of natural reasoning for each solution.

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
  "raw_analysis": "YOUR PLAIN-ENGLISH BRAINSTORMING (2-3 paragraphs). Include specific examples like: 'Looking at how Motion.ai solved competing with Google, they...' or 'Superhuman charges $30/month for email enhancement because...' Name real companies and show your actual thinking process.",
  
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
      "risk_reduction_justification": {{
        "question_1_mechanism": "HOW does this solution reduce the risk? Be specific about the mechanism.",
        "question_2_evidence": "What evidence/data supports this % reduction? Cite comparable examples.",
        "question_3_assumptions": "What must be true for this reduction to work? List all assumptions.",
        "question_4_validation": "How would you test/validate this reduction estimate?"
      }},
      "cost": $value,
      "cost_justification": {{
        "question_1_labor": "Labor costs: How many hours × $hourly rate = $X?",
        "question_2_tools": "Tools/software needed: What costs? Why?",
        "question_3_external": "External costs (consulting, services): What and why?",
        "question_4_contingency": "Contingency buffer: What % added? Why?",
        "question_5_total": "Show: labor + tools + external + contingency = total cost"
      }},
      "time_weeks": number,
      "time_justification": {{
        "question_1_tasks": "What are the major tasks? How long for each?",
        "question_2_dependencies": "What dependencies could delay this? How likely?",
        "question_3_resources": "How many people working on this? Full-time or part-time?",
        "question_4_comparable": "How long did similar solutions take for other startups? Cite examples."
      }},
      "feasibility": 0-10,
      "feasibility_justification": {{
        "question_1_resources": "Do we have the resources/skills? What's missing?",
        "question_2_complexity": "How complex is this technically? What makes it easy/hard?",
        "question_3_risks": "What could prevent successful implementation?",
        "question_4_precedent": "Has anyone done this before? What happened?"
      }},
      "score": calculated,
      "score_formula": "Show exact formula: risk_reduction(X) × feasibility(Y) / (cost($Z) + 1) = score",
      "pros": ["...", "..."],
      "cons": ["...", "..."],
      "tradeoff_analysis": {{
        "what_you_gain": "Specific benefits with quantified impact",
        "what_you_sacrifice": "Specific costs/downsides with quantified impact",
        "net_value": "Gains ($X) - Sacrifices ($Y) = Net Value ($Z)"
      }}
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
