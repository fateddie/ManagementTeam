# ==============================================
# file: /ManagementTeam/src/agents/planning_agent_with_research.py
# ==============================================
"""
Planning Agent with Perplexity Research Integration
----------------------------------------------------
Enhanced Planning Agent that can query Perplexity AI for:
  - Latest frameworks and best practices
  - Technical research on topics
  - Industry trends and news
  - Code examples and patterns

Workflow:
  1. Load context from docs/
  2. Identify knowledge gaps
  3. Query Perplexity for missing information
  4. Incorporate research into planning
  5. Generate comprehensive roadmap
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import yaml
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.initialize_context import initialize_context
from src.utils.perplexity_connector import PerplexityConnector
from src.utils.log_utils import logger


class PlanningAgentWithResearch:
    """
    Context-aware Planning Agent enhanced with Perplexity research capabilities.
    """
    
    def __init__(self, config_path: str = "./config/planning_agent_context.yaml"):
        """
        Initialize the enhanced Planning Agent.
        
        Args:
            config_path: Path to context configuration file
        """
        self.config_path = config_path
        self.context: Optional[Dict[str, Any]] = None
        self.perplexity: Optional[PerplexityConnector] = None
        self.research_cache: Dict[str, Any] = {}
        self.outputs_dir = Path("./outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        logger.info("🤖 Planning Agent with Research initialized")
    
    def initialize(self, enable_research: bool = True):
        """
        Initialize context and optionally enable Perplexity research.
        
        Args:
            enable_research: Whether to enable Perplexity integration
        """
        logger.info("📚 Loading project context...")
        self.context = initialize_context(self.config_path)
        logger.info(f"✅ Context loaded: {len(self.context['files'])} files")
        
        if enable_research:
            try:
                self.perplexity = PerplexityConnector()
                logger.info("✅ Perplexity research enabled")
            except ValueError as e:
                logger.warning(f"⚠️  Perplexity not available: {e}")
                self.perplexity = None
    
    def research_topic(self, topic: str, focus: str = "research") -> Dict[str, Any]:
        """
        Query Perplexity for research on a specific topic.
        
        Args:
            topic: Research question or topic
            focus: Context mode (research/news/code)
            
        Returns:
            Research result dictionary
        """
        if not self.perplexity:
            logger.warning("⚠️  Perplexity not enabled, skipping research")
            return {"error": "Perplexity not enabled"}
        
        # Check cache first
        cache_key = f"{topic}_{focus}"
        if cache_key in self.research_cache:
            logger.info(f"📦 Using cached research for: {topic}")
            return self.research_cache[cache_key]
        
        logger.info(f"🔍 Researching: {topic}")
        result = self.perplexity.search(topic, focus=focus)
        
        # Cache result
        self.research_cache[cache_key] = result
        logger.info(f"✅ Research complete: {len(result['summary'])} chars")
        
        return result
    
    def identify_research_needs(self) -> List[str]:
        """
        Analyze context to identify topics that need research.
        
        Returns:
            List of research topics
        """
        topics = []
        
        # Look for TODO, TBD, or question marks in docs
        for filename, content in self.context["files"].items():
            if isinstance(content, str):
                if "TODO" in content or "TBD" in content or "?" in content:
                    # Extract the line for research
                    for line in content.splitlines():
                        if any(marker in line for marker in ["TODO:", "TBD:", "Research:"]):
                            topics.append(line.strip("- *#"))
        
        logger.info(f"🔍 Identified {len(topics)} potential research topics")
        return topics[:5]  # Limit to top 5
    
    def generate_enhanced_roadmap(self, project_name: str) -> Dict[str, Any]:
        """
        Generate a roadmap enhanced with Perplexity research.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Dictionary with roadmap path and research results
        """
        if not self.context:
            self.initialize()
        
        logger.info(f"🗺️  Generating enhanced roadmap for: {project_name}")
        
        # 1. Identify what needs research
        research_topics = self.identify_research_needs()
        
        # 2. Conduct research if topics found
        research_results = []
        if research_topics and self.perplexity:
            logger.info(f"📡 Conducting research on {len(research_topics)} topics...")
            for topic in research_topics:
                result = self.research_topic(topic, focus="research")
                if "error" not in result:
                    research_results.append(result)
        
        # 3. Generate roadmap with research insights
        roadmap_path = self.outputs_dir / f"{project_name}_roadmap_enhanced.md"
        
        with open(roadmap_path, "w", encoding="utf-8") as f:
            f.write(f"# 🗺️ Enhanced Project Roadmap: {project_name}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Research-Enhanced:** {'Yes' if research_results else 'No'}\n\n")
            f.write("---\n\n")
            
            # Add research section
            if research_results:
                f.write("## 📚 Research Insights\n\n")
                f.write("*The following research was automatically conducted to inform this roadmap:*\n\n")
                
                for result in research_results:
                    f.write(PerplexityConnector.format_markdown(result))
                    f.write("\n\n---\n\n")
            
            # Add milestones section (using scope analysis)
            f.write("## 📋 Milestones\n\n")
            
            # Extract goals from PRD
            prd_content = self.context["files"].get("PRD.md", "")
            goals = []
            for line in prd_content.splitlines():
                if line.strip().startswith(("-", "*")) and any(word in line.lower() for word in ["goal", "objective", "deliver"]):
                    goals.append(line.strip("- *"))
            
            # Generate milestones from goals
            for i, goal in enumerate(goals[:10], 1):
                f.write(f"### M{i}: {goal[:80]}\n")
                f.write(f"- **Target:** Week {i}\n")
                f.write(f"- **Status:** Planned\n\n")
            
            f.write("\n---\n\n")
            f.write(f"**Generated by:** Planning Agent with Research v2.0\n")
            f.write(f"**Context Files:** {len(self.context['files'])}\n")
            f.write(f"**Research Queries:** {len(research_results)}\n")
        
        logger.info(f"✅ Enhanced roadmap written to: {roadmap_path}")
        
        return {
            "roadmap_path": str(roadmap_path),
            "research_conducted": len(research_results),
            "topics_researched": research_topics,
            "context_files": len(self.context['files'])
        }


# ---------------------------------------------------------
# Integration Example: Usage from Planning Agent
# ---------------------------------------------------------
def planning_with_research_example():
    """
    Example showing how to use Perplexity in planning workflow.
    """
    print("\n" + "=" * 70)
    print("🧭 PLANNING AGENT WITH PERPLEXITY RESEARCH - DEMO")
    print("=" * 70 + "\n")
    
    # Create agent
    agent = PlanningAgentWithResearch()
    
    # Initialize with research enabled
    agent.initialize(enable_research=True)
    
    # Generate enhanced roadmap
    result = agent.generate_enhanced_roadmap("AI-Management-Layer")
    
    print("\n" + "=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)
    print(f"Roadmap: {result['roadmap_path']}")
    print(f"Research Queries: {result['research_conducted']}")
    print(f"Context Files: {result['context_files']}")
    
    if result['topics_researched']:
        print(f"\nTopics Researched:")
        for topic in result['topics_researched']:
            print(f"  - {topic[:80]}")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70 + "\n")


# ---------------------------------------------------------
# Example Direct Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    planning_with_research_example()

