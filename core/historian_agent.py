"""
HistorianAgent - Project snapshot creator for crash recovery and context continuity

WHY: Maintains lightweight, LLM-readable project memory across sessions.
Instead of relying on Git diffs (noisy) or manual notes (incomplete),
HistorianAgent creates structured snapshots at key moments.

AUTO-TRIGGERS:
- End of focused work block
- >150 LOC modified
- PRD/architecture documents changed
- Major milestones reached

USAGE:
    agent = HistorianAgent()
    result = agent.create_snapshot({
        'modified_files': ['core/auth.py', 'tests/test_auth.py'],
        'modified_loc': 180,
        'milestone_reached': True,
        'session_summary': 'Implemented JWT authentication'
    })

OUTPUT:
    {
        'snapshot_path': '.history/checkpoints/20250104_015900.md',
        'project_snapshot_updated': True,
        'summary': '...',
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


class HistorianAgent:
    """
    Creates project snapshots for continuity and crash recovery.

    Maintains two outputs:
    1. PROJECT_SNAPSHOT.md - Rolling snapshot (≤200 lines, always current)
    2. .history/checkpoints/{timestamp}.md - Detailed checkpoint (archived)

    Snapshots include:
    - What changed (files, LOC, features)
    - Why it changed (rationale, decisions)
    - What's next (open tasks, risks)
    """

    MAX_SNAPSHOT_LINES = 200

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize HistorianAgent.

        Args:
            project_root: Root directory (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.snapshot_file = self.project_root / 'PROJECT_SNAPSHOT.md'
        self.checkpoints_dir = self.project_root / '.history' / 'checkpoints'

    def create_snapshot(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create project snapshot at current moment.

        Args:
            context: Snapshot context with:
                - session_summary: Brief summary of work done
                - modified_files: List of modified file paths
                - modified_loc: Lines of code modified
                - milestone_reached: Boolean, major milestone
                - rationale: Why changes were made
                - next_steps: List of next tasks
                - open_risks: List of known risks

        Returns:
            Dict with snapshot_path, project_snapshot_updated, summary, _audit_trail
        """
        session_summary = context.get('session_summary', 'Work session completed')
        modified_files = context.get('modified_files', [])
        modified_loc = context.get('modified_loc', 0)

        logger.info(f"📸 HistorianAgent creating snapshot: {session_summary}")

        # Detect modified files from git if not provided
        if not modified_files:
            modified_files = self._detect_modified_files()

        # Build checkpoint data
        checkpoint = self._build_checkpoint(context, modified_files)

        # Save detailed checkpoint
        checkpoint_path = self._save_checkpoint(checkpoint)

        # Update PROJECT_SNAPSHOT.md
        self._update_project_snapshot(checkpoint)

        # Generate summary
        summary = f"Snapshot created: {len(modified_files)} files changed, {modified_loc} LOC modified"

        result = {
            'success': True,
            'snapshot_path': str(checkpoint_path),
            'project_snapshot_updated': True,
            'summary': summary,
            'artifact_type': 'checkpoint',
            'checkpoint': checkpoint,
            '_audit_trail': {
                'generated_at': datetime.now().isoformat(),
                'session_summary': session_summary,
                'files_modified': len(modified_files),
                'loc_modified': modified_loc,
                'milestone_reached': context.get('milestone_reached', False)
            }
        }

        logger.info(f"✅ HistorianAgent: {summary}")

        return result

    def _detect_modified_files(self) -> List[str]:
        """Detect modified files from git status."""
        try:
            # Use git diff to find modified files
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
                return files

        except Exception as e:
            logger.warning(f"Git detection failed: {e}")

        return []

    def _build_checkpoint(self, context: Dict, modified_files: List[str]) -> Dict[str, Any]:
        """Build structured checkpoint data."""

        # File summaries (10-line max per file)
        file_summaries = []
        for file_path in modified_files[:10]:  # Max 10 files
            summary = self._summarize_file(file_path)
            file_summaries.append({
                'path': file_path,
                'summary': summary
            })

        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'session_summary': context.get('session_summary', 'Work completed'),
            'what_changed': {
                'files': file_summaries,
                'total_files': len(modified_files),
                'total_loc': context.get('modified_loc', 0),
                'milestone_reached': context.get('milestone_reached', False)
            },
            'why_changed': context.get('rationale', 'Feature implementation'),
            'next_steps': context.get('next_steps', ['Continue development']),
            'open_risks': context.get('open_risks', [])
        }

        return checkpoint

    def _summarize_file(self, file_path: str) -> str:
        """Generate 1-line summary of file changes."""

        full_path = self.project_root / file_path

        if not full_path.exists():
            return "File not found"

        try:
            # Check if it's a new file
            result = subprocess.run(
                ['git', 'diff', '--cached', '--', file_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3
            )

            if 'new file mode' in result.stdout:
                # Count lines
                lines = full_path.read_text(encoding='utf-8', errors='ignore').count('\n')
                return f"New file created ({lines} lines)"

            # Get diff stats
            result = subprocess.run(
                ['git', 'diff', '--shortstat', '--', file_path],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.stdout.strip():
                return result.stdout.strip().replace('1 file changed, ', '')

            return "Modified"

        except Exception:
            return "Changes detected"

    def _save_checkpoint(self, checkpoint: Dict) -> Path:
        """Save detailed checkpoint to .history/checkpoints/"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = self.checkpoints_dir / f"{timestamp}.md"

        # Create checkpoint content
        content = f"""# Checkpoint: {checkpoint['session_summary']}

**Timestamp:** {checkpoint['timestamp']}
**Milestone Reached:** {checkpoint['what_changed']['milestone_reached']}

---

## 📋 What Changed

**Files Modified:** {checkpoint['what_changed']['total_files']}
**Lines of Code:** {checkpoint['what_changed']['total_loc']}

"""

        # List file changes
        for file_info in checkpoint['what_changed']['files']:
            content += f"### {file_info['path']}\n"
            content += f"{file_info['summary']}\n\n"

        content += f"""---

## 💡 Why These Changes

{checkpoint['why_changed']}

---

## 🎯 Next Steps

"""

        for i, step in enumerate(checkpoint['next_steps'], 1):
            content += f"{i}. {step}\n"

        if checkpoint['open_risks']:
            content += "\n---\n\n## ⚠️ Open Risks\n\n"
            for risk in checkpoint['open_risks']:
                content += f"- {risk}\n"

        content += f"""
---

*Generated by HistorianAgent v1.0*
"""

        # Write checkpoint
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        checkpoint_path.write_text(content, encoding='utf-8')

        logger.info(f"📄 Checkpoint saved: {checkpoint_path}")

        return checkpoint_path

    def _update_project_snapshot(self, checkpoint: Dict):
        """Update PROJECT_SNAPSHOT.md with rolling snapshot."""

        # Build updated snapshot content
        content = f"""# 📸 Project Snapshot

**Last Updated:** {checkpoint['timestamp']}
**Updated By:** HistorianAgent
**Session:** {checkpoint['session_summary']}

---

## 🎯 Project Overview

**Name:** AI Management-Team System
**Status:** Active Development
**Last Major Milestone:** {checkpoint['session_summary'] if checkpoint['what_changed']['milestone_reached'] else 'In Progress'}

---

## 📋 What Changed Recently

{checkpoint['session_summary']}

**Files Modified:** {checkpoint['what_changed']['total_files']}
**Lines Changed:** {checkpoint['what_changed']['total_loc']}

"""

        # File changes
        content += "## 🔧 Key Files Modified\n\n"
        for file_info in checkpoint['what_changed']['files'][:5]:  # Top 5
            content += f"- **{file_info['path']}**: {file_info['summary']}\n"

        content += f"""
---

## 💡 Why These Changes

{checkpoint['why_changed']}

---

## ⚠️ Open Risks & Issues

"""

        if checkpoint['open_risks']:
            for risk in checkpoint['open_risks']:
                content += f"- {risk}\n"
        else:
            content += "*No critical risks identified*\n"

        content += "\n---\n\n## 🎯 Next Steps\n\n"

        for i, step in enumerate(checkpoint['next_steps'], 1):
            content += f"{i}. {step}\n"

        content += f"""
---

## 📌 Notes

This file is automatically maintained by **HistorianAgent** and provides a rolling snapshot of project state for crash recovery and context continuity.

**Max Length:** {self.MAX_SNAPSHOT_LINES} lines (older entries archived to `.history/checkpoints/`)
**Update Triggers:** End of work blocks, >150 LOC modified, PRD changes, milestones

---

*Generated by HistorianAgent v1.0*
"""

        # Trim to max lines if needed
        lines = content.split('\n')
        if len(lines) > self.MAX_SNAPSHOT_LINES:
            logger.info(f"Trimming snapshot from {len(lines)} to {self.MAX_SNAPSHOT_LINES} lines")
            lines = lines[:self.MAX_SNAPSHOT_LINES]
            lines.append("\n*[Older content archived to checkpoints]*")
            content = '\n'.join(lines)

        # Write snapshot
        self.snapshot_file.write_text(content, encoding='utf-8')

        logger.info(f"📄 Updated {self.snapshot_file}")

    def cleanup_old_snapshots(self, keep_count: int = 10):
        """Remove old checkpoint files, keeping only N most recent."""

        checkpoints = sorted(self.checkpoints_dir.glob('*.md'), reverse=True)

        if len(checkpoints) > keep_count:
            for checkpoint_path in checkpoints[keep_count:]:
                logger.info(f"🧹 Deleting old checkpoint: {checkpoint_path.name}")
                checkpoint_path.unlink()


# Convenience function for direct usage
def create_project_snapshot(
    session_summary: str,
    modified_files: Optional[List[str]] = None,
    modified_loc: int = 0,
    rationale: str = "Feature implementation",
    next_steps: Optional[List[str]] = None,
    open_risks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to create snapshot.

    Usage:
        result = create_project_snapshot(
            session_summary="Implemented JWT authentication",
            modified_files=["core/auth.py", "tests/test_auth.py"],
            modified_loc=180,
            rationale="Replace basic auth with secure JWT tokens",
            next_steps=["Add refresh token support", "Test edge cases"],
            open_risks=["Token expiry handling needs review"]
        )
    """
    agent = HistorianAgent()
    return agent.create_snapshot({
        'session_summary': session_summary,
        'modified_files': modified_files,
        'modified_loc': modified_loc,
        'rationale': rationale,
        'next_steps': next_steps or [],
        'open_risks': open_risks or []
    })
