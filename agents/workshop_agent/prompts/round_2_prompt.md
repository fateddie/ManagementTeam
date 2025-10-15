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

For each solution, provide:
1. Solution name (concise, actionable)
2. How it addresses the risk (specific mechanism)
3. Risk reduction percentage (0-100%)
4. Implementation cost ($0-$X)
5. Time to implement (weeks)
6. Feasibility score (0-10)
7. Overall score (calculated: risk_reduction × feasibility / (cost + 1))

EVALUATION CRITERIA:
- Prioritize high risk reduction with low cost
- Consider feasibility and time constraints
- Favor solutions that can be tested quickly
- Look for creative, unconventional approaches

OUTPUT FORMAT: JSON
{{
  "risk_being_addressed": {{
    "risk": "...",
    "probability": 0-100,
    "impact": $value,
    "score": calculated
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
      "cons": ["...", "..."]
    }},
    ...5+ solutions
  ],
  "recommended_solution": {{
    "name": "...",
    "reasoning": "Why this is the best choice",
    "expected_outcome": "What will improve"
  }},
  "evolved_idea": {{
    "title": "Updated if changed",
    "description": "Updated with mitigation",
    "target_customer": "Narrowed/focused if applicable",
    "value_proposition": "Enhanced if applicable",
    "changes_made": "Summary of what changed"
  }}
}}
```
