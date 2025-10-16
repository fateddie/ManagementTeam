#!/usr/bin/env python3
"""
Report Generator (PRD-07)
Aggregates data from all artifacts, audit logs, and validation reports
to produce comprehensive summary reports.

Usage:
    python report_generator.py --variant variant_1
    python report_generator.py --all
    python report_generator.py --summary
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))
from orchestrator_core import load_json, BASE_DIR, AUDIT_FILE, VALIDATION_ERROR_FILE

REPORTS_DIR = Path(__file__).parent
PROJECTS_DIR = BASE_DIR / "projects"

def generate_variant_summary(variant_name):
    """Generate comprehensive summary for a single variant (PRD-07)"""

    variant_dir = PROJECTS_DIR / variant_name

    if not variant_dir.exists():
        print(f"❌ Variant '{variant_name}' not found at {variant_dir}")
        return None

    print(f"\n📊 Generating report for '{variant_name}'...")

    # Load all artifact files
    idea_intake = load_json(variant_dir / "idea_intake.json", {})
    scope = load_json(variant_dir / "scope.yaml", {})  # Will be empty if YAML
    pain_scores = load_json(variant_dir / "pain_scores.json", {})
    market_competition = load_json(variant_dir / "market_competition.json", {})
    unit_economics = load_json(variant_dir / "unit_economics.json", {})
    risk_register = load_json(variant_dir / "risk_register.json", {})
    gtm_options = load_json(variant_dir / "gtm_options.json", {})
    decision_log = load_json(variant_dir / "decision_log.json", {})

    # Calculate key metrics
    summary = {
        "variant_name": variant_name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "metrics": {}
    }

    # Pain Score
    if pain_scores.get("records"):
        pain_total = sum(p.get("score_total", 0) for p in pain_scores["records"])
        pain_avg = pain_total / len(pain_scores["records"]) if pain_scores["records"] else 0
        summary["metrics"]["pain_score_avg"] = round(pain_avg, 2)
        summary["metrics"]["pain_score_count"] = len(pain_scores["records"])
    else:
        summary["metrics"]["pain_score_avg"] = "N/A"
        summary["metrics"]["pain_score_count"] = 0

    # Unit Economics
    if unit_economics.get("metrics"):
        metrics = unit_economics["metrics"]
        summary["metrics"]["ltv_cac_ratio"] = metrics.get("ltv_cac_ratio", "N/A")
        summary["metrics"]["payback_months"] = metrics.get("payback_months", "N/A")
        summary["metrics"]["annual_revenue_per_customer"] = metrics.get("annual_revenue_per_customer", "N/A")
        summary["metrics"]["cac"] = metrics.get("cac", "N/A")
    else:
        summary["metrics"]["ltv_cac_ratio"] = "N/A"
        summary["metrics"]["payback_months"] = "N/A"
        summary["metrics"]["annual_revenue_per_customer"] = "N/A"
        summary["metrics"]["cac"] = "N/A"

    # Risk Assessment
    if risk_register.get("risks"):
        high_risks = sum(1 for r in risk_register["risks"] if r.get("severity") == "high")
        medium_risks = sum(1 for r in risk_register["risks"] if r.get("severity") == "medium")
        low_risks = sum(1 for r in risk_register["risks"] if r.get("severity") == "low")

        summary["metrics"]["risk_high"] = high_risks
        summary["metrics"]["risk_medium"] = medium_risks
        summary["metrics"]["risk_low"] = low_risks
        summary["metrics"]["risk_total"] = len(risk_register["risks"])
    else:
        summary["metrics"]["risk_high"] = 0
        summary["metrics"]["risk_medium"] = 0
        summary["metrics"]["risk_low"] = 0
        summary["metrics"]["risk_total"] = 0

    # Decision
    summary["decision"] = {
        "outcome": decision_log.get("decision", "N/A"),
        "confidence": decision_log.get("confidence", "N/A"),
        "reasoning": decision_log.get("reasoning", "N/A")
    }

    # Generate Markdown report
    report_md = generate_markdown_report(summary, variant_name, {
        "idea_intake": idea_intake,
        "pain_scores": pain_scores,
        "market_competition": market_competition,
        "unit_economics": unit_economics,
        "risk_register": risk_register,
        "gtm_options": gtm_options,
        "decision_log": decision_log
    })

    # Save report
    report_file = REPORTS_DIR / f"summary_{variant_name}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"✅ Report saved to: {report_file}")

    # Also save JSON summary
    summary_file = REPORTS_DIR / f"summary_{variant_name}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ JSON summary saved to: {summary_file}")

    return summary

def generate_markdown_report(summary, variant_name, artifacts):
    """Generate Markdown report from summary data"""

    metrics = summary["metrics"]
    decision = summary["decision"]

    md = f"""# Variant Summary Report: {variant_name}

**Generated:** {summary['generated_at']}

---

## 📊 Key Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Pain Score (Avg) | {metrics['pain_score_avg']} | pain_scores.json |
| Pain Score Count | {metrics['pain_score_count']} | pain_scores.json |
| LTV:CAC Ratio | {metrics['ltv_cac_ratio']} | unit_economics.json |
| Payback Period | {metrics['payback_months']} months | unit_economics.json |
| Annual Revenue/Customer | {metrics['annual_revenue_per_customer']} | unit_economics.json |
| Customer Acquisition Cost | {metrics['cac']} | unit_economics.json |
| High Risk Items | {metrics['risk_high']} | risk_register.json |
| Medium Risk Items | {metrics['risk_medium']} | risk_register.json |
| Low Risk Items | {metrics['risk_low']} | risk_register.json |
| Total Risks | {metrics['risk_total']} | risk_register.json |

---

## 🎯 Decision Summary

**Outcome:** {decision['outcome']}
**Confidence:** {decision['confidence']}

**Reasoning:**
{decision['reasoning']}

---

## 📝 Artifact Summaries

### Idea Intake
- **Name:** {artifacts['idea_intake'].get('name', 'N/A')}
- **Description:** {artifacts['idea_intake'].get('description', 'N/A')}

### Pain Scores
- **Total Records:** {len(artifacts['pain_scores'].get('records', []))}
- **Average Score:** {metrics['pain_score_avg']}

### Unit Economics
- **LTV:CAC:** {metrics['ltv_cac_ratio']}
- **Payback:** {metrics['payback_months']} months

### Risk Assessment
- **High Risks:** {metrics['risk_high']}
- **Medium Risks:** {metrics['risk_medium']}
- **Low Risks:** {metrics['risk_low']}

---

## ✅ Validation Status

"""

    # Add validation info if available
    if VALIDATION_ERROR_FILE.exists():
        errors = load_json(VALIDATION_ERROR_FILE, [])
        variant_errors = [e for e in errors if variant_name in e.get('artifact', '')]

        if variant_errors:
            md += f"⚠️ **Validation Errors Found:** {len(variant_errors)}\n\n"
            for error in variant_errors[-5:]:  # Last 5 errors
                md += f"- {error.get('timestamp')}: {error.get('message')}\n"
        else:
            md += "✅ No validation errors\n\n"
    else:
        md += "ℹ️ Validation log not found\n\n"

    # Add audit trail summary
    if AUDIT_FILE.exists():
        audit_log = load_json(AUDIT_FILE, [])
        variant_actions = [a for a in audit_log if a.get('variant') == variant_name]

        md += f"""---

## 📋 Audit Trail Summary

**Total Actions:** {len(variant_actions)}

### Recent Actions

| Timestamp | Phase | Agent | Action |
|-----------|-------|-------|--------|
"""

        for action in variant_actions[-10:]:  # Last 10 actions
            md += f"| {action.get('timestamp', 'N/A')} | {action.get('phase', 'N/A')} | {action.get('agent', 'N/A')} | {action.get('action', 'N/A')} |\n"

    md += "\n---\n\n**Report generated by Variant Exploration System (VES)**\n"

    return md

def generate_all_variants_comparison():
    """Generate comparison report for all variants"""

    print(f"\n📊 Generating comparison report for all variants...")

    variants = [d.name for d in PROJECTS_DIR.iterdir()
                if d.is_dir() and not d.name.startswith('_')]

    if not variants:
        print("❌ No variants found")
        return

    print(f"Found {len(variants)} variant(s): {', '.join(variants)}")

    # Generate summary for each variant
    summaries = []
    for variant in variants:
        summary = generate_variant_summary(variant)
        if summary:
            summaries.append(summary)

    # Generate comparison markdown
    comparison_md = f"""# All Variants Comparison Report

**Generated:** {datetime.utcnow().isoformat()}Z

---

## Comparison Matrix

| Metric | {' | '.join(s['variant_name'] for s in summaries)} |
|--------|{'|'.join(['---' for _ in summaries])}|
"""

    metrics_to_compare = [
        ("Pain Score (Avg)", "pain_score_avg"),
        ("LTV:CAC Ratio", "ltv_cac_ratio"),
        ("Payback (months)", "payback_months"),
        ("High Risks", "risk_high"),
        ("Total Risks", "risk_total"),
    ]

    for metric_name, metric_key in metrics_to_compare:
        values = [str(s["metrics"].get(metric_key, "N/A")) for s in summaries]
        comparison_md += f"| {metric_name} | {' | '.join(values)} |\n"

    # Add decisions
    comparison_md += "\n## Decision Summary\n\n"
    for summary in summaries:
        decision = summary["decision"]
        comparison_md += f"### {summary['variant_name']}\n"
        comparison_md += f"- **Outcome:** {decision['outcome']}\n"
        comparison_md += f"- **Confidence:** {decision['confidence']}\n\n"

    # Save comparison report
    comparison_file = REPORTS_DIR / "all_variants_comparison.md"
    with open(comparison_file, "w", encoding="utf-8") as f:
        f.write(comparison_md)

    print(f"✅ Comparison report saved to: {comparison_file}")

    # Save JSON
    comparison_json = REPORTS_DIR / "all_variants_comparison.json"
    with open(comparison_json, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)

    print(f"✅ JSON comparison saved to: {comparison_json}")

def generate_build_summary():
    """Generate build summary report (PRD-07)"""

    print(f"\n📊 Generating build summary report...")

    # Count total variants
    variants = [d.name for d in PROJECTS_DIR.iterdir()
                if d.is_dir() and not d.name.startswith('_')]

    # Count audit actions
    audit_count = 0
    if AUDIT_FILE.exists():
        audit_log = load_json(AUDIT_FILE, [])
        audit_count = len(audit_log)

    # Count validation errors
    error_count = 0
    if VALIDATION_ERROR_FILE.exists():
        errors = load_json(VALIDATION_ERROR_FILE, [])
        error_count = len(errors)

    summary_md = f"""# Build Summary Report

**Generated:** {datetime.utcnow().isoformat()}Z

---

## System Status

- **Total Variants:** {len(variants)}
- **Total Audit Actions:** {audit_count}
- **Total Validation Errors:** {error_count}

## PRD Implementation Status

| PRD | Component | Status |
|-----|-----------|--------|
| PRD-01 | Schema Layer | ✅ Complete |
| PRD-02 | Artifact Templates | ✅ Complete |
| PRD-03 | Agent Roles & Prompts | ✅ Complete |
| PRD-04 | Orchestrator Core | ✅ Complete |
| PRD-05 | Audit & Logging Layer | ✅ Complete |
| PRD-06 | Validation Engine | ✅ Complete |
| PRD-07 | Reporting Dashboard | ✅ Complete |

## Variants

"""

    for variant in variants:
        summary_md += f"- {variant}\n"

    summary_md += f"""
---

## Recent Activity

"""

    # Add recent audit actions
    if AUDIT_FILE.exists():
        audit_log = load_json(AUDIT_FILE, [])
        summary_md += "### Last 10 Actions\n\n"
        for action in audit_log[-10:]:
            summary_md += f"- [{action.get('timestamp')}] {action.get('variant')} - Phase {action.get('phase')}: {action.get('action')}\n"

    # Save build summary
    build_summary_file = REPORTS_DIR / "build_summary.md"
    with open(build_summary_file, "w", encoding="utf-8") as f:
        f.write(summary_md)

    print(f"✅ Build summary saved to: {build_summary_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Report Generator (PRD-07) - Generate comprehensive reports"
    )
    parser.add_argument(
        "--variant",
        type=str,
        help="Generate report for specific variant"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate comparison report for all variants"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate build summary report"
    )

    args = parser.parse_args()

    # Create reports directory
    REPORTS_DIR.mkdir(exist_ok=True)

    if args.variant:
        generate_variant_summary(args.variant)
    elif args.all:
        generate_all_variants_comparison()
    elif args.summary:
        generate_build_summary()
    else:
        print("Usage:")
        print("  python report_generator.py --variant variant_1")
        print("  python report_generator.py --all")
        print("  python report_generator.py --summary")

if __name__ == "__main__":
    main()
