#!/usr/bin/env python3
"""
update_changelog.py
-------------------
Auto-update CHANGELOG.md from recent git commits.

Triggered by post-commit hook for significant commits (feat:, refactor:, perf:).

Usage:
    python scripts/update_changelog.py
"""
import subprocess
from datetime import datetime
from pathlib import Path
import sys


def get_recent_commits(n=10):
    """
    Get last N commits.

    Returns:
        List of dicts with hash, message, date
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%H|%s|%ad", "--date=short"],
            capture_output=True,
            text=True,
            check=True
        )

        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|')
            if len(parts) == 3:
                hash, msg, date = parts
                commits.append({
                    "hash": hash[:7],
                    "message": msg,
                    "date": date
                })
        return commits

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get git commits: {e}")
        return []


def update_changelog():
    """
    Update CHANGELOG.md with recent commits.

    Adds significant commits (feat:, fix:, refactor:, perf:) to the top
    of CHANGELOG.md under today's date.
    """
    changelog_path = Path("docs/CHANGELOG.md")

    # Read existing changelog
    if changelog_path.exists():
        with open(changelog_path) as f:
            content = f.read()
    else:
        content = "# Changelog\n\nAll notable changes to this project.\n\n"

    # Get recent commits
    commits = get_recent_commits()
    if not commits:
        print("ℹ️  No commits found")
        return

    # Filter for significant commits
    significant = []
    for commit in commits:
        msg = commit['message']
        if msg.startswith(('feat:', 'fix:', 'refactor:', 'perf:', 'docs:')):
            significant.append(commit)

    if not significant:
        print("ℹ️  No significant commits to add")
        return

    # Build new entry
    today = datetime.now().strftime("%Y-%m-%d")

    # Check if today's entry already exists
    if f"## {today}" in content:
        print(f"ℹ️  Entry for {today} already exists")
        return

    new_entry = f"## {today}\n\n"
    for commit in significant[:5]:  # Limit to 5 most recent
        # Format: - [abc1234] feat: Add new feature
        new_entry += f"- [`{commit['hash']}`] {commit['message']}\n"
    new_entry += "\n"

    # Insert after header
    lines = content.split('\n')

    # Find insertion point (after "# Changelog" and description)
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('##'):
            insert_idx = i
            break

    if insert_idx == 0:
        # No existing entries, insert after header
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#'):
                insert_idx = i + 1
                break

    # Insert new entry
    lines.insert(insert_idx, new_entry.rstrip())
    updated = '\n'.join(lines)

    # Write back
    with open(changelog_path, 'w') as f:
        f.write(updated)

    print(f"✅ Updated CHANGELOG.md with {len(significant)} commits")
    return True


def main():
    """Main entry point."""
    try:
        success = update_changelog()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error updating changelog: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
