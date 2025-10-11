"""
documentation_agent.py
Phase 5 – Research & Documentation Integration
---------------------------------------------------------
Compiles PRD and Technical Specification from prior YAML outputs
and research notes.

Purpose:
    Final documentation compilation agent that:
    - Reads project_plan.yaml, technical_design.yaml, research notes
    - Generates professional documentation:
      * prd.md - Product Requirements Document
      * tech_spec.md - Technical Specification
      * final_summary.md - Complete project summary

Outputs:
    - outputs/prd.md
    - outputs/tech_spec.md
    - outputs/final_summary.md
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class DocumentationAgent:
    """
    Documentation generator that compiles all planning artifacts
    into professional documentation.
    """
    
    def __init__(
        self,
        plan_path: str = "./outputs/project_plan.yaml",
        design_path: str = "./outputs/technical_design.yaml",
        research_path: str = "./outputs/research_notes.md",
        output_dir: str = "./outputs/"
    ):
        """
        Initialize Documentation Agent.
        
        Args:
            plan_path: Path to unified project plan
            design_path: Path to technical design
            research_path: Path to research notes
            output_dir: Output directory
        """
        self.plan_path = Path(plan_path)
        self.design_path = Path(design_path)
        self.research_path = Path(research_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def run(self) -> Dict[str, Any]:
        """
        Main execution - generate all documentation.
        
        Returns:
            Dictionary with status and output files
        """
        print("🧾 Documentation Agent running...")
        
        # Check inputs
        if not self.plan_path.exists() or not self.design_path.exists():
            print("⚠️  Missing plan/design — skipping documentation.")
            print(f"   Plan: {'✅' if self.plan_path.exists() else '❌'} {self.plan_path}")
            print(f"   Design: {'✅' if self.design_path.exists() else '❌'} {self.design_path}")
            return {"status": "skipped", "reason": "Missing input files"}

        # Load inputs
        plan = yaml.safe_load(self.plan_path.read_text(encoding='utf-8'))
        design = yaml.safe_load(self.design_path.read_text(encoding='utf-8'))
        research = self.research_path.read_text(encoding='utf-8') if self.research_path.exists() else ""

        print(f"✅ Loaded project plan")
        print(f"✅ Loaded technical design")
        print(f"{'✅' if research else '⚪'} Research notes {'loaded' if research else 'not found (optional)'}")
        
        # Generate documents
        prd_text = self._create_prd(plan, research)
        tech_text = self._create_tech_spec(design, research)
        summary_text = self._create_summary(plan, design, research)

        # Write outputs
        prd_path = self.output_dir / "prd.md"
        tech_path = self.output_dir / "tech_spec.md"
        summary_path = self.output_dir / "final_summary.md"
        
        prd_path.write_text(prd_text, encoding='utf-8')
        tech_path.write_text(tech_text, encoding='utf-8')
        summary_path.write_text(summary_text, encoding='utf-8')
        
        print(f"✅ PRD generated: {prd_path}")
        print(f"✅ Tech spec generated: {tech_path}")
        print(f"✅ Final summary generated: {summary_path}")
        print("✅ Documentation complete.")
        
        return {
            "status": "complete",
            "outputs": ["prd.md", "tech_spec.md", "final_summary.md"],
            "files_generated": 3
        }

    def _create_prd(self, plan: Dict[str, Any], research: str) -> str:
        """Generate Product Requirements Document."""
        project_name = plan.get('project')
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'Unnamed Project')
        
        text = f"# Product Requirements Document\n\n"
        text += f"**Project:** {project_name}  \n"
        text += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
        text += f"**Summary:** {plan.get('summary', 'N/A')}  \n\n"
        text += "---\n\n"
        
        # Goals
        text += "## 🎯 Strategic Goals\n\n"
        for idx, g in enumerate(plan.get("goals", []), start=1):
            text += f"{idx}. {g}\n"
        text += "\n---\n\n"
        
        # Constraints
        text += "## ⚠️ Constraints\n\n"
        constraints = plan.get("constraints", [])
        if constraints:
            for c in constraints:
                text += f"- {c}\n"
        else:
            text += "*No constraints specified*\n"
        text += "\n---\n\n"
        
        # Phases
        text += "## 📋 Phases\n\n"
        for idx, phase in enumerate(plan.get("phases", []), start=1):
            if isinstance(phase, dict):
                text += f"### Phase {idx}: {phase.get('description', phase.get('id', 'Unnamed'))}\n"
                if 'duration_days' in phase:
                    text += f"**Duration:** {phase['duration_days']} days  \n\n"
            else:
                text += f"### Phase {idx}: {phase}\n\n"
        
        text += "---\n\n"
        
        # Risks
        text += "## 🔴 Risks\n\n"
        risks = plan.get("risks", [])
        if risks:
            for r in risks:
                if isinstance(r, dict):
                    text += f"- **{r.get('id', 'RX')}:** {r.get('description', 'N/A')}  \n"
                    text += f"  *Mitigation:* {r.get('mitigation', 'TBD')}  \n\n"
                else:
                    text += f"- {r}\n"
        else:
            text += "*No risks identified*\n"
        
        text += "\n---\n\n"
        
        # Priorities
        text += "## 📊 Priorities (MoSCoW)\n\n"
        priorities = plan.get("priorities", {})
        if isinstance(priorities, dict):
            for category in ['must_have', 'should_have', 'could_have', 'wont_have']:
                items = priorities.get(category, [])
                if items:
                    text += f"### {category.replace('_', ' ').title()}\n"
                    for item in items:
                        text += f"- {item}\n"
                    text += "\n"
        
        text += "---\n\n"
        
        # Research References
        if research:
            text += "## 📚 Research References\n\n"
            text += research
            text += "\n\n"
        
        text += "---\n\n"
        text += f"**Generated by:** Documentation Agent v1.0  \n"
        text += f"**Source Files:** project_plan.yaml, research notes  \n"
        
        return text

    def _create_tech_spec(self, design: Dict[str, Any], research: str) -> str:
        """Generate Technical Specification."""
        text = f"# Technical Specification\n\n"
        text += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n\n"
        text += "---\n\n"
        
        # Modules
        text += "## 🏗️  System Modules\n\n"
        for mod in design.get("modules", []):
            if isinstance(mod, dict):
                text += f"### {mod.get('name', 'Unnamed Module')}\n\n"
                text += f"**Purpose:** {mod.get('purpose', 'N/A')}  \n\n"
                
                if 'inputs' in mod:
                    text += f"**Inputs:**  \n"
                    for inp in mod.get('inputs', []):
                        text += f"- {inp}  \n"
                    text += "\n"
                
                if 'outputs' in mod:
                    text += f"**Outputs:**  \n"
                    for out in mod.get('outputs', []):
                        text += f"- {out}  \n"
                    text += "\n"
                
                if 'dependencies' in mod:
                    deps = mod['dependencies']
                    if isinstance(deps, list):
                        text += f"**Dependencies:** {', '.join(deps)}  \n\n"
                    else:
                        text += f"**Dependencies:** {deps}  \n\n"
                
                text += "---\n\n"
        
        # Data Models
        text += "## 💾 Data Models\n\n"
        for model in design.get("data_models", []):
            if isinstance(model, dict):
                text += f"### {model.get('name', 'Unnamed Model')}\n\n"
                fields = model.get('fields', [])
                if fields:
                    text += "**Fields:**  \n"
                    for field in fields:
                        text += f"- `{field}`  \n"
                    text += "\n"
        
        text += "---\n\n"
        
        # Tech Stack
        text += "## 🔧 Technology Stack\n\n"
        for key, val in design.get("tech_stack", {}).items():
            if isinstance(val, list):
                text += f"**{key.replace('_', ' ').title()}:**  \n"
                for item in val:
                    text += f"- {item}  \n"
                text += "\n"
            else:
                text += f"**{key.replace('_', ' ').title()}:** {val}  \n\n"
        
        text += "---\n\n"
        
        # Interfaces
        text += "## 🔌 Interfaces\n\n"
        for interface in design.get("interfaces", []):
            if isinstance(interface, dict):
                text += f"### {interface.get('agent', 'Unknown Agent')}\n\n"
                text += f"**Provides:** `{interface.get('provides', 'N/A')}`  \n"
                text += f"**Consumes:** `{interface.get('consumes', 'N/A')}`  \n\n"
        
        # Research References
        if research:
            text += "---\n\n"
            text += "## 📚 Research References\n\n"
            text += research
            text += "\n\n"
        
        text += "---\n\n"
        text += f"**Generated by:** Documentation Agent v1.0  \n"
        text += f"**Source Files:** technical_design.yaml, research notes  \n"
        
        return text

    def _create_summary(self, plan: Dict[str, Any], design: Dict[str, Any], research: str) -> str:
        """Generate final project summary."""
        project_name = plan.get('project')
        if isinstance(project_name, dict):
            project_name = project_name.get('name', 'Unnamed Project')
        
        text = f"# 🎉 Final Project Summary\n\n"
        text += f"**Project:** {project_name}  \n"
        text += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  \n"
        text += f"**Status:** Documentation Complete  \n\n"
        text += "---\n\n"
        
        text += "## 📊 Project Overview\n\n"
        text += f"**Summary:** {plan.get('summary', 'N/A')}  \n\n"
        text += f"**Strategic Goals:** {len(plan.get('goals', []))}  \n"
        text += f"**Modules:** {len(design.get('modules', []))}  \n"
        text += f"**Data Models:** {len(design.get('data_models', []))}  \n"
        text += f"**Phases:** {len(plan.get('phases', []))}  \n"
        text += f"**Risks:** {len(plan.get('risks', []))}  \n\n"
        
        text += "---\n\n"
        
        text += "## ✅ Deliverables Generated\n\n"
        text += "- ✅ Product Requirements Document (prd.md)\n"
        text += "- ✅ Technical Specification (tech_spec.md)\n"
        text += "- ✅ Project Plan (project_plan.yaml)\n"
        text += "- ✅ Roadmap (roadmap.md)\n"
        text += "- ✅ Dependency Map (dependency_map.yaml)\n"
        text += "- ✅ Final Summary (this document)\n\n"
        
        text += "---\n\n"
        
        text += "## 🎯 Next Steps\n\n"
        text += "1. Review generated documentation\n"
        text += "2. Validate against requirements\n"
        text += "3. Begin implementation using generated specs\n"
        text += "4. Track progress against milestones\n\n"
        
        if research:
            text += "---\n\n"
            text += "## 📚 Key Research Sources\n\n"
            text += research[:1000]  # First 1000 chars
            if len(research) > 1000:
                text += "\n\n*(...research truncated)*\n"
            text += "\n\n"
        
        text += "---\n\n"
        text += f"**Generated by:** Documentation Agent v1.0  \n"
        text += f"**Phase:** 5 - Final Documentation  \n"
        text += f"**All Agents:** Strategy → Architecture → Planning → Research → Documentation  \n"
        
        return text


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧾 DOCUMENTATION AGENT - PHASE 5")
    print("=" * 70 + "\n")
    
    agent = DocumentationAgent()
    
    print(f"📖 Reading from:")
    print(f"   - Project Plan: {agent.plan_path}")
    print(f"   - Technical Design: {agent.design_path}")
    print(f"   - Research Notes: {agent.research_path}")
    print()
    
    try:
        result = agent.run()
        
        if result.get("status") == "skipped":
            print(f"\n⚠️  Skipped: {result.get('reason')}")
        else:
            print(f"\n✅ Documentation generation complete!")
            print(f"\n📄 Generated Documents:")
            for doc in result.get('outputs', []):
                print(f"   ✅ {doc}")
        
        print("\n" + "=" * 70)
        print("✅ DOCUMENTATION AGENT TEST COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

