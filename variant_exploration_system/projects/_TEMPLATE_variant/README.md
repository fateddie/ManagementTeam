# Variant Template

**Purpose:** Starting point for each new variant exploration.

**Templates align with:** PRD-01 (Schema Layer) and PRD-02 (Artifact Templates)

---

## Usage

### **Automatic (Recommended):**
```bash
# Orchestrator automatically copies templates
python orchestrator.py --variant my_variant
```

### **Manual:**
```bash
cp -r projects/_TEMPLATE_variant projects/my_idea_variant_1
python orchestrator.py --variant my_idea_variant_1
```

---

## Files

Each variant workspace contains **12 structured files** that capture the complete analysis:

| Phase | File | Format | Purpose |
|-------|------|--------|---------|
| 0 | `idea_intake.md` | Markdown | Base idea and success criteria |
| 1 | `scope.yaml` | YAML | Hypothesis, ICP, and boundaries |
| 2 | `research_plan.md` | Markdown | Research methodology |
| 5 | `pains_tagged.json` | JSON | Categorized pain points |
| 6 | `pain_scores.json` | JSON | Quantified pain severity (frequency, severity, urgency) |
| 7 | `market_competition.md` | Markdown | Market analysis and competitive landscape |
| 8 | `unit_economics.json` | JSON | Financial model (LTV, CAC, payback, ROI) |
| 9 | `risk_register.json` | JSON | Risk assessment with mitigation strategies |
| 10 | `gtm_options.md` | Markdown | Go-to-market strategy options |
| 11 | `report_ADSR.md` | Markdown | Synthesis report (Assess, Decide, Set, Review) |
| 12 | `decision_log.json` | JSON | Final decision and rationale |
| 13 | `comparison_matrix.md` | Markdown | Cross-variant comparison (generated at Phase 13) |

**Note:** Phases 3 & 4 (Evidence Collection, Data Cleaning) save to `/data/raw/` and `/data/clean/` respectively.

---

## Principles

- ✅ Every metric must have a source
- ✅ All files use machine-readable formats (JSON/YAML/MD)
- ✅ Identical schema across all variants for comparability
- ✅ Templates include placeholders and examples
- ✅ Schema-validated against PRD-01 definitions

---

## Template Sources

Templates are sourced from:
- **Template directory:** `../../templates/`
- **Defined by:** PRD-02 Artifact Templates
- **Schema compliance:** PRD-01 Schema Layer
- **Version:** 1.0

---

**These templates ensure every variant follows the same rigorous, auditable process.** 📋

