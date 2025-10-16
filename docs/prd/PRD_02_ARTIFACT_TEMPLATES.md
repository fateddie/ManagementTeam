---
title: "PRD-02 — Artifact Templates"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System"
status: "Planned"
description: >
  Defines standardized Markdown, YAML, and JSON templates for each phase of the
  13-phase SOP. These templates ensure all outputs follow a consistent format
  and are compatible with schema definitions from PRD-01.
---

# 📘 PRD-02 — Artifact Templates

## 1️⃣ Objective
Design and implement standardized **artifact templates** for each SOP phase, ensuring data captured during the process is structured, comparable, and machine-readable.
These templates act as the “molds” for all project outputs, providing field headers, guidance text, and justification prompts.

---

## 2️⃣ Scope

### Included
- One template file per core SOP artifact, aligned with corresponding JSON schema.
- Templates will include:
  - Human-readable **section headings** (Markdown/YAML).
  - **Field placeholders** that map directly to schema fields.
  - **Guidance text** prompting for “what” and “why” reasoning.
- Directory path: `/templates/`.

### Excluded
- Automation logic (that belongs to the orchestrator in PRD-04).
- Optional future artifacts (e.g., trend snapshots, surveys).
- Database or API connectors (no external integrations in v1).

---

## 3️⃣ Deliverables

| File | Type | Description |
|------|------|--------------|
| `/templates/idea_intake.md` | MD | Form to capture idea metadata and initiation rationale. |
| `/templates/scope.yaml` | YAML | Defines hypotheses, market focus, and success metrics. |
| `/templates/research_plan.md` | MD | Outlines research data sources, keywords, and collection methods. |
| `/templates/pains_tagged.json` | JSON | Placeholder for structured pain extraction results. |
| `/templates/pain_scores.json` | JSON | Standardized scoring table for quantified pains. |
| `/templates/market_competition.md` | MD | Market and competitor summary layout. |
| `/templates/unit_economics.json` | JSON | Standardized pricing and ROI metrics table. |
| `/templates/risk_register.json` | JSON | Risk list structure matching schema. |
| `/templates/gtm_options.md` | MD | Template for RICE and MoSCoW scoring documentation. |
| `/templates/report_ADSR.md` | MD | “Actionable Decision-Support Report” layout with Q&A and rationale fields. |
| `/templates/decision_log.json` | JSON | Final decision outcome template. |
| `/templates/comparison_matrix.md` | MD | Layout for cross-variant KPI comparison. |

---

## 4️⃣ Template Example (Markdown)

### Example: `scope.yaml`
```yaml
# --- Scope Definition Template ---
# Maps to /schema/scope_schema.json
# Purpose: capture key hypotheses and markets for variant exploration.

hypothesis: "<Enter your main hypothesis here>"
target_segments:
  - "<Primary ICP / customer type>"
  - "<Secondary segment if applicable>"
success_metrics:
  - metric: "Payback under 12 months"
  - metric: "Validated pain > 60% ICP response"
notes: |
  Explain *why* this hypothesis matters and how it links to commercial ROI.
```

### Example: `report_ADSR.md`
```markdown
# Actionable Decision-Support Report (ADSR)

## Question
What core business question was addressed?

## How We Answered It
Describe the research or model applied and why it was chosen.

## Evidence Summary
- Source(s): [link]
- Method: [survey/interview/data scraping]
- Confidence: High / Medium / Low

## Findings
Summarize key quantitative and qualitative findings.

## Why It Matters
Explain the reasoning and implications for decision-making.
```

---

## 5️⃣ Acceptance Criteria

| ID | Requirement | Verification |
|----|--------------|--------------|
| AT-1 | Each core artifact has a matching template file | Directory listing check |
| AT-2 | Templates align field names with PRD-01 schemas | Manual cross-check |
| AT-3 | Templates include guidance for both *what* and *why* reasoning | Visual check |
| AT-4 | Markdown/YAML/JSON syntax validated | Linter or parser test |
| AT-5 | Files saved under `/templates/` with consistent naming | Git diff or file structure check |

---

## 6️⃣ Dependencies

| Dependency | Type | Relation |
|-------------|------|----------|
| PRD-01 Schema Layer | Upstream | Provides schema field definitions |
| PRD-04 Orchestrator | Downstream | Will populate templates during execution |
| Management Layer Config | External | Determines how templates are instantiated per variant |

---

## 7️⃣ Milestones

| Step | Deliverable | ETA | Owner |
|------|--------------|-----|-------|
| M1 | Create `/templates/` directory | Day 1 | Rob |
| M2 | Draft all template files with field placeholders | Day 2 | Dev Agent |
| M3 | Cross-check with schema definitions | Day 3 | Rob |
| M4 | Commit + tag `templates-v1.0` | Day 3 | Planner Agent |

---

## 8️⃣ Success Metrics
- 100 % coverage for all core artifacts.  
- Template placeholders directly map to schema fields.  
- Each template readable and usable by orchestrator and human user alike.

---

## 9️⃣ Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| Field mismatches vs schema | High | Use field name validation script |
| Overly complex templates | Medium | Keep layout human-readable first |
| Prompt ambiguity | Low | Include explicit “why this matters” notes |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025-10-16 | — |
| Technical Reviewer | TBD | — | — |
