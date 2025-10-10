# CLAUDE OPERATIONAL RULES
**Version:** 1.0  
**Date:** 2025-10-08  
**Maintainer:** Founder (Rob)

---

## 🧠 PURPOSE
These rules define how Claude should interpret, create, or modify files in this repository.  
They protect code integrity, maintain consistency, and ensure traceability across the system.

---

## ✅ PERMITTED ACTIONS
Claude may:
- Create or update `.py`, `.md`, `.yaml`, `.json` files within approved folders.  
- Generate documentation under `/docs/system/`.  
- Propose, but not directly implement, structural changes to `/config/` or `/setup/` scripts without approval.  
- Refactor code for clarity or modularity if structure remains unchanged.  
- Automatically update `/docs/system/file_structure.md` when adding files.

---

## 🚫 RESTRICTED ACTIONS
Claude may **not**:
- Modify or delete any `.env`, `.venv`, or environment credential file.  
- Alter version history or TDRs without explicit review.  
- Push commits without a corresponding changelog entry.  
- Overwrite more than one major subsystem in a single request.  
- Introduce new dependencies without updating `requirements.txt` **and** `TDR_index.md`.

---

## 🔁 INTERACTION RULES
| Action | Required Step |
|--------|----------------|
| Add new module | Create `.py` file under `src/` + update file_structure.md |
| Add new agent | Update `agent_definitions.yaml` + define role in docs |
| Update logic | Reference original doc in commit message |
| Add dependency | Modify `requirements.txt` + note in `change_log.md` |
| Major design change | Trigger new TDR under `/docs/system/` |

---

## 🧩 CLAUDE BEHAVIOUR MODES
| Mode | Description |
|------|--------------|
| **Planning Mode** | Claude focuses on generating structured plans, PRDs, and TDRs. |
| **Build Mode** | Claude generates modular, testable code conforming to config guidelines. |
| **Review Mode** | Claude audits recent changes for consistency and documentation compliance. |

---

## 🧭 PROJECT CONTEXT SUMMARY
Claude operates under:
- Governance: `management_team_charter_v1.0.md`
- Rules: `management_team_rules.yaml`
- Agents: `management_team_agent_definitions.yaml`
- System flow: `system_context.yaml`

All actions must align with these documents.

---

## 📜 VERSION HISTORY
| Version | Date | Author | Notes |
|----------|------|---------|-------|
| 1.0 | 2025-10-08 | Founder | Initial rules definition for Claude operation. |

