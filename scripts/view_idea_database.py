#!/usr/bin/env python3
"""
view_idea_database.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
View Ideas Database

CLI tool to view stored ideas and their scoring metadata.

Usage:
    python scripts/view_idea_database.py
    python scripts/view_idea_database.py --idea idea-001
    
Location: scripts/view_idea_database.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.utils.metadata_writer import MetadataWriter


def main():
    """View ideas database."""
    parser = argparse.ArgumentParser(
        description="View stored ideas and scoring metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--db",
        default="data/ideas.db",
        help="Path to SQLite database"
    )
    
    parser.add_argument(
        "--idea",
        help="View specific idea ID"
    )
    
    args = parser.parse_args()
    
    writer = MetadataWriter(args.db)
    
    print("\n" + "="*70)
    print("💾 IDEAS DATABASE VIEWER")
    print("="*70 + "\n")
    
    if args.idea:
        # View specific idea metadata
        print(f"📊 Metadata for: {args.idea}\n")
        
        metadata = writer.get_idea_metadata(args.idea)
        
        if not metadata:
            print(f"⚠️  No metadata found for idea: {args.idea}")
        else:
            print(f"Found {len(metadata)} metadata entries:\n")
            
            for entry in metadata:
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"Category: {entry['category'].upper()}")
                print(f"Score: {entry['score']}/10")
                print(f"Justification: {entry['justification']}")
                print(f"Source: {entry['source']}")
                print(f"Confidence: {entry['confidence_score']}/10")
                print(f"Created: {entry['created_at']}")
                print()
    
    else:
        # View all ideas
        ideas = writer.get_all_ideas()
        
        if not ideas:
            print("⚠️  No ideas in database yet\n")
            print("💡 Try running: python src/utils/metadata_writer.py")
        else:
            print(f"📋 All Ideas ({len(ideas)} total):\n")
            
            for i, idea in enumerate(ideas, 1):
                print(f"{i}. {idea['id']}")
                print(f"   Raw: {idea['raw_input']}")
                print(f"   Refined: {idea['refined_summary']}")
                print(f"   Industry: {idea['industry']}")
                print(f"   Created: {idea['created_at']}")
                
                # Get metadata count
                metadata = writer.get_idea_metadata(idea['id'])
                print(f"   Metadata: {len(metadata)} entries")
                print()
    
    print("="*70)
    print("✅ Database View Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

