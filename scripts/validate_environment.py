#!/usr/bin/env python3
# ==============================================
# file: /ManagementTeam/scripts/validate_environment.py
# ==============================================
"""
Environment Validation Script
------------------------------
Validates that all environment variables are properly configured
and that the central config/.env file is being loaded correctly.

Usage:
    python scripts/validate_environment.py
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config_loader import (
    load_env,
    get_env,
    is_env_loaded,
    validate_required_keys,
    print_env_status,
    get_project_root,
    get_config_dir
)


def main():
    """Run comprehensive environment validation."""
    print("\n" + "=" * 70)
    print("🔍 ENVIRONMENT VALIDATION")
    print("=" * 70 + "\n")
    
    # Test 1: Check if .env file exists
    print("📋 Test 1: Checking config/.env file...")
    env_file = get_config_dir() / ".env"
    env_example = get_config_dir() / ".env.example"
    
    if env_file.exists():
        print(f"✅ Found: {env_file}")
    else:
        print(f"❌ Missing: {env_file}")
        if env_example.exists():
            print(f"💡 Template available at: {env_example}")
            print(f"💡 Run: cp config/.env.example config/.env")
        return False
    
    # Test 2: Load environment
    print("\n📋 Test 2: Loading environment variables...")
    success = load_env(force_reload=True)
    
    if success:
        print("✅ Environment loaded successfully")
    else:
        print("❌ Failed to load environment")
        return False
    
    # Test 3: Verify env is loaded
    print("\n📋 Test 3: Verifying environment state...")
    if is_env_loaded():
        print("✅ Environment marked as loaded")
    else:
        print("❌ Environment not marked as loaded")
        return False
    
    # Test 4: Check required keys
    print("\n📋 Test 4: Validating required keys...")
    required_keys = [
        "PROJECT_NAME",
        "ENVIRONMENT",
        "MANAGEMENT_TEAM_ROOT",
    ]
    
    optional_keys = [
        "PERPLEXITY_API_KEY",
        "MEM0_API_KEY",
        "OPENAI_API_KEY",
        "SLACK_WEBHOOK_URL",
    ]
    
    print("\n🔑 Required Keys:")
    required_status = validate_required_keys(required_keys)
    all_required_set = True
    for key, is_set in required_status.items():
        icon = "✅" if is_set else "❌"
        print(f"  {icon} {key}")
        if not is_set:
            all_required_set = False
    
    print("\n🔑 Optional Keys (for advanced features):")
    optional_status = validate_required_keys(optional_keys)
    for key, is_set in optional_status.items():
        icon = "✅" if is_set else "⚪"
        status = "Set" if is_set else "Not set"
        print(f"  {icon} {key:25} : {status}")
    
    # Test 5: Test get_env function
    print("\n📋 Test 5: Testing config_loader functions...")
    try:
        project_name = get_env("PROJECT_NAME", default="AI_Management_Team")
        print(f"✅ get_env() works: PROJECT_NAME = {project_name}")
    except Exception as e:
        print(f"❌ get_env() failed: {e}")
        return False
    
    # Test 6: Test required parameter
    print("\n📋 Test 6: Testing required parameter...")
    try:
        # This should work
        project = get_env("PROJECT_NAME", required=True)
        print(f"✅ Required key test passed: {project}")
    except ValueError as e:
        print(f"❌ Required key test failed: {e}")
    
    try:
        # This should fail gracefully
        fake_key = get_env("NONEXISTENT_KEY", required=False)
        print(f"✅ Optional key test passed: {fake_key}")
    except Exception as e:
        print(f"❌ Optional key test failed unexpectedly: {e}")
    
    # Final status
    print("\n" + "=" * 70)
    print("📊 FINAL STATUS")
    print("=" * 70)
    print_env_status()
    
    if all_required_set:
        print("\n✅ ALL TESTS PASSED - Environment is properly configured!")
        print("\n🎯 You're ready to:")
        print("   • Run the Planner Agent")
        print("   • Use Perplexity research (if API key set)")
        print("   • Execute any agent in the system")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED - Please fix configuration issues above")
        print("\n💡 Next steps:")
        print("   1. Edit config/.env")
        print("   2. Add missing required variables")
        print("   3. Run this script again")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

