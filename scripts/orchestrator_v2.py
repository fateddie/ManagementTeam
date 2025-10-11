"""
orchestrator.py
Phase 1: Orchestration Setup
---------------------------------------------------------
Connects Planning Agent and Research Connector to create
a unified planning workflow with automatic research validation.

Purpose:
    - Coordinate PlanningAgent and PerplexityConnector
    - Run complete planning cycle
    - Generate session summaries
    - Log all activities for audit trail

Usage:
    python scripts/orchestrator_v2.py
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.planning_agent_v2 import PlanningAgent
from src.utils.perplexity_connector import PerplexityConnector
from src.utils.config_loader import load_env, get_env

# Ensure environment is loaded
load_env()


class Orchestrator:
    """
    Phase 1 Orchestrator - Coordinates Planning Agent with Research Connector.
    
    This orchestrator manages the workflow between:
    - Context-aware Planning Agent (reads project docs)
    - Perplexity Research Connector (validates with external research)
    """
    
    def __init__(self):
        """Initialize the orchestrator with logging and session tracking."""
        self.log_path = Path("./logs/orchestrator.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger("orchestrator")
        
        # Create session ID
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.logger.info(f"🚀 Session start: {self.session_id}")
        
        # Results storage
        self.results = {}
        
        print("\n" + "=" * 70)
        print(f"🎭 ORCHESTRATOR v2.0 - Session {self.session_id}")
        print("=" * 70 + "\n")

    def run(self) -> dict:
        """
        Execute the complete orchestration workflow.
        
        Workflow:
        1. Initialize Planning Agent
        2. Run planning cycle (loads context, generates milestones)
        3. Validate with Perplexity research
        4. Generate session summary
        
        Returns:
            Dictionary with planning and research results
        """
        try:
            # Step 1: Planning
            self.logger.info("📋 Running planning cycle")
            print("📋 Step 1: Running Planning Agent...")
            
            planner = PlanningAgent()
            plan_results = planner.run_cycle()
            self.results["planning"] = plan_results
            
            self.logger.info(f"✅ Planning complete: {len(plan_results)} stages executed")
            print(f"✅ Planning complete: {len(plan_results)} stages")
            
            # Step 2: Research Validation
            self.logger.info("🔍 Running research validation")
            print("\n🔍 Step 2: Validating with Perplexity Research...")
            
            try:
                research = PerplexityConnector()
                topic = "current best practices for AI project orchestration frameworks"
                research_result = research.search(topic, focus="research")
                self.results["research"] = research_result
                
                self.logger.info(f"✅ Research complete: {len(research_result.get('summary', ''))} chars")
                print(f"✅ Research complete")
                
            except ValueError as e:
                # Perplexity not configured - skip gracefully
                self.logger.warning(f"⚠️  Research skipped: {e}")
                print(f"⚠️  Research skipped (API key not set)")
                self.results["research"] = {"skipped": str(e)}
            
            # Step 3: Write summary
            self.logger.info("📝 Generating session summary")
            print("\n📝 Step 3: Generating Summary...")
            
            self._write_summary()
            
            self.logger.info("✅ Session complete")
            print("\n✅ Session complete!")
            
            return self.results
            
        except Exception as e:
            self.logger.error(f"❌ Orchestration failed: {e}")
            print(f"\n❌ Error: {e}")
            raise

    def _write_summary(self):
        """Generate a comprehensive session summary in Markdown format."""
        path = Path(f"./outputs/session_summary_{self.session_id}.md")
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# 🎭 Orchestration Session Summary\n\n")
            f.write(f"**Session ID:** {self.session_id}  \n")
            f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC  \n")
            f.write(f"**Phase:** 1 - Orchestration Setup  \n\n")
            f.write("---\n\n")
            
            # Planning Results
            f.write("## 📋 Planning Results\n\n")
            planning = self.results.get("planning", {})
            
            for stage_name, stage_result in planning.items():
                f.write(f"### {stage_name.replace('_', ' ').title()}\n\n")
                if isinstance(stage_result, dict):
                    for key, value in stage_result.items():
                        f.write(f"**{key}:** {value}\n\n")
                else:
                    f.write(f"{stage_result}\n\n")
            
            # Research Results
            f.write("---\n\n")
            f.write("## 🔍 Research Validation\n\n")
            research = self.results.get("research", {})
            
            if "skipped" in research:
                f.write(f"⚠️ Research was skipped: {research['skipped']}\n\n")
            else:
                f.write(f"**Query:** {research.get('query', 'N/A')}  \n")
                f.write(f"**Model:** {research.get('model', 'N/A')}  \n\n")
                f.write(f"{research.get('summary', 'No summary available')}\n\n")
                
                if research.get('sources'):
                    f.write("**Sources:**\n\n")
                    for source in research['sources']:
                        f.write(f"- {source}\n")
            
            f.write("\n---\n\n")
            f.write(f"**Generated by:** Orchestrator v2.0  \n")
            f.write(f"**Log file:** {self.log_path}  \n")
        
        self.logger.info(f"📄 Summary written to {path}")
        print(f"📄 Summary written to: {path}")
        
        return path


# ---------------------------------------------------------
# Example Direct Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎭 ORCHESTRATOR V2.0 - PHASE 1 IMPLEMENTATION")
    print("=" * 70)
    print("\nThis orchestrator coordinates:")
    print("  1. Planning Agent (context-aware)")
    print("  2. Perplexity Research (validation)")
    print("  3. Session summary generation")
    print("\n" + "=" * 70 + "\n")
    
    orchestrator = Orchestrator()
    results = orchestrator.run()
    
    print("\n" + "=" * 70)
    print("📊 ORCHESTRATION COMPLETE")
    print("=" * 70)
    print(f"\n✅ Planning stages: {len(results.get('planning', {}))}")
    print(f"✅ Research: {'Completed' if 'summary' in results.get('research', {}) else 'Skipped'}")
    print(f"📁 Check outputs/ for session summary")
    print("\n" + "=" * 70 + "\n")

