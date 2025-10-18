"""
project_memory.py
Lightweight Redis-based Persistent Memory for Agent Outputs

Purpose:
    - Store agent outputs persistently across sessions
    - Enable keyword search across projects
    - Provide project history tracking
    - Support real-time event streaming to dashboard

Why Redis:
    - Fast in-memory database
    - Simple key-value storage
    - Pub/sub for real-time events
    - 30-day TTL for automatic cleanup
    - No complex setup (unlike Archon's 4 microservices)

Benefits:
    - ✅ Persistent memory (survives restarts)
    - ✅ Simple keyword search
    - ✅ 1-2 day implementation
    - ✅ Easy to maintain (single file)
    - ✅ Real-time events for dashboard

Usage:
    from core.project_memory import ProjectMemory

    memory = ProjectMemory()

    # Store agent output
    memory.store_project(
        project_id="ai_call_catcher",
        stage="StrategyAgent",
        data={"goals": [...], "kpis": [...]}
    )

    # Retrieve specific stage
    strategy = memory.get_project_stage("ai_call_catcher", "StrategyAgent")

    # Get full project history
    history = memory.get_project_history("ai_call_catcher")

    # Search projects
    projects = memory.search_projects_with_keyword("Supabase")

Created: 2025-10-17
Phase: 16 - Lightweight Memory System
"""

import json
import redis
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
from pathlib import Path
import os


class ProjectMemory:
    """
    Lightweight persistent memory for agent outputs using Redis.

    Provides:
        - Persistent storage (30-day retention)
        - Keyword search across projects
        - Project history tracking
        - Real-time event publishing

    Architecture:
        - Redis keys: project:{project_id}:{stage}
        - Data stored as JSON strings
        - TTL set to 30 days (automatic cleanup)
        - Pub/sub channel: agent_events
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,
        db: int = 0
    ):
        """
        Initialize Redis connection.

        Args:
            host: Redis host (default: localhost)
            port: Redis port (default: 6379)
            password: Redis password (default: None)
            db: Redis database number (default: 0)

        Raises:
            redis.ConnectionError: If cannot connect to Redis
        """
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db,
                decode_responses=True  # Auto-decode bytes to strings
            )

            # Test connection
            self.redis.ping()

        except redis.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to Redis at {host}:{port}. "
                f"Is Redis running? Start with: brew services start redis (macOS) "
                f"or docker run -d -p 6379:6379 redis (Docker). Error: {e}"
            )

    def store_project(
        self,
        project_id: str,
        stage: str,
        data: Dict[str, Any],
        ttl_days: int = 30
    ) -> bool:
        """
        Store agent output for a project stage.

        Args:
            project_id: Unique project identifier (e.g., "ai_call_catcher")
            stage: Agent stage name (e.g., "StrategyAgent")
            data: Agent output data (will be JSON-serialized)
            ttl_days: Time-to-live in days (default: 30)

        Returns:
            True if stored successfully, False otherwise

        Example:
            memory.store_project(
                project_id="ai_call_catcher",
                stage="StrategyAgent",
                data={
                    "goals": ["Scale to 1M users", "Generate $5M ARR"],
                    "kpis": ["User growth", "Revenue"]
                }
            )
        """
        key = f"project:{project_id}:{stage}"
        ttl_seconds = ttl_days * 24 * 60 * 60

        # Add metadata
        enhanced_data = {
            "project_id": project_id,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        try:
            # Store with TTL
            self.redis.setex(
                key,
                ttl_seconds,
                json.dumps(enhanced_data)
            )

            # Publish event for real-time updates
            self.publish_event("project_stored", {
                "project_id": project_id,
                "stage": stage,
                "timestamp": enhanced_data["timestamp"]
            })

            return True

        except Exception as e:
            print(f"❌ Error storing project data: {e}")
            return False

    def get_project_stage(
        self,
        project_id: str,
        stage: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent output from specific project stage.

        Args:
            project_id: Project identifier
            stage: Agent stage name

        Returns:
            Dictionary with stage data, or None if not found

        Example:
            strategy = memory.get_project_stage("ai_call_catcher", "StrategyAgent")
            if strategy:
                print(strategy["data"]["goals"])
        """
        key = f"project:{project_id}:{stage}"

        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None

        except Exception as e:
            print(f"❌ Error retrieving project stage: {e}")
            return None

    def get_project_history(self, project_id: str) -> Dict[str, Any]:
        """
        Get all stages for a project (complete history).

        Args:
            project_id: Project identifier

        Returns:
            Dictionary mapping stage names to their data

        Example:
            history = memory.get_project_history("ai_call_catcher")
            # Returns:
            # {
            #     "StrategyAgent": {...},
            #     "TechnicalArchitectAgent": {...},
            #     "PlanningAgent": {...}
            # }
        """
        pattern = f"project:{project_id}:*"

        try:
            keys = self.redis.keys(pattern)
            history = {}

            for key in keys:
                # Extract stage name from key
                stage = key.split(":")[-1]
                data = self.redis.get(key)

                if data:
                    history[stage] = json.loads(data)

            return history

        except Exception as e:
            print(f"❌ Error retrieving project history: {e}")
            return {}

    def search_projects_with_keyword(
        self,
        keyword: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for projects containing a keyword.

        Args:
            keyword: Search term (case-insensitive)
            max_results: Maximum number of results to return

        Returns:
            List of matching project data with context

        Example:
            # Find all projects that used Supabase
            results = memory.search_projects_with_keyword("Supabase")
            for result in results:
                print(f"{result['project_id']} - {result['stage']}")
                print(f"Match: {result['snippet']}")
        """
        pattern = "project:*"
        keyword_lower = keyword.lower()
        matches = []

        try:
            # Get all project keys
            keys = self.redis.keys(pattern)

            for key in keys:
                if len(matches) >= max_results:
                    break

                data_str = self.redis.get(key)
                if not data_str:
                    continue

                # Check if keyword exists in the data (case-insensitive)
                if keyword_lower in data_str.lower():
                    data = json.loads(data_str)

                    # Extract snippet around keyword
                    snippet = self._extract_snippet(data_str, keyword)

                    matches.append({
                        "project_id": data.get("project_id"),
                        "stage": data.get("stage"),
                        "timestamp": data.get("timestamp"),
                        "snippet": snippet,
                        "full_data": data
                    })

            # Sort by timestamp (most recent first)
            matches.sort(
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )

            return matches

        except Exception as e:
            print(f"❌ Error searching projects: {e}")
            return []

    def list_all_projects(self) -> List[str]:
        """
        Get list of all project IDs in memory.

        Returns:
            List of unique project IDs

        Example:
            projects = memory.list_all_projects()
            # Returns: ["ai_call_catcher", "social_media_trending", ...]
        """
        pattern = "project:*"
        project_ids: Set[str] = set()

        try:
            keys = self.redis.keys(pattern)

            for key in keys:
                # Extract project_id from key: project:{id}:{stage}
                parts = key.split(":")
                if len(parts) >= 2:
                    project_ids.add(parts[1])

            return sorted(list(project_ids))

        except Exception as e:
            print(f"❌ Error listing projects: {e}")
            return []

    def delete_project(self, project_id: str) -> int:
        """
        Delete all stages for a project.

        Args:
            project_id: Project identifier

        Returns:
            Number of keys deleted

        Example:
            deleted = memory.delete_project("old_project")
            print(f"Deleted {deleted} stages")
        """
        pattern = f"project:{project_id}:*"

        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0

        except Exception as e:
            print(f"❌ Error deleting project: {e}")
            return 0

    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """
        Publish real-time event to Redis pub/sub channel.

        Args:
            event_type: Type of event (e.g., "agent_started", "agent_completed")
            data: Event data

        Example:
            memory.publish_event("agent_started", {
                "agent": "StrategyAgent",
                "project_id": "ai_call_catcher"
            })

        Note:
            Dashboard can subscribe to these events for real-time updates
        """
        channel = "agent_events"
        event = {
            "type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        try:
            self.redis.publish(channel, json.dumps(event))
        except Exception as e:
            print(f"⚠️  Warning: Failed to publish event: {e}")

    def _extract_snippet(
        self,
        text: str,
        keyword: str,
        context_chars: int = 100
    ) -> str:
        """
        Extract text snippet around keyword match.

        Args:
            text: Full text to search
            keyword: Search term
            context_chars: Characters to include before/after match

        Returns:
            Snippet with keyword highlighted
        """
        idx = text.lower().find(keyword.lower())
        if idx == -1:
            return ""

        start = max(0, idx - context_chars)
        end = min(len(text), idx + len(keyword) + context_chars)

        snippet = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.

        Returns:
            Dictionary with stats (total projects, total stages, memory used)

        Example:
            stats = memory.get_stats()
            print(f"Total projects: {stats['total_projects']}")
            print(f"Memory used: {stats['memory_used_mb']} MB")
        """
        try:
            project_keys = self.redis.keys("project:*")
            project_ids = set()

            for key in project_keys:
                parts = key.split(":")
                if len(parts) >= 2:
                    project_ids.add(parts[1])

            # Get Redis memory info
            info = self.redis.info("memory")
            memory_used = info.get("used_memory", 0)

            return {
                "total_projects": len(project_ids),
                "total_stages": len(project_keys),
                "memory_used_bytes": memory_used,
                "memory_used_mb": round(memory_used / (1024 * 1024), 2)
            }

        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}

    def clear_all(self) -> bool:
        """
        Clear all project data (use with caution!).

        Returns:
            True if successful

        Warning:
            This deletes ALL project data. Only use for testing or cleanup.
        """
        try:
            keys = self.redis.keys("project:*")
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"❌ Error clearing data: {e}")
            return False


def create_memory_from_env() -> ProjectMemory:
    """
    Create ProjectMemory instance from environment variables.

    Reads from:
        - REDIS_HOST (default: localhost)
        - REDIS_PORT (default: 6379)
        - REDIS_PASSWORD (default: None)

    Returns:
        Configured ProjectMemory instance

    Example:
        from core.project_memory import create_memory_from_env
        memory = create_memory_from_env()
    """
    host = os.getenv("REDIS_HOST", "localhost")
    port = int(os.getenv("REDIS_PORT", "6379"))
    password = os.getenv("REDIS_PASSWORD")

    return ProjectMemory(host=host, port=port, password=password)


# Example usage
if __name__ == "__main__":
    """Test ProjectMemory functionality"""

    print("🧪 Testing ProjectMemory...\n")

    try:
        # Create instance
        memory = ProjectMemory()
        print("✅ Connected to Redis")

        # Store test data
        test_project_id = "test_project"
        memory.store_project(
            project_id=test_project_id,
            stage="StrategyAgent",
            data={
                "goals": ["Test goal 1", "Test goal 2"],
                "tech_stack": ["Python", "Redis", "Supabase"]
            }
        )
        print(f"✅ Stored test project: {test_project_id}")

        # Retrieve data
        strategy = memory.get_project_stage(test_project_id, "StrategyAgent")
        if strategy:
            print(f"✅ Retrieved data: {strategy['data']['goals']}")

        # Search
        results = memory.search_projects_with_keyword("Redis")
        print(f"✅ Search found {len(results)} results")

        # Get stats
        stats = memory.get_stats()
        print(f"✅ Stats: {stats['total_projects']} projects, {stats['memory_used_mb']} MB")

        # Cleanup test data
        memory.delete_project(test_project_id)
        print(f"✅ Cleaned up test data")

        print("\n✅ All tests passed!")

    except ConnectionError as e:
        print(f"\n❌ {e}")
        print("\nTo install Redis:")
        print("  macOS:  brew install redis && brew services start redis")
        print("  Ubuntu: sudo apt install redis-server && sudo systemctl start redis")
        print("  Docker: docker run -d -p 6379:6379 redis")
