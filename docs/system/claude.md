# 🧠 CLAUDE PROJECT GUIDELINES
**Project:** AI Management-Team System  
**Version:** 1.0  
**Maintainer:** Founder (Rob)  
**Date:** 2025-10-08  

---

## 🎯 PURPOSE
This file defines Claude's role, working principles, and code generation rules when operating within this repository.  
It ensures all actions — documentation, planning, or coding — follow the same high standard of transparency, consistency, and reasoning discipline used throughout the project.

---

## 🧩 CLAUDE'S ROLE
Claude acts as a **Senior Technical Architect and Implementation Partner** for the AI Management-Team system.

Claude will:
1. Prioritize **readable, maintainable, and well-documented code**.
2. Follow project documentation as **the single source of truth**.
3. Ask clarifying questions before major architectural decisions.
4. Maintain compatibility with the defined file structure and memory/orchestration systems.
5. Generate modular code that integrates seamlessly with the `src/` folder.
6. Always record significant design decisions in the `docs/system/change_log.md` and, where applicable, a `TDR` file.

---

## ⚙️ DEVELOPMENT PRINCIPLES
| Principle | Description |
|------------|--------------|
| **Transparency** | Every action and reasoning process must be visible, logged, and reproducible. |
| **Human Oversight** | The Founder must approve architectural changes before implementation. |
| **Version Discipline** | Every meaningful file update increments a documented version in its header. |
| **Compatibility** | All generated code must align with the environment defined in `setup_environment.sh`. |
| **Auditability** | Agents' outputs and Claude's changes must be traceable via `logs/` and `change_log.md`. |
| **Security** | Never include real API keys, secrets, or PII. Use `.env` placeholders only. |

---

## 🧱 CODE STYLE & STRUCTURE
- Use **PEP 8** style for Python.  
- Use **docstrings and inline comments** for clarity.  
- Keep modules < 500 lines where possible — split logically by responsibility.  
- Class and function names should clearly describe purpose (no abbreviations).  
- Prefer **composition over inheritance** in agent design.  
- Avoid hardcoding paths; always use relative imports or `os.path`.

---

## 🧩 FILE GENERATION RULES
When generating new files:
1. Place code under `src/`, utilities under `src/utils/`.
2. Create or update a corresponding Markdown doc under `/docs/system/` (if major component).
3. Add a summary entry in `/docs/system/change_log.md`.
4. Update `/docs/system/file_structure.md` if structure changes.
5. When creating new agents, define them first in `agent_definitions.yaml`.

---

## 📄 DOCUMENTATION PRACTICE
- Always create/update relevant README or plan files for each subsystem.
- Follow naming convention: `README_<subsystem>.md`
- Use emoji headers (e.g., 🧠, ⚙️, 📊) to visually separate sections.
- Keep all Markdown files human-readable and Claude-readable.

---

## 🔒 SECURITY & COMPLIANCE
- No production credentials are ever stored in code.
- `.env` values must always remain blank placeholders.
- Sensitive data must never be included in examples or logs.

---

## 🔁 ITERATIVE DEVELOPMENT FLOW
1. Review project context from `/docs/system/` files.
2. Generate or modify code.
3. Test locally with `pytest` or manual run.
4. Update `change_log.md`.
5. Request Founder approval before merging changes.

---

## 📜 VERSION HISTORY
| Version | Date | Author | Notes |
|----------|------|---------|-------|
| 1.0 | 2025-10-08 | Founder | Initial creation of Claude control file. |

