---
title: "PRD-06 — Validation Engine"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System"
status: "Planned"
description: >
  Introduces automated validation for schema compliance, logical integrity, and
  completeness across all artifacts before progression to next SOP phase.
---

# 📘 PRD‑06 — Validation Engine

## 1️⃣ Objective
Create a lightweight engine that validates artifact data against schema rules
to prevent downstream errors, ensuring only high‑quality, complete data passes
each gate.

---

## 2️⃣ Scope

### Included
- JSON Schema validation for all core artifacts.  
- Range and type checks (numeric, string, list).  
- Completeness verification (required fields).  
- Error reporting with contextual messages.

### Excluded
- Full AI reasoning checks (handled by agents).  
- UI‑based validation (dashboard layer).

---

## 3️⃣ Functional Overview

| Function | Description |
|-----------|-------------|
| **Schema Loader** | Loads relevant JSON schema by phase. |
| **Validator** | Compares artifact fields to schema definitions. |
| **Reporter** | Generates structured error list with recommendations. |
| **Gate Control** | Blocks phase advancement until validation passes. |

---

## 4️⃣ Validation Example

**Input:** `unit_economics.json`  
**Schema rule:** `ltv_cac_ratio` > 3  

**Output:**  
```
[Validation Error]
Field: ltv_cac_ratio
Expected: > 3
Actual: 2.5
Recommendation: Review CAC assumption or price model.
```

---

## 5️⃣ Acceptance Criteria

| ID | Requirement | Verification |
|----|--------------|--------------|
| VE‑1 | Each artifact validated before phase approval | Manual run |
| VE‑2 | Errors logged to `/logs/validation_errors.json` | File inspection |
| VE‑3 | Gate prevents advancement on failure | Orchestrator test |
| VE‑4 | All schemas load without errors | Parser test |

---

## 6️⃣ Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| False negatives (missed errors) | Medium | Use strict schema typing |
| Schema drift | Medium | Version tag each schema |
| User fatigue on errors | Low | Offer concise error summaries |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025‑10‑16 | — |
| Technical Reviewer | TBD | — | — |
