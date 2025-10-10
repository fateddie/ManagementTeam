# ==============================================
# file: /ManagementTeam/scripts/run_planner.py
# ==============================================
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.planner_agent import run


def main() -> None:
    """CLI entry point for the Planner Agent with oversight mode."""
    parser = argparse.ArgumentParser(
        description="Run the Planner Agent to scaffold a new project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python scripts/run_planner.py "my-project" "Build a trading bot"
  
  # With custom author
  python scripts/run_planner.py "my-project" "Build a trading bot" --author "John Doe"
  
  # Interactive mode with human oversight
  python scripts/run_planner.py "my-project" "Build a trading bot" --interactive
        """
    )
    
    parser.add_argument(
        "project_name",
        help="Name for /projects/<project_name>/"
    )
    parser.add_argument(
        "description",
        help="Free-text project description"
    )
    parser.add_argument(
        "--author",
        default="Rob Freyne",
        help="Project author name (default: Rob Freyne)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enable interactive review mode with pause points"
    )
    
    args = parser.parse_args()

    try:
        print("\n" + "=" * 70)
        print("🚀 PLANNER AGENT - AI Management Layer System")
        print("=" * 70 + "\n")
        
        summary = run(
            args.project_name,
            args.description,
            author=args.author,
            interactive=args.interactive
        )
        
        print("\n" + "=" * 70)
        print("✅ Planner Agent completed successfully!")
        print("=" * 70)
        print(f"\n📁 Project root: {summary['project_root']}")
        print("\n📄 Generated files:")
        for filepath in summary['generated']:
            print(f"  ✓ {filepath}")
        
        if summary['gaps']:
            print("\n⚠️  Information gaps detected:")
            for key, reason in summary['gaps'].items():
                print(f"  • {key}: {reason}")
            print(f"\n💡 Review missing_info.md for details")
        else:
            print("\n✨ No information gaps detected! Project is ready to proceed.")
        
        print("\n📋 Next steps:")
        print("  1. Review generated files in the planning/ directory")
        print("  2. Address any information gaps in missing_info.md")
        print("  3. Validate project_plan.yaml against requirements")
        print("  4. Begin implementation using the Documentation Agent")
        print("\n" + "=" * 70 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print("\n" + "=" * 70, file=sys.stderr)
        print(f"❌ Error: {e}", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
