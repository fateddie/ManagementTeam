"""
architect_agent.py
Phase 3 — Technical Architect Agent
---------------------------------------------------------
Converts strategy_plan.yaml into a structured technical design document.

Purpose:
    Analyzes strategic plan and generates technical architecture including:
    - System modules and their purposes
    - Inputs, outputs, and dependencies
    - Recommended tech stack
    - Data models and schemas
    - Interface definitions

Output:
    technical_design.yaml with complete technical architecture
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import OpenAI, fall back gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class TechnicalArchitectAgent:
    """
    Technical architecture agent that converts strategy into technical design.
    """
    
    def __init__(
        self, 
        strategy_path: str = "./outputs/strategy_plan.yaml",
        output_path: str = "./outputs/technical_design.yaml"
    ):
        """
        Initialize Technical Architect Agent.
        
        Args:
            strategy_path: Path to strategy_plan.yaml
            output_path: Where to save technical_design.yaml
        """
        self.strategy_path = Path(strategy_path)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and not api_key.startswith("sk-your"):
                self.client = OpenAI(api_key=api_key)
                self.llm_enabled = True
            else:
                self.client = None
                self.llm_enabled = False
        else:
            self.client = None
            self.llm_enabled = False
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution method - analyze strategy and generate technical design.
        
        Returns:
            Dictionary containing technical design data
        """
        # Check if strategy plan exists
        if not self.strategy_path.exists():
            print(f"⚠️  Strategy plan not found: {self.strategy_path}")
            print("   Creating fallback technical design...")
            return self._generate_fallback_design()
        
        # Read strategy plan
        strategy_text = self.strategy_path.read_text(encoding='utf-8')
        
        # Generate technical design
        if self.llm_enabled:
            technical_design = self._generate_with_llm(strategy_text)
        else:
            technical_design = self._generate_fallback_design(strategy_text)
        
        # Save as YAML
        yaml_output = yaml.safe_dump(
            technical_design, 
            sort_keys=False, 
            default_flow_style=False
        )
        self.output_path.write_text(yaml_output, encoding='utf-8')
        
        print(f"✅ Technical design saved to: {self.output_path}")
        
        return technical_design
    
    def _generate_with_llm(self, strategy_text: str) -> Dict[str, Any]:
        """Generate technical design using OpenAI."""
        prompt = f"""You are a senior technical architect.

Read this strategy plan and design a complete technical architecture:
1. System modules with purposes
2. Inputs, outputs, and dependencies for each module
3. Recommended tech stack (backend, storage, orchestration)
4. Data models with field definitions
5. Interface definitions between components

Output strictly in valid YAML format.

STRATEGY PLAN:
{strategy_text}
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        yaml_text = response.choices[0].message.content.strip()
        
        # Extract YAML from markdown code blocks if present
        import re
        if "```yaml" in yaml_text:
            yaml_text = re.search(r'```yaml\n(.*?)\n```', yaml_text, re.DOTALL).group(1)
        elif "```" in yaml_text:
            yaml_text = re.search(r'```\n(.*?)\n```', yaml_text, re.DOTALL).group(1)
        
        data = yaml.safe_load(yaml_text)
        return data
    
    def _generate_fallback_design(self, strategy_text: str = "") -> Dict[str, Any]:
        """Fallback technical design without LLM."""
        design = {
            "project": "AI Management Layer System",
            "modules": [
                {
                    "name": "PlanningAgent",
                    "purpose": "Converts strategy YAML to roadmap and milestones",
                    "inputs": ["strategy_plan.yaml"],
                    "outputs": ["roadmap.md", "project_plan.yaml"],
                    "dependencies": ["ResearchAgent"]
                },
                {
                    "name": "ResearchAgent",
                    "purpose": "Fetches external frameworks and references",
                    "inputs": ["research_queries"],
                    "outputs": ["research_summaries"],
                    "interfaces": ["Perplexity API"]
                },
                {
                    "name": "Orchestrator",
                    "purpose": "Controls sequencing and logging across agents",
                    "inputs": ["agent_registry.yaml"],
                    "outputs": ["session_summary.md", "logs"],
                    "dependencies": ["All active agents"]
                }
            ],
            "data_models": [
                {
                    "name": "ProjectPlan",
                    "fields": ["goal", "constraint", "milestone_id", "risk_id"]
                },
                {
                    "name": "RiskRegister",
                    "fields": ["risk_id", "description", "mitigation"]
                },
                {
                    "name": "StrategyPlan",
                    "fields": ["goals", "constraints", "milestones", "priorities"]
                }
            ],
            "tech_stack": {
                "backend": ["Python 3.11", "YAML", "OpenAI API"],
                "storage": ["Local JSON/YAML files"],
                "orchestration": ["Logging", "Pathlib", "Importlib"]
            },
            "interfaces": [
                {
                    "agent": "PlanningAgent",
                    "provides": "plan_generation()",
                    "consumes": "strategy_plan.yaml"
                },
                {
                    "agent": "ResearchAgent",
                    "provides": "search(query, focus)",
                    "consumes": "research_queries"
                },
                {
                    "agent": "StrategyAgent",
                    "provides": "strategy_extraction()",
                    "consumes": "PRD.md"
                }
            ]
        }
        
        return design


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🏗️  TECHNICAL ARCHITECT AGENT - PHASE 3")
    print("=" * 70 + "\n")
    
    agent = TechnicalArchitectAgent()
    
    if agent.llm_enabled:
        print("✅ OpenAI client initialized")
    else:
        print("⚠️  OpenAI not available - using fallback design")
    
    print(f"📖 Reading strategy from: {agent.strategy_path}")
    
    try:
        result = agent.run()
        
        print(f"\n✅ Technical design generated!")
        print(f"📁 Saved to: {agent.output_path}")
        print(f"\n📊 Generated:")
        print(f"   - Modules: {len(result.get('modules', []))}")
        print(f"   - Data Models: {len(result.get('data_models', []))}")
        print(f"   - Interfaces: {len(result.get('interfaces', []))}")
        
        print("\n" + "=" * 70)
        print("✅ TECHNICAL ARCHITECT AGENT TEST COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

