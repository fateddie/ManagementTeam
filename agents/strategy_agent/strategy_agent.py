"""
strategy_agent.py
Phase 2 — Strategy Agent
Phase 1.1 Update — Now inherits from BaseAgent
---------------------------------------------------------
Converts free-form briefs or PRD into structured strategy YAML.

Purpose:
    Analyzes project requirements and extracts:
    - Project summary
    - Strategic goals (3-7)
    - Constraints
    - Milestones with durations
    - Risks with mitigations
    - Priorities (MoSCoW method)

Output:
    strategy_plan.yaml with structured strategic planning data

Changes in Phase 1.1:
    - Inherits from BaseAgent for standardized interface
    - Implements name and dependencies properties
    - Renamed run() → execute(context)
    - Returns AgentOutput instead of Dict
    - Added input validation
"""

import yaml
import json
import re
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


class StrategyAgent(BaseAgent):
    """
    Strategic planning agent that analyzes PRDs and generates structured strategy plans.

    Phase 1.1: Now implements BaseAgent interface for standardized orchestration.
    """

    # Phase 1.1: Implement required BaseAgent properties
    @property
    def name(self) -> str:
        """Agent name for identification and logging."""
        return "StrategyAgent"

    @property
    def dependencies(self) -> List[str]:
        """
        No dependencies - this agent runs first in the pipeline.

        StrategyAgent analyzes the PRD directly and doesn't need
        outputs from other agents.
        """
        return []

    def __init__(
        self,
        prd_path: str = "./projects/swing-fx-trading-assistant/docs/trading_strategy_prd.md",
        output_path: str = "./outputs/strategy_plan.yaml",
        addendum_path: str = None
    ):
        """
        Initialize Strategy Agent.

        Args:
            prd_path: Path to PRD markdown file
            output_path: Where to save strategy_plan.yaml
            addendum_path: Optional path to YAML addendum with milestones/risks/modules/phases
        """
        self.prd_path = Path(prd_path)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        # Auto-detect addendum file in same directory as PRD
        if addendum_path is None:
            potential_addendum = self.prd_path.parent / (self.prd_path.stem + "_addendum.yaml")
            self.addendum_path = potential_addendum if potential_addendum.exists() else None
        else:
            self.addendum_path = Path(addendum_path) if addendum_path else None
        
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
        Validate that PRD file exists before execution.

        Args:
            context: Execution context (not used, PRD path from __init__)

        Returns:
            True if PRD file exists, False otherwise
        """
        if not self.prd_path.exists():
            print(f"❌ PRD file not found: {self.prd_path}")
            return False
        return True

    # Phase 1.1: Renamed run() → execute(), now returns AgentOutput
    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Main execution method - analyze PRD and generate strategy plan.

        Phase 1.1 Changes:
            - Renamed from run() to execute() for BaseAgent compliance
            - Takes AgentContext parameter (for future enhancements)
            - Returns AgentOutput instead of Dict
            - Includes confidence score and decision reasoning

        Args:
            context: Shared execution context

        Returns:
            AgentOutput with strategy plan data
        """
        # Read PRD
        if not self.prd_path.exists():
            raise FileNotFoundError(f"PRD not found: {self.prd_path}")

        prd_text = self.prd_path.read_text(encoding='utf-8')

        # Generate strategy plan
        if self.llm_enabled:
            strategy_data = self._generate_with_llm(prd_text)
        else:
            strategy_data = self._generate_fallback(prd_text)

        # Merge addendum if available
        if self.addendum_path and self.addendum_path.exists():
            strategy_data = self._merge_addendum(strategy_data)

        # Save as YAML
        yaml_output = yaml.safe_dump(strategy_data, sort_keys=False, default_flow_style=False)
        self.output_path.write_text(yaml_output, encoding='utf-8')

        # Phase 1.1: Return AgentOutput instead of Dict
        return AgentOutput(
            agent_name=self.name,
            decision="approve",
            reasoning=f"Extracted {len(strategy_data.get('goals', []))} goals, "
                     f"{len(strategy_data.get('milestones', []))} milestones, "
                     f"{len(strategy_data.get('risks', []))} risks from PRD",
            data_for_next_agent=strategy_data,
            confidence=0.90 if self.llm_enabled else 0.75,
            flags=[],
            metadata={
                "prd_path": str(self.prd_path),
                "output_path": str(self.output_path),
                "llm_enabled": self.llm_enabled,
                "has_addendum": self.addendum_path is not None
            }
        )
    
    def _generate_with_llm(self, prd_text: str) -> Dict[str, Any]:
        """Generate strategy plan using OpenAI."""
        prompt = f"""You are a strategic planning assistant.
Analyze the following project description and extract:
1. Project summary (2-3 sentences)
2. Goals (3-7 strategic goals)
3. Constraints (technical, business, timeline)
4. Milestones (id, description, duration_days)
5. Risks (id, description, mitigation)
6. Priorities (using MoSCoW: Must-have, Should-have, Could-have, Won't-have)

Format strictly as valid YAML.

PRD Content:
{prd_text[:3000]}
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        yaml_text = response.choices[0].message.content.strip()
        
        # Extract YAML from markdown code blocks if present
        if "```yaml" in yaml_text:
            yaml_text = re.search(r'```yaml\n(.*?)\n```', yaml_text, re.DOTALL).group(1)
        elif "```" in yaml_text:
            yaml_text = re.search(r'```\n(.*?)\n```', yaml_text, re.DOTALL).group(1)
        
        data = yaml.safe_load(yaml_text)
        return data
    
    def _generate_fallback(self, prd_text: str) -> Dict[str, Any]:
        """Enhanced fallback strategy extraction with YAML frontmatter and section parsing."""

        # 1. Extract YAML frontmatter if present
        project_name = "AI Management Layer System"
        project_summary = "Extracted from PRD using enhanced fallback method"

        yaml_match = re.search(r'^---\n(.*?)\n---', prd_text, re.DOTALL | re.MULTILINE)
        if yaml_match:
            try:
                yaml_data = yaml.safe_load(yaml_match.group(1))
                if 'project' in yaml_data:
                    project_name = yaml_data['project'].get('name', project_name)
                    project_summary = yaml_data['project'].get('description', project_summary)
            except:
                pass

        strategy = {
            "project": {
                "name": project_name,
                "summary": project_summary
            },
            "goals": [],
            "constraints": [],
            "milestones": [],
            "risks": [],
            "priorities": {
                "must_have": [],
                "should_have": [],
                "could_have": [],
                "wont_have": []
            }
        }

        # 2. Parse document into sections
        sections = {}
        current_section = None
        current_content = []

        for line in prd_text.splitlines():
            # Detect section headers (## or ###)
            if line.strip().startswith('##'):
                if current_section:
                    sections[current_section] = current_content
                current_section = line.strip('#').strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = current_content

        # 3. Extract goals from relevant sections
        goal_sections = ['1.2 Goals', 'Goals', '1. Overview', 'Purpose']
        for section_name in goal_sections:
            if section_name in sections:
                for line in sections[section_name]:
                    line_stripped = line.strip()
                    if line_stripped.startswith(('-', '*')) and len(line_stripped) > 5:
                        goal = line_stripped.strip('- *').strip()
                        if goal and not goal.startswith('#'):
                            strategy['goals'].append(goal)

        # 4. Extract constraints from Non-Functional Requirements
        constraint_sections = ['4. Non-Functional Requirements', 'Non-Functional Requirements', 'Constraints']
        for section_name in constraint_sections:
            if section_name in sections:
                table_rows = self._parse_markdown_table(sections[section_name])
                for row in table_rows:
                    if 'Requirement' in row and row['Requirement']:
                        strategy['constraints'].append(row['Requirement'])
                    elif 'Area' in row and 'Requirement' in row:
                        strategy['constraints'].append(f"{row['Area']}: {row['Requirement']}")

        # 5. Extract risks
        risk_sections = ['Risks', '8. Risks & Mitigation', 'Risk Management']
        for section_name in risk_sections:
            if section_name in sections:
                for line in sections[section_name]:
                    line_stripped = line.strip()
                    if line_stripped.startswith(('-', '*')) and 'risk' in line_stripped.lower():
                        strategy['risks'].append({
                            "id": f"R{len(strategy['risks'])+1}",
                            "description": line_stripped.strip('- *').strip(),
                            "mitigation": "To be defined"
                        })

        # 6. Extract dependencies as potential milestones
        dep_sections = ['5. Dependencies', 'Dependencies', 'Technology Stack']
        for section_name in dep_sections:
            if section_name in sections:
                for line in sections[section_name]:
                    line_stripped = line.strip()
                    if line_stripped.startswith(('-', '*', '**')) and len(line_stripped) > 10:
                        dep = line_stripped.strip('- *').strip()
                        if dep and ':' in dep:
                            milestone_desc = f"Integrate {dep.split(':')[0]}"
                            strategy['milestones'].append({
                                "id": f"M{len(strategy['milestones'])+1}",
                                "description": milestone_desc,
                                "duration_days": 14
                            })

        # 7. Extract acceptance criteria as priorities
        accept_sections = ['7. Acceptance Criteria', 'Acceptance Criteria', 'Success Criteria']
        for section_name in accept_sections:
            if section_name in sections:
                for line in sections[section_name]:
                    line_stripped = line.strip()
                    if line_stripped.startswith(('-', '*', '✅')) and len(line_stripped) > 5:
                        priority = line_stripped.strip('- *✅').strip()
                        if priority:
                            strategy['priorities']['must_have'].append(priority)

        # 8. Validation: Remove malformed entries
        strategy['goals'] = [g for g in strategy['goals'] if not g.startswith('1.') and len(g) > 10]
        strategy['constraints'] = [c for c in strategy['constraints'] if len(c) > 10]

        return strategy

    def _parse_markdown_table(self, lines: list) -> list:
        """Parse markdown table into list of dicts."""
        rows = []
        headers = []

        for line in lines:
            if '|' not in line:
                continue
            cells = [cell.strip() for cell in line.split('|')]
            cells = [c for c in cells if c]  # Remove empty cells

            if not headers and cells:
                headers = cells
            elif cells and not line.strip().startswith('|--'):  # Skip separator row
                if len(cells) == len(headers):
                    row_dict = dict(zip(headers, cells))
                    rows.append(row_dict)

        return rows

    def _merge_addendum(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge data from YAML addendum file into strategy plan.
        Addendum takes precedence for milestones, risks, and modules.
        Phases are added to strategy data.
        """
        try:
            addendum_text = self.addendum_path.read_text(encoding='utf-8')
            addendum = yaml.safe_load(addendum_text)

            if not addendum:
                return strategy_data

            # Merge milestones (addendum overrides)
            if 'milestones' in addendum and addendum['milestones']:
                strategy_data['milestones'] = addendum['milestones']

            # Merge risks (addendum overrides)
            if 'risks' in addendum and addendum['risks']:
                strategy_data['risks'] = addendum['risks']

            # Add phases (new field)
            if 'phases' in addendum and addendum['phases']:
                strategy_data['phases'] = addendum['phases']

            # Store modules for Technical Architect to consume
            if 'modules' in addendum and addendum['modules']:
                strategy_data['recommended_modules'] = addendum['modules']

            return strategy_data

        except Exception as e:
            print(f"⚠️  Error merging addendum: {e}")
            return strategy_data


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 STRATEGY AGENT - PHASE 2 + Phase 1.1 Update")
    print("=" * 70 + "\n")

    agent = StrategyAgent()

    print(f"Agent Name: {agent.name}")
    print(f"Dependencies: {agent.dependencies}")

    if agent.llm_enabled:
        print("✅ OpenAI client initialized")
    else:
        print("⚠️  OpenAI not available - using fallback extraction")

    print(f"📖 Reading PRD from: {agent.prd_path}")

    try:
        # Phase 1.1: Create AgentContext
        from core.cache import Cache
        context = AgentContext(
            session_id="test_session",
            inputs={"prd_path": str(agent.prd_path)},
            cache=Cache(),
            shared_data={}
        )

        # Phase 1.1: Validate inputs
        if not agent.validate_inputs(context):
            print("❌ Input validation failed")
            exit(1)

        # Phase 1.1: Execute with context (replaces run())
        result = agent.execute(context)

        print(f"\n✅ Strategy plan generated!")
        print(f"📁 Saved to: {agent.output_path}")
        print(f"\n📊 AgentOutput:")
        print(f"   - Agent: {result.agent_name}")
        print(f"   - Decision: {result.decision}")
        print(f"   - Confidence: {result.confidence}")
        print(f"   - Reasoning: {result.reasoning}")

        # Access the strategy data
        strategy_data = result.data_for_next_agent
        print(f"\n📊 Extracted Strategy Data:")
        print(f"   - Goals: {len(strategy_data.get('goals', []))}")
        print(f"   - Constraints: {len(strategy_data.get('constraints', []))}")
        print(f"   - Milestones: {len(strategy_data.get('milestones', []))}")
        print(f"   - Risks: {len(strategy_data.get('risks', []))}")

        print("\n" + "=" * 70)
        print("✅ STRATEGY AGENT TEST COMPLETE (Phase 1.1)")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

