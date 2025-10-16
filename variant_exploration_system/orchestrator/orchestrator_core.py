"""
Variant Exploration System — Orchestrator Core
----------------------------------------------
Modular orchestrator implementing PRD-04 specifications.

Coordinates 5 agents (Planner, Market Intelligence, Finance, Risk, Documentation)
through the 13-phase SOP with human-in-loop confirmation at each gate.

Usage:
    python orchestrator_core.py
    python orchestrator_core.py --variant my_variant
    python orchestrator_core.py --phase 5
"""

import json
import os
import sys
import datetime
import argparse
from pathlib import Path

# ---------------------------------------------------------------------
# Directory Setup
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent.absolute()
STATE_DIR = Path(__file__).parent / "state"
LOGS_DIR = Path(__file__).parent / "logs"
CONFIG_DIR = Path(__file__).parent / "config"

# Ensure directories exist
STATE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
CONFIG_DIR.mkdir(exist_ok=True)

STATE_FILE = STATE_DIR / "state_schema.json"
AUDIT_FILE = LOGS_DIR / "audit_trail.json"
PHASE_MAP_FILE = CONFIG_DIR / "phase_agent_map.json"

# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def load_json(path, default):
    """Load JSON file with fallback to default"""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    """Save data to JSON file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def timestamp():
    """Generate ISO 8601 timestamp"""
    return datetime.datetime.utcnow().isoformat() + "Z"

def log_action(variant, phase, agent, action, notes=""):
    """Log every action to audit trail"""
    audit_log = load_json(AUDIT_FILE, [])
    audit_log.append({
        "timestamp": timestamp(),
        "variant": variant,
        "phase": phase,
        "agent": agent,
        "action": action,
        "notes": notes
    })
    save_json(AUDIT_FILE, audit_log)

def load_agent_definition(agent_name):
    """Load agent definition file"""
    agent_file = BASE_DIR / "agents" / f"{agent_name.lower().replace(' ', '_')}_agent.md"
    if agent_file.exists():
        with open(agent_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"[Agent definition not found: {agent_file}]"

def load_template(template_name):
    """Load template file"""
    if not template_name:
        return None
    template_file = BASE_DIR / "templates" / template_name
    if template_file.exists():
        with open(template_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"[Template not found: {template_file}]"

# ---------------------------------------------------------------------
# Core Orchestrator Logic
# ---------------------------------------------------------------------
def initialize_variant(variant_name):
    """Initialize new variant with templates"""
    variant_dir = BASE_DIR / "projects" / variant_name
    variant_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all templates to variant folder
    template_dir = BASE_DIR / "templates"
    if template_dir.exists():
        print(f"\n📋 Initializing variant '{variant_name}' with templates...")
        import shutil
        for template_file in template_dir.glob("*"):
            if template_file.suffix in ['.md', '.json', '.yaml'] and template_file.name != "README.md":
                dst = variant_dir / template_file.name
                shutil.copy2(template_file, dst)
        print(f"✅ Templates copied to {variant_dir}")
    
    return variant_dir

def run_phase(variant_name, phase_num, phase_data, state):
    """Execute a single phase with agent coordination"""
    
    phase_name = phase_data["phase_name"]
    agent_name = phase_data["agent"]
    template_name = phase_data.get("template")
    
    # Display phase header
    print(f"\n{'='*70}")
    print(f"[Phase {phase_num}] {phase_name} → Assigned Agent: {agent_name}")
    print(f"{'='*70}\n")
    
    # Load and display agent definition
    agent_def = load_agent_definition(agent_name)
    # Extract just the prompt section for this phase
    print(f"📖 Agent Guidance:\n")
    print(f"See agents/{agent_name.lower().replace(' ', '_')}_agent.md for complete guidance.\n")
    
    # Show task
    if template_name:
        print(f"→ Task: Fill out /templates/{template_name}")
        
        # Show template
        template_content = load_template(template_name)
        if template_content and len(template_content) < 1000:
            print(f"\n📄 Template Preview:")
            print(f"{'-'*70}")
            print(template_content[:500])
            if len(template_content) > 500:
                print("... [see full template in file]")
            print(f"{'-'*70}\n")
    else:
        output_dir = phase_data.get("output_dir", "/data/")
        print(f"→ Task: Complete data collection for {output_dir}")
    
    # Confirmation gate
    print(f"\n{'='*70}")
    print("⏸️  CONFIRMATION GATE")
    print(f"{'='*70}")
    print("Have you completed the required task for this phase?")
    print("  (y) Yes - Save and continue")
    print("  (n) No - Pause workflow, resume later")
    print("  (s) Skip this phase (not recommended)")
    print(f"{'='*70}\n")
    
    confirmation = input("Confirm completion (y/n/s): ").strip().lower()
    
    if confirmation == "y":
        print(f"\n✅ Phase {phase_num} complete. Saving and proceeding...")
        log_action(variant_name, phase_num, agent_name, f"Phase {phase_num} approved by user")
        return "approved"
        
    elif confirmation == "s":
        print(f"\n⚠️  Phase {phase_num} skipped.")
        log_action(variant_name, phase_num, agent_name, f"Phase {phase_num} skipped by user")
        return "skipped"
        
    else:
        print(f"\n⏸️  Workflow paused. Please complete artifact and restart orchestrator.")
        log_action(variant_name, phase_num, agent_name, f"Phase {phase_num} paused - user needs more time")
        return "paused"

def run_orchestrator(variant_name="variant_1", start_phase=None):
    """Main orchestrator loop"""
    
    # Load state
    state = load_json(STATE_FILE, {
        "variant_name": variant_name,
        "current_phase": 0,
        "status": "initialized",
        "started_at": timestamp(),
        "approvals": []
    })
    
    # If resuming, use saved phase
    if start_phase is not None:
        state["current_phase"] = start_phase
    
    # Initialize variant directory
    variant_dir = initialize_variant(variant_name)
    
    # Load phase-agent mapping
    phase_map = load_json(PHASE_MAP_FILE, {"phases": []})
    phases = {p["phase"]: p for p in phase_map.get("phases", [])}
    
    # Display header
    print(f"\n{'='*70}")
    print(f"  VARIANT EXPLORATION SYSTEM - ORCHESTRATOR")
    print(f"{'='*70}")
    print(f"Variant: {variant_name}")
    print(f"Current Phase: {state['current_phase']}")
    print(f"Status: {state.get('status', 'initialized')}")
    print(f"{'='*70}\n")
    
    # Main loop
    while state["current_phase"] <= 13:
        phase_num = state["current_phase"]
        
        # Get phase data
        if phase_num not in phases:
            print(f"⚠️  Phase {phase_num} not found in mapping. Skipping...")
            state["current_phase"] += 1
            continue
        
        phase_data = phases[phase_num]
        
        # Run phase
        result = run_phase(variant_name, phase_num, phase_data, state)
        
        if result == "paused":
            # Save state and exit
            state["status"] = "paused"
            state["paused_at"] = timestamp()
            save_json(STATE_FILE, state)
            print(f"\n💾 State saved. Resume with: python orchestrator_core.py --variant {variant_name}")
            break
            
        elif result in ["approved", "skipped"]:
            # Advance to next phase
            state["approvals"].append({
                "phase": phase_num,
                "result": result,
                "timestamp": timestamp()
            })
            state["current_phase"] += 1
            state["last_updated"] = timestamp()
            save_json(STATE_FILE, state)
            
        if state["current_phase"] > 13:
            # Workflow complete
            print(f"\n{'='*70}")
            print("🎯 WORKFLOW COMPLETE!")
            print(f"{'='*70}")
            print(f"Variant '{variant_name}' has completed all 13 phases.")
            print(f"\nNext steps:")
            print(f"  1. Review outputs in: {variant_dir}")
            print(f"  2. Run additional variants if needed")
            print(f"  3. Compare variants: python orchestrator_core.py --compare")
            print(f"{'='*70}\n")
            
            state["status"] = "completed"
            state["completed_at"] = timestamp()
            save_json(STATE_FILE, state)
            log_action(variant_name, 13, "Orchestrator", "Workflow completed")
            break

def compare_variants():
    """Compare all completed variants (Phase 13)"""
    
    print(f"\n{'='*70}")
    print("  CROSS-VARIANT COMPARISON (Phase 13)")
    print(f"{'='*70}\n")
    
    projects_dir = BASE_DIR / "projects"
    variants = [d.name for d in projects_dir.iterdir() 
                if d.is_dir() and not d.name.startswith('_')]
    
    if not variants:
        print("❌ No variants found. Please complete at least one variant first.")
        return
    
    print(f"Found {len(variants)} variant(s): {', '.join(variants)}\n")
    
    # Load key metrics from each variant
    comparison_data = []
    
    for variant in variants:
        variant_dir = projects_dir / variant
        
        # Load metrics
        pain_scores = load_json(variant_dir / "pain_scores.json", {})
        economics = load_json(variant_dir / "unit_economics.json", {})
        decision = load_json(variant_dir / "decision_log.json", {})
        
        comparison_data.append({
            "variant": variant,
            "pain_score": pain_scores.get("records", [{}])[0].get("score_total", "N/A") if pain_scores.get("records") else "N/A",
            "ltv_cac": economics.get("metrics", {}).get("ltv_cac_ratio", "N/A"),
            "payback": economics.get("metrics", {}).get("payback_months", "N/A"),
            "decision": decision.get("decision", "N/A"),
            "confidence": decision.get("confidence", "N/A")
        })
    
    # Display comparison
    print(f"{'='*70}")
    print("COMPARISON MATRIX")
    print(f"{'='*70}\n")
    
    header = f"| {'Metric':<20} | " + " | ".join([f"{v['variant']:<15}" for v in comparison_data]) + " |"
    sep = "|" + ("-" * 22) + "|" + "|".join(["-" * 17 for _ in comparison_data]) + "|"
    
    print(header)
    print(sep)
    
    metrics = [
        ("Pain Score", "pain_score"),
        ("LTV:CAC", "ltv_cac"),
        ("Payback (months)", "payback"),
        ("Decision", "decision"),
        ("Confidence", "confidence")
    ]
    
    for metric_name, metric_key in metrics:
        values = [str(v[metric_key]) for v in comparison_data]
        row = f"| {metric_name:<20} | " + " | ".join([f"{val:<15}" for val in values]) + " |"
        print(row)
    
    print(f"\n{'='*70}\n")
    
    # Save comparison
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    comparison_file = reports_dir / "comparison_matrix.md"
    with open(comparison_file, "w", encoding="utf-8") as f:
        f.write("# Cross-Variant Comparison Matrix\n\n")
        f.write(f"Generated: {timestamp()}\n\n")
        f.write("## Comparison Table\n\n")
        f.write(header + "\n")
        f.write(sep + "\n")
        for metric_name, metric_key in metrics:
            values = [str(v[metric_key]) for v in comparison_data]
            row = f"| {metric_name:<20} | " + " | ".join([f"{val:<15}" for val in values]) + " |"
            f.write(row + "\n")
    
    print(f"✅ Comparison saved to: {comparison_file}\n")
    save_json(reports_dir / "variant_summary.json", comparison_data)
    
    # Next action prompt
    print(f"{'='*70}")
    print("NEXT ACTIONS")
    print(f"{'='*70}")
    print("How would you like to proceed?")
    print("  1. ✅ Advance one variant to development")
    print("  2. 🔗 Combine variants into a hybrid")
    print("  3. ⏸️  Park all variants for now")
    print(f"{'='*70}\n")
    
    choice = input("Your choice [1/2/3]: ").strip()
    
    if choice == "1":
        variant = input("\nWhich variant to advance? ").strip()
        print(f"\n🚀 Advancing '{variant}' to development!")
        log_action(variant, 13, "Planner", f"Variant advanced to development")
        
    elif choice == "2":
        variants_list = input("\nWhich variants to combine? (comma-separated): ").strip()
        print(f"\n🔗 Creating hybrid from: {variants_list}")
        log_action("hybrid", 13, "Planner", f"Hybrid created from: {variants_list}")
        
    else:
        print(f"\n⏸️  All variants parked for future consideration.")
        log_action("all", 13, "Planner", "All variants parked")

# ---------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Variant Exploration System - Orchestrator Core"
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="variant_1",
        help="Variant name (default: variant_1)"
    )
    parser.add_argument(
        "--phase",
        type=int,
        default=None,
        help="Start from specific phase (resume)"
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
        run_orchestrator(args.variant, args.phase)

if __name__ == "__main__":
    main()

