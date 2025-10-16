"""
file_manager.py
File system operations for dashboard
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from config import PROJECT_ROOT, OUTPUTS_DIR, RESULTS_DIR, DATA_DIR, MONITORED_EXTENSIONS


class FileManager:
    """Manages file operations for the dashboard."""

    def __init__(self):
        self.root = PROJECT_ROOT
        self.watch_dirs = [OUTPUTS_DIR, RESULTS_DIR, DATA_DIR]

    def get_file_tree(self, root_path: Path = None, sort_by: str = "name",
                      extension_filter: str = None) -> List[Dict[str, Any]]:
        """
        Build a file tree structure with optional sorting and filtering.

        Args:
            root_path: Root directory (defaults to watch_dirs)
            sort_by: Sort method - "name", "date", "size", "type"
            extension_filter: Filter by extension (e.g., ".md", ".yaml") or None for all

        Returns:
            List of directory/file dicts

        WHY: Flexible tree building for different use cases
        REASONING: Dashboard needs different views - recent files, config files, docs, etc.
        """
        self._extension_filter = extension_filter

        if root_path is None:
            # Return tree for all watched directories
            return [
                {
                    "name": dir.name,
                    "path": str(dir.relative_to(self.root)),
                    "type": "directory",
                    "children": self._build_tree(dir, sort_by)
                }
                for dir in self.watch_dirs if dir.exists()
            ]

        return self._build_tree(root_path, sort_by)

    def _build_tree(self, path: Path, sort_by: str = "name") -> List[Dict[str, Any]]:
        """
        Recursively build file tree with sorting.

        Args:
            path: Directory path to build tree from
            sort_by: Sort method - "name", "date", "size", "type"

        WHY: Users need organized file views to quickly find what they need
        REASONING: Alphabetical by default (predictable), but date/size useful for debugging
        """
        items = []

        try:
            for item in path.iterdir():
                # WHY: Skip hidden files - reduce noise, they're rarely needed
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    items.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.root)),
                        "type": "directory",
                        "children": self._build_tree(item, sort_by)
                    })
                else:
                    # Only include monitored file types
                    if item.suffix in MONITORED_EXTENSIONS or item.suffix == '':
                        # Apply extension filter if specified
                        if hasattr(self, '_extension_filter') and self._extension_filter:
                            if item.suffix != self._extension_filter:
                                continue

                        items.append({
                            "name": item.name,
                            "path": str(item.relative_to(self.root)),
                            "type": "file",
                            "size": item.stat().st_size,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                            "modified_timestamp": item.stat().st_mtime,
                            "extension": item.suffix
                        })
        except PermissionError:
            pass

        # WHY: Sort items for better UX
        # REASONING: Directories first (standard file browser behavior), then files by chosen method
        items = self._sort_items(items, sort_by)

        # Clean up temporary timestamp field
        for item in items:
            if "modified_timestamp" in item:
                del item["modified_timestamp"]

        return items

    def _sort_items(self, items: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """
        Sort file tree items.

        WHY: Consistent ordering makes files easier to find
        DESIGN: Directories always come first (standard file browser behavior)
        """
        # Separate directories and files
        dirs = [item for item in items if item["type"] == "directory"]
        files = [item for item in items if item["type"] == "file"]

        # Sort directories by name
        dirs.sort(key=lambda x: x["name"].lower())

        # Sort files by chosen method
        if sort_by == "name":
            files.sort(key=lambda x: x["name"].lower())
        elif sort_by == "date":
            # WHY: Most recent first - usually what developers care about
            files.sort(key=lambda x: x.get("modified_timestamp", 0), reverse=True)
        elif sort_by == "size":
            # WHY: Largest first - helps spot bloated files
            files.sort(key=lambda x: x.get("size", 0), reverse=True)
        elif sort_by == "type":
            # WHY: Group by extension - useful when looking for all .yaml or .md files
            files.sort(key=lambda x: (x.get("extension", ""), x["name"].lower()))

        return dirs + files

    def read_file(self, relative_path: str) -> Dict[str, Any]:
        """
        Read file contents.

        Args:
            relative_path: Path relative to project root

        Returns:
            Dict with content and metadata
        """
        file_path = self.root / relative_path

        if not file_path.exists():
            return {"error": "File not found", "path": relative_path}

        if not file_path.is_file():
            return {"error": "Not a file", "path": relative_path}

        try:
            content = file_path.read_text(encoding='utf-8')

            return {
                "path": relative_path,
                "content": content,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "extension": file_path.suffix
            }
        except Exception as e:
            return {"error": str(e), "path": relative_path}

    def write_file(self, relative_path: str, content: str) -> Dict[str, Any]:
        """
        Write file contents.

        Args:
            relative_path: Path relative to project root
            content: New file content

        Returns:
            Dict with success status
        """
        file_path = self.root / relative_path

        try:
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content, encoding='utf-8')

            return {
                "success": True,
                "path": relative_path,
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e), "path": relative_path}

    def delete_file(self, relative_path: str) -> Dict[str, Any]:
        """
        Delete a file.

        Args:
            relative_path: Path relative to project root

        Returns:
            Dict with success status
        """
        file_path = self.root / relative_path

        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return {"success": True, "path": relative_path}
            else:
                return {"success": False, "error": "File not found", "path": relative_path}
        except Exception as e:
            return {"success": False, "error": str(e), "path": relative_path}

    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently modified files.

        Args:
            limit: Number of files to return

        Returns:
            List of file dicts sorted by modification time
        """
        files = []

        for watch_dir in self.watch_dirs:
            if not watch_dir.exists():
                continue

            for file_path in watch_dir.rglob('*'):
                if file_path.is_file() and file_path.suffix in MONITORED_EXTENSIONS:
                    files.append({
                        "name": file_path.name,
                        "path": str(file_path.relative_to(self.root)),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "modified_timestamp": file_path.stat().st_mtime
                    })

        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified_timestamp'], reverse=True)

        # Remove timestamp and return limited results
        for f in files:
            del f['modified_timestamp']

        return files[:limit]
