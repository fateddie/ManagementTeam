# Orchestrator Core

**Purpose:** Coordinate agent execution through the 13-phase SOP with human-in-loop confirmation.

**Defined by:** PRD-04 Orchestrator Core  
**Version:** 1.0

---

## Architecture

```
orchestrator/
├── orchestrator_core.py    Main controller implementing PRD-04 logic
├── state/
│   └── state_schema.json   Workflow state tracking
├── logs/
│   └── audit_trail.json    Complete decision audit log
└── config/
    └── phase_agent_map.json Phase-to-agent mapping
```

---

## How It Works

### **1. Initialization**
```python
# Load or create state
state = {
    "variant_name": "my_variant",
    "current_phase": 0,
    "status": "initialized"
}
```

### **2. Phase Execution**
```python
for phase in range(14):  # Phases 0-13
    # Load agent for this phase
    agent = get_agent(phase)
    
    # Display task
    print(f"[Phase {phase}] {phase_name} → Agent: {agent}")
    print(f"→ Task: Fill out {template_file}")
    
    # Wait for confirmation
    confirmed = input("Confirm completion (y/n)? ")
    
    if confirmed == "y":
        save_artifact()
        log_decision()
        advance_phase()
    else:
        pause_workflow()
        break
```

### **3. State Management**
```python
# After each action
state["current_phase"] = next_phase
state["last_updated"] = timestamp()
save_json(STATE_FILE, state)

# If paused
state["status"] = "paused"
state["paused_at"] = timestamp()
# Can resume later at same phase
```

### **4. Audit Logging**
```python
# Every action logged
audit_trail.append({
    "timestamp": "2025-10-16T10:30:00Z",
    "variant": "my_variant",
    "phase": 5,
    "agent": "Market Intelligence",
    "action": "Phase 5 approved by user",
    "notes": ""
})
```

---

## Phase-Agent Mapping

See `config/phase_agent_map.json` for complete mapping.

| Phases | Agent | Focus |
|--------|-------|-------|
| 0-1 | Planner | Intake, scope |
| 2-7 | Market Intelligence | Research, evidence, pain, market |
| 8 | Finance | Unit economics |
| 9 | Risk | Risk assessment |
| 10 | Planner | GTM strategy |
| 11-12 | Documentation | Synthesis, decision |
| 13 | Planner | Comparison |

---

## Usage

### **Start New Variant:**
```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/variant_exploration_system
python run_orchestrator.py --variant my_variant
```

### **Resume Paused Variant:**
```bash
python run_orchestrator.py --variant my_variant
# Auto-resumes at saved phase
```

### **Start at Specific Phase:**
```bash
python run_orchestrator.py --variant my_variant --phase 5
```

### **Compare Variants:**
```bash
python run_orchestrator.py --compare
```

---

## Interaction Example

```
==========================================
  VARIANT EXPLORATION SYSTEM - ORCHESTRATOR
==========================================
Variant: email_for_freelancers
Current Phase: 0
Status: initialized
==========================================

==========================================
[Phase 0] Idea Intake → Assigned Agent: Planner
==========================================

📖 Agent Guidance:
See agents/planner_agent.md for complete guidance.

→ Task: Fill out /templates/idea_intake.md

📄 Template Preview:
----------------------------------------------------------------------
# Idea Intake Template

## Idea Name
<Enter your idea name>

## Description
<Briefly describe the concept>
...
----------------------------------------------------------------------

==========================================
⏸️  CONFIRMATION GATE
==========================================
Have you completed the required task for this phase?
  (y) Yes - Save and continue
  (n) No - Pause workflow, resume later
  (s) Skip this phase (not recommended)
==========================================

Confirm completion (y/n/s): y

✅ Phase 0 complete. Saving and proceeding...

[continues to Phase 1...]
```

---

## State Persistence

### **State Schema:**
```json
{
  "variant_name": "email_for_freelancers",
  "current_phase": 5,
  "status": "in_progress",
  "approvals": [
    {"phase": 0, "result": "approved", "timestamp": "..."},
    {"phase": 1, "result": "approved", "timestamp": "..."},
    ...
  ],
  "started_at": "2025-10-16T09:00:00Z",
  "last_updated": "2025-10-16T10:30:00Z"
}
```

### **Audit Trail:**
```json
[
  {
    "timestamp": "2025-10-16T09:05:00Z",
    "variant": "email_for_freelancers",
    "phase": 0,
    "agent": "Planner",
    "action": "Phase 0 approved by user",
    "notes": ""
  },
  {
    "timestamp": "2025-10-16T09:15:00Z",
    "variant": "email_for_freelancers",
    "phase": 1,
    "agent": "Planner",
    "action": "Phase 1 approved by user",
    "notes": ""
  }
]
```

---

## Key Features

- ✅ **Human-in-loop** - Confirmation required at every phase
- ✅ **State persistence** - Can pause and resume anytime
- ✅ **Agent coordination** - Right agent for each phase
- ✅ **Complete audit trail** - Every action logged
- ✅ **Template integration** - Auto-copies templates to variants
- ✅ **Comparison engine** - Cross-variant analysis built-in

---

## Error Handling

- Missing templates → Warning but continue
- Invalid JSON → Pause and request fix
- Missing agent definition → Use generic prompt
- State corruption → Backup and recovery

---

**The modular orchestrator implements PRD-04 specifications for rigorous, transparent workflow control.** ⚙️

