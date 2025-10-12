"""
strategic_planner.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Strategic Planner Agent (Management Layer)

Purpose:
    Decides WHAT to build next based on Vertical Agent's recommendation,
    then invokes the tactical Planning Agent to scaffold the project.

Location: agents/strategic_planner/strategic_planner.py

Key Features:
    • Reads Vertical Agent recommendation
    • Extracts top business vertical
    • Invokes tactical Planning Agent
    • Logs strategic decisions
    • Integrates with Agent Protocol

Author: Management Team AI System
Phase: 13 - Strategic Planning Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import yaml
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import agent protocol
try:
    from core.agent_protocol import AgentOutput
except ImportError:
    AgentOutput = None


class StrategicPlannerAgent:
    """
    Management-layer agent that bridges Vertical Agent and Planning Agent.
    
    Flow:
    1. Reads Vertical Agent output (recommendation.md or vertical_scores.yaml)
    2. Extracts top recommendation
    3. Makes strategic decision to proceed
    4. Invokes Planning Agent for tactical execution
    5. Logs decision trail
    """
    
    def __init__(
        self,
        recommendation_path: str = "./outputs/recommendation.md",
        scores_path: str = "./outputs/vertical_scores.yaml",
        output_path: str = "./outputs/strategic_decision.yaml",
        interactive: bool = True
    ):
        """
        Initialize Strategic Planner Agent.
        
        Args:
            recommendation_path: Path to Vertical Agent markdown report
            scores_path: Path to Vertical Agent YAML scores
            output_path: Where to save strategic decision
            interactive: If True, ask for human approval before invoking Planning Agent
        """
        self.recommendation_path = Path(recommendation_path)
        self.scores_path = Path(scores_path)
        self.output_path = Path(output_path)
        self.interactive = interactive
        
        # Ensure directories exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        Path("logs/strategic_decisions").mkdir(parents=True, exist_ok=True)
    
    def run(self) -> Any:
        """
        Main execution method.
        
        Returns:
            AgentOutput or dict with strategic decision
        """
        print("🧠 Strategic Planner Agent starting...")
        
        # Step 1: Load Vertical Agent recommendation
        vertical_result = self._load_vertical_recommendation()
        
        if not vertical_result:
            return self._create_error_output("No vertical recommendation found")
        
        # Step 2: Extract top recommendation
        top_vertical = vertical_result.get('top_choice')
        
        if not top_vertical:
            return self._create_error_output("No top choice in vertical results")
        
        print(f"📊 Top vertical identified: {top_vertical['name']}")
        
        # Step 3: Make strategic decision
        decision = self._make_strategic_decision(top_vertical, vertical_result)
        
        # Step 4: Log decision
        self._log_decision(decision)
        
        # Step 5: Save decision
        self._save_decision(decision)
        
        # Step 6: Display proposal and ask for approval (if interactive)
        if decision['proceed']:
            if self.interactive:
                approved = self._request_human_approval(decision)
                decision['human_approved'] = approved
                
                if approved:
                    self._invoke_planning_agent(decision)
                else:
                    print("⏸️  Planning invocation skipped by user")
            else:
                # Auto-invoke if not interactive
                self._invoke_planning_agent(decision)
        
        # Step 7: Return AgentOutput
        return self._create_agent_output(decision)
    
    def _load_vertical_recommendation(self) -> Optional[Dict]:
        """
        Load recommendation from Vertical Agent output.
        
        Tries YAML first, falls back to parsing markdown.
        
        Returns:
            Dict with recommendation data or None
        """
        # Try YAML scores file first (most reliable)
        if self.scores_path.exists():
            try:
                with open(self.scores_path, 'r') as f:
                    data = yaml.safe_load(f)
                print(f"✅ Loaded vertical scores from {self.scores_path}")
                return data
            except Exception as e:
                print(f"⚠️  Failed to load YAML: {e}")
        
        # Fallback to parsing markdown
        if self.recommendation_path.exists():
            try:
                recommendation = self._parse_recommendation_md()
                print(f"✅ Parsed recommendation from {self.recommendation_path}")
                return recommendation
            except Exception as e:
                print(f"⚠️  Failed to parse markdown: {e}")
        
        print("❌ No vertical recommendation found")
        return None
    
    def _parse_recommendation_md(self) -> Dict:
        """
        Parse recommendation.md to extract top choice.
        
        Returns:
            Dict with basic recommendation data
        """
        with open(self.recommendation_path, 'r') as f:
            lines = f.readlines()
        
        top_name = None
        score = None
        
        for i, line in enumerate(lines):
            # Look for "**Name**" after "Top Recommendation"
            if "## 🏆 Top" in line:
                # Next few lines should have the name
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].startswith("**") and not lines[j].startswith("**Score"):
                        top_name = lines[j].strip().replace("**", "")
                        break
            
            # Look for score
            if "**Score**:" in line or "RICE Score:" in line:
                parts = line.split("`")
                if len(parts) >= 2:
                    try:
                        score = float(parts[1])
                    except:
                        pass
        
        if top_name:
            return {
                'top_choice': {
                    'name': top_name,
                    'score': score or 0
                },
                'all_ranked': [{'name': top_name, 'score': score or 0}]
            }
        
        return None
    
    def _make_strategic_decision(
        self,
        top_vertical: Dict,
        vertical_result: Dict
    ) -> Dict:
        """
        Make strategic decision based on vertical scoring.
        
        Args:
            top_vertical: Top-ranked vertical
            vertical_result: Full vertical evaluation
            
        Returns:
            Strategic decision dict
        """
        score = top_vertical.get('score', 0)
        name = top_vertical.get('name', 'Unknown')
        
        # Decision criteria
        proceed = score >= 50  # Minimum threshold for proceeding
        
        # Generate reasoning
        if score >= 100:
            reasoning = f"Strong opportunity (score: {score}). Recommend immediate planning and execution."
        elif score >= 50:
            reasoning = f"Moderate opportunity (score: {score}). Proceed with MVP approach."
        else:
            reasoning = f"Below threshold (score: {score}). Recommend further validation before proceeding."
        
        # Build decision
        decision = {
            'selected_vertical': name,
            'score': score,
            'proceed': proceed,
            'reasoning': reasoning,
            'decision_date': datetime.now().isoformat(),
            'vertical_details': top_vertical,
            'alternatives': vertical_result.get('alternatives', [])[:3]
        }
        
        return decision
    
    def _request_human_approval(self, decision: Dict) -> bool:
        """
        Display proposal and request human approval.
        
        Args:
            decision: Strategic decision dict
            
        Returns:
            True if approved, False otherwise
        """
        print("\n" + "="*70)
        print("🧠 STRATEGIC PLANNER DECISION")
        print("="*70 + "\n")
        
        print(f"📂 Vertical: {decision['selected_vertical']}")
        print(f"📈 RICE Score: {decision['score']}\n")
        
        print("Suggested action:")
        project_slug = decision['selected_vertical'].lower().replace(" ", "-")
        print(f"- Project Title: {project_slug}")
        print(f"- Description: Build: {decision['selected_vertical']}\n")
        
        print(f"💡 Reasoning: {decision['reasoning']}\n")
        
        # Show alternatives if available
        if decision.get('alternatives'):
            print("Alternative options considered:")
            for i, alt in enumerate(decision['alternatives'], start=1):
                print(f"  {i}. {alt.get('name', 'Unknown')} (score: {alt.get('score', 0)})")
            print()
        
        print("="*70)
        print("💡 Would you like to send this to the Planning Department?")
        print("="*70 + "\n")
        
        # Get user input
        while True:
            response = input("👉 Approve? (Y/N): ").strip().upper()
            
            if response in ['Y', 'YES']:
                print("\n✅ Approved! Proceeding to Planning Agent...\n")
                return True
            elif response in ['N', 'NO']:
                print("\n⏸️  Decision paused. Strategic plan saved but not executed.\n")
                return False
            else:
                print("⚠️  Please enter Y or N")
    
    def _log_decision(self, decision: Dict):
        """
        Log strategic decision to file.
        
        Args:
            decision: Strategic decision dict
        """
        log_dir = Path("logs/strategic_decisions")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_slug = decision['selected_vertical'].lower().replace(" ", "-")
        log_path = log_dir / f"{project_slug}_{timestamp}.txt"
        
        with open(log_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("STRATEGIC DECISION LOG\n")
            f.write("="*70 + "\n\n")
            f.write(f"Project: {decision['selected_vertical']}\n")
            f.write(f"Score: {decision['score']}\n")
            f.write(f"Decision: {'PROCEED' if decision['proceed'] else 'HOLD'}\n")
            f.write(f"Date: {decision['decision_date']}\n\n")
            f.write(f"Reasoning:\n{decision['reasoning']}\n\n")
            
            if decision.get('alternatives'):
                f.write("Alternatives Considered:\n")
                for i, alt in enumerate(decision['alternatives'], start=1):
                    f.write(f"  {i}. {alt.get('name', 'Unknown')} (score: {alt.get('score', 0)})\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("Decision logged by Strategic Planner Agent\n")
            f.write("="*70 + "\n")
        
        print(f"📝 Decision logged to {log_path}")
    
    def _save_decision(self, decision: Dict):
        """Save decision as YAML for next agents."""
        with open(self.output_path, 'w') as f:
            yaml.safe_dump(decision, f, sort_keys=False)
        
        print(f"💾 Strategic decision saved to {self.output_path}")
    
    def _invoke_planning_agent(self, decision: Dict):
        """
        Invoke the tactical Planning Agent to scaffold the project.
        
        Args:
            decision: Strategic decision dict
        """
        project_name = decision['selected_vertical'].lower().replace(" ", "-")
        description = f"Build: {decision['selected_vertical']}"
        
        print(f"\n🚀 Invoking Planning Agent for: {project_name}")
        print(f"   Description: {description}\n")
        
        # Check if run_planner.py exists
        planner_script = Path("scripts/run_planner.py")
        
        if not planner_script.exists():
            print("⚠️  scripts/run_planner.py not found - skipping tactical planning invocation")
            return
        
        try:
            result = subprocess.run(
                [
                    "python",
                    str(planner_script),
                    project_name,
                    description,
                    "--author",
                    "StrategicPlannerAgent"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Planning Agent executed successfully")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"⚠️  Planning Agent returned error code {result.returncode}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            print("⚠️  Planning Agent timeout - execution took too long")
        except Exception as e:
            print(f"⚠️  Error invoking Planning Agent: {e}")
    
    def _create_agent_output(self, decision: Dict) -> Any:
        """
        Create AgentOutput for orchestrator integration.
        
        Args:
            decision: Strategic decision dict
            
        Returns:
            AgentOutput or plain dict
        """
        if AgentOutput is None:
            return decision
        
        return AgentOutput(
            agent_name="StrategicPlannerAgent",
            decision="approve" if decision['proceed'] else "conditional",
            reasoning=decision['reasoning'],
            data_for_next_agent={
                'selected_project': decision['selected_vertical'],
                'project_score': decision['score'],
                'proceed_to_planning': decision['proceed']
            },
            confidence=0.8 if decision['score'] >= 100 else 0.6,
            flags=[] if decision['proceed'] else ["below_threshold"]
        )
    
    def _create_error_output(self, error_msg: str) -> Any:
        """Create error output."""
        if AgentOutput is None:
            return {'status': 'error', 'error': error_msg}
        
        return AgentOutput(
            agent_name="StrategicPlannerAgent",
            decision="skip",
            reasoning=f"Error: {error_msg}",
            data_for_next_agent={},
            confidence=0.0,
            flags=["input_missing"]
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Execution Support
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Run Strategic Planner from command line."""
    print("\n" + "="*70)
    print("🧠 STRATEGIC PLANNER AGENT - Project Decision Maker")
    print("="*70 + "\n")
    
    agent = StrategicPlannerAgent()
    result = agent.run()
    
    print("\n" + "="*70)
    print("✅ Strategic Planning Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

