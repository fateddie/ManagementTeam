"""
MAINTENANCE TASKS – AI MANAGEMENT TEAM SYSTEM
Version: 1.0
Date: 2025-10-08
Maintainer: Founder (Rob)

Purpose:
    Automate routine cleanup, summaries, and integrity checks for the
    AI Management-Team repository. Run weekly or on-demand.

Features:
    • Archive old logs
    • Summarize agent memory files
    • Sync dependencies
    • Validate project folder structure
    • Produce maintenance report

Usage:
    python scripts/maintenance_tasks.py
"""

import os
import json
import datetime
import shutil
import subprocess
from pathlib import Path

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
LOG_DIR = BASE_DIR / "logs"
MEMORY_DIR = BASE_DIR / "memory"
ARCHIVE_DIR = BASE_DIR / "docs" / "system" / "archive"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"
STRUCTURE_FILE = BASE_DIR / "docs" / "system" / "file_structure.md"
REPORT_FILE = BASE_DIR / "logs" / f"maintenance_report_{datetime.date.today()}.txt"

# Number of days before logs are archived
LOG_RETENTION_DAYS = 14
# Max number of project records to keep in each memory file
MEMORY_RECORD_LIMIT = 10


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------
def log_message(message: str):
    """Print and append to maintenance report."""
    print(message)
    with open(REPORT_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")


# ------------------------------------------------------------
# 1️⃣ CLEANUP OLD LOGS
# ------------------------------------------------------------
def archive_old_logs():
    """Move old logs (> LOG_RETENTION_DAYS) to archive folder."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=LOG_RETENTION_DAYS)

    count = 0
    for file in LOG_DIR.glob("*.jsonl"):
        mtime = datetime.datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff_date:
            shutil.move(str(file), ARCHIVE_DIR / file.name)
            count += 1

    log_message(f"🧹 Archived {count} old logs older than {LOG_RETENTION_DAYS} days.")


# ------------------------------------------------------------
# 2️⃣ SUMMARIZE MEMORY FILES
# ------------------------------------------------------------
def summarize_memory():
    """Trim memory files and create summarized snapshots."""
    summary_count = 0
    for mem_file in MEMORY_DIR.glob("*.json"):
        with open(mem_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        history = data.get("project_history", [])
        if len(history) > MEMORY_RECORD_LIMIT:
            data["project_history"] = history[-MEMORY_RECORD_LIMIT:]
            summary_count += 1

        # Add lightweight summary for quick reference
        data["summary_snapshot"] = {
            "total_records": len(history),
            "recent_projects": [h["project"] for h in data["project_history"][-3:]],
            "last_updated": data.get("last_updated"),
        }

        with open(mem_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    log_message(f"🧠 Summarized and trimmed {summary_count} memory files.")


# ------------------------------------------------------------
# 3️⃣ SYNC DEPENDENCIES
# ------------------------------------------------------------
def sync_dependencies():
    """Update requirements.txt with current environment packages."""
    try:
        output = subprocess.check_output(["pip", "freeze"], text=True)
        with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as f:
            f.write(output)
        log_message("📦 Dependencies synced with current virtual environment.")
    except Exception as e:
        log_message(f"⚠️ Dependency sync failed: {e}")


# ------------------------------------------------------------
# 4️⃣ VALIDATE FILE STRUCTURE
# ------------------------------------------------------------
def validate_structure():
    """Ensure all critical folders and docs exist."""
    required_dirs = [
        "src", "docs/system", "memory", "logs", "config", "scripts"
    ]
    missing = [d for d in required_dirs if not (BASE_DIR / d).exists()]

    if missing:
        log_message(f"⚠️ Missing folders detected: {missing}")
        for d in missing:
            (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
            log_message(f"   → Created missing directory: {d}")
    else:
        log_message("✅ All critical directories verified.")

    # Validate structure file exists
    if not STRUCTURE_FILE.exists():
        log_message("⚠️ file_structure.md missing — recreating placeholder.")
        STRUCTURE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STRUCTURE_FILE, "w", encoding="utf-8") as f:
            f.write("# FILE STRUCTURE – Placeholder recreated by maintenance script.\n")

    log_message("📁 Project structure validated.")


# ------------------------------------------------------------
# 5️⃣ RUN MAINTENANCE
# ------------------------------------------------------------
def run_maintenance():
    start_time = datetime.datetime.now()
    log_message(f"\n🧩 Starting maintenance cycle: {start_time.isoformat()}\n")

    archive_old_logs()
    summarize_memory()
    sync_dependencies()
    validate_structure()

    end_time = datetime.datetime.now()
    log_message(f"\n✅ Maintenance completed at {end_time.isoformat()}")
    log_message(f"⏱ Duration: {(end_time - start_time).seconds} seconds\n")


if __name__ == "__main__":
    run_maintenance()

