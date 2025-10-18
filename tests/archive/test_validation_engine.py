"""
Test Suite: Validation Engine (PRD-06)
Tests artifact validation and error handling logic.
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "variant_exploration_system" / "orchestrator"))

from orchestrator_core import validate_artifact, VALIDATION_ERROR_FILE, SCHEMA_DIR

def test_validation_directories_exist():
    """Test validation directories exist"""
    assert VALIDATION_ERROR_FILE.parent.exists(), "Logs directory should exist"
    assert SCHEMA_DIR.exists(), "Schema directory should exist"

def test_validation_non_json_file():
    """Test validation skips non-JSON files"""
    # Create temporary non-JSON file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Not a JSON file")
        temp_path = f.name

    try:
        is_valid, error = validate_artifact(temp_path)
        assert is_valid is True, "Non-JSON files should pass validation"
        assert error is None, "No error should be returned"
    finally:
        os.unlink(temp_path)

def test_validation_nonexistent_file():
    """Test validation of non-existent file"""
    is_valid, error = validate_artifact("/nonexistent/file.json")
    assert is_valid is True, "Non-existent files should pass (skip validation)"
    assert error is None

def test_validation_no_schema():
    """Test validation when no schema exists"""
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump({"test": "data"}, f)
        temp_path = f.name

    try:
        is_valid, error = validate_artifact(temp_path)
        assert is_valid is True, "Should pass when no schema exists"
        assert error is None
    finally:
        os.unlink(temp_path)

def test_validation_valid_artifact():
    """Test validation of valid artifact against schema"""
    # Create temporary schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"}
        },
        "required": ["name"]
    }

    # Create temporary artifact that matches schema
    artifact = {
        "name": "Test Artifact",
        "score": 8.5
    }

    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_schema.json') as schema_file:
        json.dump(schema, schema_file)
        schema_path = schema_file.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', dir=Path(schema_path).parent) as artifact_file:
        json.dump(artifact, artifact_file)
        artifact_path = artifact_file.name

    try:
        # Copy schema to SCHEMA_DIR with matching name
        schema_name = Path(artifact_path).stem + "_schema.json"
        target_schema = SCHEMA_DIR / schema_name

        # Ensure SCHEMA_DIR exists
        SCHEMA_DIR.mkdir(exist_ok=True, parents=True)

        import shutil
        shutil.copy2(schema_path, target_schema)

        # Validate
        is_valid, error = validate_artifact(artifact_path)
        assert is_valid is True, "Valid artifact should pass validation"
        assert error is None

        # Clean up
        target_schema.unlink()

    finally:
        os.unlink(schema_path)
        os.unlink(artifact_path)

def test_validation_invalid_artifact():
    """Test validation of invalid artifact against schema"""
    # Create temporary schema
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"}
        },
        "required": ["name"]
    }

    # Create artifact that VIOLATES schema (name is number instead of string)
    artifact = {
        "name": 12345,  # Should be string!
        "score": 8.5
    }

    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_schema.json') as schema_file:
        json.dump(schema, schema_file)
        schema_path = schema_file.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', dir=Path(schema_path).parent) as artifact_file:
        json.dump(artifact, artifact_file)
        artifact_path = artifact_file.name

    try:
        # Copy schema to SCHEMA_DIR
        schema_name = Path(artifact_path).stem + "_schema.json"
        target_schema = SCHEMA_DIR / schema_name

        SCHEMA_DIR.mkdir(exist_ok=True, parents=True)
        import shutil
        shutil.copy2(schema_path, target_schema)

        # Validate
        is_valid, error = validate_artifact(artifact_path)
        assert is_valid is False, "Invalid artifact should fail validation"
        assert error is not None, "Error message should be returned"
        assert "type" in error.lower() or "string" in error.lower(), "Error should mention type mismatch"

        # Check error was logged
        if VALIDATION_ERROR_FILE.exists():
            with open(VALIDATION_ERROR_FILE, 'r') as f:
                errors = json.load(f)
            assert len(errors) > 0, "Validation error should be logged"
            latest_error = errors[-1]
            assert 'timestamp' in latest_error
            assert 'artifact' in latest_error
            assert 'schema' in latest_error
            assert 'message' in latest_error

        # Clean up
        target_schema.unlink()

    finally:
        os.unlink(schema_path)
        os.unlink(artifact_path)

def test_validation_missing_required_field():
    """Test validation when required field is missing"""
    # Schema with required field
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "score": {"type": "number"}
        },
        "required": ["name", "score"]  # Both required
    }

    # Artifact missing 'score'
    artifact = {
        "name": "Test"
        # score is missing!
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_schema.json') as schema_file:
        json.dump(schema, schema_file)
        schema_path = schema_file.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', dir=Path(schema_path).parent) as artifact_file:
        json.dump(artifact, artifact_file)
        artifact_path = artifact_file.name

    try:
        schema_name = Path(artifact_path).stem + "_schema.json"
        target_schema = SCHEMA_DIR / schema_name

        SCHEMA_DIR.mkdir(exist_ok=True, parents=True)
        import shutil
        shutil.copy2(schema_path, target_schema)

        is_valid, error = validate_artifact(artifact_path)
        assert is_valid is False, "Missing required field should fail"
        assert error is not None
        assert "score" in error.lower() or "required" in error.lower(), "Error should mention missing field"

        target_schema.unlink()

    finally:
        os.unlink(schema_path)
        os.unlink(artifact_path)

def test_jsonschema_library():
    """Test that jsonschema library works correctly"""
    from jsonschema import validate, ValidationError

    # Valid case
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    valid_data = {"name": "test"}
    validate(instance=valid_data, schema=schema)  # Should not raise

    # Invalid case
    invalid_data = {"name": 123}
    with pytest.raises(ValidationError):
        validate(instance=invalid_data, schema=schema)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
