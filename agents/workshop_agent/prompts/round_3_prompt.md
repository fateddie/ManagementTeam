# Round 3: Opportunity Capture Prompt

**Why:** Optimizing for the biggest opportunity maximizes potential success. This round identifies strategies to capture maximum value from the best opportunity.

---

## Prompt Template

```
BIGGEST OPPORTUNITY IDENTIFIED:
{opportunity_description}
Potential Value: ${potential_value}
Probability: {probability}%

CURRENT IDEA STATE (after risk mitigation):
{current_idea_json}

YOUR TASK: Generate 5+ strategies to capture this opportunity, evaluate them, and finalize the evolved idea.

REASONING APPROACH (Chain-of-Thought):
Think step-by-step:
1. First, understand WHY this opportunity has high potential
2. Then, brainstorm strategies to maximize value capture
3. Next, evaluate each strategy for ROI and sustainability
4. Consider competitive advantages: what creates a lasting moat?
5. Finally, select the strategy with best risk-adjusted return

For each strategy, explain HOW it captures value and WHY it's sustainable.

STRATEGY REQUIREMENTS:

For each strategy, provide (WITH JUSTIFICATION FOR EVERY NUMBER):
1. Strategy name (concise, actionable)
2. How it captures the opportunity (specific mechanism)
3. Revenue impact (% increase or $value) + JUSTIFY: Show calculation based on market size, pricing, capture rate
4. Implementation cost ($0-$X) + JUSTIFY: Break down all cost components and assumptions
5. Time to value (weeks) + JUSTIFY: Why this timeline? What dependencies exist?
6. ROI (revenue_impact / cost) + SHOW CALCULATION: $revenue / $cost = X:1 ROI. Justify assumptions.
7. Overall score (calculated) + SHOW FORMULA: How did you weight revenue vs cost vs time?
8. Sustainability analysis: Will this advantage last? For how long? What could erode it?

EVALUATION CRITERIA:
- Prioritize high ROI opportunities
- Consider speed to market
- Look for sustainable competitive advantages
- Favor strategies that compound over time

OUTPUT FORMAT: JSON
{{
  "opportunity_being_captured": {{
    "opportunity": "...",
    "potential_value": $value,
    "probability": 0-100
  }},
  "thinking_process": {{
    "understanding_opportunity": "Step-by-step: Why is this opportunity the most valuable? What evidence supports this?",
    "strategy_brainstorming": "Step-by-step: How did I generate these strategies? What approaches did I consider?",
    "evaluation_criteria": "Step-by-step: How did I evaluate ROI? What factors did I weigh?",
    "selection_rationale": "Step-by-step: Why did I recommend this specific strategy over the others?"
  }},
  "strategies": [
    {{
      "name": "...",
      "description": "...",
      "revenue_impact": "% or $value",
      "revenue_justification": "WHY this revenue amount? Show calculation: market size × capture rate × pricing = revenue. Justify each assumption.",
      "cost": $value,
      "cost_justification": "WHY this cost? Break down: development($X) + marketing($Y) + ops($Z) = total. Justify each.",
      "time_weeks": number,
      "time_justification": "WHY this timeline? What factors determine this duration? What could delay it?",
      "roi": calculated,
      "roi_calculation": "Show math: revenue($X) / cost($Y) = ROI(Z:1). Explain assumptions.",
      "score": calculated,
      "score_calculation": "Show formula used and how you weighted factors. Justify the result.",
      "competitive_advantage": "How this creates moat",
      "sustainability": "Will this advantage last? For how long? Why or why not?"
    }},
    ...5+ strategies
  ],
  "recommended_strategy": {{
    "name": "...",
    "reasoning": "Why this maximizes value",
    "expected_outcome": "What will improve"
  }},
  "final_idea": {{
    "title": "Final evolved title",
    "description": "Fully evolved description",
    "target_customer": "Final focused target",
    "value_proposition": "Enhanced value prop",
    "unique_angle": "What makes this different",
    "evolution_summary": "How idea evolved through 3 rounds",
    "why_better_than_original": "Step-by-step comparison: What specific improvements were made? Why do they matter?"
  }},
  "final_viability_breakdown": {{
    "market_attractiveness": {{
      "score": 0-10,
      "change_from_round_1": "+/- X",
      "why_changed": "What improved or worsened? Justify the new score with evidence."
    }},
    "competitive_position": {{
      "score": 0-10,
      "change_from_round_1": "+/- X",
      "why_changed": "What improved or worsened? Justify the new score with evidence."
    }},
    "differentiation": {{
      "score": 0-10,
      "change_from_round_1": "+/- X",
      "why_changed": "What improved or worsened? Justify the new score with evidence."
    }},
    "unit_economics": {{
      "score": 0-10,
      "change_from_round_1": "+/- X",
      "why_changed": "What improved or worsened? Justify the new score with evidence."
    }},
    "technical_feasibility": {{
      "score": 0-10,
      "change_from_round_1": "+/- X",
      "why_changed": "What improved or worsened? Justify the new score with evidence."
    }}
  }},
  "final_viability_score": 0-50,
  "viability_calculation": "Show calculation: market(X) + competitive(X) + differentiation(X) + economics(X) + technical(X) = final score",
  "viability_improvement": "+X points from initial",
  "improvement_justification": "WHY did the score improve? What specific changes caused each point increase? Show the math.",
  "recommendation": "GO / CONDITIONAL GO / ITERATE MORE / NO-GO",
  "recommendation_justification": "WHY this recommendation? What specific factors led to this decision? What thresholds did I use?"
}}
```
