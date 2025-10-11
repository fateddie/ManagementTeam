# claude.md
## 🧭 Project Governance and Orchestration Guide
**Project:** Management Team — Planning & Research Agent System  
**Author:** Rob Freyne  
**Purpose:** Define the operational, architectural, and behavioral rules Claude Code must follow when completing this project.

---

## 1️⃣ Mission Statement
Claude Code's mission is to **implement, not redesign**.  
It must convert the approved PRD, YAML configs, and existing agent modules into a complete, working system — while preserving:

- The modular "Management Team" architecture
- Sequential, phase-gated planning
- YAML-defined behavioral logic
- Controlled use of external dependencies
- Human approval for any architectural or dependency change

---

## 2️⃣ Project Structure Overview
The repository consists of the following core layers:

| Layer | Purpose | Key Directories |
|-------|----------|----------------|
| **Management Layer** | High-level orchestration (Planning, Architect, Risk, etc.) | `/agents/management/` |
| **Planning Layer** | Reads project context, defines milestones, manages YAML-driven plans | `/agents/planning_agent/` |
| **Research Layer** | Calls Perplexity for external frameworks and validation | `/integrations/perplexity_connector.py` |
| **Execution Layer** | Later modules that act on plans (not yet implemented) | `/agents/execution_agent/` |
| **Docs & Config** | Source of truth for all behavior and planning rules | `/docs/`, `/config/` |
| **Outputs & Logs** | Generated files, reports, and research notes | `/outputs/`, `/logs/` |

Claude must **respect this hierarchy** and maintain clear boundaries between layers.

---

## 3️⃣ Phase-Gated Development Model
Claude Code must complete the system **sequentially**, not in parallel.

| Phase | Objective | Primary Deliverables |
|--------|------------|--------------------|
| **Phase 1: Orchestration Setup** | Implement clean orchestration between PlanningAgent, Research Connector, and Config | `orchestrator.py`, `config_loader.py` |
| **Phase 2: Agent Collaboration** | Establish Management layer agent that delegates tasks to Planning + Research | `management_agent.py` |
| **Phase 3: Reporting Layer** | Implement Markdown / PDF reporting and summary aggregation | `reporting_agent.py`, updated `outputs/` |
| **Phase 4: Testing & Validation** | Add automated tests, dependency checks, and basic CLI interface | `/tests/`, `cli.py` |
| **Phase 5: Integration Review** | System end-to-end validation; generate final build log and documentation summary | `build_summary.md` |

Claude must **ask for user approval** before moving to the next phase.

---

## 4️⃣ Design Principles
Claude must follow these principles throughout development:

1. **Read before writing.** Always parse the existing YAML and PRD to understand constraints before generating new code.  
2. **Never overwrite `/config/` or `/docs/` without permission.**  
3. **Modularity first.** Each agent or subsystem resides in its own folder with a clear interface.  
4. **YAML-driven logic.** Behavior should follow YAML configurations wherever possible.  
5. **Descriptive logging.** All modules must log key events to `/logs/` with timestamps.  
6. **No unnecessary dependencies.** Only use standard Python libraries unless already declared.  
7. **Reversible commits.** Each significant code block must be independent enough to roll back easily.

---

## 5️⃣ File-Level Rules
| Category | Rules |
|-----------|-------|
| **Inputs** | `/docs/PRD.md` and `/config/planning_agent_context.yaml` are the master references. |
| **Context Loader** | Do not modify `initialize_context.py` logic without explicit permission. |
| **Perplexity Integration** | Only trigger queries through the defined connector class. No direct API calls elsewhere. |
| **Output Files** | All generated files go into `/outputs/` with clear naming conventions. |
| **Logs** | Must include timestamps, event type, and agent name. |
| **Testing** | Each module must have at least one test in `/tests/` validating critical paths. |

---

## 6️⃣ Communication & Output Rules
Claude must provide:
1. A **summary.md** after each phase describing:
   - Files created or modified
   - Purpose of each file
   - Any new dependencies
   - Outstanding questions or blockers  
2. **Change previews** before applying multi-file edits.  
3. Markdown-formatted explanations for human readability.  

Example summary section:
```markdown
## Phase 1 Summary
- Added orchestrator.py — coordinates PlanningAgent + Research Connector
- Updated planning_agent.py — added orchestrator hooks
- No new dependencies added
- Next step: implement management_agent.py (Phase 2)
```

---

## 7️⃣ Workflow Cycle for Claude Code

### Before Starting a Phase:
1. Read `/docs/PRD.md` and related specs
2. Load `/config/planning_agent_context.yaml` and `/config/global.yaml`
3. Review existing code in `/src/agents/` and `/src/utils/`
4. Present plan to user for approval

### During Implementation:
1. Write clean, modular code with docstrings
2. Add logging to all critical operations
3. Follow existing code style and patterns
4. Test each component before moving on

### After Completing a Phase:
1. Generate `phase_X_summary.md` in `/outputs/`
2. Run validation script if available
3. Ask user to review before proceeding
4. Update `/docs/system/change_log.md`

---

## 8️⃣ Prohibited Actions

Claude **must not**:
- ❌ Change the fundamental architecture without approval
- ❌ Add dependencies not in `requirements.txt` without permission
- ❌ Modify YAML config files without user review
- ❌ Skip phases or work ahead
- ❌ Hardcode API keys or secrets
- ❌ Remove existing functionality without explicit request
- ❌ Auto-commit or auto-push to Git

---

## 9️⃣ Current Phase Status

**✅ Phase 0: Foundation Complete**
- Planning Agent v1 (template-based) ✅
- Planning Agent v2 (context-aware) ✅  
- Perplexity integration ✅
- Central config system ✅
- Documentation ✅

**🎯 Next: Phase 1 - Orchestration Setup**
Awaiting user approval to begin.

---

## 🔟 Success Criteria

Each phase is considered complete when:
- ✅ All planned files are created and documented
- ✅ Code passes basic manual testing
- ✅ Phase summary is generated
- ✅ User reviews and approves
- ✅ Changes are committed to Git

---

## 📋 Reference Documents (Priority Order)

1. `/docs/system/PRD.md` - Primary requirements
2. `/config/planning_agent_context.yaml` - Context rules
3. `/docs/system/planner_agent_spec.md` - Agent specifications
4. `/docs/system/file_structure.md` - Directory standards
5. `/claude/claude.md` - This file

---

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-10-11

