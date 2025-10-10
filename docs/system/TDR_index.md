# TECHNOLOGY DECISION RECORDS – INDEX
**Version:** 1.0  
**Maintainer:** Founder (Rob)  
**Date:** 2025-10-08  

---

## 🎯 PURPOSE
This index provides a centralized reference for all Technology Decision Records (TDRs).  
Each TDR documents a key architectural or technology-related choice, its rationale, and its review plan.  
The goal is to ensure **traceability**, **clarity**, and **accountability** for every major decision in the system's evolution.

---

## 📚 CURRENT DECISIONS
| ID | Title | Status | Date | Next Review | File |
|----|--------|--------|------|--------------|------|
| TDR-001 | JSON-Based Memory Over ChromaDB | Accepted | 2025-10-08 | Q1 2026 | `TDR_001_json_memory.md` |
| TDR-002 | Python Orchestrator Architecture | Accepted | 2025-10-08 | Q4 2025 | `TDR_002_orchestrator.md` |
| TDR-003 | YAML Configuration System | Accepted | 2025-10-08 | Q4 2025 | `TDR_003_yaml_config.md` |

---

## 🧩 HOW TO ADD A NEW DECISION
When a new architectural or technology choice arises:
1. Copy `TDR_template.md` (see below or separate file).
2. Save as `TDR_XXX_<topic>.md` with next sequential ID.
3. Add entry to this index with unique ID (`TDR-XXX`).
4. Reference affected files and planned review date.
5. Update `change_log.md` with the new decision.

---

## 📋 DECISION CATEGORIES
| Category | Description | Example |
|----------|-------------|---------|
| **Architecture** | System design and structure | Orchestrator pattern, agent workflow |
| **Technology** | Tool or framework selection | Python vs Node.js, FastAPI vs Flask |
| **Data** | Storage and persistence strategy | JSON vs Database, Vector memory |
| **Integration** | External service choices | Slack, ChromaDB, Supabase |
| **Security** | Authentication, authorization, compliance | GDPR alignment, API keys |
| **Performance** | Optimization decisions | Parallel execution, caching |

---

## 🔄 REVIEW SCHEDULE
- **Quarterly:** Review all "Accepted" decisions for continued relevance
- **On Trigger:** Review when technology landscape changes
- **Post-Mortem:** Review after project completion or major incident

---

## 🧱 TDR TEMPLATE
```markdown
# TECHNOLOGY DECISION RECORD (TDR)
**Title:** [Decision Title]  
**Version:** 1.0  
**Date:** [YYYY-MM-DD]  
**Owner:** [Name/Role]  
**Status:** [Proposed / Accepted / Deferred / Rejected]

## 1️⃣ CONTEXT  
[Background and problem statement]

## 2️⃣ DECISION  
[What was decided and why]

## 3️⃣ RATIONALE  
[Options considered and justification]

## 4️⃣ IMPACT  
[Short-, medium-, long-term implications]

## 5️⃣ RELATED FILES  
[List of related scripts, docs, or configs]

## 6️⃣ REVIEW PLAN  
[When and how the decision will be reviewed]

## 7️⃣ HISTORY  
| Version | Date | Author | Notes |
|----------|------|---------|-------|
| 1.0 | [Date] | [Name] | Initial creation |
```

---

## 📚 RELATED DOCUMENTATION
- `management_team_charter_v1.0.md` - Core values (Simplicity, Data-Driven)
- `project_progress_plan.md` - Technology roadmap
- `change_log.md` - System updates
- `orchestrator_extensions.md` - Future technology plans

---

## 📞 MAINTENANCE
**Review Cycle:** Quarterly  
**Owner:** Technical Architect  
**Approval Required:** Founder for major decisions  
**Archive Policy:** Keep all TDRs indefinitely, mark superseded ones clearly

---

**Version:** 1.0  
**Last Updated:** 2025-10-08  
**Next Review:** 2026-01-08

