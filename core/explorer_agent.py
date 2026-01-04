"""
ExplorerAgent - Intelligent file/code mapping for complex tasks

WHY: Reduces main agent context load by creating targeted file maps only when needed.
Instead of loading entire codebase into context, ExplorerAgent identifies relevant
files/symbols and returns a compact summary (≤200 lines).

AUTO-TRIGGERS:
- Task affects >2 files
- Task involves >150 LOC
- High complexity tasks
- Unfamiliar codebase areas

USAGE:
    agent = ExplorerAgent()
    result = agent.explore({
        'task_description': 'Refactor authentication to use JWT',
        'files_to_modify': ['auth.py', 'middleware.py', 'tests/test_auth.py']
    })

OUTPUT:
    {
        'file_map': [...],  # Targeted file/symbol map
        'summary': '...',
        'artifact_path': '.history/explorer/20250104_015900.md',
        '_audit_trail': {...}
    }

Created: 2025-01-04 (Subagent System Implementation)
"""

import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ExplorerAgent:
    """
    Maps relevant files and symbols for complex tasks.

    Uses Glob and Grep tools to identify:
    - File paths relevant to task
    - Class/function definitions
    - Dependencies and imports
    - Related tests

    Returns compact, LLM-readable file map (≤200 lines).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize ExplorerAgent.

        Args:
            project_root: Root directory for exploration (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()

    def explore(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create targeted file map for task.

        Args:
            context: Task context with:
                - task_description: What's being done
                - files_to_modify: Known files to modify (optional)
                - search_terms: Keywords to search for (optional)
                - estimated_loc: Estimated lines of code

        Returns:
            Dict with file_map, summary, artifact_path, _audit_trail
        """
        task_desc = context.get('task_description', 'Unknown task')
        files_to_modify = context.get('files_to_modify', [])
        search_terms = context.get('search_terms', [])

        logger.info(f"🔍 ExplorerAgent mapping files for: {task_desc}")

        # Build file map
        file_map = []

        # 1. Map explicitly mentioned files
        for file_path in files_to_modify:
            file_info = self._map_file(file_path)
            if file_info:
                file_map.append(file_info)

        # 2. Search for related files if search terms provided
        if search_terms:
            related_files = self._search_related_files(search_terms)
            for file_path in related_files:
                if file_path not in files_to_modify:  # Avoid duplicates
                    file_info = self._map_file(file_path)
                    if file_info:
                        file_map.append(file_info)

        # Generate summary
        summary = self._generate_summary(file_map, task_desc)

        # Save artifact
        artifact_path = self._save_artifact(file_map, summary, context)

        result = {
            'success': True,
            'file_map': file_map,
            'summary': summary,
            'artifact_path': str(artifact_path),
            'artifact_type': 'file_map',
            '_audit_trail': {
                'generated_at': datetime.now().isoformat(),
                'task_description': task_desc,
                'files_mapped': len(file_map),
                'search_terms_used': search_terms,
                'files_to_modify': files_to_modify
            }
        }

        logger.info(f"✅ ExplorerAgent: Mapped {len(file_map)} files")

        return result

    def _map_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Map single file - extract key info.

        Returns:
            Dict with path, symbols, imports, notes or None if file doesn't exist
        """
        full_path = self.project_root / file_path

        if not full_path.exists():
            logger.warning(f"File not found: {file_path}")
            return None

        try:
            # Read file
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            # Extract symbols (classes, functions)
            symbols = self._extract_symbols(content, file_path)

            # Extract imports
            imports = self._extract_imports(content)

            return {
                'path': file_path,
                'line_count': len(lines),
                'symbols': symbols,
                'imports': imports[:10],  # Limit imports
                'notes': self._generate_file_notes(file_path, symbols)
            }

        except Exception as e:
            logger.warning(f"Error mapping {file_path}: {e}")
            return {
                'path': file_path,
                'error': str(e),
                'notes': 'Failed to read file'
            }

    def _extract_symbols(self, content: str, file_path: str) -> List[Dict[str, str]]:
        """Extract class and function definitions."""
        symbols = []

        # Python files
        if file_path.endswith('.py'):
            for line_num, line in enumerate(content.split('\n'), 1):
                # Class definitions
                if line.strip().startswith('class '):
                    class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                    symbols.append({
                        'type': 'class',
                        'name': class_name,
                        'line': line_num
                    })

                # Function definitions (not indented = top-level)
                elif line.startswith('def ') or line.startswith('async def '):
                    func_line = line.replace('async ', '')
                    func_name = func_line.split('def ')[1].split('(')[0].strip()
                    symbols.append({
                        'type': 'function',
                        'name': func_name,
                        'line': line_num
                    })

        # Limit to top 20 symbols
        return symbols[:20]

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)

        return imports

    def _search_related_files(self, search_terms: List[str]) -> List[str]:
        """
        Search for files containing search terms.

        Returns list of file paths (max 10 files).
        """
        related_files = set()

        for term in search_terms[:5]:  # Limit search terms
            try:
                # Use grep to search (faster than Python)
                result = subprocess.run(
                    ['grep', '-r', '-l', term, str(self.project_root / 'src'), str(self.project_root / 'core')],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    for file_path in result.stdout.strip().split('\n'):
                        if file_path:  # Non-empty
                            # Make relative to project root
                            rel_path = Path(file_path).relative_to(self.project_root)
                            related_files.add(str(rel_path))

                            if len(related_files) >= 10:
                                break

            except Exception as e:
                logger.warning(f"Search failed for '{term}': {e}")

        return list(related_files)[:10]

    def _generate_file_notes(self, file_path: str, symbols: List[Dict]) -> str:
        """Generate 1-line note about file."""
        if not symbols:
            return "No symbols detected"

        class_count = len([s for s in symbols if s['type'] == 'class'])
        func_count = len([s for s in symbols if s['type'] == 'function'])

        parts = []
        if class_count:
            parts.append(f"{class_count} class(es)")
        if func_count:
            parts.append(f"{func_count} function(s)")

        return ", ".join(parts) if parts else "File mapped"

    def _generate_summary(self, file_map: List[Dict], task_desc: str) -> str:
        """Generate human-readable summary."""
        total_files = len(file_map)
        total_symbols = sum(len(f.get('symbols', [])) for f in file_map)

        summary = f"Mapped {total_files} files with {total_symbols} symbols for: {task_desc}\n\n"

        # List files
        for file_info in file_map:
            path = file_info['path']
            notes = file_info.get('notes', '')
            summary += f"  - {path}: {notes}\n"

        return summary.strip()

    def _save_artifact(self, file_map: List[Dict], summary: str, context: Dict) -> Path:
        """Save exploration artifact to .history/explorer/"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_path = self.project_root / '.history' / 'explorer' / f"{timestamp}.md"

        # Create artifact content
        content = f"""# ExplorerAgent File Map

**Generated:** {datetime.now().isoformat()}
**Task:** {context.get('task_description', 'Unknown')}

---

## Summary

{summary}

---

## File Details

"""

        for file_info in file_map:
            content += f"### {file_info['path']}\n\n"

            if 'error' in file_info:
                content += f"**Error:** {file_info['error']}\n\n"
                continue

            content += f"**Lines:** {file_info.get('line_count', '?')}\n\n"

            # Symbols
            symbols = file_info.get('symbols', [])
            if symbols:
                content += "**Symbols:**\n"
                for symbol in symbols:
                    content += f"- `{symbol['name']}` ({symbol['type']}) - line {symbol['line']}\n"
                content += "\n"

            # Imports
            imports = file_info.get('imports', [])
            if imports:
                content += "**Key Imports:**\n"
                for imp in imports[:5]:  # Top 5
                    content += f"- `{imp}`\n"
                content += "\n"

        content += f"""---

**Audit Trail:**
- Files mapped: {len(file_map)}
- Search terms: {context.get('search_terms', [])}
- Files to modify: {context.get('files_to_modify', [])}

*Generated by ExplorerAgent v1.0*
"""

        # Write artifact
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(content, encoding='utf-8')

        logger.info(f"📄 Artifact saved: {artifact_path}")

        return artifact_path


# Convenience function for direct usage
def explore_files(
    task_description: str,
    files_to_modify: Optional[List[str]] = None,
    search_terms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to explore files.

    Usage:
        result = explore_files(
            task_description="Refactor auth system",
            files_to_modify=["core/auth.py", "core/middleware.py"],
            search_terms=["authenticate", "jwt"]
        )
    """
    agent = ExplorerAgent()
    return agent.explore({
        'task_description': task_description,
        'files_to_modify': files_to_modify or [],
        'search_terms': search_terms or []
    })
