---
title: "Cursor Plan — Full Implementation & Testing Roadmap"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System (VES)"
status: "Active"
description: >
  Defines the full end-to-end development, validation, and testing roadmap for
  implementing all PRDs (01–07) within Cursor. This document is designed to
  guide both human developers and AI coding assistants (Claude/Cursor) through
  a structured, controlled build process.
---

# 🧭 Cursor Plan — Full Implementation & Testing Roadmap

## 🎯 Goal
To achieve a complete, validated, and auditable implementation of the
**Variant Exploration System (VES)** in Cursor — from schema to dashboard —
following strict governance, documentation, and test coverage.

---

## 1️⃣ Project Structure

```
/docs/                  ← All PRDs (01–07) + this control file
/orchestrator/          ← Core orchestrator logic + state & logs
/schema/                ← JSON schemas
/templates/             ← Artifact templates
/agents/                ← Agent role definitions (Markdown prompts)
/tests/                 ← Automated tests for each subsystem
/reports/               ← Generated dashboards and validation summaries
```

---

## 2️⃣ Sequential Implementation Plan

### Phase 1 — Initialization (Setup)
**Objective:** Prepare environment and confirm all directories and dependencies.

**Tasks:**
- [ ] Create virtual environment and install dependencies:
  ```bash
  pip install pytest jsonschema pandas colorama
  ```
- [ ] Set `USER` environment variable for logging consistency.
- [ ] Confirm schema and template directories match PRD‑01 & PRD‑02.

**Validation Gate:** All directories and files verified via Cursor `tree` command.

---

### Phase 2 — Schema & Template Validation (PRD‑01 & 02)
**Objective:** Ensure all schemas and templates are correctly formatted and aligned.

**Tasks:**
- [ ] Build validation script `/tests/test_schema_integrity.py`.
- [ ] Test JSON syntax validity and required fields.
- [ ] Cross‑reference template placeholders vs. schema keys.

**Validation Gate:** No JSONDecodeError or missing key mismatch.

**Deliverables:**
- `schema_validation_report.md`  
- `tests/test_schema_integrity.py`

---

### Phase 3 — Agent Roles & Prompts (PRD‑03)
**Objective:** Ensure all agent definitions are readable, well‑structured, and callable by Orchestrator.

**Tasks:**
- [ ] Store each agent definition in `/agents/*.md`.
- [ ] Add agent metadata (purpose, inputs, outputs) to YAML header.
- [ ] Validate prompt format via simple parser test.

**Validation Gate:** Each agent prompt passes markdown readability test.

**Deliverables:**
- `agents_index.md` summarizing each agent role.

---

### Phase 4 — Orchestrator Implementation (PRD‑04)
**Objective:** Integrate and test the orchestrator’s sequential flow.

**Tasks:**
- [x] Implement `orchestrator_core.py` (done).
- [ ] Create `/tests/test_state_flow.py` to simulate full cycle.
- [ ] Add checkpoint recovery and resume logic (future).

**Validation Gate:** End‑to‑end flow executes 0 → 13 phases without crash.

**Deliverables:**
- Updated `state_schema.json`  
- `tests/test_state_flow.py`

---

### Phase 5 — Audit & Logging Layer (PRD‑05)
**Objective:** Verify enhanced logging, hashing, and archiving functionality.

**Tasks:**
- [x] Upgrade `orchestrator_core.py` with hash + archive logic.
- [ ] Build `/tests/test_audit_layer.py`:
  - Verify SHA‑256 hashes created.
  - Confirm archived copies exist.
  - Check JSON + CSV logs align.
- [ ] Stress test with multiple phase runs.

**Validation Gate:** 100 % of actions appear in both JSON & CSV audit files.

**Deliverables:**
- `audit_integrity_report.md`  
- `tests/test_audit_layer.py`

---

### Phase 6 — Validation Engine (PRD‑06)
**Objective:** Enforce schema‑based data validation before approval.

**Tasks:**
- [ ] Create `/orchestrator/validation_engine.py`.
- [ ] Implement `validate_artifact(artifact_path, schema_path)`.
- [ ] Integrate validation call inside orchestrator phase approval.
- [ ] Log all validation errors to `/logs/validation_errors.json`.

**Validation Gate:** Any non‑compliant file blocks phase progression.

**Deliverables:**
- `validation_engine.py`
- `tests/test_validation_engine.py`
- `validation_errors.json`

---

### Phase 7 — Reporting & Dashboard (PRD‑07)
**Objective:** Aggregate and visualize all validated results.

**Tasks:**
- [ ] Build `/reports/report_generator.py`.
- [ ] Read logs, state, and economics data → produce Markdown summary.
- [ ] Optional: Implement Streamlit dashboard for interactive view.
- [ ] Validate CSV → Markdown export.

**Validation Gate:** Generated report includes all key metrics (pain scores, LTV:CAC, payback).

**Deliverables:**
- `reports/summary_dashboard.md`
- `reports/streamlit_app.py` (optional)

---

## 3️⃣ Testing Framework Overview

| Test Type | Description | Output |
|------------|-------------|--------|
| **Unit Tests** | Validate discrete modules (hashing, schema, logging). | `/tests/test_*.py` |
| **Integration Tests** | Simulate multi‑phase orchestration. | `/tests/test_workflow_end_to_end.py` |
| **Regression Tests** | Ensure no functionality loss after updates. | `/tests/test_regression_suite.py` |
| **Performance Tests** | Check archive and validation times. | `/tests/test_performance.py` |

---

## 4️⃣ Governance & Versioning

| Element | Rule |
|----------|------|
| **Commit Discipline** | Commit after each phase passes all tests. |
| **Tag Format** | `ves-v<major>.<minor>` (e.g., `ves-v1.0`). |
| **Change Log** | `/docs/CHANGELOG.md` updated automatically. |
| **Schema Versioning** | Each schema tagged `schema-v1.x`. |

---

## 5️⃣ Automation Triggers (Cursor & Claude)

| Trigger | Action |
|----------|--------|
| `#build_validation_engine` | Generate validation module per PRD‑06. |
| `#run_all_tests` | Execute pytest suite and summarize failures. |
| `#generate_dashboard` | Build summary Markdown + Streamlit preview. |
| `#export_audit` | Sync JSON + CSV logs. |
| `#release_tag` | Commit and push with new version tag. |

---

## 6️⃣ Definition of Done (DoD)

A build is **Complete & Compliant** when:
- ✅ All tests in `/tests/` pass with zero critical errors.
- ✅ Validation engine blocks all invalid data.
- ✅ Audit trail and CSV logs are hash‑consistent.
- ✅ Dashboard report renders key metrics without error.
- ✅ All PRD deliverables produced and archived.

---

## 7️⃣ Final Milestone Deliverables

| Deliverable | Description |
|--------------|-------------|
| `ves_full_suite.zip` | Packaged release (schemas, orchestrator, tests, reports). |
| `final_validation_report.md` | Human‑readable compliance summary. |
| `summary_dashboard.md` | Key metrics and ROI snapshot. |
| `audit_trail.csv` | Verified, traceable activity log. |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025‑10‑16 | — |
| Technical Reviewer | TBD | — | — |
