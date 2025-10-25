"""
config_utils.py
----------------
Shared configuration loading utilities.

Eliminates duplication across:
- reddit_connector.py
- youtube_connector.py
- x_connector.py
- demand_validator.py
- subagent_triggers.py

Usage:
    from src.utils.config_utils import load_config

    config = load_config(
        config_path="config/my_config.json",
        default_config={"key": "default_value"}
    )
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


def load_config(
    config_path: str,
    default_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Load JSON configuration file with fallback to defaults.

    Args:
        config_path: Path to JSON config file
        default_config: Default config to use if file not found

    Returns:
        Configuration dictionary

    Examples:
        >>> config = load_config("config.json", {"timeout": 30})
        >>> config = load_config("config.json")  # Returns {} if not found
    """
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            print(f"⚠️  Config file not found: {config_path}")
            return default_config or {}

    except json.JSONDecodeError as e:
        print(f"⚠️  Invalid JSON in {config_path}: {e}")
        return default_config or {}

    except Exception as e:
        print(f"⚠️  Error loading config from {config_path}: {e}")
        return default_config or {}


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary
        config_path: Path to save JSON file

    Returns:
        True if successful, False otherwise

    Examples:
        >>> save_config({"timeout": 30}, "config.json")
        True
    """
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        return True

    except Exception as e:
        print(f"⚠️  Error saving config to {config_path}: {e}")
        return False
