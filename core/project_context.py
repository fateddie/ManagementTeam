"""
Project Context Manager

High-level API for project management operations including:
- Creating and managing projects
- Tracking milestones and deadlines
- Managing action points/tasks
- Recording decision rationale
- Logging activity timeline
- Adding notes (issues, successes, ideas)
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass

from core.project_context_db import initialize_schema, verify_schema

logger = logging.getLogger(__name__)


@dataclass
class DeadlineStatus:
    """Status of project deadline."""
    project_id: str
    target_date: Optional[date]
    days_remaining: Optional[int]
    is_overdue: bool
    status: str  # 'on_track', 'at_risk', 'overdue', 'no_deadline'
    progress_percent: int


class ProjectContext:
    """
    Manages project context and memory.

    Provides high-level API for tracking project status, decisions,
    tasks, and timeline. Integrates with existing infrastructure.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize project context manager.

        Args:
            db_path: Optional path to SQLite database.
                     If None, uses config.env_manager to find it.

        Raises:
            ConnectionError: If database cannot be accessed
        """
        if db_path is None:
            try:
                # Use Path(__file__) to find the project root
                project_root = Path(__file__).parent.parent
                self.db_path = project_root / "data" / "test_ideas.db"
            except Exception as e:
                logger.error(f"Failed to locate database: {e}")
                raise ConnectionError(f"Cannot locate database: {e}")
        else:
            self.db_path = db_path

        # Initialize schema if needed
        if not self.db_path.exists():
            logger.warning(f"Database does not exist at {self.db_path}")
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            initialize_schema(self.db_path)
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise

        logger.info(f"✅ ProjectContext initialized with {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ============================================================================
    # Project Operations
    # ============================================================================

    def create_project(
        self,
        name: str,
        description: str = "",
        deadline: Optional[datetime] = None,
        priority: str = "medium",
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create a new project.

        Args:
            name: Project name
            description: Project description
            deadline: Target completion date
            priority: Priority level (low, medium, high, urgent)
            tags: Optional list of tags

        Returns:
            Project ID if successful, None otherwise
        """
        try:
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            tags_str = json.dumps(tags) if tags else None

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO projects (id, name, description, status, priority, start_date, target_date, tags)
                VALUES (?, ?, ?, 'planning', ?, DATE('now'), ?, ?)
            """, (project_id, name, description, priority, deadline, tags_str))

            # Log creation in timeline
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type)
                VALUES (?, ?, 'status_change')
            """, (project_id, f"Project created: {name}"))

            conn.commit()
            conn.close()

            logger.info(f"✅ Created project: {project_id} - {name}")
            return project_id

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            return None

    def update_project_status(
        self,
        project_id: str,
        status: str,
        progress_percent: Optional[int] = None
    ) -> bool:
        """
        Update project status.

        Args:
            project_id: Project ID
            status: New status (planning, active, paused, completed, cancelled)
            progress_percent: Optional progress percentage

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            params = [status]

            if progress_percent is not None:
                updates.append("progress_percent = ?")
                params.append(progress_percent)

            if status == 'completed':
                updates.append("completed_date = DATE('now')")

            params.append(project_id)

            cursor.execute(f"""
                UPDATE projects
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)

            # Log status change
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type)
                VALUES (?, ?, 'status_change')
            """, (project_id, f"Status changed to: {status}"))

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated project {project_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update project status: {e}")
            return False

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project details.

        Args:
            project_id: Project ID

        Returns:
            Project dictionary or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            return None

    def list_projects(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all projects, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of project dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if status:
                cursor.execute("SELECT * FROM projects WHERE status = ? ORDER BY created_at DESC", (status,))
            else:
                cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    # ============================================================================
    # Milestone Operations
    # ============================================================================

    def add_milestone(
        self,
        project_id: str,
        name: str,
        target_date: Optional[date] = None,
        order: int = 0,
        description: str = ""
    ) -> Optional[int]:
        """
        Add a milestone to a project.

        Args:
            project_id: Project ID
            name: Milestone name
            target_date: Target completion date
            order: Display order
            description: Milestone description

        Returns:
            Milestone ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO milestones (project_id, name, description, target_date, order_index)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, name, description, target_date, order))

            milestone_id = cursor.lastrowid

            # Log in timeline
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type, milestone_id)
                VALUES (?, ?, 'status_change', ?)
            """, (project_id, f"Milestone added: {name}", milestone_id))

            conn.commit()
            conn.close()

            logger.info(f"✅ Added milestone {milestone_id} to project {project_id}")
            return milestone_id

        except Exception as e:
            logger.error(f"Failed to add milestone: {e}")
            return None

    def complete_milestone(self, milestone_id: int) -> bool:
        """Mark milestone as completed."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE milestones
                SET status = 'completed', completed_date = DATE('now')
                WHERE id = ?
            """, (milestone_id,))

            # Get project_id and name for timeline
            cursor.execute("SELECT project_id, name FROM milestones WHERE id = ?", (milestone_id,))
            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    INSERT INTO timeline (project_id, activity, activity_type, milestone_id)
                    VALUES (?, ?, 'milestone_completed', ?)
                """, (row['project_id'], f"Milestone completed: {row['name']}", milestone_id))

            conn.commit()
            conn.close()

            logger.info(f"✅ Completed milestone {milestone_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to complete milestone: {e}")
            return False

    def get_milestones(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all milestones for a project."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM milestones
                WHERE project_id = ?
                ORDER BY order_index, target_date
            """, (project_id,))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get milestones: {e}")
            return []

    def record_milestone(
        self,
        project_id: str,
        session_id: str,
        milestone_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a milestone completion.

        WHY: Fixes missing method error - was being called by workflow
        state but didn't exist. Wrapper around add_milestone.

        Args:
            project_id: Project ID
            session_id: Session ID (for context)
            milestone_name: Name of milestone
            metadata: Optional metadata about the milestone

        Returns:
            True if successful, False otherwise
        """
        try:
            description = f"Session: {session_id}"
            if metadata:
                description += f" | {json.dumps(metadata)}"

            milestone_id = self.add_milestone(
                project_id=project_id,
                name=milestone_name,
                description=description
            )

            return milestone_id is not None

        except Exception as e:
            logger.error(f"Failed to record milestone: {e}")
            return False

    # ============================================================================
    # Action Point Operations
    # ============================================================================

    def add_action_point(
        self,
        project_id: str,
        title: str,
        priority: str = "medium",
        due_date: Optional[date] = None,
        description: str = "",
        milestone_id: Optional[int] = None,
        agent_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Add an action point/task.

        Args:
            project_id: Project ID
            title: Action title
            priority: Priority level (low, medium, high, urgent)
            due_date: Due date
            description: Action description
            milestone_id: Optional associated milestone
            agent_name: Optional agent that created this action

        Returns:
            Action ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO action_points
                (project_id, milestone_id, title, description, priority, due_date, agent_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, milestone_id, title, description, priority, due_date, agent_name))

            action_id = cursor.lastrowid

            # Log in timeline
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type, action_id)
                VALUES (?, ?, 'note', ?)
            """, (project_id, f"Action added: {title}", action_id))

            conn.commit()
            conn.close()

            logger.info(f"✅ Added action point {action_id} to project {project_id}")
            return action_id

        except Exception as e:
            logger.error(f"Failed to add action point: {e}")
            return None

    def update_action_status(
        self,
        action_id: int,
        status: str,
        actual_hours: Optional[float] = None
    ) -> bool:
        """Update action point status."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            updates = ["status = ?"]
            params = [status]

            if status == 'done':
                updates.append("completed_date = DATE('now')")

            if actual_hours is not None:
                updates.append("actual_hours = ?")
                params.append(actual_hours)

            params.append(action_id)

            cursor.execute(f"""
                UPDATE action_points
                SET {', '.join(updates)}
                WHERE id = ?
            """, params)

            # Log in timeline
            cursor.execute("SELECT project_id, title FROM action_points WHERE id = ?", (action_id,))
            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    INSERT INTO timeline (project_id, activity, activity_type, action_id)
                    VALUES (?, ?, 'action_completed', ?)
                """, (row['project_id'], f"Action {status}: {row['title']}", action_id))

            conn.commit()
            conn.close()

            logger.info(f"✅ Updated action {action_id} to {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update action status: {e}")
            return False

    def get_action_points(
        self,
        project_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get action points for a project, optionally filtered."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM action_points WHERE project_id = ?"
            params = [project_id]

            if status:
                query += " AND status = ?"
                params.append(status)

            if priority:
                query += " AND priority = ?"
                params.append(priority)

            query += " ORDER BY priority DESC, due_date"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get action points: {e}")
            return []

    # ============================================================================
    # Decision Operations
    # ============================================================================

    def record_decision(
        self,
        project_id: str,
        decision: str,
        rationale: str,
        alternatives: Optional[List[str]] = None,
        agent_name: Optional[str] = None,
        confidence: Optional[float] = None,
        context: str = ""
    ) -> bool:
        """
        Record a decision with rationale.

        Args:
            project_id: Project ID
            decision: The decision made
            rationale: Why this decision was made
            alternatives: Other options considered
            agent_name: Agent that made the decision
            confidence: Confidence score (0-1)
            context: Additional context

        Returns:
            True if successful, False otherwise
        """
        try:
            alternatives_str = json.dumps(alternatives) if alternatives else None

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO decisions
                (project_id, decision, rationale, alternatives, context, agent_name, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, decision, rationale, alternatives_str, context, agent_name, confidence))

            decision_id = cursor.lastrowid

            # Log in timeline
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type, decision_id, agent_name)
                VALUES (?, ?, 'decision', ?, ?)
            """, (project_id, f"Decision: {decision}", decision_id, agent_name))

            conn.commit()
            conn.close()

            logger.info(f"✅ Recorded decision for project {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to record decision: {e}")
            return False

    def get_decisions(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all decisions for a project."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM decisions
                WHERE project_id = ?
                ORDER BY created_at DESC
            """, (project_id,))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get decisions: {e}")
            return []

    # ============================================================================
    # Timeline Operations
    # ============================================================================

    def log_activity(
        self,
        project_id: str,
        activity: str,
        agent_name: Optional[str] = None,
        activity_type: str = "agent_run",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an activity to the timeline.

        Args:
            project_id: Project ID
            activity: Activity description
            agent_name: Agent that performed activity
            activity_type: Type of activity
            metadata: Optional metadata dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata_str = json.dumps(metadata) if metadata else None

            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type, agent_name, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, activity, activity_type, agent_name, metadata_str))

            conn.commit()
            conn.close()

            logger.debug(f"Logged activity for project {project_id}: {activity}")
            return True

        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return False

    def get_recent_activity(
        self,
        project_id: str,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent activity for a project.

        Args:
            project_id: Project ID
            days: Number of days to look back
            limit: Maximum number of activities to return

        Returns:
            List of activity dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM timeline
                WHERE project_id = ?
                AND created_at >= datetime('now', ? || ' days')
                ORDER BY created_at DESC
                LIMIT ?
            """, (project_id, -days, limit))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []

    # ============================================================================
    # Notes Operations
    # ============================================================================

    def add_note(
        self,
        project_id: str,
        note_type: str,
        title: str,
        content: str,
        action_id: Optional[int] = None,
        milestone_id: Optional[int] = None
    ) -> bool:
        """
        Add a note (issue, success, idea, learning).

        Args:
            project_id: Project ID
            note_type: Type (issue, success, idea, learning, general)
            title: Note title
            content: Note content
            action_id: Optional related action
            milestone_id: Optional related milestone

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO notes (project_id, note_type, title, content, action_id, milestone_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, note_type, title, content, action_id, milestone_id))

            note_id = cursor.lastrowid

            # Log in timeline
            cursor.execute("""
                INSERT INTO timeline (project_id, activity, activity_type)
                VALUES (?, ?, 'note')
            """, (project_id, f"{note_type.capitalize()}: {title}"))

            conn.commit()
            conn.close()

            logger.info(f"✅ Added {note_type} note to project {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add note: {e}")
            return False

    def get_notes(
        self,
        project_id: str,
        note_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get notes for a project, optionally filtered."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = "SELECT * FROM notes WHERE project_id = ?"
            params = [project_id]

            if note_type:
                query += " AND note_type = ?"
                params.append(note_type)

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return []

    # ============================================================================
    # Summary & Analysis Operations
    # ============================================================================

    def check_deadline_status(self, project_id: str) -> DeadlineStatus:
        """
        Check if project is on track for deadline.

        Args:
            project_id: Project ID

        Returns:
            DeadlineStatus object with analysis
        """
        project = self.get_project(project_id)

        if not project:
            return DeadlineStatus(
                project_id=project_id,
                target_date=None,
                days_remaining=None,
                is_overdue=False,
                status='no_deadline',
                progress_percent=0
            )

        target_date_str = project.get('target_date')
        if not target_date_str:
            return DeadlineStatus(
                project_id=project_id,
                target_date=None,
                days_remaining=None,
                is_overdue=False,
                status='no_deadline',
                progress_percent=project.get('progress_percent', 0)
            )

        # Parse date - handle both date-only and datetime formats
        try:
            if ' ' in target_date_str:
                # Full datetime format
                target_date = datetime.strptime(target_date_str.split()[0], '%Y-%m-%d').date()
            else:
                # Date-only format
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except Exception:
            # Fallback: try ISO format
            target_date = datetime.fromisoformat(target_date_str).date()

        today = date.today()
        days_remaining = (target_date - today).days
        progress = project.get('progress_percent', 0)

        # Determine status
        if days_remaining < 0:
            status = 'overdue'
            is_overdue = True
        elif days_remaining <= 3:
            status = 'at_risk' if progress < 80 else 'on_track'
            is_overdue = False
        elif days_remaining <= 7:
            status = 'at_risk' if progress < 50 else 'on_track'
            is_overdue = False
        else:
            status = 'on_track'
            is_overdue = False

        return DeadlineStatus(
            project_id=project_id,
            target_date=target_date,
            days_remaining=days_remaining,
            is_overdue=is_overdue,
            status=status,
            progress_percent=progress
        )

    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        """
        Get comprehensive project summary.

        Args:
            project_id: Project ID

        Returns:
            Dictionary with project summary including:
            - Project details
            - Milestone count and status
            - Action point counts by status
            - Recent activity
            - Deadline status
            - Open issues count
        """
        project = self.get_project(project_id)
        if not project:
            return {}

        milestones = self.get_milestones(project_id)
        actions = self.get_action_points(project_id)
        decisions = self.get_decisions(project_id)
        notes = self.get_notes(project_id)
        recent_activity = self.get_recent_activity(project_id, days=7)
        deadline_status = self.check_deadline_status(project_id)

        # Count actions by status
        action_counts = {
            'todo': sum(1 for a in actions if a['status'] == 'todo'),
            'in_progress': sum(1 for a in actions if a['status'] == 'in_progress'),
            'done': sum(1 for a in actions if a['status'] == 'done'),
            'blocked': sum(1 for a in actions if a['status'] == 'blocked')
        }

        # Count milestones by status
        milestone_counts = {
            'pending': sum(1 for m in milestones if m['status'] == 'pending'),
            'in_progress': sum(1 for m in milestones if m['status'] == 'in_progress'),
            'completed': sum(1 for m in milestones if m['status'] == 'completed'),
            'blocked': sum(1 for m in milestones if m['status'] == 'blocked')
        }

        # Count notes by type
        note_counts = {
            'issue': sum(1 for n in notes if n['note_type'] == 'issue' and n['status'] == 'open'),
            'success': sum(1 for n in notes if n['note_type'] == 'success'),
            'idea': sum(1 for n in notes if n['note_type'] == 'idea'),
            'learning': sum(1 for n in notes if n['note_type'] == 'learning')
        }

        return {
            'project': project,
            'milestones': {
                'total': len(milestones),
                'counts': milestone_counts,
                'items': milestones
            },
            'actions': {
                'total': len(actions),
                'counts': action_counts,
                'items': actions[:10]  # Last 10 actions
            },
            'decisions': {
                'total': len(decisions),
                'items': decisions[:5]  # Last 5 decisions
            },
            'notes': {
                'total': len(notes),
                'counts': note_counts,
                'items': notes[:10]  # Last 10 notes
            },
            'recent_activity': recent_activity,
            'deadline_status': {
                'target_date': str(deadline_status.target_date) if deadline_status.target_date else None,
                'days_remaining': deadline_status.days_remaining,
                'is_overdue': deadline_status.is_overdue,
                'status': deadline_status.status,
                'progress_percent': deadline_status.progress_percent
            }
        }

    # ============================================================================
    # Sub-Agent Operations
    # WHY: Centralized storage for sub-agent artifacts replaces file-based
    # .history/ approach. Enables dashboard querying and metrics tracking.
    # ============================================================================

    def record_subagent_artifact(
        self,
        project_id: str,
        session_id: str,
        subagent_name: str,
        artifact_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store sub-agent execution artifact.

        WHY: Replaces file-based .history/ storage with queryable database.
        Enables dashboard viewing, metrics tracking, and cross-session analysis.

        Args:
            project_id: Project ID
            session_id: Session ID
            subagent_name: Name of sub-agent (ExplorerAgent, etc.)
            artifact_type: Type of artifact ('exploration', 'research', 'checkpoint', etc.)
            data: Artifact data (output from sub-agent)
            metadata: Optional metadata (execution_mode, metrics, etc.)

        Returns:
            True if stored successfully
        """
        try:
            # Store as a special type of note with subagent metadata
            artifact_data = {
                'subagent_name': subagent_name,
                'artifact_type': artifact_type,
                'data': data,
                'metadata': metadata or {}
            }

            return self.record_note(
                project_id=project_id,
                session_id=session_id,
                note_type='subagent_artifact',
                title=f"{subagent_name}: {artifact_type}",
                content=json.dumps(artifact_data, indent=2)
            )

        except Exception as e:
            logger.error(f"Failed to record sub-agent artifact: {e}")
            return False

    def get_subagent_artifacts(
        self,
        project_id: str,
        subagent_name: Optional[str] = None,
        artifact_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get sub-agent artifacts for a project.

        Args:
            project_id: Project ID
            subagent_name: Filter by sub-agent name (optional)
            artifact_type: Filter by artifact type (optional)

        Returns:
            List of artifact dictionaries
        """
        try:
            # Get all subagent_artifact notes
            notes = self.get_notes(
                project_id=project_id,
                note_type='subagent_artifact'
            )

            artifacts = []
            for note in notes:
                try:
                    artifact_data = json.loads(note['content'])

                    # Apply filters
                    if subagent_name and artifact_data.get('subagent_name') != subagent_name:
                        continue
                    if artifact_type and artifact_data.get('artifact_type') != artifact_type:
                        continue

                    artifacts.append({
                        'id': note['id'],
                        'created_at': note['created_at'],
                        **artifact_data
                    })

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse artifact {note['id']}")
                    continue

            return artifacts

        except Exception as e:
            logger.error(f"Failed to get sub-agent artifacts: {e}")
            return []

    def get_subagent_metrics(self, project_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for all sub-agents.

        Returns:
            Dictionary of sub-agent names to their metrics
        """
        try:
            # Metrics stored in project metadata with prefix 'subagent_metrics_'
            project_data = self.get_project(project_id)
            if not project_data:
                return {}

            metadata = project_data.get('metadata', {})
            metrics = {}

            for key, value in metadata.items():
                if key.startswith('subagent_metrics_'):
                    agent_name = key.replace('subagent_metrics_', '')
                    metrics[agent_name] = value

            return metrics

        except Exception as e:
            logger.error(f"Failed to get sub-agent metrics: {e}")
            return {}

    def update_metadata(
        self,
        project_id: str,
        session_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update project metadata.

        WHY: Fixes missing method error - was being called by sub-agent
        coordinator but didn't exist.

        Args:
            project_id: Project ID
            session_id: Session ID (for context, currently unused)
            metadata: Dictionary of metadata key-value pairs to update

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Get existing metadata
            cursor.execute("SELECT metadata FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"Project {project_id} not found")
                conn.close()
                return False

            # Parse existing metadata
            existing_metadata = json.loads(row['metadata']) if row['metadata'] else {}

            # Update with new metadata
            existing_metadata.update(metadata)

            # Save back to database
            cursor.execute("""
                UPDATE projects
                SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(existing_metadata), project_id))

            conn.commit()
            conn.close()

            logger.debug(f"✅ Updated metadata for project {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")
            return False
