"""
cli_utils.py
Shared helpers for manage.py and future CLI features.
---------------------------------------------------------
Utility functions for CLI operations.
"""

from pathlib import Path
from typing import Dict, List


def list_outputs() -> List[str]:
    """List all output files."""
    outputs_dir = Path(__file__).parents[2] / "outputs"
    if not outputs_dir.exists():
        return []
    return [p.name for p in outputs_dir.glob("*.*") if p.is_file()]


def list_phases() -> Dict[int, str]:
    """Return phase definitions."""
    return {
        1: "Strategy Agent - Strategic Planning",
        2: "Technical Architect - Architecture Design",
        3: "Planning Agent - Unified Planning",
        4: "Research Agent - AI Validation",
        5: "Documentation Agent - Professional Docs",
        6: "Reporting Agent - Quality Control"
    }


def get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).parents[2]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_latest_summary() -> Path | None:
    """Get the latest build summary file."""
    reports_dir = get_project_root() / "outputs" / "reports"
    if not reports_dir.exists():
        return None
    
    summaries = sorted(
        reports_dir.glob("build_summary_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    return summaries[0] if summaries else None


def get_latest_validation() -> Path | None:
    """Get the latest validation report."""
    reports_dir = get_project_root() / "outputs" / "reports"
    if not reports_dir.exists():
        return None
    
    validations = sorted(
        reports_dir.glob("validation_report_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    return validations[0] if validations else None

