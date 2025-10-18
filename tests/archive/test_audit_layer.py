"""
Test Suite: Audit Layer Integrity (PRD-05)
Verifies JSON/CSV logging, file hashing, and archive creation.
"""

import json
import os
import csv
import hashlib
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "variant_exploration_system" / "orchestrator"))

from orchestrator_core import (
    compute_hash, archive_artifact, log_action,
    LOGS_DIR, ARCHIVE_DIR, AUDIT_FILE, AUDIT_CSV_FILE
)

def test_directories_exist():
    """Test all required directories exist"""
    assert LOGS_DIR.exists(), "Logs directory missing"
    assert ARCHIVE_DIR.exists(), "Archive directory missing"

def test_audit_json_structure():
    """Test audit JSON has correct structure"""
    if AUDIT_FILE.exists():
        with open(AUDIT_FILE, 'r') as f:
            logs = json.load(f)
        assert isinstance(logs, list), "Audit log should be a list"

        if logs:
            entry = logs[-1]
            required_fields = ['timestamp', 'agent', 'phase', 'action', 'variant', 'notes']
            assert all(k in entry for k in required_fields), f"Missing required fields in audit log"

def test_audit_csv_structure():
    """Test audit CSV has correct headers"""
    if AUDIT_CSV_FILE.exists():
        with open(AUDIT_CSV_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            expected_headers = [
                'timestamp', 'variant', 'phase', 'agent', 'action',
                'notes', 'file_changed', 'hash', 'archived_to'
            ]
            assert headers == expected_headers, f"CSV headers don't match. Got: {headers}"

def test_compute_hash():
    """Test SHA-256 hash computation"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content for hashing")
        temp_path = f.name

    try:
        # Compute hash
        file_hash = compute_hash(temp_path)

        # Verify hash format
        assert file_hash is not None, "Hash should not be None"
        assert len(file_hash) == 64, "SHA-256 hash should be 64 characters"
        assert all(c in '0123456789abcdef' for c in file_hash), "Hash should be hex"

        # Verify consistency
        hash2 = compute_hash(temp_path)
        assert file_hash == hash2, "Same file should produce same hash"

    finally:
        os.unlink(temp_path)

def test_compute_hash_nonexistent():
    """Test hash computation for non-existent file"""
    result = compute_hash("/nonexistent/file.txt")
    assert result is None, "Hash of non-existent file should be None"

def test_archive_artifact():
    """Test artifact archiving"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"test": "data"}, f)
        temp_path = f.name

    try:
        # Archive the file
        archive_path = archive_artifact(temp_path)

        # Verify archive was created
        assert archive_path is not None, "Archive path should not be None"
        assert Path(archive_path).exists(), "Archive file should exist"

        # Verify content matches
        with open(temp_path, 'r') as f1, open(archive_path, 'r') as f2:
            assert f1.read() == f2.read(), "Archive content should match original"

    finally:
        os.unlink(temp_path)

def test_log_action_basic():
    """Test basic action logging"""
    # Clear existing logs
    if AUDIT_FILE.exists():
        initial_count = len(json.load(open(AUDIT_FILE)))
    else:
        initial_count = 0

    # Log an action
    log_action(
        variant="test_variant",
        phase=1,
        agent="TestAgent",
        action="test_action",
        notes="Testing logging"
    )

    # Verify log was added
    with open(AUDIT_FILE, 'r') as f:
        logs = json.load(f)

    assert len(logs) == initial_count + 1, "New log entry should be added"

    latest = logs[-1]
    assert latest['variant'] == "test_variant"
    assert latest['phase'] == 1
    assert latest['agent'] == "TestAgent"
    assert latest['action'] == "test_action"
    assert latest['notes'] == "Testing logging"
    assert 'timestamp' in latest

def test_log_action_with_file():
    """Test action logging with file hash and archive"""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"test": "data"}, f)
        temp_path = f.name

    try:
        # Log action with file
        log_action(
            variant="test_variant",
            phase=2,
            agent="TestAgent",
            action="file_changed",
            notes="Testing file logging",
            file_changed=temp_path
        )

        # Verify log includes hash and archive info
        with open(AUDIT_FILE, 'r') as f:
            logs = json.load(f)

        latest = logs[-1]
        assert 'hash' in latest, "Log should include hash"
        assert 'archived_to' in latest, "Log should include archive path"
        assert latest['file_changed'] == temp_path
        assert len(latest['hash']) == 64, "Hash should be 64 characters"

        # Verify archived file exists
        assert Path(latest['archived_to']).exists(), "Archived file should exist"

    finally:
        os.unlink(temp_path)

def test_csv_and_json_consistency():
    """Test CSV and JSON logs stay in sync"""
    # Count entries
    json_count = len(json.load(open(AUDIT_FILE))) if AUDIT_FILE.exists() else 0

    csv_count = 0
    if AUDIT_CSV_FILE.exists():
        with open(AUDIT_CSV_FILE, 'r', newline='') as f:
            csv_count = sum(1 for _ in csv.DictReader(f))

    # They should match (or CSV might have 0 if headers-only)
    assert json_count == csv_count or csv_count == 0, "JSON and CSV logs should have same count"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
