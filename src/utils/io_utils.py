# ==============================================
# file: /ManagementTeam/src/utils/io_utils.py
# ==============================================
from __future__ import annotations
from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Create directory and all parent directories if they don't exist."""
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    """Write text content to file, creating parent directories if needed."""
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def read_text(path: Path) -> str:
    """Read text content from file."""
    return path.read_text(encoding="utf-8")

