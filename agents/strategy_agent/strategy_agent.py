"""
strategy_agent.py
Phase 2 — Strategy Agent
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
"""

import yaml
import json
import re
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import OpenAI, fall back gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class StrategyAgent:
    """
    Strategic planning agent that analyzes PRDs and generates structured strategy plans.
    """
    
    def __init__(
        self, 
        prd_path: str = "./docs/system/PRD.md",
        output_path: str = "./outputs/strategy_plan.yaml"
    ):
        """
        Initialize Strategy Agent.
        
        Args:
            prd_path: Path to PRD markdown file
            output_path: Where to save strategy_plan.yaml
        """
        self.prd_path = Path(prd_path)
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
        Main execution method - analyze PRD and generate strategy plan.
        
        Returns:
            Dictionary containing strategy plan data
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
        
        # Save as YAML
        yaml_output = yaml.safe_dump(strategy_data, sort_keys=False, default_flow_style=False)
        self.output_path.write_text(yaml_output, encoding='utf-8')
        
        return strategy_data
    
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
        """Fallback strategy extraction without LLM (rule-based)."""
        strategy = {
            "project": {
                "name": "AI Management Layer System",
                "summary": "Extracted from PRD using fallback method"
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
        
        # Simple extraction from PRD
        for line in prd_text.splitlines():
            line_lower = line.lower()
            
            # Extract goals
            if any(word in line_lower for word in ["goal", "objective"]) and line.strip().startswith(("-", "*", "##")):
                strategy["goals"].append(line.strip("- *#").strip())
            
            # Extract constraints
            if "constraint" in line_lower and line.strip().startswith(("-", "*")):
                strategy["constraints"].append(line.strip("- *").strip())
            
            # Extract risks
            if "risk" in line_lower and line.strip().startswith(("-", "*")):
                strategy["risks"].append({
                    "id": f"R{len(strategy['risks'])+1}",
                    "description": line.strip("- *").strip(),
                    "mitigation": "To be defined"
                })
        
        return strategy


# ==============================================
# Test Execution
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎯 STRATEGY AGENT - PHASE 2")
    print("=" * 70 + "\n")
    
    agent = StrategyAgent()
    
    if agent.llm_enabled:
        print("✅ OpenAI client initialized")
    else:
        print("⚠️  OpenAI not available - using fallback extraction")
    
    print(f"📖 Reading PRD from: {agent.prd_path}")
    
    try:
        result = agent.run()
        
        print(f"\n✅ Strategy plan generated!")
        print(f"📁 Saved to: {agent.output_path}")
        print(f"\n📊 Extracted:")
        print(f"   - Goals: {len(result.get('goals', []))}")
        print(f"   - Constraints: {len(result.get('constraints', []))}")
        print(f"   - Milestones: {len(result.get('milestones', []))}")
        print(f"   - Risks: {len(result.get('risks', []))}")
        
        print("\n" + "=" * 70)
        print("✅ STRATEGY AGENT TEST COMPLETE")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

