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

        task_description = context.inputs.get('task_description', '')
        target_directory = context.inputs.get('target_directory', '.')
        file_patterns = context.inputs.get('file_patterns', ['*.py'])
        max_files = context.inputs.get('max_files', 50)

        # 1. Parse task_description to identify keywords
        keywords = self._extract_keywords(task_description)

        # 2. Scan directory for matching files (gitignore-aware)
        files_found = self._scan_directory(target_directory, file_patterns, max_files)

        # 3. Build symbol map using AST
        symbols = self._extract_symbols(files_found, keywords)

        # 4. Filter to relevant paths
        relevant_files = self._filter_relevant_files(symbols, keywords)

        # 5. Generate compact summary
        summary = self._generate_summary(relevant_files, keywords)

        file_map = {
            'files_found': [str(f) for f in relevant_files],
            'symbols': symbols,
            'summary': summary,
            'keywords_matched': keywords
        }

        confidence = min(1.0, len(relevant_files) / 10.0) if relevant_files else 0.3

        return AgentOutput(
            agent_name=self.name,
            decision="complete",
            reasoning=f"Mapped {len(relevant_files)} relevant files with {len(symbols)} symbols",
            data_for_next_agent=file_map,
            confidence=confidence,
            metadata={
                'execution_mode': 'silent',
                'artifact_type': 'file_map',
                'files_scanned': len(files_found),
                'files_relevant': len(relevant_files)
            }
        )

    def _extract_keywords(self, task_description: str) -> List[str]:
        """Extract relevant keywords from task description."""
        if not task_description:
            return []

        # Simple keyword extraction - split on common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = task_description.lower().replace(',', ' ').replace('.', ' ').split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:10]  # Limit to top 10

    def _scan_directory(self, target_dir: str, patterns: List[str], max_files: int) -> List[Path]:
        """Scan directory for files matching patterns (gitignore-aware)."""
        import fnmatch

        target_path = Path(target_dir)
        if not target_path.exists():
            logger.warning(f"Directory not found: {target_dir}")
            return []

        # Load gitignore patterns
        gitignore_patterns = self._load_gitignore(target_path)

        files = []
        for pattern in patterns:
            for file_path in target_path.rglob(pattern):
                if file_path.is_file():
                    # Check if file should be ignored
                    relative_path = file_path.relative_to(target_path)
                    if not self._is_ignored(relative_path, gitignore_patterns):
                        files.append(file_path)
                        if len(files) >= max_files:
                            break
            if len(files) >= max_files:
                break

        return files

    def _load_gitignore(self, root_path: Path) -> List[str]:
        """Load gitignore patterns from .gitignore file."""
        gitignore_file = root_path / '.gitignore'
        patterns = []

        if gitignore_file.exists():
            try:
                with open(gitignore_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                logger.warning(f"Error reading .gitignore: {e}")

        # Add common patterns
        patterns.extend(['__pycache__', '*.pyc', '.git', 'node_modules', 'venv', '.env'])
        return patterns

    def _is_ignored(self, path: Path, patterns: List[str]) -> bool:
        """Check if path matches any gitignore pattern."""
        import fnmatch

        path_str = str(path)
        for pattern in patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(path_str, f'*/{pattern}'):
                return True
            # Check if any part of the path matches
            for part in path.parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False

    def _extract_symbols(self, files: List[Path], keywords: List[str]) -> Dict[str, Any]:
        """Extract symbols (classes, functions) from Python files using AST."""
        import ast

        symbols = {}
        for file_path in files:
            if not file_path.suffix == '.py':
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                file_symbols = {
                    'classes': [],
                    'functions': [],
                    'imports': []
                }

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        file_symbols['classes'].append({
                            'name': node.name,
                            'line': node.lineno
                        })
                    elif isinstance(node, ast.FunctionDef):
                        file_symbols['functions'].append({
                            'name': node.name,
                            'line': node.lineno
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            file_symbols['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_symbols['imports'].append(node.module)

                if file_symbols['classes'] or file_symbols['functions']:
                    symbols[str(file_path)] = file_symbols

            except Exception as e:
                logger.debug(f"Error parsing {file_path}: {e}")
                continue

        return symbols

    def _filter_relevant_files(self, symbols: Dict[str, Any], keywords: List[str]) -> List[Path]:
        """Filter to only files relevant to keywords."""
        if not keywords:
            return [Path(f) for f in list(symbols.keys())[:20]]  # Return first 20 if no keywords

        relevant = []
        for file_path, file_symbols in symbols.items():
            # Check if any symbol names match keywords
            all_names = (
                [c['name'].lower() for c in file_symbols.get('classes', [])] +
                [f['name'].lower() for f in file_symbols.get('functions', [])] +
                [i.lower() for i in file_symbols.get('imports', [])]
            )

            # Check file path
            file_path_lower = file_path.lower()

            for keyword in keywords:
                if any(keyword in name for name in all_names) or keyword in file_path_lower:
                    relevant.append(Path(file_path))
                    break

        return relevant[:30]  # Limit to 30 most relevant files

    def _generate_summary(self, files: List[Path], keywords: List[str]) -> str:
        """Generate compact summary of findings."""
        if not files:
            return "No relevant files found matching the task description."

        summary_parts = [
            f"Found {len(files)} relevant file(s)",
        ]

        if keywords:
            summary_parts.append(f"matching keywords: {', '.join(keywords[:5])}")

        return " ".join(summary_parts)

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: File scanning can be I/O intensive, async allows
        other agents to continue working while we map files.
        """
        # TODO: Implement async file scanning
        # For now, just call sync version
        return self.execute(context)
