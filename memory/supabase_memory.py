"""
Supabase Long-Term Memory Adapter for ManagementTeam
=====================================================
Stores agent decisions and project data in shared Supabase instance.
Enables semantic search and cross-system intelligence with AskSharon.ai.

Author: Management Team
Last Updated: 2025-11-12
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from supabase import create_client, Client
    from openai import OpenAI
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  Warning: supabase or openai not installed. Install with:")
    print("   pip install supabase openai")

# Initialize clients (lazy loading)
_supabase_client: Optional[Client] = None
_openai_client: Optional[OpenAI] = None


def _get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase_client

    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    if _supabase_client is None:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
            )

        _supabase_client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

    return _supabase_client


def _get_openai_client() -> OpenAI:
    """Get or create OpenAI client"""
    global _openai_client

    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("openai package not installed. Run: pip install openai")

    if _openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env")

        _openai_client = OpenAI(api_key=api_key)

    return _openai_client


def generate_embedding(text: str) -> List[float]:
    """
    Generate OpenAI embedding for text.

    Args:
        text: Text to embed

    Returns:
        1536-dimensional embedding vector

    Cost: ~$0.00001 per call
    """
    client = _get_openai_client()

    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )

    return response.data[0].embedding


def store_project_decision(
    project_name: str,
    decision: str,
    agent_name: str,
    notes: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store project decision in shared Supabase memory.

    Args:
        project_name: Name of the project
        decision: 'approved', 'rejected', 'on_hold', 'completed'
        agent_name: Agent making the decision (e.g., 'strategy_agent')
        notes: Additional context
        metadata: Optional structured data

    Returns:
        memory_id: ID in long_term_memory table

    Example:
        >>> memory_id = store_project_decision(
        ...     "AI_Receptionist",
        ...     "approved",
        ...     "strategy_agent",
        ...     "High market demand, strong ROI"
        ... )
    """
    supabase = _get_supabase_client()

    # Create semantic content for embedding
    content = f"Project: {project_name}\nDecision: {decision}\nAgent: {agent_name}\nNotes: {notes}"
    embedding = generate_embedding(content)

    # Prepare metadata
    meta = metadata or {}
    meta.update({
        "project": project_name,
        "decision": decision,
        "agent": agent_name,
        "timestamp": datetime.now().isoformat()
    })

    # Store in long_term_memory
    memory_result = supabase.table("long_term_memory").insert({
        "content": content,
        "embedding": embedding,
        "source_system": "management_team",
        "entity_type": "project_decision",
        "entity_id": project_name,
        "user_id": agent_name,
        "metadata": meta
    }).execute()

    if not memory_result.data:
        raise Exception("Failed to store memory in Supabase")

    memory_id = memory_result.data[0]["id"]

    # Store in project_decisions table
    supabase.table("project_decisions").insert({
        "project_name": project_name,
        "decision": decision,
        "agent_name": agent_name,
        "notes": notes,
        "memory_id": memory_id
    }).execute()

    print(f"✅ Stored: {project_name} - {decision} (Memory ID: {memory_id})")
    return memory_id


def recall_related_projects(
    query: str,
    limit: int = 5,
    min_similarity: float = 0.7
) -> List[Dict]:
    """
    Search for related projects using semantic similarity.

    Args:
        query: Natural language query (e.g., "dental clinic automation")
        limit: Maximum number of results
        min_similarity: Minimum cosine similarity (0.0 to 1.0)

    Returns:
        List of matching memories with similarity scores

    Example:
        >>> results = recall_related_projects("healthcare AI solutions")
        >>> for r in results:
        ...     print(f"{r['similarity']:.2f} - {r['metadata']['project']}")
    """
    supabase = _get_supabase_client()
    query_embedding = generate_embedding(query)

    result = supabase.rpc(
        "search_memory",
        {
            "query_embedding": query_embedding,
            "match_threshold": min_similarity,
            "match_count": limit,
            "filter_source_system": "management_team",
            "filter_entity_type": "project_decision"
        }
    ).execute()

    return result.data if result.data else []


def get_project_status(project_name: str) -> Optional[Dict[str, Any]]:
    """
    Get current status of a project.

    Args:
        project_name: Name of the project

    Returns:
        Latest decision record or None if not found
    """
    supabase = _get_supabase_client()

    result = supabase.table("project_decisions")\
        .select("*")\
        .eq("project_name", project_name)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    return result.data[0] if result.data else None


def get_all_active_projects() -> List[Dict[str, Any]]:
    """
    Get all approved or on-hold projects.

    Returns:
        List of active project records
    """
    supabase = _get_supabase_client()

    result = supabase.table("project_decisions")\
        .select("*")\
        .in_("decision", ["approved", "on_hold"])\
        .order("created_at", desc=True)\
        .execute()

    return result.data if result.data else []


def link_to_asksharon_task(
    project_name: str,
    task_id: int,
    relationship: str = "implements"
) -> int:
    """
    Create explicit link between ManagementTeam project and AskSharon task.

    Args:
        project_name: ManagementTeam project name
        task_id: AskSharon task ID
        relationship: Type of relationship ('implements', 'related_to', 'depends_on')

    Returns:
        link_id: ID in memory_links table
    """
    supabase = _get_supabase_client()

    # Get memory IDs
    project_memory = supabase.table("project_decisions")\
        .select("memory_id")\
        .eq("project_name", project_name)\
        .order("created_at", desc=True)\
        .limit(1)\
        .execute()

    task_memory = supabase.table("user_tasks")\
        .select("memory_id")\
        .eq("id", task_id)\
        .execute()

    if not project_memory.data or not task_memory.data:
        raise ValueError("Project or task not found")

    # Create link
    link_result = supabase.table("memory_links").insert({
        "memory_id_1": project_memory.data[0]["memory_id"],
        "memory_id_2": task_memory.data[0]["memory_id"],
        "relationship_type": relationship,
        "confidence": 0.9
    }).execute()

    link_id = link_result.data[0]["id"]
    print(f"✅ Linked project '{project_name}' to task {task_id}")
    return link_id


def get_memory_stats() -> Dict[str, Any]:
    """
    Get statistics about stored memories.

    Returns:
        Dictionary with counts and sizes
    """
    supabase = _get_supabase_client()

    # Count by entity type
    result = supabase.table("long_term_memory")\
        .select("entity_type", count="exact")\
        .eq("source_system", "management_team")\
        .execute()

    return {
        "total_memories": result.count if hasattr(result, 'count') else 0,
        "active_projects": len(get_all_active_projects()),
        "source_system": "management_team"
    }


# ============================================
# CLI Commands (for testing)
# ============================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ManagementTeam Supabase Memory CLI")
    parser.add_argument("command", choices=["store", "search", "status", "stats", "test"])
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--decision", choices=["approved", "rejected", "on_hold", "completed"])
    parser.add_argument("--agent", default="strategy_agent", help="Agent name")
    parser.add_argument("--notes", default="", help="Additional notes")
    parser.add_argument("--query", help="Search query")

    args = parser.parse_args()

    if args.command == "store":
        if not args.project or not args.decision:
            print("❌ --project and --decision required")
            sys.exit(1)

        memory_id = store_project_decision(
            args.project,
            args.decision,
            args.agent,
            args.notes
        )
        print(f"Memory ID: {memory_id}")

    elif args.command == "search":
        if not args.query:
            print("❌ --query required")
            sys.exit(1)

        results = recall_related_projects(args.query)
        print(f"\n🔍 Found {len(results)} results:\n")
        for r in results:
            print(f"  {r['similarity']:.2f} - {r['metadata'].get('project', 'N/A')}")
            print(f"           Decision: {r['metadata'].get('decision', 'N/A')}")
            print(f"           Agent: {r['metadata'].get('agent', 'N/A')}\n")

    elif args.command == "status":
        if not args.project:
            print("❌ --project required")
            sys.exit(1)

        status = get_project_status(args.project)
        if status:
            print(f"\n📊 Project: {args.project}")
            print(f"   Decision: {status['decision']}")
            print(f"   Agent: {status['agent_name']}")
            print(f"   Date: {status['created_at']}")
            print(f"   Notes: {status['notes']}\n")
        else:
            print(f"❌ Project '{args.project}' not found")

    elif args.command == "stats":
        stats = get_memory_stats()
        print("\n📈 Memory Statistics:")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Active projects: {stats['active_projects']}")
        print(f"   Source: {stats['source_system']}\n")

    elif args.command == "test":
        print("🧪 Testing Supabase connection...")
        try:
            client = _get_supabase_client()
            print("✅ Supabase connected")

            # Test embedding generation
            print("🧪 Testing embedding generation...")
            embedding = generate_embedding("Test text")
            print(f"✅ Generated {len(embedding)}-dimensional embedding")

            print("\n✅ All tests passed!")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
