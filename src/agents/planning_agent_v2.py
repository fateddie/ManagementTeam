"""
planning_agent.py
---------------------------------------------------------
Main Planning Agent module.
Automatically loads project context, analyzes scope,
and generates a structured roadmap and milestones file.

Dependencies:
  - initialize_context.py
  - planning_agent_context.yaml
---------------------------------------------------------
"""

import os
import yaml
import datetime
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.initialize_context import initialize_context
from src.utils.log_utils import logger


# ---------------------------------------------------------
# Core PlanningAgent Class
# ---------------------------------------------------------

class PlanningAgent:
    """
    Context-aware Planning Agent with full planning cycle.
    
    Workflow:
    → Agent Invoked
       → Auto Context Load (docs/, config/, context/)
          → Parse + Summarize + Validate
          → Store context in memory
       → Run Planning Logic (scope analysis, milestone generation, etc.)
       → Output results (roadmap.md, dependency_map.yaml)
    """
    
    def __init__(self, config_path: str = "./config/planning_agent_context.yaml"):
        """
        Initialize the Planning Agent.
        
        Args:
            config_path: Path to context configuration file
        """
        self.config_path = config_path
        self.context = None
        self.config = None
        self.outputs_dir = Path("./outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        self._load_config()
        logger.info("🤖 Planning Agent v2 initialized")

    # -----------------------------------------------------
    # Initialization and Context Load
    # -----------------------------------------------------

    def _load_config(self):
        """Load the planning agent context configuration."""
        with open(self.config_path, "r") as f:
            self.config = yaml.safe_load(f)
        logger.info(f"📋 Loaded config from {self.config_path}")

    def initialize(self):
        """Auto-load project context before any reasoning."""
        logger.info("🔄 Initializing Planning Agent context...")
        print("🔄 Initializing Planning Agent context...")
        self.context = initialize_context(self.config_path)
        logger.info(f"✅ Context loaded ({len(self.context['files'])} files).")
        print(f"✅ Context loaded ({len(self.context['files'])} files).")

    # -----------------------------------------------------
    # Planning Cycle
    # -----------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """
        Execute the full planning cycle as defined in YAML config.
        
        Returns:
            Dictionary containing results from each stage
        """
        if not self.context:
            self.initialize()

        stages = self.config.get("planning_cycle", {}).get("stages", [])
        results = {}

        logger.info("🚀 Starting planning cycle...")
        print("\n" + "=" * 70)
        print("🚀 STARTING PLANNING CYCLE")
        print("=" * 70)

        for stage in stages:
            name = stage.get("name")
            goal = stage.get("goal")
            action = stage.get("action")
            
            logger.info(f"🧭 Stage: {name} → {goal}")
            print(f"\n🧭 Stage: {name.upper()} → {goal}")

            if name == "context_check":
                results[name] = self._context_check()
            elif name == "scope_analysis":
                results[name] = self._scope_analysis()
            elif name == "dependency_mapping":
                results[name] = self._dependency_mapping()
            elif name == "milestone_generation":
                results[name] = self._generate_milestones()
            elif name == "review_cycle":
                results[name] = self._review_cycle()
            else:
                logger.warning(f"⚠️  Unknown stage '{name}' — skipping.")
                print(f"⚠️  Unknown stage '{name}' — skipping.")
        
        logger.info("✅ Planning cycle complete")
        return results

    # -----------------------------------------------------
    # Stage Implementations
    # -----------------------------------------------------

    def _context_check(self) -> str:
        """Confirm all key context pieces are present."""
        prd_present = "PRD.md" in self.context["files"]
        roadmap_present = any("roadmap" in f.lower() for f in self.context["files"])
        summary = self.context["summary"]

        status = "✅ Context complete" if prd_present else "❌ Missing PRD.md"
        logger.info(status)
        print(status)
        
        return f"Context check: {status}\n\nSummary:\n{summary[:500]}..."

    def _scope_analysis(self) -> Dict[str, Any]:
        """Extract project scope, goals, and deliverables from PRD."""
        prd = self.context["files"].get("PRD.md", "")
        goals, deliverables, risks = [], [], []

        for line in prd.splitlines():
            line_lower = line.lower()
            if "goal" in line_lower and line.strip().startswith(("-", "*")):
                goals.append(line.strip("- *"))
            if "deliverable" in line_lower and line.strip().startswith(("-", "*")):
                deliverables.append(line.strip("- *"))
            if "risk" in line_lower and line.strip().startswith(("-", "*")):
                risks.append(line.strip("- *"))

        scope_summary = {
            "goals": goals[:10],
            "deliverables": deliverables[:10],
            "risks": risks[:10],
        }

        logger.info(f"🧩 Extracted {len(goals)} goals, {len(deliverables)} deliverables.")
        print(f"🧩 Extracted {len(goals)} goals, {len(deliverables)} deliverables.")
        
        return scope_summary

    def _dependency_mapping(self) -> Dict[str, List[str]]:
        """Simple dependency mapping placeholder — can later link features to milestones."""
        roadmap = self.context["files"].get("roadmap.md", "")
        dependencies = []

        for line in roadmap.splitlines():
            if "depends on" in line.lower() or "dependency" in line.lower():
                dependencies.append(line.strip())

        mapping = {"dependencies": dependencies}
        
        logger.info(f"🔗 Found {len(dependencies)} dependency links.")
        print(f"🔗 Found {len(dependencies)} dependency links.")
        
        return mapping

    def _generate_milestones(self) -> Dict[str, Any]:
        """Auto-generate milestone plan from PRD data."""
        goals = self._scope_analysis().get("goals", [])
        milestone_list = []
        today = datetime.date.today()

        for i, goal in enumerate(goals[:5]):
            milestone_list.append({
                "id": f"M{i+1}",
                "description": goal,
                "target_date": str(today + datetime.timedelta(weeks=(i + 1))),
                "status": "Planned"
            })

        # Write roadmap.md
        roadmap_path = self.outputs_dir / "roadmap.md"
        with open(roadmap_path, "w") as f:
            f.write("# 📅 Project Roadmap\n\n")
            f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("---\n\n")
            for m in milestone_list:
                f.write(f"### {m['id']}: {m['description']}\n")
                f.write(f"- Target Date: {m['target_date']}\n")
                f.write(f"- Status: {m['status']}\n\n")

        logger.info(f"🗓️  Milestones written to {roadmap_path}")
        print(f"🗓️  Milestones written to {roadmap_path}")
        
        return {"milestones": milestone_list, "output_file": str(roadmap_path)}

    def _review_cycle(self) -> str:
        """Final check before plan publication."""
        roadmap = self.outputs_dir / "roadmap.md"
        if roadmap.exists():
            logger.info("✅ Review complete — roadmap ready for next stage.")
            print("✅ Review complete — roadmap ready for next stage.")
            return "Review complete — roadmap verified and ready."
        else:
            logger.warning("⚠️  No roadmap found during review.")
            print("⚠️  No roadmap found during review.")
            return "Review failed — roadmap missing."

    # -----------------------------------------------------
    # Helper Methods
    # -----------------------------------------------------

    def summarize_results(self, results: Dict[str, Any]) -> str:
        """Create a markdown summary of planning cycle results."""
        lines = ["# 🧾 Planning Cycle Summary\n"]
        lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        lines.append("---\n")
        
        for k, v in results.items():
            lines.append(f"## {k.replace('_', ' ').title()}\n")
            if isinstance(v, dict):
                for key, val in v.items():
                    lines.append(f"**{key}:** {val}\n")
            else:
                lines.append(f"{v}\n")
            lines.append("\n")
        
        return "\n".join(lines)

    def get_context_summary(self) -> str:
        """Get current context summary."""
        if not self.context:
            return "No context loaded. Run initialize() first."
        return self.context.get("summary", "")


# ---------------------------------------------------------
# Example Direct Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧭 PLANNING AGENT V2 - CONTEXT-AWARE EXECUTION")
    print("=" * 70 + "\n")
    
    agent = PlanningAgent()
    results = agent.run_cycle()

    summary_text = agent.summarize_results(results)
    summary_path = agent.outputs_dir / "planning_summary.md"
    with open(summary_path, "w") as f:
        f.write(summary_text)

    print("\n" + "=" * 70)
    print(f"📘 Summary written to {summary_path}")
    print("=" * 70)
    print("\n📋 RESULTS:")
    print(summary_text)
    print("\n" + "=" * 70)
    print("✅ PLANNING CYCLE COMPLETE")
    print("=" * 70 + "\n")
