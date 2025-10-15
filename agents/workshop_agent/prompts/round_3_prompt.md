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

REASONING APPROACH (Two-Step Process):

STEP 1 - WRITE YOUR STRATEGY ANALYSIS IN PLAIN ENGLISH:

Talk through your thinking:
- "This opportunity is valuable because [cite specific market data]..."
- "Looking at how Superhuman captured the premium email market, they did X and achieved $20M ARR..."
- "Strategy 1 would generate revenue of $X because: market size ($Y) × our capture rate (Z%) × pricing ($A) = $X..."
- "This would cost $B because: we need developers ($C), marketing ($D), and operations ($E)..."
- "ROI calculation: $X revenue / $B cost = Y:1 ROI. Payback in Z months..."

Example: "The AI integration opportunity is worth $20M because the AI productivity market is $4.2B growing at 18% CAGR (from Perplexity data). We could capture 0.5% = $21M potential. To capture this, Strategy 1 is 'AI-powered email prioritization'. This would increase ARPU from $25 to $40 (+$15) because users pay premium for AI features (see Superhuman at $30/month vs Gmail at $0). With 1000 users, that's +$15K/month = $180K/year revenue. Cost would be $50K (AI development 500 hours × $100/hr). ROI = $180K / $50K = 3.6:1..."

Write 2-3 paragraphs explaining your reasoning with specific numbers and examples.

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
  "raw_analysis": "YOUR PLAIN-ENGLISH STRATEGY ANALYSIS (2-3 paragraphs). Show your actual thinking with specific examples, calculations, and comparisons to real companies. Example from above.",
  
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
      "revenue_justification": "Show calculation: Market size ($X) × Capture rate (Y%) × ARPU ($Z/mo) × 12 months = $ABC Year 1 revenue. Compare to competitor benchmarks from Perplexity data.",
      "cost": $value,
      "cost_justification": "Solo founder costs: Development (X hours × $0 your time = $0-500 tools/APIs) + Marketing ($Y) = Total $Z. Show breakdown.",
      "time_weeks": number,
      "time_justification": "Build time: X weeks for core feature. Based on: similar complexity took Y weeks for solo founders. Can leverage: [APIs/tools].",
      "roi": calculated,
      "roi_calculation": "Revenue ($X/year) / Cost ($Y) = Z:1 ROI. Payback: X months. For solo founder: Time investment (A weeks) worth it if revenue >$B/year.",
      "score": calculated,
      "score_formula": "Show exact formula: (revenue_impact × probability) / (cost + time) = score. Explain weighting.",
      "competitive_advantage": "What moat does this create? How defensible? (For solo founder: Speed and niche focus are advantages)",
      "sustainability": "How long will advantage last? What could erode it? (For solo: Can pivot quickly if needed)"
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
