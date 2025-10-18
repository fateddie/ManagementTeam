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
    - Filename/path unknown; need to map module/class/function definitions
    - Repo unfamiliar or recently changed (>100 modified LOC since last checkpoint)

OUTPUT:
    - Targeted file map (only relevant paths)
    - Symbol names with 1-2 line notes per item
    - Stored as sub-agent artifact in ProjectContext (queryable by dashboard)

EXECUTION MODE: Silent (background execution with brief progress update)

Created: 2025-10-18 (Phase 1 - Sub-Agent Unification)
"""

import logging
from typing import List, Dict, Any
from pathlib import Path

from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

logger = logging.getLogger(__name__)


class ExplorerAgent(BaseAgent):
    """
    Explorer Agent - Locate relevant code/files quickly.

    WHY: Minimize main agent context load by pre-mapping relevant files.
    Runs silently in background when complexity thresholds are met.
    """

    @property
    def name(self) -> str:
        """Agent identifier for registry and logging."""
        return "ExplorerAgent"

    @property
    def dependencies(self) -> List[str]:
        """
        No dependencies - utility agent can run independently.

        WHY: Explorer doesn't need output from other agents,
        it just needs the task context to know what to map.
        """
        return []

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that we have enough context to perform mapping.

        WHY: Need at least a task description or target directory.
        """
        task_description = context.inputs.get('task_description')
        target_directory = context.inputs.get('target_directory')

        if not task_description and not target_directory:
            logger.warning(f"{self.name}: No task description or target directory provided")
            return False

        return True

    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Build targeted file map for the given task.

        WHY: Main agent needs to know what files exist and where
        relevant symbols are defined before making changes.

        Args:
            context: Contains task_description, target_directory, file_patterns

        Returns:
            AgentOutput with file map data
        """
        logger.info(f"{self.name}: Starting file/code mapping...")

        # TODO: Implement actual file mapping logic
        # 1. Parse task_description to identify relevant keywords/symbols
        # 2. Scan target_directory for matching files (respect .gitignore)
        # 3. Build symbol map (classes, functions, imports) using AST
        # 4. Filter to only relevant paths (avoid noise)
        # 5. Generate compact findings summary

        # Placeholder implementation
        file_map = {
            'files_found': [],
            'symbols': {},
            'summary': 'TODO: Implement file mapping logic'
        }

        return AgentOutput(
            agent_name=self.name,
            decision="complete",
            reasoning="File mapping skeleton ready for implementation",
            data_for_next_agent=file_map,
            confidence=1.0,  # High confidence in placeholder structure
            metadata={
                'execution_mode': 'silent',
                'artifact_type': 'file_map'
            }
        )

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: File scanning can be I/O intensive, async allows
        other agents to continue working while we map files.
        """
        # TODO: Implement async file scanning
        # For now, just call sync version
        return self.execute(context)
