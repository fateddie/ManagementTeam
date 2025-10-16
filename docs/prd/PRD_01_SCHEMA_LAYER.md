---
title: "PRD-01 — Schema Layer"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System"
status: "Approved"
description: >
  Defines the JSON schema architecture for all core artifacts within the 13-phase SOP.
  Each schema ensures consistent structure, traceability, and interoperability
  across the management layer, ROI workshop, and orchestrator subsystems.
---

# 📘 PRD-01 — Schema Layer

## 1️⃣ Objective
Create a **modular set of JSON schema files** that define the structure of every core artifact produced by the 13-phase SOP.
These schemas provide consistency, traceability, and machine-readable documentation for all downstream components (templates, orchestrator, comparison engine, dashboard).

---

## 2️⃣ Scope

### Included
- One schema file per core artifact (Phase 0 – 13).
- Each file contains:
  - `description` of artifact purpose
  - `fields` list (name → type → notes)
  - `example` object with sample values
- Directory path: `/schema/*.json`

### Excluded
- Validation logic (no min/max or regex yet)
- Non-core or optional future artifacts (trend snapshots, survey results, etc.)
- Evidence collection text logs (`/data/raw`, `/logs/cleaning_log.txt`)

---

## 3️⃣ Deliverables

| File | Description |
|------|--------------|
| `/schema/idea_intake_schema.json` | Captures idea metadata and initiation info |
| `/schema/scope_schema.json` | Defines hypotheses, markets, and success metrics |
| `/schema/research_plan_schema.json` | Outlines data-source plan and queries |
| `/schema/pains_tagged_schema.json` | Defines structure for tagged pain statements |
| `/schema/pain_scores_schema.json` | Quantified pain scoring model |
| `/schema/market_competition_schema.json` | Market sizing and competitor layout |
| `/schema/unit_economics_schema.json` | Price, CAC, LTV, payback fields |
| `/schema/risk_register_schema.json` | Risk ID, impact, probability, mitigation |
| `/schema/gtm_options_schema.json` | RICE & MoSCoW scoring for GTM plans |
| `/schema/report_ADSR_schema.json` | Q&A evidence summary schema |
| `/schema/decision_log_schema.json` | Final decision records |
| `/schema/comparison_matrix_schema.json` | Cross-variant KPI summary |

---

## 4️⃣ Acceptance Criteria

| ID | Requirement | Verification |
|----|--------------|--------------|
| SC-1 | Each schema file exists and validates as JSON | Manual open + `json.load()` passes |
| SC-2 | Each file includes: description, fields, example | Visual check |
| SC-3 | Field names match artifact file headers used by templates/orchestrator | Cross-reference template list |
| SC-4 | Example data correctly demonstrates structure | Readability test |
| SC-5 | No optional future artifacts appear in this release | Directory diff check |

---

## 5️⃣ Dependencies

| Dependency | Type | Relation |
|-------------|------|----------|
| Artifact Inventory (approved) | Input | Defines which schemas to build |
| PRD-02 Templates | Downstream | Templates will reference schema fields |
| PRD-04 Orchestrator | Downstream | Reads schema definitions for validation |

---

## 6️⃣ Milestones

| Step | Deliverable | ETA | Owner |
|------|--------------|-----|-------|
| M1 | Create `/schema/` directory + file stubs | Day 1 | Rob / Dev Agent |
| M2 | Populate all JSON schemas with field lists + examples | Day 2 | Dev Agent |
| M3 | Internal review & cross-check with template headers | Day 3 | Rob |
| M4 | Commit + tag `schema-v1.0` | Day 3 | Planner Agent |

---

## 7️⃣ Example Schema Pattern

```jsonc
{
  "description": "Defines the structure of pain score entries produced in Phase 6.",
  "fields": {
    "pain_id": "string – unique identifier",
    "segment": "string – customer segment",
    "frequency": "integer – 1–5 scale",
    "severity": "integer – 1–5 scale",
    "urgency": "integer – 1–5 scale",
    "score_total": "float – computed weighted score",
    "evidence_source": "string – URL or citation"
  },
  "example": {
    "pain_id": "P-004",
    "segment": "Dental Clinics",
    "frequency": 5,
    "severity": 4,
    "urgency": 5,
    "score_total": 4.7,
    "evidence_source": "https://trustpilot.com/review/example"
  }
}
```

---

## 8️⃣ Success Metrics
- 100 % schema coverage for all core artifacts  
- All schemas readable and consistent across files  
- Zero validation errors when imported by orchestrator prototype  

---

## 9️⃣ Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| Inconsistent field names vs templates | Medium | Cross-verify with PRD-02 |
| Schema drift between variants | Low | Version control tags (`schema-v1.x`) |
| Over-engineering (premature validation) | Low | Keep to structure + examples only |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025-10-16 | — |
| Technical Reviewer | TBD | — | — |
