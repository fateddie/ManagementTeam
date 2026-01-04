#!/usr/bin/env python3
"""
verify_docs.py
--------------
Verify documentation is current before pushing to GitHub.

Triggered by pre-push hook. Checks if recent features are documented.

Usage:
    python scripts/verify_docs.py
"""
import sys
import subprocess
from pathlib import Path


def get_recent_commits(n=10):
    """Get last N commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--oneline"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.split('\n')
    except subprocess.CalledProcessError:
        return []


def check_feature_documented(feature_name, doc_files):
    """
    Check if a feature is documented in any of the doc files.

    Args:
        feature_name: Feature to look for
        doc_files: List of documentation file paths

    Returns:
        True if documented, False otherwise
    """
    for doc_file in doc_files:
        if not doc_file.exists():
            continue

        content = doc_file.read_text().lower()
        if feature_name.lower() in content:
            return True

    return False


def verify_docs():
    """
    Verify documentation mentions recent features.

    Returns:
        True if docs are current, False if outdated
    """
    print("📋 Verifying documentation currency...")

    # Get recent commits
    recent_commits = get_recent_commits()

    # Extract features from commit messages
    features_to_check = []

    for commit in recent_commits:
        commit_lower = commit.lower()

        # Check for significant features
        if 'huggingface' in commit_lower or 'keybert' in commit_lower:
            features_to_check.append(('HuggingFace/KeyBERT', 'HuggingFace'))
        if 't5' in commit_lower and 'grammar' in commit_lower:
            features_to_check.append(('T5 Grammar', 'T5'))
        if 'semantic search' in commit_lower:
            features_to_check.append(('Semantic Search', 'semantic search'))
        if 'folder' in commit_lower and ('cleanup' in commit_lower or 'structure' in commit_lower):
            features_to_check.append(('Folder Structure', 'data/raw'))

    if not features_to_check:
        print("ℹ️  No new features to verify")
        return True

    # Remove duplicates
    features_to_check = list(set(features_to_check))

    # Documentation files to check
    doc_files = [
        Path("docs/ARCHITECTURE.md"),
        Path("docs/README.md"),
        Path("README.md"),
        Path("docs/PROJECT_SNAPSHOT.md"),
        Path("docs/COST_OPTIMIZATION.md"),
        Path("docs/FOLDER_STRUCTURE.md")
    ]

    # Check each feature
    missing = []
    for feature_name, search_term in features_to_check:
        if not check_feature_documented(search_term, doc_files):
            missing.append(feature_name)

    if missing:
        print("\n❌ Documentation is out of date!")
        print(f"   Missing documentation for: {', '.join(missing)}")
        print("\n   Please update documentation:")
        for feature in missing:
            if 'HuggingFace' in feature:
                print("   - Add HuggingFace section to docs/ARCHITECTURE.md")
            if 'T5' in feature:
                print("   - Mention T5 grammar in docs/COST_OPTIMIZATION.md")
            if 'Semantic' in feature:
                print("   - Document semantic search in docs/ARCHITECTURE.md")
            if 'Folder' in feature:
                print("   - Update folder structure in docs/FOLDER_STRUCTURE.md")
        print("\n   Or run: python scripts/update_all_docs.py (if available)")
        return False

    print("✅ Documentation is current - all recent features documented")
    return True


def main():
    """Main entry point."""
    try:
        is_current = verify_docs()
        sys.exit(0 if is_current else 1)
    except Exception as e:
        print(f"❌ Error verifying docs: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
