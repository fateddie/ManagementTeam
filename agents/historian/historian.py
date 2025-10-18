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
    - >150 modified LOC since last checkpoint
    - After PRD/architecture updates
    - Before major refactor or dependency changes

OUTPUT:
    - Snapshot of key files (paths + 10-line summaries per file)
    - Rationale for changes
    - Open risks and next steps
    - Stored as sub-agent artifact in ProjectContext (queryable by dashboard)

EXECUTION MODE: Silent (background execution with brief progress update)

Created: 2025-10-18 (Phase 1 - Sub-Agent Unification)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

logger = logging.getLogger(__name__)


class HistorianAgent(BaseAgent):
    """
    Historian Agent - Create LLM-readable project snapshots.

    WHY: Better project memory across sessions without re-scanning all files.
    Runs silently in background when change thresholds are met.
    """

    @property
    def name(self) -> str:
        """Agent identifier for registry and logging."""
        return "HistorianAgent"

    @property
    def dependencies(self) -> List[str]:
        """
        No dependencies - utility agent can run independently.

        WHY: Historian snapshots current state, doesn't need
        output from other agents to document what changed.
        """
        return []

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that we have context to create a meaningful snapshot.

        WHY: Need either project_id or files_changed to document.
        """
        project_id = context.inputs.get('project_id')
        files_changed = context.inputs.get('files_changed')

        if not project_id and not files_changed:
            logger.warning(f"{self.name}: No project_id or files_changed provided")
            return False

        return True

    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Create project snapshot of current state.

        WHY: Capture what changed and why for future sessions,
        enabling better LLM context continuity.

        Args:
            context: Contains project_id, session_id, files_changed, rationale

        Returns:
            AgentOutput with snapshot data
        """
        logger.info(f"{self.name}: Creating project snapshot...")

        project_id = context.inputs.get('project_id')
        session_id = context.inputs.get('session_id')
        files_changed = context.inputs.get('files_changed', [])
        rationale = context.inputs.get('rationale', '')

        # TODO: Implement actual snapshot logic
        # 1. Identify key files that changed (from git status or files_changed list)
        # 2. Generate 10-line summary per file (what/why/impact)
        # 3. Extract rationale from commit messages or provided context
        # 4. Identify open risks (TODOs, incomplete features, breaking changes)
        # 5. Document next steps (what's needed to complete current work)
        # 6. Store to ProjectContext as sub-agent artifact

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'project_id': project_id,
            'session_id': session_id,
            'files_changed': files_changed,
            'file_summaries': {},
            'rationale': rationale,
            'open_risks': [],
            'next_steps': [],
            'summary': 'TODO: Implement snapshot creation logic'
        }

        return AgentOutput(
            agent_name=self.name,
            decision="snapshot_created",
            reasoning="Project snapshot skeleton ready for implementation",
            data_for_next_agent=snapshot,
            confidence=1.0,  # High confidence in placeholder structure
            metadata={
                'execution_mode': 'silent',
                'artifact_type': 'checkpoint',
                'loc_changed': len(files_changed)
            }
        )

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: File reading and summarization can be I/O intensive,
        async allows other agents to continue working.
        """
        # TODO: Implement async snapshot creation
        # For now, just call sync version
        return self.execute(context)
