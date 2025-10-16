# Agent Definitions

**Purpose:** Define the 5 core agents that coordinate the Variant Exploration System.

**Defined by:** PRD-03 Agent Roles & Prompts  
**Version:** 1.0

---

## Agent Overview

| Agent | Phases | Role | Key Outputs |
|-------|--------|------|-------------|
| [**Planner**](planner_agent.md) | 0, 1, 10, 13 | SOP flow coordinator | Approvals, gates, milestones |
| [**Market Intelligence**](market_agent.md) | 2-7 | Evidence gathering & analysis | Pain scores, market data |
| [**Finance**](finance_agent.md) | 8 | Unit economics & ROI | Financial models |
| [**Risk**](risk_agent.md) | 9 | Risk assessment & mitigation | Risk register |
| [**Documentation**](doc_agent.md) | 11, 12 | Report synthesis & audit | ADSR report, decision log |

---

## Agent Interaction Pattern

```
Orchestrator
    ↓
Reads current phase → Loads agent definition
    ↓
Agent prompts user → Guides template completion
    ↓
User completes task → Confirms (y) or pauses (n)
    ↓
If confirmed → Save artifact, log decision, advance phase
If paused → Save state, wait for completion
```

---

## Phase-Agent Mapping

See `orchestrator/config/phase_agent_map.json` for complete mapping.

**Quick reference:**
- **Phases 0-1:** Planner (intake, scope)
- **Phases 2-7:** Market Intelligence (research, evidence, pain, market)
- **Phase 8:** Finance (unit economics)
- **Phase 9:** Risk (risk assessment)
- **Phase 10:** Planner (GTM strategy)
- **Phases 11-12:** Documentation (synthesis, decision)
- **Phase 13:** Planner (comparison)

---

## How Agents Work

### **Each Agent Definition Contains:**
1. **Purpose** - What this agent does
2. **Responsibilities** - Which phases they handle
3. **Interaction Pattern** - How they guide the user
4. **Prompts** - Exact prompts for each phase
5. **Inputs** - What data they need
6. **Outputs** - What artifacts they create
7. **Key Principles** - Best practices

### **Agents Guide, Don't Decide:**
- ✅ Agents ask questions
- ✅ Agents suggest options
- ✅ Agents validate inputs
- ❌ Agents never make decisions
- ❌ Agents never auto-approve

**You (the human) remain the decision-maker at every step.**

---

## Usage

### **In Cursor/Claude:**

When orchestrator runs, it:
1. Loads the agent definition file for current phase
2. Shows you the agent's prompt
3. Guides you through template completion
4. Waits for your confirmation

**Example interaction:**
```
[Phase 0] Idea Intake → Assigned Agent: Planner
→ Task: Fill out /templates/idea_intake.md
→ Agent guidance: [Shows planner_agent.md prompts]
→ You complete the template
Confirm completion (y/n)? y
✅ Phase 0 complete. Proceeding to Phase 1...
```

---

## Agent Files

- `planner_agent.md` - Flow coordination and gates
- `market_agent.md` - Evidence and competitive intelligence
- `finance_agent.md` - Economics and ROI modeling
- `risk_agent.md` - Risk identification and mitigation
- `doc_agent.md` - Synthesis and audit trail

**All agents documented, version-controlled, and cross-referenced with PRD-03.** 📋

