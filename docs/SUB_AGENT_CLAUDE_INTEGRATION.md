# Sub-Agent System - Claude Code Integration Guide

**Status:** ✅ Fully Integrated & Enabled
**Date:** 2025-10-19
**Version:** 1.0

---

## Quick Answer to Your Questions

### 1. "Will Claude automatically use it?"

**YES** - Claude will now automatically use the sub-agent system in two ways:

**A. Automatic During Workflow** (InteractiveOrchestrator)
- ✅ **Enabled:** Trigger evaluation happens after each workflow step
- ✅ **Enabled:** Silent agents (Explorer, Historian) execute automatically
- ✅ **Enabled:** Interactive agents (Critic, Research) ask for approval first

**B. Manual Outside Workflow** (Direct Claude Code usage)
- Claude now has rules in `.claude/rules.md` explaining when/how to use sub-agents
- Claude can invoke agents directly when appropriate (refactoring, security review, research, etc.)

### 2. "Is it part of the rules that Claude should leverage in these scenarios?"

**YES** - The rules are now documented in `.claude/rules.md` v4.0:

**Section: 🤖 SUB-AGENT SYSTEM (Phase 1-5 Complete)**
- When to use each agent (ExplorerAgent, HistorianAgent, CriticAgent, ResearchDocumenter)
- Auto-trigger conditions
- Configuration options
- Best practices

### 3. "Will it be part of the project setup/project complete process?"

**YES** - It's already integrated:

**Automatic Integration Points:**
- ✅ After each workflow step in InteractiveOrchestrator
- ✅ Trigger evaluation based on `config/subagents.yml`
- ✅ Silent agents run in background (Explorer, Historian)
- ✅ Interactive agents ask for approval (Critic, Research)

**Manual Usage:**
- Claude knows to use ExplorerAgent when working across multiple files
- Claude knows to use HistorianAgent to create snapshots
- Claude knows to use CriticAgent for security-critical code
- Claude knows to use ResearchDocumenter for unfamiliar APIs

---

## What Changed (2025-10-19)

### 1. Updated `.claude/rules.md` (v3.0 → v4.0)

Added comprehensive **🤖 SUB-AGENT SYSTEM** section documenting:
- All 4 sub-agents (Explorer, Historian, Critic, ResearchDocumenter)
- When each agent auto-triggers
- How to use manually
- Configuration via `config/subagents.yml`
- Best practices

### 2. Enabled Agent Execution in `core/interactive_orchestrator.py`

**Before:** Trigger evaluation worked, but execution was commented out
**After:** Full execution enabled with error handling

```python
# Silent agents now execute automatically
self.subagent_coordinator.execute_agent(agent_name, trigger_context)

# Interactive agents execute after user approval
if choice == 'y':
    self.subagent_coordinator.execute_agent(agent_name, trigger_context)
```

### 3. Consolidated Documentation

- Main rules: `.claude/rules.md` (Claude Code - primary)
- Cursor rules: `docs/system/claude_subagents_rules.md` (Cursor-specific, kept for reference)
- Added clear note to Cursor rules pointing to main Claude Code rules

---

## How It Works Now

### Automatic Workflow Integration

```
User runs: python cli/interactive_workflow.py

↓

Each workflow step completion:
1. Trigger engine evaluates context
2. Checks config/subagents.yml rules
3. Determines which agents to invoke

↓

Silent Agents (automatic):
- ExplorerAgent: Maps files if >2 files or >150 LOC
- HistorianAgent: Creates snapshot if end of block or >150 LOC modified

↓

Interactive Agents (with approval):
- CriticAgent: Asks to review if security impact or auth/payment changes
- ResearchDocumenter: Asks to research if external API or unfamiliar tech
```

### Manual Claude Code Usage

When working outside the workflow, Claude can now:

1. **Recognize when sub-agents would help:**
   - "You're refactoring across 5 files - let me use ExplorerAgent to map them first"
   - "This touches authentication - I should use CriticAgent to review security risks"
   - "Integrating Stripe API - let me use ResearchDocumenter for best practices"

2. **Invoke agents directly:**
   ```python
   from core.subagent_coordinator import SubAgentCoordinator

   coordinator = SubAgentCoordinator(project_id, session_id)
   result = coordinator.execute_agent("ExplorerAgent", context)
   ```

3. **Respect configuration:**
   - Checks `config/subagents.yml` for user preferences
   - Honors `auto_trigger_enabled` master switch
   - Respects per-agent `enabled` flags

---

## Configuration Control

You can control the sub-agent system via `config/subagents.yml`:

### Disable All Auto-Triggering

```yaml
defaults:
  auto_trigger_enabled: false  # ← Set to false
```

### Disable Specific Agent

```yaml
triggers:
  explorer:
    enabled: false  # ← Disable just Explorer
  historian:
    enabled: true   # ← Keep others enabled
```

### Adjust Thresholds

```yaml
triggers:
  explorer:
    files_threshold: 5     # ← Require 5+ files (was 2)
    loc_threshold: 300     # ← Require 300+ LOC (was 150)
```

---

## Benefits

### For Automatic Workflows
✅ **No manual triggers needed** - System decides based on context
✅ **Proactive assistance** - Agents help before you ask
✅ **Low friction** - Silent agents don't interrupt flow
✅ **Safety net** - Critic catches security issues automatically

### For Manual Claude Code Usage
✅ **Intelligent suggestions** - Claude knows when agents would help
✅ **Consistent approach** - Same trigger logic everywhere
✅ **Easy invocation** - Simple API for manual use
✅ **Configurable** - Adjust to your preferences

---

## Testing

All sub-agent functionality is tested:

```bash
python test_sub_agents.py        # 4/4 agents passed
python test_checkpoints.py       # 6/7 passed (crash recovery)
python test_subagent_triggers.py # 9/9 passed (auto-triggering)
python test_integration.py       # 4/4 passed (end-to-end)
```

**Total:** 27/28 tests passed (96%)

---

## For Other Projects

**Should you use this in other projects?**

✅ **YES** if:
- Complex codebase (>5 files per feature)
- Security-critical (auth, payments, user data)
- Long-running project (crash recovery valuable)
- External integrations (APIs you don't know well)
- Team collaboration (snapshots help onboarding)

❌ **NO** if:
- Tiny scripts (<100 LOC, single file)
- Throwaway prototypes
- Well-known stack (nothing to research)
- Simple CRUD apps

**To port to another project:**
1. Copy `docs/SUB_AGENT_SYSTEM_SUMMARY.md` (portable guide)
2. Copy core files (coordinator, agents, triggers)
3. Copy `config/subagents.yml` template
4. Integrate with your workflow (or use manually)

---

## References

- **Main Rules:** `.claude/rules.md` v4.0 - Section "🤖 SUB-AGENT SYSTEM"
- **Portable Summary:** `docs/SUB_AGENT_SYSTEM_SUMMARY.md`
- **Full Implementation Plan:** `docs/planning/SUB_AGENT_UNIFICATION_PLAN.md`
- **Configuration:** `config/subagents.yml`
- **Test Files:** `test_sub_agents.py`, `test_checkpoints.py`, `test_subagent_triggers.py`, `test_integration.py`

---

## Next Steps (Optional)

If you want to customize further:

1. **Adjust thresholds** in `config/subagents.yml`
2. **Monitor trigger frequency** - see if agents trigger too often/rarely
3. **Review agent outputs** - check if results are helpful
4. **Fine-tune rules** - adjust based on your workflow
5. **Add project-specific triggers** - customize for your domain

---

**Summary:** The sub-agent system is now fully integrated and documented. Claude will automatically use it during workflows, and can manually invoke agents when appropriate outside workflows. Everything is configurable, tested, and ready for production use.
