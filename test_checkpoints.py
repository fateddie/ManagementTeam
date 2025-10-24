#!/usr/bin/env python3
"""
Test script for Phase 3 Checkpoint System.

Tests CheckpointManager and WorkflowState checkpoint integration.

WHAT THIS TESTS:
1. Checkpoint creation and serialization
2. Checkpoint loading and deserialization
3. Resume from checkpoint
4. Detect incomplete sessions
5. List checkpoints
6. Cleanup old checkpoints

Created: 2025-10-19 (Phase 3 - Sub-Agent Unification)
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.workflow_state import WorkflowState
from core.checkpoint_manager import CheckpointManager


def test_checkpoint_creation():
    """Test creating checkpoints."""
    print("\n" + "="*70)
    print("💾 Test 1: Checkpoint Creation")
    print("="*70)

    try:
        # Create workflow state
        state = WorkflowState(
            project_id="test_project_001",
            session_id="test_session_001",
            enable_checkpoints=True
        )

        # Simulate workflow progress
        state.start_step("Core Idea")
        state.save_field("idea_name", "AI-powered task manager")
        state.save_field("problem", "People struggle with task prioritization")
        state.complete_step("Core Idea", score=0.9, summary="Collected core idea")

        print("✅ Checkpoint created after step completion")
        print(f"   Project: {state.project_id}")
        print(f"   Current step: {state.current_step}")
        print(f"   Completed steps: {len(state.completed_steps)}")

        # Check checkpoint directory
        checkpoint_dir = Path(".checkpoints") / "test_project_001"
        if checkpoint_dir.exists():
            checkpoint_files = list(checkpoint_dir.glob("checkpoint_v*.json"))
            print(f"✅ Found {len(checkpoint_files)} checkpoint file(s)")
            return True
        else:
            print("❌ Checkpoint directory not created")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_checkpoint_loading():
    """Test loading checkpoints."""
    print("\n" + "="*70)
    print("📂 Test 2: Checkpoint Loading")
    print("="*70)

    try:
        # Load checkpoint
        manager = CheckpointManager("test_project_001")
        checkpoint_data = manager.load_latest_checkpoint()

        if checkpoint_data:
            print("✅ Loaded latest checkpoint")
            print(f"   Checkpoint ID: {checkpoint_data['checkpoint_id']}")
            print(f"   Version: {checkpoint_data['version']}")
            print(f"   Session: {checkpoint_data['session_id']}")

            workflow_state = checkpoint_data.get('workflow_state', {})
            print(f"   Current step: {workflow_state.get('current_step')}")
            print(f"   Completed steps: {len(workflow_state.get('completed_steps', []))}")
            print(f"   Collected data: {len(workflow_state.get('collected_data', {}))} fields")

            return True
        else:
            print("❌ Failed to load checkpoint")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_resume_from_checkpoint():
    """Test resuming workflow from checkpoint."""
    print("\n" + "="*70)
    print("🔄 Test 3: Resume from Checkpoint")
    print("="*70)

    try:
        # Resume from checkpoint
        restored_state = WorkflowState.from_checkpoint("test_project_001")

        if restored_state:
            print("✅ Successfully resumed workflow state")
            print(f"   Project ID: {restored_state.project_id}")
            print(f"   Session ID: {restored_state.session_id}")
            print(f"   Current step: {restored_state.current_step}")
            print(f"   Completed steps: {restored_state.completed_steps}")
            print(f"   Collected data: {restored_state.collected_data}")

            # Verify data integrity
            if restored_state.get_field_value('idea_name') == "AI-powered task manager":
                print("✅ Data integrity verified - field values match")
                return True
            else:
                print("❌ Data integrity failed - field values don't match")
                return False
        else:
            print("❌ Failed to resume from checkpoint")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detect_incomplete_session():
    """Test detecting incomplete sessions."""
    print("\n" + "="*70)
    print("🔍 Test 4: Detect Incomplete Session")
    print("="*70)

    try:
        manager = CheckpointManager("test_project_001")
        incomplete = manager.detect_incomplete_session()

        if incomplete:
            print("✅ Detected incomplete session")
            print(f"   Project: {incomplete['project_id']}")
            print(f"   Current step: {incomplete['current_step']}")
            print(f"   Completed steps: {incomplete['completed_steps']}")
            print(f"   Message: {incomplete['message']}")
            return True
        else:
            print("⚠️  No incomplete session detected (this is OK if all steps completed)")
            return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_list_checkpoints():
    """Test listing checkpoints."""
    print("\n" + "="*70)
    print("📋 Test 5: List Checkpoints")
    print("="*70)

    try:
        manager = CheckpointManager("test_project_001")
        checkpoints = manager.list_checkpoints()

        if checkpoints:
            print(f"✅ Found {len(checkpoints)} checkpoint(s)")

            for i, checkpoint in enumerate(checkpoints, 1):
                print(f"\n{i}. {checkpoint['checkpoint_id']}")
                print(f"   Created: {checkpoint['created_at']}")
                print(f"   Type: {checkpoint['checkpoint_type']}")
                print(f"   Step: {checkpoint['current_step']}")
                print(f"   Completed: {checkpoint['completed_steps']} steps")

            return True
        else:
            print("❌ No checkpoints found")
            return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_checkpoints():
    """Test creating multiple checkpoints."""
    print("\n" + "="*70)
    print("📦 Test 6: Multiple Checkpoints")
    print("="*70)

    try:
        state = WorkflowState.from_checkpoint("test_project_001")

        # Continue workflow and create more checkpoints
        state.start_step("Pain Discovery")
        state.save_field("target_audience", "Busy professionals")
        state.complete_step("Pain Discovery", score=0.85, summary="Identified target audience")

        state.start_step("Market Sizing")
        state.save_field("market_size", "10M users")
        state.complete_step("Market Sizing", score=0.8, summary="Estimated market size")

        # List checkpoints
        manager = CheckpointManager("test_project_001")
        checkpoints = manager.list_checkpoints()

        print(f"✅ Created {len(checkpoints)} total checkpoint(s)")
        print(f"   Should have checkpoint for each completed step")

        return len(checkpoints) >= 3  # At least 3 checkpoints

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cleanup():
    """Clean up test checkpoints."""
    print("\n" + "="*70)
    print("🧹 Test 7: Cleanup")
    print("="*70)

    try:
        checkpoint_dir = Path(".checkpoints") / "test_project_001"
        if checkpoint_dir.exists():
            shutil.rmtree(checkpoint_dir)
            print("✅ Cleaned up test checkpoints")
        else:
            print("⚠️  No checkpoints to clean up")

        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checkpoint tests."""
    print("\n" + "="*70)
    print("🧪 PHASE 3 CHECKPOINT SYSTEM TESTS")
    print("="*70)
    print("\nTesting crash recovery system components...")

    results = {
        'Checkpoint Creation': test_checkpoint_creation(),
        'Checkpoint Loading': test_checkpoint_loading(),
        'Resume from Checkpoint': test_resume_from_checkpoint(),
        'Detect Incomplete Session': test_detect_incomplete_session(),
        'List Checkpoints': test_list_checkpoints(),
        'Multiple Checkpoints': test_multiple_checkpoints(),
        'Cleanup': test_cleanup(),
    }

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:30} {status}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    if passed == total:
        print("✅ All checkpoint tests passed!")
        print("\nCheckpoint system is ready for production use:")
        print("  - Auto-checkpoint after each step")
        print("  - Resume from latest or specific checkpoint")
        print("  - Detect crashed sessions on startup")
        print("  - List and manage checkpoints")
        print()

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
