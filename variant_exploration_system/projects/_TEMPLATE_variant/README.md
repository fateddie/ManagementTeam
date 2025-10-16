# Variant Template

Copy this folder for each new variant you want to explore.

## Usage

```bash
cp -r projects/_TEMPLATE_variant projects/my_idea_variant_1
python orchestrator.py --variant my_idea_variant_1
```

## Files

Each variant workspace contains 12+ structured files that capture the complete analysis:

- `idea_intake.json` - Phase 0: Base idea and success criteria
- `scope.yaml` - Phase 1: Hypothesis, ICP, and boundaries
- `research_plan.md` - Phase 2: Research methodology
- `pains_tagged.json` - Phase 5: Categorized pain points
- `pain_scores.json` - Phase 6: Quantified pain severity
- `market_competition.md` - Phase 7: Market analysis
- `unit_economics.json` - Phase 8: Financial model
- `feasibility_risk.md` - Phase 9: Risk assessment
- `gtm_options.md` - Phase 10: Go-to-market strategies
- `report_ADSR.md` - Phase 11: Synthesis report
- `decision_log.json` - Phase 12: Final decision

## Principles

- Every metric must have a source
- All files use machine-readable formats (JSON/YAML/MD)
- Identical schema across all variants for comparability

