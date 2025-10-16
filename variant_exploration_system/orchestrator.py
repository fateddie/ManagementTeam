"""
Variant Exploration System — Orchestrator
-----------------------------------------
Interactive controller for the 13-phase SOP.

Usage:
    python orchestrator.py                # start interactive loop
    python orchestrator.py --variant v1   # resume a specific variant
    python orchestrator.py --compare      # compare all completed variants
"""

import json, os, sys, datetime, argparse, textwrap
from pathlib import Path

BASE = os.path.dirname(__file__)
ROOT = os.path.abspath(BASE)
STATE_FILE = os.path.join(ROOT, "agent", "state_schema.json")
LOG_FILE   = os.path.join(ROOT, "logs", "audit_trail.json")

# Add parent directory to path for Workshop Agent integration
sys.path.insert(0, os.path.abspath(os.path.join(ROOT, "..")))

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def timestamp():
    return datetime.datetime.utcnow().isoformat()

def log_decision(variant, phase, decision, notes=""):
    log = load_json(LOG_FILE, [])
    log.append({
        "variant": variant,
        "phase": phase,
        "decision": decision,
        "notes": notes,
        "timestamp": timestamp()
    })
    save_json(LOG_FILE, log)

def next_phase(current_phase):
    return current_phase + 1 if current_phase < 13 else 13

def load_prompt(prompt_name):
    """Load prompt from /agent/prompts/ folder"""
    prompt_path = os.path.join(ROOT, "agent", "prompts", f"{prompt_name}.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"[Prompt {prompt_name} not found]"

# ---------------------------------------------------------------------
# SOP Phase Names
# ---------------------------------------------------------------------
PHASES = [
    "Intake & Ownership",
    "Hypothesis & Scope",
    "Research Plan",
    "Evidence Collection",
    "Cleaning & Chain-of-Custody",
    "Pain Extraction & Tagging",
    "Pain Quantification",
    "Market & Competition",
    "Unit Economics",
    "Feasibility & Risk",
    "GTM Options & Prioritisation",
    "Synthesis (ADSR Report)",
    "Decision & Logging",
    "Cross-Variant Comparison & Hybridisation"
]

# Phase to filename mapping
PHASE_FILES = {
    0: "idea_intake.json",
    1: "scope.yaml",
    2: "research_plan.md",
    3: None,  # Evidence collection - saves to /data/raw/
    4: None,  # Cleaning - saves to /data/clean/
    5: "pains_tagged.json",
    6: "pain_scores.json",
    7: "market_competition.md",
    8: "unit_economics.json",
    9: "feasibility_risk.md",
    10: "gtm_options.md",
    11: "report_ADSR.md",
    12: "decision_log.json",
    13: None  # Comparison - saves to /reports/
}

# ---------------------------------------------------------------------
# Core Orchestrator
# ---------------------------------------------------------------------
def run_orchestrator(variant="variant_1"):
    """Run the interactive 13-phase workflow for a single variant"""
    
    state = load_json(STATE_FILE, {
        "variant_name": variant,
        "phase": 0,
        "status": "pending",
        "started_at": timestamp()
    })
    
    variant_dir = os.path.join(ROOT, "projects", variant)
    os.makedirs(variant_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"  VARIANT EXPLORATION SYSTEM")
    print(f"{'='*70}")
    print(f"Variant: {variant}")
    print(f"Current Phase: {state['phase']}")
    print(f"Status: {state.get('status', 'pending')}")
    print(f"{'='*70}\n")

    while state["phase"] <= 13:
        phase_num = state["phase"]
        phase_name = PHASES[phase_num]
        
        print(f"\n{'='*70}")
        print(f"  PHASE {phase_num}: {phase_name}")
        print(f"{'='*70}\n")

        # Load and display phase-specific prompt
        if phase_num == 0:
            prompt = load_prompt("kick_off")
        elif phase_num == 13:
            prompt = load_prompt("comparison_prompt")
        else:
            prompt = load_prompt("phase_template").format(
                phase_number=phase_num,
                phase_name=phase_name
            )
        
        print(prompt)
        print(f"\n{'-'*70}")
        
        # Collect user input
        print(f"\n📝 Please provide your input for Phase {phase_num}:")
        print("(Type your response, then press Enter. For multi-line, type 'END' on a new line when done)")
        print(f"{'-'*70}\n")
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        
        user_input = "\n".join(lines)
        
        # Save phase output to appropriate file
        output_file = PHASE_FILES.get(phase_num)
        
        if output_file:
            output_path = os.path.join(variant_dir, output_file)
            
            # Save as JSON or YAML or Markdown based on extension
            if output_file.endswith('.json'):
                # Try to parse as JSON, or save raw if that fails
                try:
                    data = json.loads(user_input)
                    save_json(output_path, data)
                except json.JSONDecodeError:
                    # Save as simple JSON object with input
                    save_json(output_path, {
                        "phase": phase_num,
                        "phase_name": phase_name,
                        "input": user_input,
                        "timestamp": timestamp()
                    })
            elif output_file.endswith('.yaml'):
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {phase_name}\n")
                    f.write(f"# Updated: {timestamp()}\n\n")
                    f.write(user_input)
            else:  # .md files
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {phase_name}\n\n")
                    f.write(user_input)
                    f.write(f"\n\n---\n*Updated: {timestamp()}*\n")
            
            print(f"\n✅ Saved to: {output_file}")
        else:
            # Phases without specific output files (3, 4, 13)
            generic_file = f"phase_{phase_num:02d}_{phase_name.replace(' ', '_').lower()}.md"
            output_path = os.path.join(variant_dir, generic_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {phase_name}\n\n")
                f.write(user_input)
                f.write(f"\n\n---\n*Updated: {timestamp()}*\n")
            print(f"\n✅ Saved to: {generic_file}")

        # Gate decision
        print(f"\n{'-'*70}")
        print("📋 PHASE REVIEW:")
        print(f"{'-'*70}")
        print("✅ (C)onfirm & Continue")
        print("🔄 (R)evise this phase")
        print("⏸️  (P)ark variant for later")
        print(f"{'-'*70}\n")
        
        decision = input("Your decision [C/R/P]: ").strip().upper()
        
        if decision == "P":
            print(f"\n⏸️  Variant '{variant}' parked at Phase {phase_num}.")
            state.update({
                "status": "parked",
                "phase": phase_num,
                "parked_at": timestamp()
            })
            log_decision(variant, phase_num, "Parked")
            save_json(STATE_FILE, state)
            break
            
        elif decision == "R":
            print("\n🔄 Revision requested. Please re-enter phase data...")
            log_decision(variant, phase_num, "Revised")
            continue
            
        else:  # Confirm
            print(f"\n✅ Phase {phase_num} approved. Moving to next phase...")
            log_decision(variant, phase_num, "Approved")
            state.update({
                "status": "in_progress",
                "phase": next_phase(phase_num),
                "last_updated": timestamp()
            })
            save_json(STATE_FILE, state)

        if state["phase"] > 13:
            print(f"\n{'='*70}")
            print("🎯 WORKFLOW COMPLETE FOR THIS VARIANT!")
            print(f"{'='*70}")
            print(f"\nVariant '{variant}' has completed all 13 phases.")
            print(f"Review outputs in: {variant_dir}")
            print(f"\nNext steps:")
            print(f"  1. Run additional variants: python orchestrator.py --variant variant_2")
            print(f"  2. Compare variants: python orchestrator.py --compare")
            print(f"{'='*70}\n")
            
            state.update({
                "status": "completed",
                "completed_at": timestamp()
            })
            save_json(STATE_FILE, state)
            break

def compare_variants():
    """Compare all completed variants and generate comparison matrix"""
    
    print(f"\n{'='*70}")
    print("  CROSS-VARIANT COMPARISON")
    print(f"{'='*70}\n")
    
    projects_dir = os.path.join(ROOT, "projects")
    variants = [d for d in os.listdir(projects_dir) 
                if os.path.isdir(os.path.join(projects_dir, d)) 
                and not d.startswith('_')]
    
    if not variants:
        print("❌ No variants found. Please complete at least one variant first.")
        return
    
    print(f"Found {len(variants)} variant(s): {', '.join(variants)}\n")
    
    # Load key metrics from each variant
    comparison_data = []
    
    for variant in variants:
        variant_dir = os.path.join(projects_dir, variant)
        
        # Load pain scores
        pain_scores_file = os.path.join(variant_dir, "pain_scores.json")
        pain_data = load_json(pain_scores_file, {})
        avg_pain = pain_data.get("overall_avg_pain_score", "N/A")
        
        # Load unit economics
        economics_file = os.path.join(variant_dir, "unit_economics.json")
        economics = load_json(economics_file, {})
        metrics = economics.get("metrics", {})
        
        # Load decision
        decision_file = os.path.join(variant_dir, "decision_log.json")
        decision = load_json(decision_file, {})
        
        comparison_data.append({
            "variant": variant,
            "avg_pain_score": avg_pain,
            "ltv_cac": metrics.get("ltv_cac_ratio", "N/A"),
            "payback_months": metrics.get("payback_months", "N/A"),
            "decision": decision.get("decision", "N/A"),
            "confidence": decision.get("confidence", "N/A")
        })
    
    # Generate comparison matrix
    comparison_md = f"""# Cross-Variant Comparison Matrix

Generated: {timestamp()}

## Summary Table

| Metric | """ + " | ".join([f"**{v['variant']}**" for v in comparison_data]) + """ |
|---------|""" + "|".join(["--------" for _ in comparison_data]) + """ |
| **Avg Pain Score** | """ + " | ".join([str(v['avg_pain_score']) for v in comparison_data]) + """ |
| **LTV:CAC** | """ + " | ".join([str(v['ltv_cac']) for v in comparison_data]) + """ |
| **Payback (months)** | """ + " | ".join([str(v['payback_months']) for v in comparison_data]) + """ |
| **Decision** | """ + " | ".join([v['decision'] for v in comparison_data]) + """ |
| **Confidence** | """ + " | ".join([v['confidence'] for v in comparison_data]) + """ |

## Recommendations

"""
    
    for v in comparison_data:
        comparison_md += f"\n### {v['variant']}\n"
        comparison_md += f"- Pain Score: {v['avg_pain_score']}\n"
        comparison_md += f"- Economics: LTV:CAC {v['ltv_cac']}, Payback {v['payback_months']} months\n"
        comparison_md += f"- Decision: {v['decision']} (Confidence: {v['confidence']})\n"
    
    # Save comparison matrix
    reports_dir = os.path.join(ROOT, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    comparison_file = os.path.join(reports_dir, "comparison_matrix.md")
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write(comparison_md)
    
    print(comparison_md)
    print(f"\n{'='*70}")
    print(f"✅ Comparison saved to: {comparison_file}")
    print(f"{'='*70}\n")
    
    # Save structured JSON
    save_json(os.path.join(reports_dir, "variant_summary.json"), comparison_data)
    
    # Prompt for next action
    print("\n📋 NEXT ACTIONS:")
    print(f"{'-'*70}")
    print("1. ✅ Advance one variant to development")
    print("2. 🔗 Combine variants into a hybrid")
    print("3. ⏸️  Park all variants for now")
    print(f"{'-'*70}\n")
    
    decision = input("Your choice [1/2/3]: ").strip()
    
    if decision == "1":
        variant_choice = input("\nWhich variant to advance? ").strip()
        print(f"\n🚀 Advancing {variant_choice} to development!")
        log_decision(variant_choice, 13, "Advanced to Development")
        
    elif decision == "2":
        variants_to_merge = input("\nWhich variants to combine? (comma-separated): ").strip()
        print(f"\n🔗 Creating hybrid from: {variants_to_merge}")
        log_decision("hybrid", 13, f"Created from: {variants_to_merge}")
        
    else:
        print("\n⏸️  All variants parked for future consideration")
        log_decision("all", 13, "Parked")

# ---------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Variant Exploration System Orchestrator"
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="variant_1",
        help="Variant folder name (default: variant_1)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare all completed variants"
    )
    
    args = parser.parse_args()
    
    if args.compare:
        compare_variants()
    else:
        run_orchestrator(args.variant)

