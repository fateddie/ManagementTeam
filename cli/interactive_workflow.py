#!/usr/bin/env python3
"""
Interactive Workflow CLI

Command-line interface for conversational gated workflow.

PHASE 3 ENHANCEMENTS: Crash Recovery Support
- Auto-detect incomplete sessions
- Resume from checkpoints
- List available checkpoints
- Manual checkpoint creation

Usage:
    python cli/interactive_workflow.py                           # New idea (guided mode)
    python cli/interactive_workflow.py --expert                  # New idea (expert mode)
    python cli/interactive_workflow.py --resume PROJECT          # Resume existing project
    python cli/interactive_workflow.py --list-checkpoints        # List all checkpoints
    python cli/interactive_workflow.py --resume-checkpoint ID    # Resume from specific checkpoint
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.interactive_orchestrator import InteractiveOrchestrator
from core.project_context import ProjectContext
from core.checkpoint_manager import CheckpointManager
from core.workflow_state import WorkflowState


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

    # PHASE 3: Checkpoint arguments
    parser.add_argument(
        '--list-checkpoints',
        type=str,
        metavar='PROJECT_ID',
        help='List all available checkpoints for a project'
    )

    parser.add_argument(
        '--resume-checkpoint',
        type=str,
        metavar='CHECKPOINT_ID',
        help='Resume from a specific checkpoint ID'
    )

    parser.add_argument(
        '--no-checkpoints',
        action='store_true',
        help='Disable checkpoint creation (not recommended)'
    )

    args = parser.parse_args()

    # PHASE 3: Handle list-checkpoints command
    if args.list_checkpoints:
        return list_checkpoints(args.list_checkpoints)

    # PHASE 3: Handle resume-checkpoint command
    if args.resume_checkpoint:
        return resume_from_checkpoint(args.resume_checkpoint)

    # Determine mode
    mode = 'expert' if args.expert else args.mode
    auto_save = not args.no_autosave
    enable_checkpoints = not args.no_checkpoints

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

        # PHASE 3: Auto-detect crashed sessions
        if enable_checkpoints:
            crash_detected = detect_and_offer_recovery()
            if crash_detected:
                # User chose to resume from crash, exit gracefully
                return 0

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
        print("All progress auto-saved via checkpoint. Run again to continue.")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💾 State saved to checkpoint - you can resume from where you left off")
        import traceback
        traceback.print_exc()
        return 1


# ==================================================
# PHASE 3: Checkpoint Helper Functions
# ==================================================

def detect_and_offer_recovery() -> bool:
    """
    Auto-detect crashed sessions and offer recovery.

    Returns:
        True if user chose to resume, False if starting fresh

    WHY: Automatically detect crashes and offer seamless recovery
    """
    # Check all projects for incomplete sessions
    checkpoint_dir = Path(".checkpoints")
    if not checkpoint_dir.exists():
        return False

    incomplete_sessions = []
    for project_dir in checkpoint_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_id = project_dir.name
        manager = CheckpointManager(project_id)
        incomplete = manager.detect_incomplete_session()

        if incomplete:
            incomplete_sessions.append(incomplete)

    if not incomplete_sessions:
        return False

    # Found incomplete sessions - offer recovery
    print("\n" + "="*70)
    print("💾 INCOMPLETE SESSION DETECTED")
    print("="*70)
    print("\nFound interrupted workflow(s):\n")

    for i, session in enumerate(incomplete_sessions, 1):
        print(f"{i}. Project: {session['project_id']}")
        print(f"   Last Step: {session['current_step']}")
        print(f"   Completed: {session['completed_steps']} steps")
        print(f"   Updated: {session['created_at']}")
        print()

    print("Options:")
    print("  1) Resume from checkpoint")
    print("  2) Start fresh")
    print()

    choice = input("Your choice [1-2]: ").strip()

    if choice == '1':
        if len(incomplete_sessions) == 1:
            session_to_resume = incomplete_sessions[0]
        else:
            idx = int(input(f"\nWhich session to resume? [1-{len(incomplete_sessions)}]: ").strip()) - 1
            session_to_resume = incomplete_sessions[idx]

        # Resume the workflow
        print(f"\n📂 Resuming from checkpoint...")
        workflow_state = WorkflowState.from_checkpoint(session_to_resume['project_id'])

        if workflow_state:
            print(f"✅ Resumed at step: {workflow_state.current_step}")
            print(f"   Completed steps: {len(workflow_state.completed_steps)}")
            print(f"\nContinuing workflow...")

            # Create orchestrator with resumed state
            orchestrator = InteractiveOrchestrator(
                project_id=workflow_state.project_id,
                mode='guided',
                auto_save=True
            )

            # Inject restored state
            orchestrator.workflow_state = workflow_state

            # Continue workflow
            orchestrator.run_workflow()

            print("\n✅ Workflow completed successfully!")
            return True
        else:
            print("❌ Failed to resume from checkpoint")
            return False

    return False


def list_checkpoints(project_id: str) -> int:
    """
    List all checkpoints for a project.

    Args:
        project_id: Project ID

    Returns:
        Exit code
    """
    manager = CheckpointManager(project_id)
    checkpoints = manager.list_checkpoints()

    if not checkpoints:
        print(f"\n📋 No checkpoints found for project: {project_id}")
        return 0

    print("\n" + "="*70)
    print(f"📋 CHECKPOINTS FOR PROJECT: {project_id}")
    print("="*70)
    print()

    for checkpoint in checkpoints:
        print(f"Checkpoint ID: {checkpoint['checkpoint_id']}")
        print(f"  Created: {checkpoint['created_at']}")
        print(f"  Type: {checkpoint['checkpoint_type']}")
        print(f"  Step: {checkpoint['current_step']}")
        print(f"  Completed: {checkpoint['completed_steps']} steps")
        print()

    print(f"Total: {len(checkpoints)} checkpoint(s)")
    print("="*70)
    print()
    print("To resume from a checkpoint:")
    print(f"  python cli/interactive_workflow.py --resume-checkpoint CHECKPOINT_ID")
    print()

    return 0


def resume_from_checkpoint(checkpoint_id: str) -> int:
    """
    Resume workflow from a specific checkpoint.

    Args:
        checkpoint_id: Checkpoint ID to resume from

    Returns:
        Exit code
    """
    # Find which project this checkpoint belongs to
    checkpoint_dir = Path(".checkpoints")
    if not checkpoint_dir.exists():
        print(f"❌ No checkpoints directory found")
        return 1

    for project_dir in checkpoint_dir.iterdir():
        if not project_dir.is_dir():
            continue

        project_id = project_dir.name
        manager = CheckpointManager(project_id)
        checkpoint_data = manager.load_checkpoint(checkpoint_id)

        if checkpoint_data:
            print(f"\n📂 Resuming from checkpoint: {checkpoint_id}")
            print(f"   Project: {project_id}")

            workflow_state = WorkflowState.from_checkpoint(project_id, checkpoint_id)

            if workflow_state:
                print(f"✅ Resumed at step: {workflow_state.current_step}")
                print(f"   Completed steps: {len(workflow_state.completed_steps)}")
                print()

                # Create orchestrator with resumed state
                orchestrator = InteractiveOrchestrator(
                    project_id=workflow_state.project_id,
                    mode='guided',
                    auto_save=True
                )

                # Inject restored state
                orchestrator.workflow_state = workflow_state

                # Continue workflow
                orchestrator.run_workflow()

                print("\n✅ Workflow completed successfully!")
                return 0
            else:
                print("❌ Failed to resume from checkpoint")
                return 1

    print(f"❌ Checkpoint not found: {checkpoint_id}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
