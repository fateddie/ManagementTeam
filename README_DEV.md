# 🧭 Developer Guide — Variant Exploration System (VES)

## 🎯 Purpose
This repository implements a modular, auditable framework for evaluating business ideas and market variants.
It combines schemas, templates, orchestrators, and agents into a human‑in‑loop decision system.

---

## ⚙️ Environment Setup

### 1. Prerequisites
- Python 3.10+
- Git
- Cursor or VSCode (recommended)

### 2. Setup
Run the environment setup script:
```bash
bash setup_env.sh
source venv/bin/activate
```

### 3. Install Dependencies Manually (if needed)
```bash
pip install pytest jsonschema pandas colorama streamlit
```

---

## 📂 Project Structure
```
/docs/                  ← PRDs, control plan, and documentation
/orchestrator/          ← Core orchestrator logic, state, and logs
/schema/                ← JSON schema definitions
/templates/             ← Markdown/YAML/JSON templates
/agents/                ← Role prompt definitions
/tests/                 ← Automated unit/integration tests
/reports/               ← Generated dashboards and summaries
```

---

## 🧪 Testing
Run all tests with:
```bash
pytest -v
```

### Types of Tests
| Type | Location | Purpose |
|------|-----------|----------|
| Unit | `/tests/test_*.py` | Validate specific modules (hashing, validation) |
| Integration | `/tests/test_workflow_end_to_end.py` | Full orchestrator cycle |
| Regression | `/tests/test_regression_suite.py` | Detect functional drift |
| Performance | `/tests/test_performance.py` | Benchmark key functions |

Test results are logged under `/reports/test_results.log`.

---

## 🧱 Development Workflow

### Step 1 — Implement per PRD
Follow each PRD (01–07) sequentially:
1. Build component →
2. Test locally →
3. Log validation →
4. Commit with message referencing PRD ID.

### Step 2 — Validation Gates
Each PRD includes success metrics and acceptance criteria.
Cursor or Claude Code should pause execution at each gate until confirmed.

### Step 3 — Commit & Tag
```bash
git add .
git commit -m "Implement PRD-05 audit layer with validation tests"
git tag ves-v1.0
```

---

## 🧩 Automation Triggers (for Cursor)
| Trigger | Description |
|----------|--------------|
| `#build_validation_engine` | Create validation module as per PRD‑06 |
| `#run_all_tests` | Run all pytest suites |
| `#generate_dashboard` | Produce summary report (PRD‑07) |
| `#export_audit` | Sync audit logs to CSV |
| `#release_tag` | Tag a stable release |

---

## ✅ Definition of Done
A phase is **done** when:
- All relevant tests pass
- Logs and audit files match expected hashes
- Validation gates are approved
- Reports update without error

---

## 🧠 Notes for Developers
- Always work within the `venv` virtual environment.
- Use the orchestrator only after confirming all schemas and templates load correctly.
- Every PRD change should be auditable via logs and commits.
- PRDs serve as **contract documents** — do not modify mid‑development without version bump.

---

**Maintainer:** Rob  
**Version:** 1.0  
**Last Updated:** 2025‑10‑16
