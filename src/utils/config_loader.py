# ==============================================
# file: /ManagementTeam/src/utils/config_loader.py
# ==============================================
"""
Central Configuration Loader
-----------------------------
Ensures all agents and utilities load environment variables
from the central config/.env file.

Usage in any module:
    from src.utils.config_loader import load_env, get_env
    
    load_env()  # Call once at module start
    api_key = get_env("PERPLEXITY_API_KEY")
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


# Determine project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / "config" / ".env"
ENV_EXAMPLE = PROJECT_ROOT / "config" / ".env.example"

# Track if environment has been loaded
_ENV_LOADED = False


def load_env(force_reload: bool = False) -> bool:
    """
    Load environment variables from central config/.env file.
    
    Args:
        force_reload: Force reload even if already loaded
        
    Returns:
        True if .env was loaded, False if file not found
    """
    global _ENV_LOADED
    
    if _ENV_LOADED and not force_reload:
        return True
    
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE, override=True)
        _ENV_LOADED = True
        return True
    else:
        # Try to create from example
        if ENV_EXAMPLE.exists() and not ENV_FILE.exists():
            import shutil
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            load_dotenv(dotenv_path=ENV_FILE, override=True)
            _ENV_LOADED = True
            print(f"⚠️  Created config/.env from template. Please update with your API keys!")
            return True
        
        print(f"⚠️  Warning: {ENV_FILE} not found. Environment variables not loaded.")
        return False


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get an environment variable with optional validation.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: Raise error if not found and no default
        
    Returns:
        Environment variable value or default
        
    Raises:
        ValueError: If required=True and variable not found
    """
    # Ensure env is loaded
    load_env()
    
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(
            f"Required environment variable '{key}' not found. "
            f"Please set it in {ENV_FILE}"
        )
    
    return value


def get_project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


def get_config_dir() -> Path:
    """Get the config directory."""
    return PROJECT_ROOT / "config"


def is_env_loaded() -> bool:
    """Check if environment variables have been loaded."""
    return _ENV_LOADED


def validate_required_keys(keys: list[str]) -> dict[str, bool]:
    """
    Validate that required environment variables are set.
    
    Args:
        keys: List of required variable names
        
    Returns:
        Dictionary mapping keys to whether they're set
    """
    load_env()
    
    results = {}
    for key in keys:
        value = os.getenv(key)
        results[key] = value is not None and value != "" and "your-" not in value
    
    return results


def print_env_status():
    """Print status of key environment variables (without revealing values)."""
    load_env()
    
    print("\n" + "=" * 70)
    print("🔑 ENVIRONMENT VARIABLES STATUS")
    print("=" * 70)
    
    important_keys = [
        "PERPLEXITY_API_KEY",
        "MEM0_API_KEY",
        "OPENAI_API_KEY",
        "PROJECT_NAME",
        "ENVIRONMENT",
    ]
    
    status = validate_required_keys(important_keys)
    
    for key, is_set in status.items():
        icon = "✅" if is_set else "❌"
        value_display = "Set" if is_set else "Not set"
        print(f"{icon} {key:25} : {value_display}")
    
    print("=" * 70)
    print(f"📁 Config file: {ENV_FILE}")
    print(f"📋 Example file: {ENV_EXAMPLE}")
    print("=" * 70 + "\n")


# Auto-load on import
load_env()

