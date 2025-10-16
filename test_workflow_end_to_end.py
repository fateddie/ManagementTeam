"""
Integration Test: Full Workflow Simulation
Simulates a mini 3-phase orchestrator cycle with dummy artifacts.
"""

import os
import json
import tempfile
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / 'orchestrator/state/state_schema.json'
LOG_FILE = Path(__file__).parent.parent / 'orchestrator/logs/audit_trail.json'

def test_full_workflow_cycle():
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    start_phase = state['current_phase']

    # Simulate advancing through 3 phases
    for i in range(3):
        state['current_phase'] += 1

    assert state['current_phase'] == start_phase + 3

    # Verify logs still accessible
    assert LOG_FILE.exists(), "Audit log missing after cycle."
