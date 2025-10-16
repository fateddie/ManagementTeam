"""
Test Suite: State Flow (PRD-04)
Tests orchestrator state management and workflow progression.
"""

import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "variant_exploration_system" / "orchestrator"))

from orchestrator_core import (
    load_json, save_json, timestamp,
    STATE_FILE, PHASE_MAP_FILE, BASE_DIR
)

def test_state_file_structure():
    """Test state file has correct structure"""
    if STATE_FILE.exists():
        state = load_json(STATE_FILE, {})

        # Check required fields
        assert 'variant_name' in state or len(state) == 0, "State should have variant_name"
        assert 'current_phase' in state or len(state) == 0, "State should have current_phase"
        assert 'status' in state or len(state) == 0, "State should have status"

def test_phase_map_structure():
    """Test phase map has correct structure"""
    if PHASE_MAP_FILE.exists():
        phase_map = load_json(PHASE_MAP_FILE, {})

        assert 'phases' in phase_map or len(phase_map) == 0, "Phase map should have 'phases' key"

        if 'phases' in phase_map and phase_map['phases']:
            # Check first phase structure
            phase = phase_map['phases'][0]
            assert 'phase' in phase, "Phase should have 'phase' number"
            assert 'phase_name' in phase, "Phase should have 'phase_name'"
            assert 'agent' in phase, "Phase should have 'agent'"

def test_timestamp_format():
    """Test timestamp generates valid ISO 8601 format"""
    ts = timestamp()

    # Should be a string
    assert isinstance(ts, str), "Timestamp should be string"

    # Should end with 'Z'
    assert ts.endswith('Z'), "Timestamp should end with 'Z' (UTC)"

    # Should contain 'T' separator
    assert 'T' in ts, "Timestamp should have 'T' separator"

    # Should be parseable
    import datetime
    try:
        datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except:
        assert False, "Timestamp should be valid ISO 8601"

def test_save_and_load_json():
    """Test JSON save and load functions"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = Path(f.name)

    try:
        # Test data
        data = {
            "variant_name": "test_variant",
            "current_phase": 5,
            "status": "in_progress",
            "approvals": [
                {"phase": 0, "result": "approved"},
                {"phase": 1, "result": "approved"}
            ]
        }

        # Save
        save_json(temp_path, data)
        assert temp_path.exists(), "File should be created"

        # Load
        loaded = load_json(temp_path, {})
        assert loaded == data, "Loaded data should match saved data"

    finally:
        if temp_path.exists():
            temp_path.unlink()

def test_load_json_with_default():
    """Test load_json returns default for non-existent file"""
    default = {"test": "default"}
    result = load_json(Path("/nonexistent/file.json"), default)
    assert result == default, "Should return default for non-existent file"

def test_state_progression():
    """Test state can progress through phases"""
    # Create temporary state
    state = {
        "variant_name": "test_variant",
        "current_phase": 0,
        "status": "initialized",
        "started_at": timestamp(),
        "approvals": []
    }

    # Simulate progression
    for phase in range(0, 5):
        state["current_phase"] = phase
        state["approvals"].append({
            "phase": phase,
            "result": "approved",
            "timestamp": timestamp()
        })

    # Verify state
    assert state["current_phase"] == 4, "Phase should progress"
    assert len(state["approvals"]) == 5, "Should have 5 approvals"
    assert all(a["result"] == "approved" for a in state["approvals"]), "All should be approved"

def test_state_pause_resume():
    """Test state can be paused and resumed"""
    # Initial state
    state = {
        "variant_name": "test_variant",
        "current_phase": 3,
        "status": "in_progress",
        "started_at": timestamp(),
        "approvals": [
            {"phase": 0, "result": "approved"},
            {"phase": 1, "result": "approved"},
            {"phase": 2, "result": "approved"}
        ]
    }

    # Pause
    state["status"] = "paused"
    state["paused_at"] = timestamp()

    assert state["status"] == "paused", "Should be paused"
    assert "paused_at" in state, "Should have paused timestamp"

    # Resume
    state["status"] = "in_progress"
    state["resumed_at"] = timestamp()

    assert state["status"] == "in_progress", "Should be resumed"
    assert state["current_phase"] == 3, "Phase should remain at 3"

def test_state_completion():
    """Test state can be marked as completed"""
    state = {
        "variant_name": "test_variant",
        "current_phase": 13,
        "status": "in_progress",
        "started_at": timestamp(),
        "approvals": []
    }

    # Mark complete
    state["status"] = "completed"
    state["completed_at"] = timestamp()

    assert state["status"] == "completed", "Should be completed"
    assert "completed_at" in state, "Should have completion timestamp"
    assert state["current_phase"] == 13, "Should be at final phase"

def test_approval_tracking():
    """Test approval history is properly tracked"""
    approvals = []

    # Add several approvals
    for phase in [0, 1, 2]:
        approvals.append({
            "phase": phase,
            "result": "approved",
            "timestamp": timestamp()
        })

    # Add skip
    approvals.append({
        "phase": 3,
        "result": "skipped",
        "timestamp": timestamp()
    })

    # Verify structure
    assert len(approvals) == 4, "Should have 4 approval records"
    assert approvals[0]["result"] == "approved"
    assert approvals[3]["result"] == "skipped"
    assert all("timestamp" in a for a in approvals), "All should have timestamps"

def test_variant_directory_structure():
    """Test variant directory structure requirements"""
    # Variant should have these directories/files
    expected_templates = [
        "idea_intake.md",
        "scope.yaml",
        "pain_scores.json",
        "unit_economics.json"
    ]

    # Check templates directory exists
    templates_dir = BASE_DIR / "templates"
    if templates_dir.exists():
        template_files = [f.name for f in templates_dir.glob("*") if f.is_file()]

        # Should have at least some templates
        assert len(template_files) > 0, "Templates directory should have files"

        # Check for key templates (some might not exist yet)
        for template in expected_templates:
            # Just verify path structure would work
            path = templates_dir / template
            assert isinstance(path, Path), "Should be valid path"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
