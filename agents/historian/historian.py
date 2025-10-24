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

        project_id = context.inputs.get('project_id', 'unknown')
        session_id = context.inputs.get('session_id', 'unknown')
        files_changed = context.inputs.get('files_changed', [])
        rationale = context.inputs.get('rationale', '')
        project_root = context.inputs.get('project_root', '.')

        # 1. Identify key files that changed
        if not files_changed:
            files_changed = self._get_git_changed_files(project_root)

        # 2. Generate summaries per file
        file_summaries = self._generate_file_summaries(files_changed, project_root)

        # 3. Extract/use rationale
        if not rationale:
            rationale = self._extract_rationale_from_git(project_root)

        # 4. Identify open risks
        open_risks = self._identify_risks(files_changed, project_root)

        # 5. Document next steps
        next_steps = self._extract_next_steps(files_changed, project_root)

        # 6. Update PROJECT_SNAPSHOT.md
        snapshot_path = Path(project_root) / 'PROJECT_SNAPSHOT.md'
        self._update_snapshot_file(snapshot_path, file_summaries, rationale, open_risks, next_steps)

        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'project_id': project_id,
            'session_id': session_id,
            'files_changed': files_changed,
            'file_summaries': file_summaries,
            'rationale': rationale,
            'open_risks': open_risks,
            'next_steps': next_steps,
            'summary': f'Snapshot created: {len(files_changed)} files, {len(open_risks)} risks, {len(next_steps)} next steps'
        }

        confidence = 0.9 if files_changed else 0.5

        return AgentOutput(
            agent_name=self.name,
            decision="snapshot_created",
            reasoning=f"Created snapshot with {len(files_changed)} files and {len(open_risks)} identified risks",
            data_for_next_agent=snapshot,
            confidence=confidence,
            metadata={
                'execution_mode': 'silent',
                'artifact_type': 'checkpoint',
                'loc_changed': self._count_loc_changed(files_changed, project_root)
            }
        )

    def _get_git_changed_files(self, project_root: str) -> List[str]:
        """Get list of changed files from git status."""
        import subprocess

        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                files = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        # Parse git status output (format: "XY filename")
                        parts = line.strip().split(maxsplit=1)
                        if len(parts) == 2:
                            files.append(parts[1])
                return files
        except Exception as e:
            logger.warning(f"Error getting git status: {e}")

        return []

    def _generate_file_summaries(self, files: List[str], project_root: str) -> Dict[str, str]:
        """Generate 10-line summary per file."""
        summaries = {}

        for file_path in files[:20]:  # Limit to 20 files
            full_path = Path(project_root) / file_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Simple summary: first 10 non-empty lines or docstring
                summary_lines = []
                for line in lines[:50]:  # Check first 50 lines
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        summary_lines.append(line.rstrip())
                    if len(summary_lines) >= 10:
                        break

                summaries[file_path] = '\n'.join(summary_lines[:10])

            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")
                summaries[file_path] = f"[Error reading file: {e}]"

        return summaries

    def _extract_rationale_from_git(self, project_root: str) -> str:
        """Extract rationale from recent git commit messages."""
        import subprocess

        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Error getting git log: {e}")

        return "No recent commit messages found"

    def _identify_risks(self, files: List[str], project_root: str) -> List[str]:
        """Identify open risks from TODOs, FIXMEs, and incomplete features."""
        risks = []

        for file_path in files[:20]:
            full_path = Path(project_root) / file_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        line_lower = line.lower()
                        if 'todo' in line_lower or 'fixme' in line_lower or 'xxx' in line_lower:
                            risks.append(f"{file_path}:{line_num} - {line.strip()}")

                        if len(risks) >= 10:  # Limit to top 10 risks
                            break

            except Exception as e:
                logger.debug(f"Error scanning {file_path}: {e}")

        return risks[:10]

    def _extract_next_steps(self, files: List[str], project_root: str) -> List[str]:
        """Extract next steps from TODO comments and incomplete implementations."""
        next_steps = []

        # Look for TODO comments that suggest next steps
        for file_path in files[:10]:
            full_path = Path(project_root) / file_path
            if not full_path.exists():
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if 'TODO:' in line or 'NEXT:' in line:
                            # Extract the TODO text
                            todo_text = line.split('TODO:', 1)[-1].split('NEXT:', 1)[-1].strip()
                            if todo_text and len(todo_text) > 10:
                                next_steps.append(todo_text[:100])  # Limit length

                        if len(next_steps) >= 5:
                            break

            except Exception as e:
                logger.debug(f"Error reading {file_path}: {e}")

        if not next_steps:
            next_steps = ["Continue implementation", "Add tests", "Update documentation"]

        return next_steps[:5]

    def _count_loc_changed(self, files: List[str], project_root: str) -> int:
        """Count lines of code changed."""
        import subprocess

        try:
            result = subprocess.run(
                ['git', 'diff', '--stat'],
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse last line which has format: "X files changed, Y insertions(+), Z deletions(-)"
                last_line = result.stdout.strip().split('\n')[-1]
                if 'changed' in last_line:
                    # Extract numbers
                    import re
                    numbers = re.findall(r'\d+', last_line)
                    if len(numbers) >= 2:
                        return int(numbers[1])  # insertions count
        except Exception as e:
            logger.debug(f"Error counting LOC: {e}")

        return len(files) * 10  # Rough estimate

    def _update_snapshot_file(
        self,
        snapshot_path: Path,
        file_summaries: Dict[str, str],
        rationale: str,
        risks: List[str],
        next_steps: List[str]
    ):
        """Update PROJECT_SNAPSHOT.md with rolling state (≤200 lines)."""
        try:
            content = f"""# PROJECT SNAPSHOT
Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Recent Changes

{rationale}

## Modified Files ({len(file_summaries)})

"""
            # Add file summaries (limit to keep under 200 lines)
            for file_path, summary in list(file_summaries.items())[:10]:
                content += f"### {file_path}\n```\n{summary}\n```\n\n"

            content += "## Open Risks\n\n"
            for risk in risks:
                content += f"- {risk}\n"

            content += "\n## Next Steps\n\n"
            for i, step in enumerate(next_steps, 1):
                content += f"{i}. {step}\n"

            # Write to file
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Updated {snapshot_path}")

        except Exception as e:
            logger.warning(f"Error updating snapshot file: {e}")

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: File reading and summarization can be I/O intensive,
        async allows other agents to continue working.
        """
        # TODO: Implement async snapshot creation
        # For now, just call sync version
        return self.execute(context)
