# ==============================================
# file: /ManagementTeam/src/utils/validation_utils.py
# ==============================================
from __future__ import annotations
from typing import List
import yaml


def safe_load_yaml(text: str) -> dict:
    """
    Safely load YAML text into a dictionary.
    
    Args:
        text: YAML-formatted string
        
    Returns:
        Dictionary representation of YAML
    """
    return yaml.safe_load(text) or {}


def validate_yaml_structure(text: str, required_top_keys: List[str] | None = None) -> None:
    """
    Validate that YAML text contains required top-level keys.
    
    Args:
        text: YAML-formatted string
        required_top_keys: List of required top-level keys
        
    Raises:
        ValueError: If required keys are missing
    """
    data = safe_load_yaml(text)
    required_top_keys = required_top_keys or []
    missing = [k for k in required_top_keys if k not in data]
    if missing:
        raise ValueError(f"YAML validation failed; missing keys: {missing}")

