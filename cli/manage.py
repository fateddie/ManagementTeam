#!/usr/bin/env python3
"""
manage.py
Phase 7 – CLI & User Automation
---------------------------------------------------------
Controls the full Management Team AI pipeline via command-line interface.

Usage:
    python cli/manage.py run              # Run full pipeline
    python cli/manage.py phase --n 3      # Run specific phase
    python cli/manage.py validate         # Run validation tests
    python cli/manage.py status           # Show latest summary
    python cli/manage.py clean            # Archive old files
    python cli/manage.py --help           # Show help
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import shutil

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from cli.helpers.cli_utils import (
    list_outputs, list_phases, get_project_root,
    format_file_size, get_latest_summary, get_latest_validation
)

LOG_DIR = BASE_DIR / "logs"
OUT_DIR = BASE_DIR / "outputs"


def run_orchestrator(phase: int | None = None):
    """Run the full orchestrator or specific phase."""
    print("=" * 70)
    if phase:
        print(f"🚀 Running Phase {phase}: {list_phases().get(phase, 'Unknown')}")
    else:
        print("🚀 Running Full AI Management Pipeline (All 6 Agents)")
    print("=" * 70 + "\n")
    
    os.chdir(BASE_DIR)
    cmd = [sys.executable, "agents/orchestrator/orchestrator.py"]
    
    if phase:
        os.environ["PHASE_OVERRIDE"] = str(phase)
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
        )
        
        print("\n" + "=" * 70)
        print("✅ Pipeline execution complete!")
        print("=" * 70)
        
        # Show quick summary
        show_quick_summary()
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print(f"❌ Pipeline failed with exit code {e.returncode}")
        print("=" * 70)
        return e.returncode


def show_status():
    """Display the most recent build summary."""
    print("=" * 70)
    print("📊 LATEST BUILD STATUS")
    print("=" * 70 + "\n")
    
    summary_file = get_latest_summary()
    validation_file = get_latest_validation()
    
    if summary_file:
        print(f"📄 Build Summary: {summary_file.name}\n")
        content = summary_file.read_text(encoding='utf-8')
        # Show first 50 lines
        lines = content.split('\n')[:50]
        print('\n'.join(lines))
        if len(content.split('\n')) > 50:
            print("\n... (truncated, see full file for details)")
    else:
        print("⚠️  No build summaries found. Run the pipeline first:")
        print("   python cli/manage.py run")
    
    print("\n" + "=" * 70)


def show_quick_summary():
    """Show a quick summary of latest run."""
    print("\n📊 Quick Summary:")
    
    validation_file = get_latest_validation()
    if validation_file:
        content = validation_file.read_text(encoding='utf-8')
        # Extract key metrics
        for line in content.split('\n'):
            if 'Valid Files:' in line or 'Invalid Files:' in line:
                print(f"   {line.strip()}")


def run_validation():
    """Run validation tests only."""
    print("=" * 70)
    print("🧪 RUNNING VALIDATION TESTS")
    print("=" * 70 + "\n")
    
    os.chdir(BASE_DIR)
    cmd = [sys.executable, "agents/reporting_agent/tests/validation_tests.py"]
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            env={**os.environ, "PYTHONPATH": str(BASE_DIR)}
        )
        
        print("\n" + "=" * 70)
        print("✅ All validation tests passed!")
        print("=" * 70)
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print(f"❌ Validation tests failed with exit code {e.returncode}")
        print("=" * 70)
        return e.returncode


def clean_old(days: int = 7):
    """Archive files older than specified days."""
    print("=" * 70)
    print(f"🧹 CLEANING FILES OLDER THAN {days} DAYS")
    print("=" * 70 + "\n")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    archived_count = 0
    
    for folder in [OUT_DIR, LOG_DIR]:
        if not folder.exists():
            continue
        
        for f in folder.glob("*"):
            if not f.is_file():
                continue
            
            # Skip important files
            if any(skip in f.name for skip in ['PHASE', 'SYSTEM', '100_PERCENT']):
                continue
            
            # Check age
            file_time = datetime.fromtimestamp(f.stat().st_mtime)
            if file_time < cutoff:
                # Archive
                archive_dir = folder / "archive"
                archive_dir.mkdir(exist_ok=True, parents=True)
                
                try:
                    shutil.move(str(f), archive_dir / f.name)
                    archived_count += 1
                    print(f"   📦 Archived: {f.name}")
                except Exception as e:
                    print(f"   ⚠️  Could not archive {f.name}: {e}")
    
    print(f"\n✅ Archived {archived_count} file(s).")
    print("=" * 70)


def list_commands():
    """List available phases and commands."""
    print("=" * 70)
    print("📋 AVAILABLE PHASES")
    print("=" * 70 + "\n")
    
    phases = list_phases()
    for num, desc in phases.items():
        print(f"   Phase {num}: {desc}")
    
    print("\n" + "=" * 70)
    print("📋 AVAILABLE COMMANDS")
    print("=" * 70 + "\n")
    
    commands = {
        "run": "Execute full pipeline (all 6 agents)",
        "phase --n <N>": "Run specific phase only",
        "validate": "Run validation tests only",
        "status": "Show latest build summary",
        "clean --days <N>": "Archive files older than N days (default: 7)",
        "list": "Show available phases and commands"
    }
    
    for cmd, desc in commands.items():
        print(f"   {cmd:20s} - {desc}")
    
    print("\n" + "=" * 70)
    print("\n💡 Examples:")
    print("   python cli/manage.py run")
    print("   python cli/manage.py phase --n 3")
    print("   python cli/manage.py validate")
    print("   python cli/manage.py status")
    print("   python cli/manage.py clean --days 7")
    print("=" * 70 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Management Team AI Pipeline Controller",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/manage.py run              # Run full pipeline
  python cli/manage.py phase --n 3      # Run phase 3 only
  python cli/manage.py validate         # Run tests
  python cli/manage.py status           # Show latest summary
  python cli/manage.py clean --days 7   # Archive old files
  python cli/manage.py list             # List phases/commands
        """
    )
    
    parser.add_argument(
        "command",
        choices=["run", "phase", "validate", "clean", "status", "list"],
        help="Task to perform"
    )
    
    parser.add_argument(
        "--n",
        type=int,
        help="Phase number (1-6) for 'phase' command"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Retention days for 'clean' command (default: 7)"
    )
    
    args = parser.parse_args()
    
    # Execute command
    try:
        if args.command == "run":
            return run_orchestrator()
            
        elif args.command == "phase":
            if not args.n:
                print("❌ Error: Please specify --n <phase number>")
                print("   Available phases: 1-6")
                sys.exit(1)
            
            if args.n < 1 or args.n > 6:
                print(f"❌ Error: Invalid phase number {args.n}")
                print("   Available phases: 1-6")
                sys.exit(1)
            
            return run_orchestrator(args.n)
            
        elif args.command == "validate":
            return run_validation()
            
        elif args.command == "clean":
            clean_old(args.days)
            return 0
            
        elif args.command == "status":
            show_status()
            return 0
            
        elif args.command == "list":
            list_commands()
            return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

