#!/usr/bin/env python3
# =====================================================
# Variant Exploration System (VES) — Validation Engine
# =====================================================
# Implements schema-based artifact validation per PRD‑06.
# Ensures that all artifacts meet defined structural rules
# before being approved by the orchestrator.
#
# Features:
#  • Schema-based validation using jsonschema
#  • Validation error logging (JSON + console)
#  • Optional auto-repair for missing optional fields
#  • Integration-ready with orchestrator_core.py
# =====================================================

import json
import os
from jsonschema import validate, ValidationError
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
SCHEMA_DIR = BASE_DIR / "schema"
ERROR_LOG = LOGS_DIR / "validation_errors.json"

os.makedirs(LOGS_DIR, exist_ok=True)


def load_json(path):
    """Load a JSON file safely."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def log_error(artifact_path, schema_name, message):
    """Log a validation error to /logs/validation_errors.json."""
    if ERROR_LOG.exists():
        with open(ERROR_LOG, "r") as f:
            errors = json.load(f)
    else:
        errors = []

    errors.append({
        "timestamp": datetime.utcnow().isoformat(),
        "artifact": str(artifact_path),
        "schema": schema_name,
        "message": message
    })

    save_json(ERROR_LOG, errors)


def validate_artifact(artifact_path, schema_path, auto_repair=False):
    """Validate a JSON artifact against its schema."""
    try:
        artifact = load_json(artifact_path)
        schema = load_json(schema_path)
    except Exception as e:
        log_error(artifact_path, schema_path, f"Load error: {str(e)}")
        return False

    try:
        validate(instance=artifact, schema=schema)
        print(f"✅ Validation passed for {artifact_path}")
        return True
    except ValidationError as e:
        print(f"❌ Validation failed for {artifact_path}: {e.message}")
        log_error(artifact_path, os.path.basename(schema_path), e.message)

        if auto_repair:
            repaired = _attempt_autofix(artifact, schema)
            with open(artifact_path, "w") as f:
                json.dump(repaired, f, indent=2)
            print(f"🛠 Auto-repair applied to {artifact_path}")
        return False


def _attempt_autofix(artifact, schema):
    """Try to fill in missing optional fields with defaults."""
    if "properties" not in schema:
        return artifact

    repaired = artifact.copy()
    for key, rule in schema["properties"].items():
        if key not in repaired:
            if "default" in rule:
                repaired[key] = rule["default"]
            elif rule.get("type") == "string":
                repaired[key] = ""
            elif rule.get("type") == "number":
                repaired[key] = 0
            elif rule.get("type") == "array":
                repaired[key] = []
    return repaired


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate artifact against schema.")
    parser.add_argument("--artifact", required=True, help="Path to artifact JSON file")
    parser.add_argument("--schema", required=True, help="Path to schema JSON file")
    parser.add_argument("--auto-repair", action="store_true", help="Enable auto repair")
    args = parser.parse_args()

    success = validate_artifact(args.artifact, args.schema, auto_repair=args.auto_repair)
    if not success:
        print("🚫 Validation failed — see logs/validation_errors.json for details.")
    else:
        print("🎯 Validation successful.")
