#!/usr/bin/env python3
"""
export_evidence.py
-------------------
Export validation evidence in multiple formats with full transparency.

Supports:
- CSV: Raw data export
- Excel: Rich formatted export
- JSON: Machine-readable
- Markdown: Human-readable evidence report with decision checkboxes

Usage:
    # Generate evidence report (Markdown)
    python scripts/export_evidence.py --format markdown

    # Export full data to Excel
    python scripts/export_evidence.py --format excel

    # Export filtered data
    python scripts/export_evidence.py --format csv --filter industry=dental

    # Generate all formats
    python scripts/export_evidence.py --all
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.demand_validator import DemandValidator


def export_evidence(
    csv_path: str,
    format: str = "markdown",
    output_path: str = None,
    filter_criteria: dict = None
):
    """
    Export evidence in specified format.

    Args:
        csv_path: Path to enriched CSV
        format: Export format (csv, excel, json, markdown)
        output_path: Output file path (auto-generated if None)
        filter_criteria: Optional filters
    """
    print(f"\n📤 Exporting evidence in {format.upper()} format...")

    try:
        validator = DemandValidator(csv_path)

        if format == "markdown":
            # Generate evidence report
            output = output_path or "evidence_report.md"
            validator.export_evidence_report(output)

        elif format == "json":
            # Generate full validation report
            output = output_path or "demand_validation_report.json"
            validator.save_report(output)

        elif format in ["csv", "excel"]:
            # Export raw data
            output = validator.export_data(
                format=format,
                output_path=output_path,
                filter_criteria=filter_criteria
            )

        else:
            print(f"❌ Unsupported format: {format}")
            print("   Supported: csv, excel, json, markdown")
            return

        print(f"\n✅ Export complete!")
        print(f"   Output: {output}")
        print(f"   Size: {Path(output).stat().st_size / 1024:.1f} KB")

    except FileNotFoundError:
        print(f"\n❌ Data file not found: {csv_path}")
        print("   Run data collection first:")
        print("   python cli/interactive_workflow.py")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def export_all(csv_path: str):
    """Export all formats."""
    formats = {
        "markdown": "evidence_report.md",
        "json": "demand_validation_report.json",
        "csv": "data_export.csv",
        "excel": "data_export.xlsx"
    }

    print("\n" + "="*80)
    print("📦 EXPORTING ALL FORMATS")
    print("="*80)

    for fmt, default_output in formats.items():
        export_evidence(csv_path, format=fmt, output_path=default_output)
        print()

    print("="*80)
    print("✅ ALL EXPORTS COMPLETE")
    print("="*80)
    print("\nGenerated files:")
    for fmt, path in formats.items():
        if Path(path).exists():
            size = Path(path).stat().st_size / 1024
            print(f"   • {path} ({size:.1f} KB)")


def main():
    parser = argparse.ArgumentParser(
        description="Export validation evidence in multiple formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Markdown evidence report
  python scripts/export_evidence.py --format markdown

  # Export to Excel
  python scripts/export_evidence.py --format excel --output insights.xlsx

  # Export filtered CSV
  python scripts/export_evidence.py --format csv --filter industry=dental

  # Export all formats
  python scripts/export_evidence.py --all
        """
    )

    parser.add_argument(
        '--csv',
        default='social_posts_enriched.csv',
        help='Path to enriched CSV file'
    )

    parser.add_argument(
        '--format',
        choices=['csv', 'excel', 'json', 'markdown'],
        default='markdown',
        help='Export format'
    )

    parser.add_argument(
        '--output',
        help='Output file path (auto-generated if not specified)'
    )

    parser.add_argument(
        '--filter',
        help='Filter criteria (e.g., industry=dental,urgency=critical)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Export all formats'
    )

    args = parser.parse_args()

    # Parse filters
    filter_criteria = None
    if args.filter:
        filter_criteria = {}
        for item in args.filter.split(','):
            if '=' in item:
                key, value = item.split('=', 1)
                filter_criteria[key.strip()] = value.strip()

    # Export
    if args.all:
        export_all(args.csv)
    else:
        export_evidence(
            csv_path=args.csv,
            format=args.format,
            output_path=args.output,
            filter_criteria=filter_criteria
        )


if __name__ == "__main__":
    main()
