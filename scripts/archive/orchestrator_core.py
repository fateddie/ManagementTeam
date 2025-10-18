#!/usr/bin/env python3
import json
import os
import hashlib
import shutil
from datetime import datetime

# ----------------------------------------------------
# Variant Exploration System — Orchestrator Core v2
# Includes PRD-05 Audit & Logging Layer Enhancements
# ----------------------------------------------------
# Key Features:
#  - Structured audit trail (JSON + CSV)
#  - SHA-256 artifact hashing for integrity
#  - Automatic archiving of changed artifacts
#  - Real-time CSV export for analysis
# ----------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, 'state', 'state_schema.json')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'audit_trail.json')
CSV_FILE = os.path.join(BASE_DIR, 'logs', 'audit_trail.csv')
ARCHIVE_DIR = os.path.join(BASE_DIR, 'logs', 'archive')
AGENT_MAP_FILE = os.path.join(BASE_DIR, 'config', 'phase_agent_map.json')

os.makedirs(ARCHIVE_DIR, exist_ok=True)

# ---------- Utility Functions ----------

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def file_hash(path):
    """Compute SHA-256 hash of a file for integrity verification."""
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def export_csv(logs):
    """Sync the audit trail JSON into CSV format."""
    import csv
    keys = ['timestamp','user','agent','phase','action','file_changed','hash','comment']
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in logs:
            writer.writerow({k: row.get(k, '') for k in keys})

def archive_artifact(file_path):
    """Archive artifact to timestamped folder in /logs/archive."""
    if not os.path.exists(file_path):
        return None
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H%M%S')
    archive_folder = os.path.join(ARCHIVE_DIR, timestamp)
    os.makedirs(archive_folder, exist_ok=True)
    dest = os.path.join(archive_folder, os.path.basename(file_path))
    shutil.copy2(file_path, dest)
    return dest

def log_action(agent, phase, action, comment, file_changed=None):
    logs = load_json(LOG_FILE, [])
    user = os.getenv('USER', 'Rob')
    hash_val = file_hash(file_changed) if file_changed else None
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "agent": agent,
        "phase": phase,
        "action": action,
        "file_changed": file_changed or "",
        "hash": hash_val or "",
        "comment": comment or ""
    }
    logs.append(entry)
    save_json(LOG_FILE, logs)
    export_csv(logs)

    if file_changed and os.path.exists(file_changed):
        archive_path = archive_artifact(file_changed)
        print(f"📦 Archived artifact to: {archive_path}")

def advance_phase(state):
    state['current_phase'] += 1
    state['next_phase'] = state['current_phase'] + 1
    return state

# ---------- Main Orchestrator Loop ----------

def run_orchestrator():
    print("\n=== Variant Exploration System Orchestrator (Enhanced) ===\n")
    state = load_json(STATE_FILE, {})
    agent_map = load_json(AGENT_MAP_FILE, {})

    while state['current_phase'] <= 13:
        phase = state['current_phase']
        agent = agent_map.get(str(phase), 'Unknown Agent')
        phase_name = state.get('phase_name', f'Phase {phase}')
        print(f"[Phase {phase}] {phase_name} — Assigned to: {agent}")
        print(f"→ Complete the artifact for this phase before continuing.")

        # Ask for artifact path
        artifact_path = input("Enter artifact file path (relative or full): ").strip()
        if artifact_path and not os.path.exists(artifact_path):
            print("⚠️ Warning: File not found. Continue anyway?")
            cont = input("Proceed (y/n)? ").lower()
            if cont != 'y':
                print("⏸ Aborted. File must exist or path corrected.")
                break

        confirm = input("Confirm completion (y/n)? ").strip().lower()
        if confirm == 'y':
            comment = input("Optional comment: ").strip()
            log_action(agent, phase, "approved", comment, artifact_path)
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
