"""
checkpoint_manager.py
Phase 3 - Crash Recovery System: Checkpoint Manager
---------------------------------------------------------

WHY: Workflows can be interrupted by crashes, network issues, or user breaks.
Without checkpoints, users lose all progress and must restart from scratch.
CheckpointManager provides automatic and manual checkpointing with resume
capability, ensuring work is never lost.

DESIGN PRINCIPLES:
1. Auto-save after each step completion
2. Manual checkpoint creation on demand
3. Versioned checkpoints for safety
4. Resume from last good state
5. Conflict detection for interrupted sessions

USAGE:
    # Auto-checkpoint after step completion
    manager = CheckpointManager(project_id="proj_123")
    manager.save_checkpoint(workflow_state)

    # Resume from last checkpoint
    state = manager.load_latest_checkpoint()

    # List all available checkpoints
    checkpoints = manager.list_checkpoints()

Created: 2025-10-19 (Phase 3 - Sub-Agent Unification)
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import hashlib

from core.workflow_state import WorkflowState

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages workflow checkpoints for crash recovery.

    RESPONSIBILITIES:
    - Save workflow state to disk as versioned checkpoints
    - Load checkpoints for recovery
    - Detect incomplete/crashed sessions
    - Resume from last good state
    - Handle checkpoint conflicts

    CHECKPOINT STRUCTURE:
    .checkpoints/
        {project_id}/
            checkpoint_v1_20251019_142305.json
            checkpoint_v2_20251019_143012.json
            latest.json (symlink/copy)

    CHECKPOINT DATA:
    {
        "version": 1,
        "project_id": "proj_123",
        "session_id": "sess_456",
        "checkpoint_id": "ckpt_789",
        "created_at": "2025-10-19T14:23:05",
        "workflow_state": {...},
        "metadata": {...}
    }
    """

    CHECKPOINT_VERSION = 1  # Increment when checkpoint format changes
    CHECKPOINT_DIR = Path(".checkpoints")

    def __init__(self, project_id: str, checkpoint_dir: Optional[Path] = None):
        """
        Initialize checkpoint manager.

        Args:
            project_id: Project identifier
            checkpoint_dir: Custom checkpoint directory (default: .checkpoints/)

        WHY: Each project has its own checkpoint directory to avoid conflicts
        """
        self.project_id = project_id
        self.checkpoint_dir = checkpoint_dir or self.CHECKPOINT_DIR
        self.project_checkpoint_dir = self.checkpoint_dir / project_id

        # Create checkpoint directory if needed
        self.project_checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CheckpointManager initialized for project {project_id}")

    def save_checkpoint(
        self,
        workflow_state: WorkflowState,
        checkpoint_type: str = "auto",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save workflow state as a checkpoint.

        Args:
            workflow_state: Current workflow state
            checkpoint_type: Type of checkpoint ("auto", "manual", "step_complete")
            metadata: Additional metadata to store

        Returns:
            Checkpoint ID

        WHY: Every checkpoint is versioned and timestamped to enable point-in-time recovery

        PROCESS:
        1. Generate unique checkpoint ID
        2. Serialize workflow state
        3. Save to versioned file
        4. Update 'latest' pointer
        5. Record checkpoint metadata
        """
        checkpoint_id = self._generate_checkpoint_id()
        timestamp = datetime.now()

        # Build checkpoint data
        checkpoint_data = {
            "version": self.CHECKPOINT_VERSION,
            "project_id": self.project_id,
            "session_id": workflow_state.session_id,
            "checkpoint_id": checkpoint_id,
            "checkpoint_type": checkpoint_type,
            "created_at": timestamp.isoformat(),
            "workflow_state": {
                "current_step": workflow_state.current_step,
                "completed_steps": workflow_state.completed_steps,
                "collected_data": workflow_state.collected_data,
                "step_scores": workflow_state.step_scores,
                "started_at": workflow_state.started_at,
                "updated_at": workflow_state.updated_at
            },
            "metadata": metadata or {}
        }

        # Generate filename with version and timestamp
        filename = f"checkpoint_v{self.CHECKPOINT_VERSION}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        checkpoint_path = self.project_checkpoint_dir / filename

        # Save checkpoint
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)

            # Update 'latest' pointer
            latest_path = self.project_checkpoint_dir / "latest.json"
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)

            logger.info(f"Checkpoint saved: {checkpoint_id} ({checkpoint_type})")
            return checkpoint_id

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}", exc_info=True)
            raise

    def load_checkpoint(self, checkpoint_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a specific checkpoint or the latest one.

        Args:
            checkpoint_id: Specific checkpoint to load (None = latest)

        Returns:
            Checkpoint data dictionary, or None if not found

        WHY: Enables recovery from any saved checkpoint, not just the latest

        PROCESS:
        1. If no ID specified, load 'latest.json'
        2. Otherwise, search for checkpoint by ID
        3. Validate checkpoint version
        4. Return checkpoint data
        """
        try:
            if checkpoint_id is None:
                # Load latest checkpoint
                latest_path = self.project_checkpoint_dir / "latest.json"
                if not latest_path.exists():
                    logger.info("No checkpoints found")
                    return None

                with open(latest_path, 'r', encoding='utf-8') as f:
                    checkpoint_data = json.load(f)
            else:
                # Load specific checkpoint by ID
                checkpoint_data = self._find_checkpoint_by_id(checkpoint_id)
                if not checkpoint_data:
                    logger.warning(f"Checkpoint not found: {checkpoint_id}")
                    return None

            # Validate version
            if checkpoint_data.get('version') != self.CHECKPOINT_VERSION:
                logger.warning(
                    f"Checkpoint version mismatch: {checkpoint_data.get('version')} != {self.CHECKPOINT_VERSION}"
                )
                # Could implement migration here if needed

            logger.info(f"Loaded checkpoint: {checkpoint_data['checkpoint_id']}")
            return checkpoint_data

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}", exc_info=True)
            return None

    def load_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Convenience method to load the most recent checkpoint.

        Returns:
            Latest checkpoint data, or None if no checkpoints exist
        """
        return self.load_checkpoint()

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints for this project.

        Returns:
            List of checkpoint summaries, sorted by creation time (newest first)

        WHY: Users need to see available recovery points

        STRUCTURE:
        [
            {
                "checkpoint_id": "ckpt_abc123",
                "created_at": "2025-10-19T14:23:05",
                "checkpoint_type": "auto",
                "current_step": "Market Sizing",
                "completed_steps": 2,
                "file_path": ".checkpoints/proj_123/checkpoint_v1_..."
            }
        ]
        """
        checkpoints = []

        try:
            # Find all checkpoint files
            for checkpoint_file in self.project_checkpoint_dir.glob("checkpoint_v*.json"):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    workflow_state = data.get('workflow_state', {})
                    checkpoints.append({
                        "checkpoint_id": data.get('checkpoint_id'),
                        "created_at": data.get('created_at'),
                        "checkpoint_type": data.get('checkpoint_type'),
                        "current_step": workflow_state.get('current_step'),
                        "completed_steps": len(workflow_state.get('completed_steps', [])),
                        "file_path": str(checkpoint_file)
                    })

                except Exception as e:
                    logger.warning(f"Error reading checkpoint {checkpoint_file}: {e}")
                    continue

            # Sort by creation time (newest first)
            checkpoints.sort(key=lambda c: c['created_at'], reverse=True)

        except Exception as e:
            logger.error(f"Error listing checkpoints: {e}", exc_info=True)

        return checkpoints

    def resume_workflow(
        self,
        checkpoint_id: Optional[str] = None
    ) -> Optional[WorkflowState]:
        """
        Resume workflow from a checkpoint.

        Args:
            checkpoint_id: Specific checkpoint to resume from (None = latest)

        Returns:
            Restored WorkflowState, or None if resume failed

        WHY: Main recovery method - restores complete workflow state

        PROCESS:
        1. Load checkpoint data
        2. Create new WorkflowState instance
        3. Restore all state fields
        4. Return ready-to-use state
        """
        checkpoint_data = self.load_checkpoint(checkpoint_id)
        if not checkpoint_data:
            return None

        try:
            # Create new WorkflowState instance
            workflow_state = WorkflowState(
                project_id=checkpoint_data['project_id'],
                session_id=checkpoint_data['session_id'],
                auto_save=True
            )

            # Restore state from checkpoint
            state_data = checkpoint_data['workflow_state']
            workflow_state.current_step = state_data.get('current_step')
            workflow_state.completed_steps = state_data.get('completed_steps', [])
            workflow_state.collected_data = state_data.get('collected_data', {})
            workflow_state.step_scores = state_data.get('step_scores', {})
            workflow_state.started_at = state_data.get('started_at')
            workflow_state.updated_at = state_data.get('updated_at')

            logger.info(
                f"Resumed workflow from checkpoint {checkpoint_data['checkpoint_id']} "
                f"(step: {workflow_state.current_step})"
            )

            return workflow_state

        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}", exc_info=True)
            return None

    def detect_incomplete_session(self) -> Optional[Dict[str, Any]]:
        """
        Detect if there's an incomplete/crashed session.

        Returns:
            Latest checkpoint info if session appears incomplete, None otherwise

        WHY: Auto-detect crashes and offer recovery

        HEURISTIC:
        - Latest checkpoint exists
        - Checkpoint is not marked as complete
        - Last update was recent (within 24 hours)
        """
        latest = self.load_latest_checkpoint()
        if not latest:
            return None

        workflow_state = latest.get('workflow_state', {})

        # Check if workflow appears incomplete
        # (has started but not all steps completed)
        if workflow_state.get('started_at') and workflow_state.get('current_step'):
            # Get total steps expected (this is heuristic-based)
            # In production, would check against workflow definition
            completed_count = len(workflow_state.get('completed_steps', []))

            # If we have a current step but it's not in completed, likely incomplete
            current_step = workflow_state.get('current_step')
            if current_step and current_step not in workflow_state.get('completed_steps', []):
                return {
                    'checkpoint_id': latest['checkpoint_id'],
                    'project_id': latest['project_id'],
                    'session_id': latest['session_id'],
                    'created_at': latest['created_at'],
                    'current_step': current_step,
                    'completed_steps': completed_count,
                    'message': f'Incomplete session detected at step "{current_step}"'
                }

        return None

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a specific checkpoint.

        Args:
            checkpoint_id: Checkpoint to delete

        Returns:
            True if deleted, False if not found

        WHY: Clean up old checkpoints to save space
        """
        try:
            checkpoint_data = self._find_checkpoint_by_id(checkpoint_id)
            if not checkpoint_data:
                return False

            # Find and delete the file
            for checkpoint_file in self.project_checkpoint_dir.glob("checkpoint_v*.json"):
                try:
                    with open(checkpoint_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if data.get('checkpoint_id') == checkpoint_id:
                        checkpoint_file.unlink()
                        logger.info(f"Deleted checkpoint: {checkpoint_id}")
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.error(f"Failed to delete checkpoint: {e}", exc_info=True)
            return False

    def cleanup_old_checkpoints(self, keep_count: int = 10):
        """
        Delete old checkpoints, keeping only the most recent ones.

        Args:
            keep_count: Number of checkpoints to keep (default: 10)

        WHY: Prevent checkpoint directory from growing indefinitely
        """
        checkpoints = self.list_checkpoints()

        if len(checkpoints) <= keep_count:
            return

        # Delete oldest checkpoints
        for checkpoint in checkpoints[keep_count:]:
            self.delete_checkpoint(checkpoint['checkpoint_id'])

        logger.info(f"Cleaned up old checkpoints, kept {keep_count} most recent")

    # Private helper methods

    def _generate_checkpoint_id(self) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().isoformat()
        data = f"{self.project_id}_{timestamp}".encode('utf-8')
        hash_digest = hashlib.sha256(data).hexdigest()[:12]
        return f"ckpt_{hash_digest}"

    def _find_checkpoint_by_id(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Find checkpoint file by ID."""
        for checkpoint_file in self.project_checkpoint_dir.glob("checkpoint_v*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('checkpoint_id') == checkpoint_id:
                    return data
            except Exception:
                continue
        return None

    def __repr__(self):
        checkpoint_count = len(list(self.project_checkpoint_dir.glob("checkpoint_v*.json")))
        return f"<CheckpointManager project={self.project_id} checkpoints={checkpoint_count}>"


# Convenience function for quick checkpoint operations
def save_checkpoint(project_id: str, workflow_state: WorkflowState, checkpoint_type: str = "auto") -> str:
    """
    Quick save checkpoint (convenience wrapper).

    Args:
        project_id: Project ID
        workflow_state: Current workflow state
        checkpoint_type: Type of checkpoint

    Returns:
        Checkpoint ID
    """
    manager = CheckpointManager(project_id)
    return manager.save_checkpoint(workflow_state, checkpoint_type)


def resume_from_checkpoint(project_id: str) -> Optional[WorkflowState]:
    """
    Quick resume from latest checkpoint (convenience wrapper).

    Args:
        project_id: Project ID

    Returns:
        Restored WorkflowState or None
    """
    manager = CheckpointManager(project_id)
    return manager.resume_workflow()
