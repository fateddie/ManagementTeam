# PROJECT SNAPSHOT
Last Updated: 2025-10-24 11:02:50

## Recent Changes

Testing Phase 2 sub-agent implementation

## Modified Files (18)

### .claude/rules.md
```
**Version:** 3.0
**Date:** 2025-10-18
**Maintainer:** Founder (Rob)
---
**WHY These Rules Exist:**
These rules define how Claude should interpret, create, or modify files in this repository. They protect code integrity, maintain consistency, ensure traceability, and enforce modern best practices including error handling, async patterns, and tool usage.
**REASONING Behind Our Approach:**
Every technical decision in this project has a "why" - from error handling patterns to async execution to conversational workflows. We prioritize:
- **User Experience First**: Features should feel natural, not technical
- **Graceful Degradation**: System works with reduced features, never crashes
```

### agents/critic/critic.py
```
"""
critic.py
Critic Agent - Adversarial review sub-agent.
---------------------------------------------------------
WHY: Even well-intentioned plans have blind spots. The Critic provides
adversarial review before execution, identifying security vulnerabilities,
performance bottlenecks, edge cases, and failure modes that optimistic
planning might miss.
TRIGGER RULES (any):
    - Risky changes (auth, payments, credentials)
```

### agents/explorer/explorer.py
```
"""
explorer.py
Explorer Agent - File/code mapping utility sub-agent.
---------------------------------------------------------
WHY: When tackling refactors, bugfixes, or features spanning multiple files,
manually searching wastes time and context. Explorer builds a targeted file map
showing relevant paths, symbols, and brief notes—freeing the main agent to focus
on the task at hand.
TRIGGER RULES (any):
    - Task involves >2 files or >150 LOC
```

### agents/historian/historian.py
```
"""
historian.py
Historian Agent - Project snapshot utility sub-agent.
---------------------------------------------------------
WHY: Git diffs are machine-readable but LLM-unfriendly. Historian creates
lightweight snapshots capturing what changed, why it changed, and what's next—
enabling better context continuity across sessions and helping agents recall
project state without re-scanning everything.
TRIGGER RULES (any):
    - End of focused work block
```

### agents/orchestrator/agent_registry.yaml
```
agents:
  - name: StrategyAgent
    path: "agents.strategy_agent.strategy_agent:StrategyAgent"
    active: true # ✅ Phase 2 - NOW ACTIVE
    stage: 1
  - name: TechnicalArchitectAgent
    path: "agents.technical_architect.architect_agent:TechnicalArchitectAgent"
    active: true # ✅ Phase 3 - NOW ACTIVE
    stage: 2
  - name: PlanningAgent
```

### cli/interactive_workflow.py
```
"""
Interactive Workflow CLI
Command-line interface for conversational gated workflow.
PHASE 3 ENHANCEMENTS: Crash Recovery Support
- Auto-detect incomplete sessions
- Resume from checkpoints
- List available checkpoints
- Manual checkpoint creation
Usage:
    python cli/interactive_workflow.py                           # New idea (guided mode)
```

### config/subagents.yml
```
defaults:
  max_parallel_research: 3
  historian_snapshot_loc_threshold: 150
  ask_before_overwrite: true
  doc_domains_priority:
    - official       # Official docs first
    - github         # GitHub issues/examples second
    - trusted-blogs  # Trusted community blogs third
  auto_trigger_enabled: true
```

### core/interactive_orchestrator.py
```
"""
Interactive Orchestrator - Conversational gated workflow for idea validation.
Conducts natural conversation to refine ideas, gather requirements, and guide
users through research phases with educational context and soft validation.
"""
import sys
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
```

### core/workflow_state.py
```
"""
Workflow State - Persistent state management for gated workflow.
Handles auto-save, resume capability, and integration with ProjectContext.
PHASE 3 ENHANCEMENTS:
- Checkpoint integration for crash recovery
- Auto-checkpoint after each step completion
- Resume from checkpoint capability
- Version tracking for state format changes
"""
import json
```

### docs/system/claude_subagents_rules.md
```
> **⚠️ NOTE:** This document contains the original Cursor-specific sub-agent rules. For **Claude Code** usage, see the comprehensive sub-agent system documentation in `.claude/rules.md` (v4.0) which includes the fully-implemented Phase 1-5 system with ExplorerAgent, HistorianAgent, CriticAgent, and ResearchDocumenter.
>
> **This file is kept for:**
> - Reference for Cursor-based workflows
> - Historical context on original design
> - Alternative implementation approaches
>
> **For current Claude Code usage:** See `.claude/rules.md` → Section "🤖 SUB-AGENT SYSTEM"
---
Enable Claude Code to **automatically decide** when to invoke helpful subagents during project creation and task execution in Cursor—**without** Rob manually choosing. Keep it simple; prefer reuse of existing tools and data. No over‑engineering.
```

## Open Risks

- agents/critic/critic.py:363 - # TODO: Implement async adversarial review
- agents/explorer/explorer.py:295 - # TODO: Implement async file scanning
- agents/historian/historian.py:224 - """Identify open risks from TODOs, FIXMEs, and incomplete features."""
- agents/historian/historian.py:236 - if 'todo' in line_lower or 'fixme' in line_lower or 'xxx' in line_lower:
- agents/historian/historian.py:248 - """Extract next steps from TODO comments and incomplete implementations."""
- agents/historian/historian.py:251 - # Look for TODO comments that suggest next steps
- agents/historian/historian.py:260 - if 'TODO:' in line or 'NEXT:' in line:
- agents/historian/historian.py:261 - # Extract the TODO text
- agents/historian/historian.py:262 - todo_text = line.split('TODO:', 1)[-1].split('NEXT:', 1)[-1].strip()
- agents/historian/historian.py:263 - if todo_text and len(todo_text) > 10:

## Next Steps

1. Implement async adversarial review
2. Implement async file scanning
3. ', 1)[-1].strip()
4. Implement async snapshot creation
5. List available projects
