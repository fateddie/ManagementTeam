"""
Project Context Database Schema

Extends data/test_ideas.db with project management tables for tracking:
- Projects and their status
- Milestones and deadlines
- Action points and tasks
- Decision rationale
- Timeline of activities
- Notes (issues, successes, ideas)
"""

import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def initialize_schema(db_path: Path) -> bool:
    """
    Create project context tables in existing database.

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if successful, False if database unavailable

    Raises:
        ConnectionError: If database permissions are incorrect
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")

        # ============================================================================
        # Table 1: Projects - Master project list
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT CHECK(status IN ('planning', 'active', 'paused', 'completed', 'cancelled')) DEFAULT 'planning',
                priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                start_date DATE,
                target_date DATE,
                completed_date DATE,
                progress_percent INTEGER DEFAULT 0 CHECK(progress_percent BETWEEN 0 AND 100),
                tags TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ============================================================================
        # Table 2: Milestones - Major project phases
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'blocked')) DEFAULT 'pending',
                target_date DATE,
                completed_date DATE,
                order_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # ============================================================================
        # Table 3: Action Points - Tasks and TODOs
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                milestone_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT CHECK(status IN ('todo', 'in_progress', 'done', 'blocked', 'cancelled')) DEFAULT 'todo',
                priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                assigned_to TEXT DEFAULT 'Rob',
                due_date DATE,
                completed_date DATE,
                estimated_hours REAL,
                actual_hours REAL,
                agent_name TEXT,
                parent_action_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(milestone_id) REFERENCES milestones(id) ON DELETE SET NULL,
                FOREIGN KEY(parent_action_id) REFERENCES action_points(id) ON DELETE SET NULL
            )
        """)

        # ============================================================================
        # Table 4: Decisions - Why we chose X over Y
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                rationale TEXT NOT NULL,
                alternatives TEXT,
                outcome TEXT,
                context TEXT,
                agent_name TEXT,
                confidence REAL,
                reviewed_date DATE,
                would_choose_again BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # ============================================================================
        # Table 5: Timeline - Auto-generated activity log
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                activity_type TEXT CHECK(activity_type IN ('agent_run', 'milestone_completed', 'action_completed', 'status_change', 'note', 'decision')) DEFAULT 'note',
                agent_name TEXT,
                milestone_id INTEGER,
                action_id INTEGER,
                decision_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(milestone_id) REFERENCES milestones(id) ON DELETE SET NULL,
                FOREIGN KEY(action_id) REFERENCES action_points(id) ON DELETE SET NULL,
                FOREIGN KEY(decision_id) REFERENCES decisions(id) ON DELETE SET NULL
            )
        """)

        # ============================================================================
        # Table 6: Notes - Issues, successes, ideas, learnings
        # ============================================================================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL,
                note_type TEXT CHECK(note_type IN ('issue', 'success', 'idea', 'learning', 'general')) DEFAULT 'general',
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT CHECK(status IN ('open', 'in_progress', 'resolved', 'wont_fix')) DEFAULT 'open',
                action_id INTEGER,
                milestone_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY(action_id) REFERENCES action_points(id) ON DELETE SET NULL,
                FOREIGN KEY(milestone_id) REFERENCES milestones(id) ON DELETE SET NULL
            )
        """)

        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_milestones_project ON milestones(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_project ON action_points(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_actions_status ON action_points(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_project ON timeline(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeline_created ON timeline(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_project ON notes(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_type ON notes(note_type)")

        conn.commit()
        conn.close()

        logger.info(f"✅ Project context schema initialized at {db_path}")
        return True

    except PermissionError as e:
        logger.error(f"❌ No write permission for {db_path}: {e}")
        raise ConnectionError(
            f"Cannot write to database at {db_path}\n"
            f"Check file permissions or disk space"
        )
    except sqlite3.OperationalError as e:
        logger.error(f"⚠️ Database locked or unavailable: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to initialize schema: {e}")
        raise


def verify_schema(db_path: Path) -> bool:
    """
    Verify that all required tables exist.

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if all tables exist, False otherwise
    """
    required_tables = [
        'projects',
        'milestones',
        'action_points',
        'decisions',
        'timeline',
        'notes'
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}

        conn.close()

        missing = set(required_tables) - existing_tables
        if missing:
            logger.warning(f"⚠️ Missing tables: {missing}")
            return False

        logger.info(f"✅ Schema verified - all {len(required_tables)} tables present")
        return True

    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        return False


def migrate_add_metadata_column(db_path: Path) -> bool:
    """
    Add metadata column to projects table for existing databases.

    WHY: Stores workflow conversation data (collected_data) for long-term reference.
         Without this, detailed idea validation data only lives in checkpoints (30 days).

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if migration successful or column already exists, False on error
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if metadata column already exists
        cursor.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'metadata' in columns:
            logger.info("✅ Metadata column already exists")
            conn.close()
            return True

        # Add metadata column
        cursor.execute("ALTER TABLE projects ADD COLUMN metadata TEXT")
        conn.commit()
        conn.close()

        logger.info("✅ Added metadata column to projects table")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def migrate_link_ideas_to_projects(db_path: Path) -> bool:
    """
    Add project_id column to ideas table to link ideas with projects.

    WHY: Enables tracking which ideas became active projects, creating a complete
         lifecycle view from idea validation → project execution.

    Args:
        db_path: Path to SQLite database file

    Returns:
        True if migration successful or column already exists, False on error
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Check if ideas table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ideas'")
        if not cursor.fetchone():
            logger.info("⚠️ Ideas table doesn't exist yet, skipping migration")
            conn.close()
            return True

        # Check if project_id column already exists
        cursor.execute("PRAGMA table_info(ideas)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'project_id' in columns:
            logger.info("✅ project_id column already exists in ideas table")
            conn.close()
            return True

        # Add project_id column with foreign key reference
        # Note: SQLite doesn't support adding foreign keys to existing tables,
        # so we just add the column without the constraint
        cursor.execute("ALTER TABLE ideas ADD COLUMN project_id TEXT")

        # Create index for faster lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ideas_project ON ideas(project_id)")

        conn.commit()
        conn.close()

        logger.info("✅ Added project_id column to ideas table")
        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
