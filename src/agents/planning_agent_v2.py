"""
planning_agent.py
Phase 4 – Integration Upgrade
---------------------------------------------------------
Reads strategy_plan.yaml + technical_design.yaml and generates
a unified project plan and roadmap.

Purpose:
    Central coordinator for plan generation that:
    - Merges strategy and technical architecture
    - Generates unified project plan
    - Creates human-readable roadmap
    - Maps dependencies between modules

Outputs:
    - project_plan.yaml - Unified project plan
    - roadmap.md - Human-readable roadmap
    - dependency_map.yaml - Module dependencies
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class PlanningAgent:
    """
    Integration-upgraded Planning Agent that merges strategy and technical design
    into unified project plans.
    """
    
    def __init__(
        self,
        strategy_path: str = "./outputs/strategy_plan.yaml",
        design_path: str = "./outputs/technical_design.yaml",
        output_dir: str = "./outputs/"
    ):
        """
        Initialize Planning Agent with input/output paths.
        
        Args:
            strategy_path: Path to strategy_plan.yaml
            design_path: Path to technical_design.yaml
            output_dir: Directory for output files
        """
        self.strategy_path = Path(strategy_path)
        self.design_path = Path(design_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def run(self) -> Dict[str, Any]:
        """
        Main execution - merge inputs and generate unified plan.
        
        Returns:
            Merged project plan dictionary
        """
        print("🧭 Planning Agent – Integration Upgrade")
        
        # Check inputs
        if not self.strategy_path.exists() or not self.design_path.exists():
            print("⚠️  Missing inputs – skipping full integration.")
            print(f"   Strategy: {'✅' if self.strategy_path.exists() else '❌'} {self.strategy_path}")
            print(f"   Design: {'✅' if self.design_path.exists() else '❌'} {self.design_path}")
            return {"status": "skipped", "reason": "Missing input files"}

        # Load inputs
        strategy = yaml.safe_load(self.strategy_path.read_text(encoding='utf-8'))
        design = yaml.safe_load(self.design_path.read_text(encoding='utf-8'))
        
        print(f"✅ Loaded strategy plan: {len(strategy.get('goals', []))} goals")
        print(f"✅ Loaded technical design: {len(design.get('modules', []))} modules")
        
        # Merge
        plan = self._merge(strategy, design)
        
        # Write outputs
        self._write_outputs(plan)
        
        return plan

    def _merge(self, strategy: Dict[str, Any], design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge strategy and design into unified plan.
        
        Args:
            strategy: Strategy plan data
            design: Technical design data
            
        Returns:
            Merged project plan
        """
        merged = {
            "project": strategy.get("project", {}) or design.get("project", "Unnamed"),
            "summary": strategy.get("project", {}).get("summary", "") if isinstance(strategy.get("project"), dict) else "",
            "goals": strategy.get("goals", []),
            "constraints": strategy.get("constraints", []),
            "phases": strategy.get("milestones", []),
            "modules": design.get("modules", []),
            "data_models": design.get("data_models", []),
            "tech_stack": design.get("tech_stack", {}),
            "interfaces": design.get("interfaces", []),
            "risks": strategy.get("risks", []),
            "priorities": strategy.get("priorities", {}),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"✅ Merged plan: {len(merged.get('modules', []))} modules, {len(merged.get('goals', []))} goals")
        
        return merged

    def _write_outputs(self, plan: Dict[str, Any]):
        """
        Write all output files.
        
        Args:
            plan: Merged project plan
        """
        # 1. Write project plan YAML
        plan_path = self.output_dir / "project_plan.yaml"
        with plan_path.open("w", encoding='utf-8') as f:
            yaml.safe_dump(plan, f, sort_keys=False, default_flow_style=False)
        print(f"✅ Project plan written to {plan_path}")

        # 2. Write dependency map YAML
        dep_map = {
            "modules": plan.get("modules", []),
            "generated_at": plan.get("generated_at")
        }
        dep_path = self.output_dir / "dependency_map.yaml"
        with dep_path.open("w", encoding='utf-8') as f:
            yaml.safe_dump(dep_map, f, sort_keys=False, default_flow_style=False)
        print(f"✅ Dependency map written to {dep_path}")

        # 3. Write roadmap Markdown
        roadmap_path = self.output_dir / "roadmap.md"
        with roadmap_path.open("w", encoding='utf-8') as f:
            f.write(f"# 📅 Project Roadmap – {plan['project']}\n\n")
            f.write(f"**Generated:** {plan.get('generated_at')}  \n\n")
            f.write("---\n\n")
            
            # Goals
            f.write("## 🎯 Strategic Goals\n\n")
            for idx, goal in enumerate(plan.get("goals", []), start=1):
                f.write(f"{idx}. {goal}\n")
            f.write("\n---\n\n")
            
            # Phases/Milestones
            f.write("## 📋 Phases\n\n")
            for idx, phase in enumerate(plan.get("phases", []), start=1):
                if isinstance(phase, dict):
                    f.write(f"### Phase {idx}: {phase.get('description', phase.get('id', 'Unnamed'))}\n")
                    if 'duration_days' in phase:
                        f.write(f"**Duration:** {phase['duration_days']} days  \n")
                else:
                    f.write(f"### Phase {idx}: {phase}\n")
                f.write("\n")
            
            f.write("---\n\n")
            
            # Tech Stack
            f.write("## 🔧 Technical Stack\n\n")
            for key, val in plan.get("tech_stack", {}).items():
                if isinstance(val, list):
                    f.write(f"**{key.replace('_', ' ').title()}:** {', '.join(val)}  \n")
                else:
                    f.write(f"**{key.replace('_', ' ').title()}:** {val}  \n")
            
            f.write("\n---\n\n")
            
            # Modules
            f.write("## 🏗️  System Modules\n\n")
            for module in plan.get("modules", []):
                if isinstance(module, dict):
                    f.write(f"### {module.get('name', 'Unnamed Module')}\n")
                    f.write(f"**Purpose:** {module.get('purpose', 'N/A')}  \n")
                    if 'dependencies' in module:
                        f.write(f"**Dependencies:** {', '.join(module['dependencies']) if isinstance(module['dependencies'], list) else module['dependencies']}  \n")
                    f.write("\n")
            
            f.write("---\n\n")
            f.write(f"**Generated by:** Planning Agent v4.0 (Integration Upgrade)  \n")
        
        print(f"✅ Roadmap written to {roadmap_path}")


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧭 PLANNING AGENT v4.0 - INTEGRATION UPGRADE")
    print("=" * 70 + "\n")
    
    agent = PlanningAgent()
    
    print(f"📖 Reading from:")
    print(f"   - Strategy: {agent.strategy_path}")
    print(f"   - Design: {agent.design_path}")
    print()
    
    try:
        result = agent.run()
        
        if result.get("status") == "skipped":
            print(f"\n⚠️  Skipped: {result.get('reason')}")
        else:
            print(f"\n✅ Planning complete!")
            print(f"\n📊 Merged Plan Contains:")
            print(f"   - Goals: {len(result.get('goals', []))}")
            print(f"   - Modules: {len(result.get('modules', []))}")
            print(f"   - Data Models: {len(result.get('data_models', []))}")
            print(f"   - Risks: {len(result.get('risks', []))}")
        
        print("\n" + "=" * 70)
        print("✅ PLANNING AGENT TEST COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
