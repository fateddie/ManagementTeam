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
      "revenue_justification": {{
        "question_1_market_size": "What's the TAM for this opportunity? (cite Perplexity data)",
        "question_2_current_arpu": "What's current expected ARPU without this strategy?",
        "question_3_new_arpu": "What's new ARPU with this strategy? Based on what comparable?",
        "question_4_customer_increase": "Will this increase customer count? By how many? Why?",
        "question_5_calculation": "Show: (new ARPU - old ARPU) × customers + (new customers × ARPU) = revenue impact",
        "question_6_timeframe": "Over what period? Year 1? Lifetime? Why?"
      }},
      "cost": $value,
      "cost_justification": {{
        "question_1_development": "Development costs: hours × rate = $X. Show breakdown.",
        "question_2_marketing": "Marketing costs to launch: What channels? How much each?",
        "question_3_operations": "Ongoing operational costs: What and why?",
        "question_4_hidden_costs": "What hidden costs might emerge? Buffer amount?",
        "question_5_total": "Show: dev + marketing + ops + buffer = total cost"
      }},
      "time_weeks": number,
      "time_justification": {{
        "question_1_phases": "What are the implementation phases? How long for each?",
        "question_2_dependencies": "What must happen first? What could block progress?",
        "question_3_team_size": "How many people? What skills needed?",
        "question_4_comparable": "How long did competitors take to implement similar? Cite examples."
      }},
      "roi": calculated,
      "roi_calculation": {{
        "question_1_revenue": "Total revenue expected: $X (from revenue_justification)",
        "question_2_cost": "Total cost: $Y (from cost_justification)",
        "question_3_formula": "ROI = revenue / cost = $X / $Y = Z:1",
        "question_4_payback": "Payback period: cost / (monthly revenue) = X months. Is this acceptable?",
        "question_5_risk_adjusted": "Risk-adjusted ROI: ROI × probability of success = X:1. Show calculation."
      }},
      "score": calculated,
      "score_formula": "Show exact formula: (revenue_impact × probability) / (cost + time) = score. Explain weighting.",
      "competitive_advantage": {{
        "what_moat": "What specific moat does this create?",
        "how_defensible": "How hard to copy? What % of competitors could replicate? Timeline?",
        "network_effects": "Are there network effects? If yes, quantify the value increase.",
        "switching_costs": "What switching costs for customers? Quantify if possible."
      }},
      "sustainability": {{
        "question_1_duration": "How long will this advantage last? 1 year? 5 years? Why?",
        "question_2_erosion": "What could erode this advantage? How likely? When?",
        "question_3_defense": "How do you defend against erosion? What cost?",
        "question_4_exit_strategy": "If advantage erodes, what's Plan B?"
      }}
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
