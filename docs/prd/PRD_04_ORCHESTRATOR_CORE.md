---
title: "PRD-04 — Orchestrator Core"
version: "1.0"
owner: "Rob"
date: "2025-10-16"
project: "Variant Exploration System"
status: "Planned"
description: >
  Defines the architecture, workflow logic, and data interactions for the
  Orchestrator Core. The Orchestrator coordinates agent execution, manages
  state transitions, enforces gating, and maintains full auditability of the
  Variant Exploration System (VES) process.
---

# 📘 PRD‑04 — Orchestrator Core

## 1️⃣ Objective
Develop a lightweight orchestrator that coordinates all agent activities,
phase transitions, and artifact creation within the Variant Exploration
System. The orchestrator ensures human‑in‑loop confirmation at each stage,
tracking every decision for audit and reproducibility.

---

## 2️⃣ Scope

### Included
- Orchestration logic for sequential phase control (0–13).
- Activation of the appropriate agent based on SOP phase.
- State management via `/state/state_schema.json`.
- Logging of every action, file creation, and user confirmation.
- Integration hooks for Cursor and Claude execution loops.

### Excluded
- Full backend automation (to be implemented later).
- External data collection or API connectors.
- UI or dashboard visualization (handled in future PRDs).

---

## 3️⃣ Functional Overview

| Function | Description |
|-----------|-------------|
| **Phase Control** | Reads current SOP phase and invokes correct agent. |
| **Confirmation Gate** | Awaits human approval before advancing to next phase. |
| **Artifact Binding** | Loads schema and template for current phase, validates output. |
| **State Logging** | Updates `/logs/audit_trail.json` after every interaction. |
| **Agent Routing** | Sends context and outputs between agents and human. |
| **Error Handling** | Detects missing data or schema violations and pauses for correction. |

---

## 4️⃣ Core Data Structures

### `/state/state_schema.json`
Tracks overall workflow status.

```jsonc
{
  "current_phase": 0,
  "phase_name": "idea_intake",
  "status": "in_progress",
  "last_action": "initialized",
  "approvals": [],
  "next_phase": 1
}
```

### `/logs/audit_trail.json`
Stores chronological event data for compliance and transparency.

```jsonc
{
  "timestamp": "2025-10-16T12:00:00Z",
  "agent": "Planner",
  "phase": 3,
  "action": "User confirmed completion of research_plan.md",
  "comment": "Proceed to next phase."
}
```

---

## 5️⃣ High‑Level Workflow

1. **Initialization**
   - Load state file; if none exists, create one at phase 0.
   - Confirm schema and template directories exist.

2. **Agent Activation**
   - Read current phase → map to assigned agent.
   - Load relevant schema and template.
   - Pass current state + user context to agent.

3. **Human‑in‑Loop Confirmation**
   - Present agent’s output to user (in Cursor or Claude).
   - Request approval / modification / rejection.
   - On approval → save artifact + update state.

4. **Validation & Logging**
   - Validate artifact structure against schema.
   - Log action, timestamp, and responsible agent.

5. **Transition**
   - Increment phase index.
   - If phase = 13 (final), trigger Documentation Agent → close workflow.

---

## 6️⃣ Integration Diagram (Text‑based)

```
[Human User]
     │
     ▼
[Orchestrator] ──► Reads state_schema.json
     │
     ├──► [Planner Agent] → controls phase flow
     ├──► [Market Intelligence Agent]
     ├──► [Finance Agent]
     ├──► [Risk Agent]
     ├──► [Documentation Agent]
     ▼
 Updates
(audit_trail.json, decision_log.json)
```

**Commentary:**  
This architecture mirrors a lightweight *state machine* pattern. Cursor executes the
main orchestrator script, which loads the next agent prompt (in Markdown) and
waits for human approval before proceeding. The design keeps transparency high
and allows human override at any stage.

---

## 7️⃣ Example Pseudocode

```python
def run_orchestrator():
    state = load_state("state/state_schema.json")
    while state["current_phase"] <= 13:
        phase = state["current_phase"]
        agent = assign_agent(phase)
        schema = load_schema(phase)
        template = load_template(phase)

        output = agent.run(schema, template, context=state)

        show_to_user(output)
        approval = get_user_confirmation()

        if approval:
            save_artifact(phase, output)
            log_action(agent, phase, "approved")
            state = advance_phase(state)
        else:
            log_action(agent, phase, "rework_requested")
            break

    finalize_workflow(state)
```

---

## 8️⃣ Acceptance Criteria

| ID | Requirement | Verification |
|----|--------------|--------------|
| OC‑1 | Orchestrator loads and maintains `state_schema.json` | Manual test |
| OC‑2 | Correct agent called for each phase | Functional test |
| OC‑3 | Human confirmation required for every transition | Simulated workflow |
| OC‑4 | All artifacts validated against schemas | JSON validation |
| OC‑5 | Full audit trail persisted in `/logs/audit_trail.json` | File inspection |

---

## 9️⃣ Dependencies

| Dependency | Type | Relation |
|-------------|------|----------|
| PRD‑01 Schema Layer | Upstream | Provides artifact definitions |
| PRD‑02 Templates | Upstream | Provides structured inputs |
| PRD‑03 Agent Roles | Upstream | Provides agent logic and prompts |
| PRD‑05 Audit & Logging | Downstream | Will extend logging and version control |

---

## 🔟 Milestones

| Step | Deliverable | ETA | Owner |
|------|--------------|-----|-------|
| M1 | Define `/state/` and `/logs/` directories | Day 1 | Dev Agent |
| M2 | Build orchestrator core script with pseudocode logic | Day 2 | Dev Agent |
| M3 | Manual run‑through of full SOP cycle (mock data) | Day 3 | Rob |
| M4 | Commit + tag `orchestrator-v1.0` | Day 3 | Planner Agent |

---

## 11️⃣ Success Metrics
- Orchestrator completes full SOP cycle end‑to‑end without errors.  
- All decisions traceable in audit trail.  
- Cursor and Claude can both operate seamlessly within the flow.  

---

## 12️⃣ Risks & Mitigations

| Risk | Impact | Mitigation |
|-------|---------|------------|
| Agent mis‑triggering | High | Use strict mapping table per phase |
| State corruption | Medium | Save backup before each transition |
| Human fatigue from confirmations | Low | Allow batch confirmation on non‑critical steps |

---

## ✅ Approval

| Role | Name | Date | Signature |
|------|------|------|------------|
| Product Owner | Rob | 2025‑10‑16 | — |
| Technical Reviewer | TBD | — | — |
