# Variant Exploration System

A repeatable, evidence-based workflow for evaluating multiple variants of any idea.
Use it to explore markets, customer types, or delivery models in parallel, collect
transparent evidence, and make data-backed go / combine / park decisions.

## Workflow Overview

1. **Kick-off** → Define base idea and variants
2. **For each variant**, run the 13-phase SOP (from scope to decision)
3. **Compare** metrics across variants
4. **Choose** whether to advance, merge, or archive

## Folder Structure

```
/variant_exploration_system/
 ├── README.md                        — This file
 ├── SOP/
 │   └── variant_exploration_SOP.md   — Standard Operating Procedure (13 phases)
 ├── agent/
 │   ├── orchestrator_script.md       — Orchestrator logic and behavior rules
 │   ├── prompts/
 │   │   ├── kick_off.txt            — Initial intake prompt
 │   │   ├── variant_generation.txt  — Variant suggestion prompt
 │   │   ├── phase_template.txt      — Generic phase execution template
 │   │   └── comparison_prompt.txt   — Cross-variant comparison prompt
 │   └── state_schema.json            — State tracking schema
 ├── projects/
 │   ├── _TEMPLATE_variant/           — Copy this for each new variant
 │   │   ├── idea_intake.json         — Phase 0: Base idea details
 │   │   ├── scope.yaml               — Phase 1: Hypothesis and boundaries
 │   │   ├── research_plan.md         — Phase 2: Research methodology
 │   │   ├── pains_tagged.json        — Phase 5: Tagged pain points
 │   │   ├── pain_scores.json         — Phase 6: Quantified pain scores
 │   │   ├── market_competition.md    — Phase 7: Market and competitive analysis
 │   │   ├── unit_economics.json      — Phase 8: Financial model
 │   │   ├── feasibility_risk.md      — Phase 9: Technical and operational risk
 │   │   ├── gtm_options.md           — Phase 10: Go-to-market strategies
 │   │   ├── report_ADSR.md           — Phase 11: Synthesis report (Assess, Decide, Set, Review)
 │   │   └── decision_log.json        — Phase 12: Final decision and rationale
 │   ├── variant_1/                   — Example variant workspace
 │   ├── variant_2/
 │   └── variant_3/
 ├── reports/
 │   ├── comparison_matrix.md         — Side-by-side variant comparison
 │   ├── variant_summary.json         — Structured comparison data
 │   ├── hybrid_scope.yaml            — Combined scope if merging variants
 │   └── variant_rankings.json        — Ranked variants by criteria
 ├── data/
 │   ├── raw/                         — Unprocessed data from Perplexity/sources
 │   ├── clean/                       — Validated and cleaned data
 │   └── processed/                   — Final analyzed data
 └── logs/
     ├── source_log.csv               — Data provenance tracking
     ├── cleaning_log.txt             — Data cleaning audit trail
     ├── scoring_log.json             — Scoring methodology and calculations
     └── audit_trail.json             — All decisions and approvals
```

## Principles

- **Evidence-first, not intuition-first**  
  Every claim must be backed by a source with URL, date, and method.

- **Machine-readable artifacts**  
  All outputs use structured formats (JSON, YAML, Markdown tables) for comparability.

- **AI facilitator never decides**  
  The system elicits information, summarizes findings, and waits for human approval.

- **Identical schema → comparable outputs**  
  All variants follow the same 13-phase structure, enabling apples-to-apples comparison.

- **Governance gates**  
  Each phase ends with **Confirm / Revise / Park** decision point.

## Quick Start

### Start a new variant exploration:

```bash
# 1. Copy the template for your first variant
cp -r variant_exploration_system/projects/_TEMPLATE_variant variant_exploration_system/projects/my_idea_variant_1

# 2. Run the orchestrator (interactive mode)
python variant_exploration_system/agent/orchestrator.py --interactive

# 3. Follow the prompts through all 13 phases

# 4. Copy template for additional variants
cp -r variant_exploration_system/projects/_TEMPLATE_variant variant_exploration_system/projects/my_idea_variant_2

# 5. Run comparison after all variants complete
python variant_exploration_system/agent/orchestrator.py --compare
```

### Or run a specific phase for a specific variant:

```bash
python variant_exploration_system/agent/orchestrator.py --variant variant_1 --phase 6
```

## Integration with Existing Workshop Agent

The Variant Exploration System **integrates** with the existing Workshop Agent:

- **Phase 3 (Evidence Collection)**: Uses Workshop Agent's Perplexity integration to gather market data
- **Phase 7 (Market Analysis)**: Leverages Workshop Agent's competitive intelligence
- **Phase 9 (Risk Assessment)**: Uses Workshop Agent's risk quantification methodology

This ensures you get:
- ✅ Real-time market data (75+ sources per variant)
- ✅ Transparent reasoning with Chain-of-Thought
- ✅ Solo founder optimization
- ✅ Evidence-based recommendations

## Outputs

After completing all variants, you'll have:

1. **Structured data** for each variant (12+ files per variant)
2. **Comparison matrix** showing metrics side-by-side
3. **Ranked recommendations** based on your success criteria
4. **Audit trail** of all decisions and evidence
5. **Hybrid scope** (optional) combining best elements from multiple variants

## Example Use Case

**Base Idea:** "Personal productivity assistant"

**Variants Generated:**
- **Variant 1:** Email management for freelance designers
- **Variant 2:** Calendar assistant for ADHD entrepreneurs  
- **Variant 3:** Morning routine coach for busy parents

**After 13-phase exploration:**

| Metric | Variant 1 | Variant 2 | Variant 3 |
|---------|-----------|-----------|-----------|
| Avg Pain Score | 8.5/10 | 9.2/10 | 7.1/10 |
| TAM (€M) | €450M | €280M | €620M |
| Payback (months) | 4 | 6 | 8 |
| LTV:CAC | 4.2 | 3.8 | 5.1 |
| Compliance Risk | Low | Medium | Low |
| Feasibility | High | Medium | High |

**Decision:** Advance Variant 1 (email for designers) + Combine calendar features from Variant 2

## Next Steps

1. Read the [SOP documentation](SOP/variant_exploration_SOP.md) for detailed phase descriptions
2. Review the [orchestrator script](agent/orchestrator_script.md) for execution logic
3. Examine the [template files](projects/_TEMPLATE_variant/) to understand output structure
4. Run your first variant exploration!

---

**Built by:** Robert Freyne  
**Version:** 1.0  
**Last Updated:** 2025-10-16

