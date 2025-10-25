"""
Workflow State - Persistent state management for gated workflow.

Handles auto-save, resume capability, and integration with ProjectContext.

PHASE 3 ENHANCEMENTS:
- Checkpoint integration for crash recovery
- Auto-checkpoint after each step completion
- Resume from checkpoint capability
- Version tracking for state format changes
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from core.project_context import ProjectContext


class WorkflowState:
    """
    Manages workflow state with auto-save and resume capability.

    Stores:
    - Current step
    - Completed steps
    - Collected requirements (all field data)
    - Step completion scores
    - Timestamps
    """

    def __init__(
        self,
        project_id: str,
        session_id: str,
        auto_save: bool = True,
        enable_checkpoints: bool = True,
        project_name: str = None
    ):
        """
        Initialize workflow state.

        Args:
            project_id: Project ID
            session_id: Current session ID
            auto_save: Enable auto-save after each field (default: True)
            enable_checkpoints: Enable checkpoint creation (default: True)
            project_name: Optional human-readable project name

        PHASE 3: Added checkpoint support for crash recovery
        """
        self.project_id = project_id
        self.session_id = session_id
        self.auto_save = auto_save
        self.enable_checkpoints = enable_checkpoints
        self.project_name = project_name
        self.context = ProjectContext()

        # State data
        self.current_step = None
        self.completed_steps = []
        self.collected_data = {}
        self.step_scores = {}
        self.started_at = None
        self.updated_at = None

        # Checkpoint manager (lazy-loaded to avoid circular imports)
        self._checkpoint_manager = None

        # Load existing state if available
        self._load_state()

    def _load_state(self):
        """Load existing workflow state from project context."""
        try:
            # Try to load workflow state from context metadata
            project_data = self.context.get_project_summary(self.project_id)
            if project_data and 'workflow_state' in project_data.get('metadata', {}):
                state = project_data['metadata']['workflow_state']
                self.current_step = state.get('current_step')
                self.completed_steps = state.get('completed_steps', [])
                self.collected_data = state.get('collected_data', {})
                self.step_scores = state.get('step_scores', {})
                self.started_at = state.get('started_at')
                self.updated_at = state.get('updated_at')
        except Exception:
            # Fresh start if no existing state
            pass

    def save_field(self, field_name: str, value: str, step: str = None):
        """
        Save a single field value.

        Args:
            field_name: Name of the field
            value: Field value
            step: Current step (optional, uses self.current_step if not provided)
        """
        step = step or self.current_step

        # Update collected data
        self.collected_data[field_name] = value
        self.updated_at = datetime.now().isoformat()

        # Auto-save if enabled
        if self.auto_save:
            self._persist()
            print("💾 Auto-saved")

    def save_requirements(self, requirements: Dict[str, Any], step: str = None):
        """
        Save multiple requirements at once (expert mode).

        Args:
            requirements: Dictionary of field_name: value
            step: Current step
        """
        step = step or self.current_step

        # Update collected data
        self.collected_data.update(requirements)
        self.updated_at = datetime.now().isoformat()

        # Auto-save if enabled
        if self.auto_save:
            self._persist()
            print("💾 Auto-saved all requirements")

    def start_step(self, step_name: str):
        """
        Mark a step as started (current).

        Args:
            step_name: Step to start
        """
        self.current_step = step_name

        if not self.started_at:
            self.started_at = datetime.now().isoformat()

        self.updated_at = datetime.now().isoformat()
        self._persist()

    def complete_step(self, step_name: str, score: float, summary: str = None):
        """
        Mark a step as completed.

        Args:
            step_name: Step that was completed
            score: Completion score (0.0-1.0)
            summary: Optional summary of what was collected

        PHASE 3: Auto-creates checkpoint after step completion
        """
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)

        self.step_scores[step_name] = {
            'score': score,
            'completed_at': datetime.now().isoformat(),
            'summary': summary
        }

        self.updated_at = datetime.now().isoformat()
        self._persist()

        # Also record milestone in project context
        try:
            self.context.record_milestone(
                project_id=self.project_id,
                session_id=self.session_id,
                milestone_name=f"Completed {step_name}",
                description=summary or f"Finished {step_name} with {score*100:.0f}% confidence",
                metadata={'score': score, 'step': step_name}
            )
        except Exception as e:
            print(f"⚠️ Could not record milestone: {e}")

        # PHASE 3: Auto-checkpoint after step completion
        if self.enable_checkpoints:
            self.create_checkpoint(
                checkpoint_type="step_complete",
                metadata={'step': step_name, 'score': score}
            )

    def is_step_completed(self, step_name: str) -> bool:
        """Check if a step is completed."""
        return step_name in self.completed_steps

    def get_step_score(self, step_name: str) -> Optional[float]:
        """Get completion score for a step."""
        return self.step_scores.get(step_name, {}).get('score')

    def get_collected_data(self) -> Dict[str, Any]:
        """Get all collected data."""
        return self.collected_data.copy()

    def get_field_value(self, field_name: str, default: Any = None) -> Any:
        """Get value of a specific field."""
        return self.collected_data.get(field_name, default)

    def _persist(self):
        """Persist state to project context metadata."""
        try:
            state_data = {
                'current_step': self.current_step,
                'completed_steps': self.completed_steps,
                'collected_data': self.collected_data,
                'step_scores': self.step_scores,
                'started_at': self.started_at,
                'updated_at': self.updated_at
            }

            # Store in project context metadata
            self.context.update_metadata(
                project_id=self.project_id,
                session_id=self.session_id,
                metadata={'workflow_state': state_data}
            )

        except Exception as e:
            print(f"⚠️ Auto-save failed: {e}")

    def export_summary(self) -> Dict[str, Any]:
        """
        Export workflow summary for display.

        Returns:
            {
                'started': timestamp,
                'updated': timestamp,
                'current_step': step_name,
                'completed_steps': [...],
                'progress': {
                    'total_steps': 4,
                    'completed': 2,
                    'percent': 50.0
                },
                'data': {...}
            }
        """
        from core.workflow_gates import get_step_order

        total_steps = len(get_step_order())
        completed_count = len(self.completed_steps)

        return {
            'started': self.started_at,
            'updated': self.updated_at,
            'current_step': self.current_step,
            'completed_steps': self.completed_steps,
            'progress': {
                'total_steps': total_steps,
                'completed': completed_count,
                'percent': (completed_count / total_steps * 100) if total_steps > 0 else 0
            },
            'step_scores': self.step_scores,
            'data': self.collected_data
        }

    def reset(self):
        """Reset workflow state (start fresh)."""
        self.current_step = None
        self.completed_steps = []
        self.collected_data = {}
        self.step_scores = {}
        self.started_at = None
        self.updated_at = None
        self._persist()

    # ==================================================
    # PHASE 3: Checkpoint Integration Methods
    # ==================================================

    @property
    def checkpoint_manager(self):
        """Lazy-load checkpoint manager to avoid circular imports."""
        if self._checkpoint_manager is None and self.enable_checkpoints:
            from core.checkpoint_manager import CheckpointManager
            self._checkpoint_manager = CheckpointManager(self.project_id)
        return self._checkpoint_manager

    def create_checkpoint(
        self,
        checkpoint_type: str = "manual",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a checkpoint of current state.

        Args:
            checkpoint_type: Type of checkpoint ("manual", "auto", "step_complete")
            metadata: Additional metadata to store

        Returns:
            Checkpoint ID, or None if checkpoints disabled

        WHY: Enables manual checkpointing and auto-checkpoint after steps

        USAGE:
            # Manual checkpoint
            state.create_checkpoint(checkpoint_type="manual")

            # Auto-checkpoint (called by complete_step)
            state.create_checkpoint(checkpoint_type="step_complete", metadata={'step': 'Market Sizing'})
        """
        if not self.enable_checkpoints or not self.checkpoint_manager:
            return None

        try:
            checkpoint_id = self.checkpoint_manager.save_checkpoint(
                workflow_state=self,
                checkpoint_type=checkpoint_type,
                metadata=metadata
            )

            # Enhanced checkpoint display
            if checkpoint_id:
                # Calculate progress
                from core.workflow_gates import get_step_order
                total_steps = len(get_step_order())
                completed_count = len(self.completed_steps)
                progress_pct = int((completed_count / total_steps * 100)) if total_steps > 0 else 0

                # Format checkpoint message
                project_display = f'"{self.project_name}"' if self.project_name else self.project_id
                step_display = metadata.get('step', self.current_step) if metadata else self.current_step

                print(f"💾 Checkpoint saved: {project_display}")
                print(f"   Progress: {progress_pct}% ({completed_count}/{total_steps} steps)")
                if step_display:
                    print(f"   Current step: {step_display}")

            return checkpoint_id
        except Exception as e:
            print(f"⚠️ Checkpoint creation failed: {e}")
            return None

    @classmethod
    def from_checkpoint(
        cls,
        project_id: str,
        checkpoint_id: Optional[str] = None
    ) -> Optional['WorkflowState']:
        """
        Create WorkflowState by resuming from a checkpoint.

        Args:
            project_id: Project ID
            checkpoint_id: Specific checkpoint to resume from (None = latest)

        Returns:
            Restored WorkflowState, or None if resume failed

        WHY: Primary recovery method for crash scenarios

        USAGE:
            # Resume from latest checkpoint
            state = WorkflowState.from_checkpoint("proj_123")

            # Resume from specific checkpoint
            state = WorkflowState.from_checkpoint("proj_123", "ckpt_abc")
        """
        from core.checkpoint_manager import CheckpointManager

        manager = CheckpointManager(project_id)
        return manager.resume_workflow(checkpoint_id)

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints for this project.

        Returns:
            List of checkpoint summaries

        WHY: Users need to see available recovery points
        """
        if not self.checkpoint_manager:
            return []

        return self.checkpoint_manager.list_checkpoints()

    def detect_crash(self) -> Optional[Dict[str, Any]]:
        """
        Detect if there's an incomplete/crashed session.

        Returns:
            Crash info if detected, None otherwise

        WHY: Auto-detect crashes on startup to offer recovery
        """
        if not self.checkpoint_manager:
            return None

        return self.checkpoint_manager.detect_incomplete_session()

    def __repr__(self):
        return f"<WorkflowState project={self.project_id} step={self.current_step} completed={len(self.completed_steps)}>"
