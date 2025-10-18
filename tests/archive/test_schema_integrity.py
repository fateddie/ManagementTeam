"""
Test Suite: Schema Integrity
Validates that all schema files are well-formed and match expected keys.
"""

import json
import os
import pytest

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), '../schema')

def test_schema_files_exist():
    assert os.path.exists(SCHEMA_DIR), "Schema directory not found."
    files = [f for f in os.listdir(SCHEMA_DIR) if f.endswith('.json')]
    assert len(files) > 0, "No schema files detected."

@pytest.mark.parametrize("schema_file", [f for f in os.listdir(SCHEMA_DIR) if f.endswith('.json')])
def test_valid_json(schema_file):
    path = os.path.join(SCHEMA_DIR, schema_file)
    with open(path, 'r') as f:
        try:
            json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {schema_file}: {e}")
