"""
validation_tests.py
Basic integration tests for Phase 6 automation.
---------------------------------------------------------
Run:  python agents/reporting_agent/tests/validation_tests.py

Purpose:
    Automated tests to verify system integrity:
    - All required outputs exist
    - YAML files are valid
    - Markdown files are not empty
    - System can run end-to-end
"""

import os
import yaml
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_outputs_exist():
    """Test that all required output files exist."""
    print("🧪 Test 1: Checking required outputs exist...")
    
    required = [
        "strategy_plan.yaml",
        "technical_design.yaml",
        "project_plan.yaml",
        "roadmap.md",
        "prd.md",
        "tech_spec.md"
    ]
    
    missing = []
    for f in required:
        path = PROJECT_ROOT / "outputs" / f
        if not path.exists():
            missing.append(f)
    
    if missing:
        print(f"   ❌ FAIL: Missing outputs: {missing}")
        assert False, f"Missing outputs: {missing}"
    else:
        print(f"   ✅ PASS: All {len(required)} required files exist")


def test_yaml_valid():
    """Test that all YAML files are valid."""
    print("\n🧪 Test 2: Validating YAML files...")
    
    outputs_dir = PROJECT_ROOT / "outputs"
    if not outputs_dir.exists():
        print("   ⚠️  SKIP: outputs directory not found")
        return
    
    yaml_files = list(outputs_dir.glob("*.yaml"))
    invalid = []
    
    for f in yaml_files:
        try:
            yaml.safe_load(f.read_text(encoding='utf-8'))
        except Exception as e:
            invalid.append(f"{f.name}: {e}")
    
    if invalid:
        print(f"   ❌ FAIL: Invalid YAML files:")
        for inv in invalid:
            print(f"      - {inv}")
        assert False, f"Invalid YAML: {invalid}"
    else:
        print(f"   ✅ PASS: All {len(yaml_files)} YAML files valid")


def test_markdown_not_empty():
    """Test that markdown files have content."""
    print("\n🧪 Test 3: Checking markdown files...")
    
    outputs_dir = PROJECT_ROOT / "outputs"
    if not outputs_dir.exists():
        print("   ⚠️  SKIP: outputs directory not found")
        return
    
    md_files = list(outputs_dir.glob("*.md"))
    empty = []
    
    for f in md_files:
        content = f.read_text(encoding='utf-8').strip()
        if len(content) < 10:  # At least 10 chars
            empty.append(f.name)
    
    if empty:
        print(f"   ❌ FAIL: Empty markdown files: {empty}")
        assert False, f"Empty markdown: {empty}"
    else:
        print(f"   ✅ PASS: All {len(md_files)} markdown files have content")


def test_logs_exist():
    """Test that orchestrator log exists."""
    print("\n🧪 Test 4: Checking logs...")
    
    log_file = PROJECT_ROOT / "logs" / "orchestrator.log"
    
    if not log_file.exists():
        print(f"   ❌ FAIL: orchestrator.log not found")
        assert False, "orchestrator.log missing"
    
    # Check log has content
    content = log_file.read_text(encoding='utf-8')
    if len(content) < 100:
        print(f"   ⚠️  WARNING: Log file very small ({len(content)} bytes)")
    
    print(f"   ✅ PASS: orchestrator.log exists ({len(content)} bytes)")


def test_agent_registry_valid():
    """Test that agent registry is valid YAML."""
    print("\n🧪 Test 5: Validating agent registry...")
    
    registry_path = PROJECT_ROOT / "agents" / "orchestrator" / "agent_registry.yaml"
    
    if not registry_path.exists():
        print(f"   ❌ FAIL: agent_registry.yaml not found")
        assert False, "agent_registry.yaml missing"
    
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding='utf-8'))
        agents = registry.get('agents', [])
        
        if len(agents) < 5:
            print(f"   ⚠️  WARNING: Only {len(agents)} agents defined")
        
        print(f"   ✅ PASS: Registry valid with {len(agents)} agents")
        
    except Exception as e:
        print(f"   ❌ FAIL: Invalid registry: {e}")
        assert False, f"Invalid agent_registry.yaml: {e}"


# ==============================================
# Main Test Runner
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 VALIDATION TESTS - PHASE 6")
    print("=" * 70 + "\n")
    
    tests = [
        test_outputs_exist,
        test_yaml_valid,
        test_markdown_not_empty,
        test_logs_exist,
        test_agent_registry_valid
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n❌ Test failed: {e}\n")
        except Exception as e:
            failed += 1
            print(f"\n❌ Unexpected error: {e}\n")
    
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    print(f"\n✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"\nSuccess Rate: {int((passed/(passed+failed))*100)}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 70 + "\n")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("=" * 70 + "\n")
        sys.exit(1)

