# Variant Exploration Templates

**Purpose:** These templates standardize the output of each SOP phase, ensuring consistency and machine-readability across all variants.

**Defined by:** PRD-02 Artifact Templates  
**Schema compliance:** PRD-01 Schema Layer  
**Version:** 1.0

---

## 📁 Template Files

| Phase | Template File | Format | Purpose |
|-------|---------------|--------|---------|
| 0 | `idea_intake.md` | Markdown | Capture initial idea, initiator, intent |
| 1 | `scope.yaml` | YAML | Define hypothesis, ICP, success metrics |
| 2 | `research_plan.md` | Markdown | Document research methodology |
| 5 | `pains_tagged.json` | JSON | Tagged and categorized pain points |
| 6 | `pain_scores.json` | JSON | Quantified pain scores (frequency, severity, urgency) |
| 7 | `market_competition.md` | Markdown | Market analysis and competitive landscape |
| 8 | `unit_economics.json` | JSON | Financial metrics (LTV, CAC, payback, ROI) |
| 9 | `risk_register.json` | JSON | Identified risks with mitigation strategies |
| 10 | `gtm_options.md` | Markdown | Go-to-market strategy options |
| 11 | `report_ADSR.md` | Markdown | Synthesis report (Assess, Decide, Set, Review) |
| 12 | `decision_log.json` | JSON | Final decision and rationale |
| 13 | `comparison_matrix.md` | Markdown | Cross-variant comparison matrix |

**Note:** Phases 3 & 4 (Evidence Collection, Data Cleaning) save directly to `/data/raw/` and `/data/clean/` respectively.

---

## 🎯 Design Principles

### **1. Format Choice:**
- **Markdown (.md):** Human-readable narrative content
- **YAML (.yaml):** Hierarchical structured data
- **JSON (.json):** Strict machine-readable data with validation

### **2. Schema Alignment:**
All JSON templates align with schemas defined in `/schema/*.json` (see PRD-01).

### **3. Progressive Detail:**
- **Early phases (0-2):** Broad, strategic input
- **Middle phases (5-9):** Detailed, analytical metrics
- **Late phases (10-12):** Synthesis and decision
- **Final phase (13):** Cross-variant comparison

### **4. Templates as Question Sheets:**
Each template includes:
- Clear section headers
- Placeholder text (`<Enter value>`)
- Example data
- Schema references
- Purpose documentation

---

## 🔄 Usage

### **For New Variants:**

When you run:
```bash
python orchestrator.py --variant my_variant
```

The orchestrator will:
1. Copy all templates to `projects/my_variant/`
2. Guide you through filling each template
3. Validate JSON/YAML syntax
4. Save your inputs

### **Manual Usage:**

```bash
# Copy template to variant folder
cp templates/pain_scores.json projects/my_variant/pain_scores.json

# Edit with your data
# Validate schema compliance
python scripts/validate_schema.py projects/my_variant/pain_scores.json
```

---

## 📊 Template Structure Examples

### **JSON Template (pain_scores.json):**
```json
{
  "description": "Quantified scores for pains using 1–5 scales.",
  "records": [
    {
      "pain_id": "P-001",
      "frequency": 5,
      "severity": 4,
      "urgency": 5,
      "score_total": 4.7,
      "evidence_source": "https://example.com"
    }
  ]
}
```

### **YAML Template (scope.yaml):**
```yaml
hypothesis: "<Main hypothesis>"
target_segments:
  - "<Primary segment>"
  - "<Secondary segment>"
success_metrics:
  - metric: "Payback < 12 months"
  - metric: "Validated pain >= 60% ICP"
notes: |
  Explain *why* this scope is valid and what assumptions need testing.
```

### **Markdown Template (idea_intake.md):**
```markdown
# Idea Intake Template

## Idea Name
<Enter your idea name>

## Description
<Briefly describe the concept>

## Why It Matters
<Explain why this idea is worth exploring>
```

---

## ✅ Validation

All templates are:
- ✅ Schema-compliant (PRD-01)
- ✅ Machine-readable
- ✅ Human-friendly
- ✅ Cross-referenced (PRD-02)
- ✅ Version controlled

---

## 🔗 References

- **PRD-01:** Schema Layer definitions
- **PRD-02:** Artifact Templates specifications
- **SOP:** 13-phase methodology
- **Orchestrator:** Template usage logic

---

**These templates ensure every variant is evaluated using identical, auditable criteria.** 📋

