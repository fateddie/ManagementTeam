#!/usr/bin/env python3
"""
test_summary_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Test Suite for Summary Parser

Tests parsing of well-formed and malformed summary files.

Usage:
    python scripts/test_summary_parser.py
    
Location: scripts/test_summary_parser.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.utils.summary_parser import parse_vertical_summary, validate_summary


def test_well_formed():
    """Test with well-formed recommendation."""
    print("\n" + "="*70)
    print("TEST 1: Well-Formed Summary")
    print("="*70 + "\n")
    
    path = "outputs/recommendation.md"
    
    if not Path(path).exists():
        print(f"⚠️  File not found: {path}")
        return
    
    try:
        summary = parse_vertical_summary(path)
        validation = validate_summary(path, strict=True)
        
        print(f"✅ Parse successful")
        print(f"   Top: {summary['title']}")
        print(f"   Score: {summary['score']}")
        print(f"   Framework: {summary['framework']}")
        
        print(f"\n📊 Validation:")
        print(f"   Valid: {validation['valid']}")
        print(f"   Errors: {len(validation['errors'])}")
        print(f"   Warnings: {len(validation['warnings'])}")
        
        if validation['warnings']:
            print(f"\n⚠️  Warnings:")
            for w in validation['warnings']:
                print(f"   - {w}")
        
        print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}\n")


def test_malformed_missing_plan():
    """Test with summary missing plan section."""
    print("=" * 70)
    print("TEST 2: Malformed Summary (Missing Plan)")
    print("="*70 + "\n")
    
    # Create test file
    test_dir = Path("outputs/test_summaries")
    test_dir.mkdir(exist_ok=True)
    
    malformed_path = test_dir / "malformed_missing_plan.md"
    
    with open(malformed_path, 'w') as f:
        f.write("""# 📄 Vertical Agent Summary Report

## 🏆 Top Recommendation

**AI Hairdresser Booking Assistant**

- **Score**: `75.5`

---

## 📊 Complete Rankings

| Rank | Idea | Score |
|------|------|-------|
| 🥇 1 | AI Hairdresser | 75.5 |

---

## 🤖 Proactive Agent Observations

This is a promising idea due to volume of missed calls.

(Oops, no framework or other details!)

""")
    
    try:
        summary = parse_vertical_summary(str(malformed_path))
        validation = validate_summary(str(malformed_path), strict=True)
        
        print(f"✅ Parse successful (graceful fallback)")
        print(f"   Top: {summary['title']}")
        print(f"   Score: {summary['score']}")
        
        print(f"\n📊 Validation:")
        print(f"   Valid: {validation['valid']}")
        print(f"   Errors: {len(validation['errors'])}")
        print(f"   Warnings: {len(validation['warnings'])}")
        
        if validation['errors']:
            print(f"\n❌ Errors:")
            for e in validation['errors']:
                print(f"   - {e}")
        
        if validation['warnings']:
            print(f"\n⚠️  Warnings:")
            for w in validation['warnings']:
                print(f"   - {w}")
        
        print()
        
    except Exception as e:
        print(f"⚠️  Parse handled gracefully: {e}\n")


def test_malformed_missing_score():
    """Test with summary missing score."""
    print("="*70)
    print("TEST 3: Malformed Summary (Missing Score)")
    print("="*70 + "\n")
    
    test_dir = Path("outputs/test_summaries")
    test_dir.mkdir(exist_ok=True)
    
    malformed_path = test_dir / "malformed_missing_score.md"
    
    with open(malformed_path, 'w') as f:
        f.write("""# 📄 Vertical Agent Summary Report

## 🏆 Top Recommendation

**Pet Grooming App**

## 🤖 Proactive Agent Observations

Good opportunity but score calculation failed!

""")
    
    try:
        summary = parse_vertical_summary(str(malformed_path))
        validation = validate_summary(str(malformed_path))
        
        print(f"✅ Parse successful (with fallbacks)")
        print(f"   Top: {summary['title']}")
        print(f"   Score: {summary['score']} (fallback)")
        
        print(f"\n📊 Validation:")
        print(f"   Valid: {validation['valid']}")
        
        if validation['warnings']:
            print(f"\n⚠️  Warnings:")
            for w in validation['warnings']:
                print(f"   - {w}")
        
        print()
        
    except Exception as e:
        print(f"❌ Parse failed: {e}\n")


def test_completely_broken():
    """Test with completely invalid file."""
    print("="*70)
    print("TEST 4: Completely Broken File")
    print("="*70 + "\n")
    
    test_dir = Path("outputs/test_summaries")
    test_dir.mkdir(exist_ok=True)
    
    broken_path = test_dir / "broken.md"
    
    with open(broken_path, 'w') as f:
        f.write("Random text with no structure at all!")
    
    try:
        summary = parse_vertical_summary(str(broken_path))
        validation = validate_summary(str(broken_path))
        
        print(f"✅ Parse handled (fallback mode)")
        print(f"   Top: {summary['title']}")
        print(f"   Score: {summary['score']}")
        
        print(f"\n📊 Validation:")
        print(f"   Valid: {validation['valid']}")
        
        if validation['errors']:
            print(f"\n❌ Errors:")
            for e in validation['errors']:
                print(f"   - {e}")
        
        print()
        
    except Exception as e:
        print(f"❌ Parse failed as expected: {e}\n")


def cleanup_test_files():
    """Remove test files."""
    test_dir = Path("outputs/test_summaries")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print("🧹 Test files cleaned up\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 SUMMARY PARSER TEST SUITE")
    print("="*70)
    
    test_well_formed()
    test_malformed_missing_plan()
    test_malformed_missing_score()
    test_completely_broken()
    
    print("="*70)
    print("✅ All Tests Complete!")
    print("="*70 + "\n")
    
    cleanup_test_files()

