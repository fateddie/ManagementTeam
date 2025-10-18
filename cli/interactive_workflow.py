#!/usr/bin/env python3
"""
Interactive Workflow CLI

Command-line interface for conversational gated workflow.

Usage:
    python cli/interactive_workflow.py                    # New idea (guided mode)
    python cli/interactive_workflow.py --expert           # New idea (expert mode)
    python cli/interactive_workflow.py --resume PROJECT   # Resume existing project
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.interactive_orchestrator import InteractiveOrchestrator
from core.project_context import ProjectContext


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive conversational workflow for idea validation"
    )

    parser.add_argument(
        '--mode',
        choices=['guided', 'expert'],
        default='guided',
        help='Workflow mode: guided (conversational) or expert (fast input)'
    )

    parser.add_argument(
        '--expert',
        action='store_true',
        help='Shortcut for --mode=expert'
    )

    parser.add_argument(
        '--resume',
        type=str,
        metavar='PROJECT_ID',
        help='Resume existing project by ID'
    )

    parser.add_argument(
        '--no-autosave',
        action='store_true',
        help='Disable auto-save after each field'
    )

    args = parser.parse_args()

    # Determine mode
    mode = 'expert' if args.expert else args.mode
    auto_save = not args.no_autosave

    # Check if resuming
    if args.resume:
        project_id = args.resume
        print(f"\n📂 Resuming project: {project_id}")

        # Verify project exists
        context = ProjectContext()
        try:
            project_data = context.get_project_summary(project_id)
            if not project_data:
                print(f"❌ Project '{project_id}' not found")
                print("\nAvailable projects:")
                # TODO: List available projects
                return 1
        except Exception as e:
            print(f"❌ Error loading project: {e}")
            return 1
    else:
        project_id = None
        print("\n🆕 Starting new idea workflow")

    # Create and run orchestrator
    try:
        orchestrator = InteractiveOrchestrator(
            project_id=project_id,
            mode=mode,
            auto_save=auto_save
        )

        orchestrator.run_workflow()

        print("\n✅ Workflow completed successfully!")
        print(f"Project ID: {orchestrator.project_id}")
        print(f"\nView in dashboard or run full pipeline:")
        print(f"  python cli/manage.py run --project {orchestrator.project_id}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⏸️  Workflow paused.")
        print("All progress auto-saved. Run again to continue.")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
