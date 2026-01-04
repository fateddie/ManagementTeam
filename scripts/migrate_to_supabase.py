#!/usr/bin/env python3
"""
Migrate ManagementTeam JSON Memory to Supabase
===============================================
One-time migration script to upload existing agent memory
from JSON files to shared Supabase long-term memory.

Usage:
    python scripts/migrate_to_supabase.py
    python scripts/migrate_to_supabase.py --dry-run  # Preview without uploading

Author: Management Team
Last Updated: 2025-11-12
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from memory.supabase_memory import (
    store_project_decision,
    get_project_status,
    DEPENDENCIES_AVAILABLE
)

MEMORY_DIR = PROJECT_ROOT / "memory"


def load_agent_memory(agent_name: str) -> Dict[str, Any]:
    """Load agent memory from JSON file"""
    json_file = MEMORY_DIR / f"{agent_name}.json"

    if not json_file.exists():
        print(f"⚠️  No memory file found for {agent_name}")
        return {}

    with open(json_file, 'r') as f:
        return json.load(f)


def get_all_agent_files() -> List[str]:
    """Get list of all agent memory files"""
    if not MEMORY_DIR.exists():
        print(f"❌ Memory directory not found: {MEMORY_DIR}")
        return []

    return [f.stem for f in MEMORY_DIR.glob("*.json")]


def migrate_agent(agent_name: str, dry_run: bool = False) -> Dict[str, int]:
    """
    Migrate single agent's memory to Supabase.

    Args:
        agent_name: Name of agent (e.g., 'strategy_agent')
        dry_run: If True, preview without uploading

    Returns:
        Statistics dict with counts
    """
    print(f"\n📦 Processing agent: {agent_name}")

    data = load_agent_memory(agent_name)
    if not data:
        return {"skipped": 1}

    stats = {
        "total_projects": 0,
        "migrated": 0,
        "skipped": 0,
        "already_exists": 0
    }

    project_history = data.get("project_history", [])
    stats["total_projects"] = len(project_history)

    if not project_history:
        print(f"   ℹ️  No project history found")
        return stats

    print(f"   Found {len(project_history)} project records")

    for project in project_history:
        project_name = project.get("project")
        decision = project.get("decision")
        notes = project.get("notes", "")
        date = project.get("date", "")

        if not project_name or not decision:
            print(f"   ⚠️  Skipping invalid record: {project}")
            stats["skipped"] += 1
            continue

        # Check if already exists
        if not dry_run:
            try:
                existing = get_project_status(project_name)
                if existing:
                    print(f"   ⏭️  Already exists: {project_name}")
                    stats["already_exists"] += 1
                    continue
            except Exception:
                pass  # Assume doesn't exist if error

        # Prepare metadata
        metadata = {
            "original_date": date,
            "migrated_from": "json",
            "migration_timestamp": "2025-11-12"
        }

        if dry_run:
            print(f"   🔍 Would migrate: {project_name} - {decision}")
            stats["migrated"] += 1
        else:
            try:
                memory_id = store_project_decision(
                    project_name=project_name,
                    decision=decision,
                    agent_name=agent_name,
                    notes=f"[Migrated from JSON - {date}] {notes}",
                    metadata=metadata
                )
                print(f"   ✅ Migrated: {project_name} (ID: {memory_id})")
                stats["migrated"] += 1
            except Exception as e:
                print(f"   ❌ Failed to migrate {project_name}: {e}")
                stats["skipped"] += 1

    return stats


def migrate_all(dry_run: bool = False):
    """Migrate all agent memories"""
    print("=" * 60)
    print("🚀 ManagementTeam Memory Migration")
    print("=" * 60)

    if not DEPENDENCIES_AVAILABLE:
        print("\n❌ Missing dependencies!")
        print("Install with: pip install supabase openai")
        sys.exit(1)

    if dry_run:
        print("\n🔍 DRY RUN MODE - No data will be uploaded\n")
    else:
        print("\n⚠️  This will upload data to Supabase")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    agents = get_all_agent_files()
    if not agents:
        print("\n❌ No agent memory files found in /memory/")
        sys.exit(1)

    print(f"\nFound {len(agents)} agent(s): {', '.join(agents)}\n")

    total_stats = {
        "total_agents": len(agents),
        "total_projects": 0,
        "migrated": 0,
        "skipped": 0,
        "already_exists": 0
    }

    for agent in agents:
        stats = migrate_agent(agent, dry_run)
        total_stats["total_projects"] += stats.get("total_projects", 0)
        total_stats["migrated"] += stats.get("migrated", 0)
        total_stats["skipped"] += stats.get("skipped", 0)
        total_stats["already_exists"] += stats.get("already_exists", 0)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    print(f"Agents processed:      {total_stats['total_agents']}")
    print(f"Total projects:        {total_stats['total_projects']}")
    print(f"Successfully migrated: {total_stats['migrated']}")
    print(f"Already existed:       {total_stats['already_exists']}")
    print(f"Skipped/Failed:        {total_stats['skipped']}")
    print("=" * 60)

    if dry_run:
        print("\n🔍 This was a dry run. Run without --dry-run to upload.")
    else:
        print("\n✅ Migration complete!")
        print("\nℹ️  Original JSON files preserved in /memory/")
        print("   You can keep them as backup or delete after verification.")


def backup_json_files():
    """Create backup of JSON files before migration"""
    backup_dir = MEMORY_DIR / "backup_pre_migration"
    backup_dir.mkdir(exist_ok=True)

    for json_file in MEMORY_DIR.glob("*.json"):
        import shutil
        shutil.copy(json_file, backup_dir / json_file.name)

    print(f"✅ Backup created: {backup_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migrate ManagementTeam JSON memory to Supabase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview migration without uploading data"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of JSON files before migration"
    )
    parser.add_argument(
        "--agent",
        help="Migrate specific agent only"
    )

    args = parser.parse_args()

    try:
        if args.backup and not args.dry_run:
            backup_json_files()

        if args.agent:
            print(f"\n🎯 Migrating single agent: {args.agent}\n")
            stats = migrate_agent(args.agent, args.dry_run)
            print("\n📊 Results:")
            print(f"   Migrated: {stats.get('migrated', 0)}")
            print(f"   Skipped:  {stats.get('skipped', 0)}")
            print(f"   Existed:  {stats.get('already_exists', 0)}")
        else:
            migrate_all(args.dry_run)

    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
