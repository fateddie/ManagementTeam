"""
vertical_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Vertical Agent - Business Vertical Evaluation & Scoring

Purpose:
    Evaluates potential business verticals using RICE scoring
    to recommend the best next project.

Location: agents/vertical_agent/vertical_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any

# Import scoring utilities
from src.utils.scoring_utils import score_all_verticals, get_recommendation

# Import agent protocol for orchestrator integration
try:
    from core.agent_protocol import AgentOutput
except ImportError:
    AgentOutput = None


def run_vertical_agent(ideas: List[Dict], framework: str = "RICE") -> Dict:
    """
    Accepts a list of verticals with scoring inputs.
    Returns the top candidate + full ranked list.
    
    Args:
        ideas: List of dicts with keys: name, reach, impact, confidence, effort
        framework: "RICE" or "ICE"
        
    Returns:
        Dict with top_choice, all_ranked, and summary
        
    Example:
        ideas = [
            {"name": "Golf Courses", "reach": 6, "impact": 7, "confidence": 8, "effort": 4},
            {"name": "Car Garages", "reach": 7, "impact": 8, "confidence": 7, "effort": 3},
        ]
        result = run_vertical_agent(ideas)
    """
    # Score and rank all verticals
    ranked = score_all_verticals(ideas, framework)
    
    # Generate recommendation
    recommendation = get_recommendation(ranked)
    
    return recommendation


class VerticalAgent:
    """
    Class-based Vertical Agent for orchestrator integration.
    
    Can load verticals from YAML file and save results.
    """
    
    def __init__(
        self,
        verticals_path: str = "./inputs/verticals.yaml",
        output_path: str = "./outputs/vertical_scores.yaml",
        framework: str = "RICE"
    ):
        """
        Initialize Vertical Agent.
        
        Args:
            verticals_path: Path to YAML file with vertical ideas
            output_path: Where to save scoring results
            framework: "RICE" or "ICE"
        """
        self.verticals_path = Path(verticals_path)
        self.output_path = Path(output_path)
        self.framework = framework
        
        # Ensure directories exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def run(self) -> Any:
        """
        Main execution method - loads, scores, saves, returns results.
        
        Returns:
            AgentOutput or dict with results
        """
        print("🎯 Vertical Agent starting...")
        
        # Load verticals from file
        if not self.verticals_path.exists():
            print(f"⚠️  No verticals file found at {self.verticals_path}")
            print("💡 Using example verticals...")
            ideas = self._get_example_verticals()
        else:
            ideas = self._load_verticals()
            print(f"📊 Loaded {len(ideas)} vertical ideas")
        
        # Score and rank
        result = run_vertical_agent(ideas, self.framework)
        
        # Save results
        self._save_results(result)
        
        # Print summary
        print(f"\n{result['summary']}")
        
        # Return AgentOutput for orchestrator
        return self._create_agent_output(result)
    
    def _load_verticals(self) -> List[Dict]:
        """Load vertical ideas from YAML file."""
        with open(self.verticals_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get('verticals', [])
    
    def _get_example_verticals(self) -> List[Dict]:
        """Return example verticals for testing."""
        return [
            {
                "name": "Golf Courses",
                "reach": 6,
                "impact": 7,
                "confidence": 8,
                "effort": 4,
                "description": "Management software for golf course operations"
            },
            {
                "name": "Car Garages",
                "reach": 7,
                "impact": 8,
                "confidence": 7,
                "effort": 3,
                "description": "Booking and inventory system for auto repair shops"
            },
            {
                "name": "Hair Salons",
                "reach": 5,
                "impact": 6,
                "confidence": 9,
                "effort": 2,
                "description": "Appointment and client management for salons"
            }
        ]
    
    def _save_results(self, result: Dict):
        """Save scoring results to YAML file."""
        with open(self.output_path, 'w') as f:
            yaml.safe_dump(result, f, sort_keys=False)
        print(f"💾 Results saved to {self.output_path}")
    
    def _create_agent_output(self, result: Dict) -> Any:
        """
        Create AgentOutput for orchestrator integration.
        
        Args:
            result: Scoring result dict
            
        Returns:
            AgentOutput or plain dict
        """
        if AgentOutput is None:
            return result
        
        top = result['top_choice']
        
        return AgentOutput(
            agent_name="VerticalAgent",
            decision="approve",
            reasoning=result['summary'],
            data_for_next_agent={
                'recommended_vertical': top['name'],
                'score': top['score'],
                'all_scores': result['all_ranked']
            },
            confidence=0.85,
            flags=[]
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Run Vertical Agent from command line."""
    print("\n" + "="*60)
    print("🎯 VERTICAL AGENT - Business Idea Evaluation")
    print("="*60 + "\n")
    
    agent = VerticalAgent()
    result = agent.run()
    
    print("\n" + "="*60)
    print("✅ Evaluation Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
