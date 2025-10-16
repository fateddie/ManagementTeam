#!/usr/bin/env python3
import json
import os
from datetime import datetime

# -----------------------------
# Simple CLI Orchestrator Core
# -----------------------------
# Purpose:
#  - Manage SOP workflow phases (0-13)
#  - Enforce human confirmation gates
#  - Log all actions to /logs/audit_trail.json
#  - Persist workflow state to /state/state_schema.json
# This version is designed for Cursor testing and easy extension.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, 'state', 'state_schema.json')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'audit_trail.json')
AGENT_MAP_FILE = os.path.join(BASE_DIR, 'config', 'phase_agent_map.json')

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def log_action(agent, phase, action, comment):
    logs = load_json(LOG_FILE, [])
    logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "phase": phase,
        "action": action,
        "comment": comment
    })
    save_json(LOG_FILE, logs)

def advance_phase(state):
    state['current_phase'] += 1
    state['next_phase'] = state['current_phase'] + 1
    return state

def run_orchestrator():
    print("\n=== Variant Exploration System Orchestrator ===\n")

    # Load files
    state = load_json(STATE_FILE, {})
    agent_map = load_json(AGENT_MAP_FILE, {})

    while state['current_phase'] <= 13:
        phase = state['current_phase']
        agent = agent_map.get(str(phase), 'Unknown Agent')
        phase_name = state.get('phase_name', f'Phase {phase}')
        print(f"[Phase {phase}] {phase_name} — Assigned to: {agent}")
        print(f"→ Please complete the artifact for this phase before continuing.")

        user_input = input("Confirm completion (y/n)? ").strip().lower()
        if user_input == 'y':
            comment = input("Optional comment: ").strip()
            log_action(agent, phase, "approved", comment or "Phase approved.")
            print(f"✅ Phase {phase} approved. Moving to next phase...\n")
            state = advance_phase(state)
            state['status'] = 'in_progress'
            state['last_action'] = f'Phase {phase} approved'
            save_json(STATE_FILE, state)
        else:
            log_action(agent, phase, "paused", "User chose to pause.")
            state['status'] = 'paused'
            save_json(STATE_FILE, state)
            print("⏸ Workflow paused. Complete artifact and rerun orchestrator to resume.")
            break

    if state['current_phase'] > 13:
        print("🎯 All phases complete! Workflow finished.")
        state['status'] = 'completed'
        save_json(STATE_FILE, state)
        log_action('Orchestrator', 13, 'completed', 'Workflow finished.')

if __name__ == '__main__':
    run_orchestrator()
