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

STRATEGY REQUIREMENTS:

For each strategy, provide:
1. Strategy name (concise, actionable)
2. How it captures the opportunity (specific mechanism)
3. Revenue impact (% increase or $value)
4. Implementation cost ($0-$X)
5. Time to value (weeks)
6. ROI (revenue_impact / cost)
7. Overall score (calculated: revenue_impact × probability / (cost + time))

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
  "strategies": [
    {{
      "name": "...",
      "description": "...",
      "revenue_impact": "% or $value",
      "cost": $value,
      "time_weeks": number,
      "roi": calculated,
      "score": calculated,
      "competitive_advantage": "How this creates moat"
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
    "evolution_summary": "How idea evolved through 3 rounds"
  }},
  "final_viability_score": 0-50,
  "viability_improvement": "+X points from initial",
  "recommendation": "GO / CONDITIONAL GO / ITERATE MORE / NO-GO"
}}
```
