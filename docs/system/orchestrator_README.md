# ORCHESTRATOR – README
**Version:** 1.0  
**Maintainer:** Founder (Rob)  
**Date:** 2025-10-08  

---

## 🎯 PURPOSE
The **Orchestrator** is the coordination layer of the AI Management-Team system.  
It manages agent execution order, persistent memory updates, and structured logging — forming the backbone for workflow automation, oversight, and later Slack / dashboard integration.

---

## 🧱 CORE RESPONSIBILITIES
| Function | Description |
|-----------|--------------|
| **Load Memory** | Fetch each agent's persistent state from `/memory/{agent}.json`. |
| **Execute Agent** | Call or simulate agent reasoning (placeholder now, Claude call later). |
| **Update Memory** | Write new decisions, notes, and metrics back to memory files. |
| **Log Activity** | Record structured JSONL logs for auditing and analytics. |
| **Print Summary** | Display a quick, human-readable report for the Founder. |

---

## 🧩 FILE STRUCTURE

```
/scripts/
  └── orchestrator.py        # Main coordination script

/src/utils/
  └── memory_manager.py      # Persistent memory utilities

/memory/
  ├── strategy_agent.json
  ├── financial_agent.json
  ├── technical_architect.json
  ├── operations_agent.json
  └── data_agent.json

/logs/
  └── YYYY-MM-DD_ProjectName.jsonl   # Structured activity log
```

---

## 🚀 USAGE

### Basic Invocation
```bash
# Activate virtual environment
source .venv/bin/activate

# Run orchestrator for a project
python scripts/orchestrator.py
```

### Custom Project
```python
from scripts.orchestrator import Orchestrator

orchestrator = Orchestrator("Custom_Project_Name")
orchestrator.run()
```

---

## 🔄 WORKFLOW SEQUENCE

The orchestrator follows the agent order defined in `system_context.yaml`:

```
1. Strategy Agent       → Market positioning & prioritization
2. Financial Agent      → ROI validation & budget approval  
3. Technical Architect  → Architecture & compliance review
4. Operations Agent     → Execution planning & sequencing
5. Data Agent          → Performance metrics & learning
```

### For Each Agent:
1. **Load Memory** → Retrieve agent's past decisions and preferences
2. **Execute** → Run agent logic (currently simulated, will integrate with Claude)
3. **Log Result** → Record decision, score, and reasoning to JSONL
4. **Update Memory** → Save new project record and metrics
5. **Continue** → Move to next agent in sequence

---

## 📊 MEMORY STRUCTURE

Each agent maintains a JSON file with:

```json
{
  "agent": "strategy_agent",
  "last_updated": "2025-10-08T14:30:00",
  "project_history": [
    {
      "date": "2025-10-08",
      "project": "AI_Receptionist",
      "decision": "approved",
      "notes": "Strong ROI, market fit confirmed"
    }
  ],
  "preferences": {},
  "notes": [],
  "last_decision_score": 4.3
}
```

---

## 📝 LOG FORMAT

Activity logs use JSONL (JSON Lines) format:

```jsonl
{"event": "memory_loaded", "agent": "strategy_agent", "memory": {...}}
{"event": "agent_result", "agent": "strategy_agent", "result": {...}}
{"event": "memory_updated", "agent": "strategy_agent"}
{"event": "orchestration_complete", "project": "AI_Receptionist"}
```

---

## 🔧 CURRENT LIMITATIONS & FUTURE ENHANCEMENTS

### Current Version (1.0)
- ✅ Sequential agent execution
- ✅ Persistent memory per agent
- ✅ Structured logging
- ✅ Human-readable summaries
- ⚠️ Simulated agent logic (placeholder)

### Planned Enhancements
| Feature | Status | Target |
|---------|--------|--------|
| **Claude Code Integration** | 🕓 Planned | v1.1 |
| **YAML Config Loading** | 🕓 Planned | v1.1 |
| **Slack Notifications** | 🕓 Planned | v1.2 |
| **Dashboard API** | 🕓 Planned | v1.3 |
| **Vector Memory** | 🔜 Future | v2.0 |
| **Parallel Agent Execution** | 🔜 Future | v2.1 |

---

## 🛠️ INTEGRATION POINTS

### Memory Manager
```python
from src.utils.memory_manager import (
    load_memory,           # Load agent state
    update_memory,         # Save agent state
    add_project_record,    # Add project to history
    print_memory_summary   # Display agent summary
)
```

### System Context (Future)
```python
# Will load from system_context.yaml
import yaml

with open('docs/system/system_context.yaml') as f:
    config = yaml.safe_load(f)
    AGENT_ORDER = config['workflow_order']
```

---

## 🧪 TESTING

### Test Basic Flow
```bash
python scripts/orchestrator.py
```

Expected output:
```
🚀 Starting orchestration for project: AI_Receptionist

→ Loaded memory for strategy_agent
✅ strategy_agent completed with decision: approved (score 4.0)
💾 Memory updated for strategy_agent

→ Loaded memory for financial_agent
✅ financial_agent completed with decision: reviewed (score 3.5)
💾 Memory updated for financial_agent

[... continues for all agents ...]

🎯 All agents completed. Memory persisted.

🧠 Final Memory Summary:
[... displays recent projects for each agent ...]
```

### Verify Persistence
1. Run orchestrator once
2. Check `/memory/*.json` files created
3. Run orchestrator again
4. Verify project history accumulates

---

## 📋 TROUBLESHOOTING

### Issue: Import Error
**Symptom:** `ModuleNotFoundError: No module named 'src'`  
**Solution:** Ensure you're running from project root and path is set correctly

### Issue: Memory Not Persisting
**Symptom:** Agent history doesn't accumulate  
**Solution:** Check write permissions on `/memory/` directory

### Issue: Logs Not Creating
**Symptom:** No JSONL files in `/logs/`  
**Solution:** Verify `/logs/` directory exists (created automatically)

---

## 🔐 SECURITY & COMPLIANCE

- **PII Protection:** No client data in logs by default
- **File Permissions:** Memory files use standard permissions
- **Audit Trail:** JSONL logs provide complete activity history
- **GDPR Alignment:** Technical Architect validates compliance

---

## 📚 RELATED DOCUMENTATION

| File | Purpose |
|------|---------|
| `management_team_charter_v1.0.md` | System governance |
| `management_team_rules.yaml` | Decision criteria |
| `system_context.yaml` | Workflow dependencies |
| `project_progress_plan.md` | Development roadmap |
| `change_log.md` | System updates |

---

## 📞 SUPPORT & MAINTENANCE

**Owner:** Founder (Rob)  
**Review Cycle:** Monthly  
**Version Updates:** Track in `change_log.md`  
**Issues:** Document in `/docs/system/archive/issues/`

---

## 🎓 EXAMPLE SESSION

```bash
$ source .venv/bin/activate
$ python scripts/orchestrator.py

🚀 Starting orchestration for project: AI_Receptionist

→ Loaded memory for strategy_agent
✅ strategy_agent completed with decision: approved (score 4.0)
💾 Memory updated for strategy_agent

→ Loaded memory for financial_agent
✅ financial_agent completed with decision: reviewed (score 3.5)
💾 Memory updated for financial_agent

→ Loaded memory for technical_architect
✅ technical_architect completed with decision: reviewed (score 4.0)
💾 Memory updated for technical_architect

→ Loaded memory for operations_agent
✅ operations_agent completed with decision: reviewed (score 3.5)
💾 Memory updated for operations_agent

→ Loaded memory for data_agent
✅ data_agent completed with decision: reviewed (score 4.5)
💾 Memory updated for data_agent

🎯 All agents completed. Memory persisted.

🧠 Final Memory Summary:

🧠 MEMORY SUMMARY – strategy_agent
Last Updated: 2025-10-08T14:30:00
Recent Projects:
  - AI_Receptionist (approved) – Strong ROI, market fit confirmed
```

---

**Next Steps:**
1. Replace `_simulate_agent_run()` with actual Claude Code integration
2. Add YAML config loading for dynamic workflow
3. Integrate Slack webhook notifications (Phase 1)
4. Build dashboard API endpoints

---

**Version:** 1.0  
**Last Updated:** 2025-10-08  
**Status:** ✅ Core functionality complete, ready for Claude integration

