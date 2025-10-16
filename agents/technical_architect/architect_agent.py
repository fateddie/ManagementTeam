"""
architect_agent.py
Phase 3 — Technical Architect Agent
Phase 1.1 Update — Now inherits from BaseAgent
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

Changes in Phase 1.1:
    - Inherits from BaseAgent for standardized interface
    - Depends on StrategyAgent output
    - Renamed run() → execute(context)
    - Returns AgentOutput instead of Dict
    - Accesses strategy data from shared context
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

# Phase 1.1: Import BaseAgent and AgentOutput
from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

# Try to import OpenAI, fall back gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class TechnicalArchitectAgent(BaseAgent):
    """
    Technical architecture agent that converts strategy into technical design.

    Phase 1.1: Now implements BaseAgent interface for standardized orchestration.
    """

    # Phase 1.1: Implement required BaseAgent properties
    @property
    def name(self) -> str:
        """Agent name for identification and logging."""
        return "TechnicalArchitectAgent"

    @property
    def dependencies(self) -> List[str]:
        """
        Depends on StrategyAgent - needs strategy plan to generate architecture.

        The technical design is based on the strategic goals and
        constraints identified by the StrategyAgent.
        """
        return ["StrategyAgent"]

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

    # Phase 1.1: Implement input validation
    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that strategy data is available (either from file or shared context).

        Args:
            context: Execution context with shared agent data

        Returns:
            True if strategy data is available, False otherwise
        """
        # Check if strategy is available from upstream agent
        strategy_output = context.get_agent_output("StrategyAgent")
        if strategy_output:
            return True

        # Fallback: check if strategy file exists
        if self.strategy_path.exists():
            return True

        print(f"❌ Strategy data not available from agent or file: {self.strategy_path}")
        return False

    # Phase 1.1: Renamed run() → execute(), now returns AgentOutput
    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Main execution method - analyze strategy and generate technical design.

        Phase 1.1 Changes:
            - Renamed from run() to execute() for BaseAgent compliance
            - Takes AgentContext parameter
            - Returns AgentOutput instead of Dict
            - Prioritizes shared context data over file reading
            - Includes confidence score and decision reasoning

        Args:
            context: Shared execution context with strategy data

        Returns:
            AgentOutput with technical design data
        """
        # Phase 1.1: Try to get strategy from shared context first
        strategy_output = context.get_agent_output("StrategyAgent")
        if strategy_output:
            print(f"✅ Using strategy data from StrategyAgent (confidence: {strategy_output.confidence})")
            strategy_data = strategy_output.data_for_next_agent
            strategy_text = yaml.safe_dump(strategy_data)
        elif self.strategy_path.exists():
            # Fallback: read from file (for backwards compatibility)
            print(f"⚠️  Reading strategy from file: {self.strategy_path}")
            strategy_text = self.strategy_path.read_text(encoding='utf-8')
            strategy_data = yaml.safe_load(strategy_text)
        else:
            # No strategy data available
            print(f"⚠️  Strategy plan not found, creating fallback design...")
            strategy_data = None
            strategy_text = ""

        # Generate technical design
        if self.llm_enabled:
            technical_design = self._generate_with_llm(strategy_text)
        else:
            technical_design = self._generate_fallback_design(strategy_text, strategy_data)
        
        # Save as YAML
        yaml_output = yaml.safe_dump(
            technical_design,
            sort_keys=False,
            default_flow_style=False
        )
        self.output_path.write_text(yaml_output, encoding='utf-8')

        print(f"✅ Technical design saved to: {self.output_path}")

        # Phase 1.1: Return AgentOutput instead of Dict
        return AgentOutput(
            agent_name=self.name,
            decision="approve",
            reasoning=f"Designed {len(technical_design.get('modules', []))} modules, "
                     f"{len(technical_design.get('data_models', []))} data models based on strategy",
            data_for_next_agent=technical_design,
            confidence=0.85 if self.llm_enabled else 0.70,
            flags=[],
            metadata={
                "strategy_path": str(self.strategy_path),
                "output_path": str(self.output_path),
                "llm_enabled": self.llm_enabled,
                "used_shared_context": strategy_output is not None if 'strategy_output' in locals() else False
            }
        )
    
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
    
    def _generate_fallback_design(self, strategy_text: str = "", strategy_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced fallback technical design - uses recommended_modules from strategy if available."""

        # Extract project name from strategy
        project_name = "AI Management Layer System"
        if strategy_data and 'project' in strategy_data:
            if isinstance(strategy_data['project'], dict):
                project_name = strategy_data['project'].get('name', project_name)
            elif isinstance(strategy_data['project'], str):
                project_name = strategy_data['project']

        # Check if strategy contains recommended modules from addendum
        modules = []
        if strategy_data and 'recommended_modules' in strategy_data:
            modules = strategy_data['recommended_modules']
        else:
            # Fallback to generic modules
            modules = [
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
            ]

        design = {
            "project": project_name,
            "modules": modules,
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

