#!/usr/bin/env python3
# =====================================================
# Variant Exploration System (VES) — Orchestrator Core v3
# =====================================================
# Includes PRD‑05 (Audit Layer) + PRD‑06 (Validation Engine)
# Guided Governance Mode — validation required or explicit override.
# =====================================================

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from validation_engine import validate_artifact

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = BASE_DIR / 'state' / 'state_schema.json'
LOG_FILE = BASE_DIR / 'logs' / 'audit_trail.json'
CSV_FILE = BASE_DIR / 'logs' / 'audit_trail.csv'
ARCHIVE_DIR = BASE_DIR / 'logs' / 'archive'
AGENT_MAP_FILE = BASE_DIR / 'config' / 'phase_agent_map.json'
SCHEMA_DIR = BASE_DIR / 'schema'

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
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def export_csv(logs):
    import csv
    keys = ['timestamp','user','agent','phase','action','file_changed','hash','comment','override','validation_passed']
    with open(CSV_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for row in logs:
            writer.writerow({k: row.get(k, '') for k in keys})

def archive_artifact(file_path):
    if not os.path.exists(file_path):
        return None
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H%M%S')
    archive_folder = ARCHIVE_DIR / timestamp
    archive_folder.mkdir(parents=True, exist_ok=True)
    dest = archive_folder / os.path.basename(file_path)
    shutil.copy2(file_path, dest)
    return dest

def log_action(agent, phase, action, comment, file_changed=None, override=False, validation_passed=None):
    logs = load_json(LOG_FILE, [])
    user = os.getenv('USER', 'Rob')
    hash_val = file_hash(file_changed) if file_changed else None
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "agent": agent,
        "phase": phase,
        "action": action,
        "file_changed": str(file_changed) if file_changed else "",
        "hash": hash_val or "",
        "comment": comment or "",
        "override": override,
        "validation_passed": validation_passed
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
    print("\n=== Variant Exploration System Orchestrator (v3 — Guided Governance) ===\n")
    state = load_json(STATE_FILE, {})
    agent_map = load_json(AGENT_MAP_FILE, {})

    while state['current_phase'] <= 13:
        phase = state['current_phase']
        agent = agent_map.get(str(phase), 'Unknown Agent')
        phase_name = state.get('phase_name', f'Phase {phase}')
        print(f"[Phase {phase}] {phase_name} — Assigned to: {agent}")
        print(f"→ Complete the artifact for this phase before continuing.")

        artifact_path = input("Enter artifact file path (relative or full): ").strip()
        if not artifact_path or not os.path.exists(artifact_path):
            print("⚠️ Warning: File not found. Continue anyway?")
            cont = input("Proceed (y/n)? ").lower()
            if cont != 'y':
                print("⏸ Aborted. File must exist or path corrected.")
                break

        # -------- Validation Step --------
        schema_path = SCHEMA_DIR / f"phase_{phase}.json"
        validation_passed = False

        if schema_path.exists():
            print(f"🔍 Running validation for {artifact_path} against {schema_path} ...")
            validation_passed = validate_artifact(artifact_path, schema_path, auto_repair=False)
        else:
            print(f"⚠️ No schema found for Phase {phase}, skipping validation.")
            validation_passed = True

        if not validation_passed:
            print("❌ Validation failed.")
            override = input("Override and continue? (y/n): ").strip().lower() == 'y'
            if override:
                justification = input("Enter justification for override: ").strip()
                log_action(agent, phase, "override_approval", justification, artifact_path, override=True, validation_passed=False)
                print("⚠️ Override accepted; proceeding under human review.")
            else:
                log_action(agent, phase, "validation_failed", "Phase halted due to validation error.", artifact_path, override=False, validation_passed=False)
                print("🚫 Phase halted; fix validation errors before continuing.")
                break
        else:
            print("✅ Validation passed. Proceeding to approval stage.")

        confirm = input("Confirm final approval (y/n)? ").strip().lower()
        if confirm == 'y':
            comment = input("Optional comment: ").strip()
            log_action(agent, phase, "approved", comment, artifact_path, override=False, validation_passed=validation_passed)
            print(f"✅ Phase {phase} approved. Moving to next phase...\n")
            state = advance_phase(state)
            state['status'] = 'in_progress'
            state['last_action'] = f'Phase {phase} approved'
            save_json(STATE_FILE, state)
        else:
            log_action(agent, phase, "paused", "User chose to pause.", artifact_path)
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
