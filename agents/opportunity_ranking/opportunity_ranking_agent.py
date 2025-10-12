"""
opportunity_ranking_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Opportunity Ranking Agent

Advanced weighted scoring for business/project opportunities.

Purpose:
    Ranks business ideas using 7 strategic criteria with custom weights.
    More sophisticated than basic RICE scoring.

Location: agents/opportunity_ranking/opportunity_ranking_agent.py

Criteria:
    - Market Size
    - Niche Attractiveness  
    - Competitive Edge
    - Personal Fit / Skill Match
    - Resource Requirement
    - Speed to MVP
    - Scalability Potential

Phase: 14 - Advanced Opportunity Ranking
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import yaml
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import scoring utilities
from src.utils.score_utils import weighted_score

# Import agent protocol
try:
    from core.agent_protocol import AgentOutput
except ImportError:
    AgentOutput = None


class OpportunityRankingAgent:
    """
    Advanced opportunity ranking with weighted scoring.
    
    Uses 7 strategic criteria instead of simple RICE scoring.
    """
    
    def __init__(
        self,
        ideas_path: str = "./data/opportunity/idea_blocks.json",
        weights_path: str = "./config/weights/weight_config.yaml",
        output_path: str = "./results/opportunity_report.md"
    ):
        """
        Initialize Opportunity Ranking Agent.
        
        Args:
            ideas_path: Path to idea blocks JSON
            weights_path: Path to weight configuration YAML
            output_path: Where to save markdown report
        """
        self.ideas_path = Path(ideas_path)
        self.weights_path = Path(weights_path)
        self.output_path = Path(output_path)
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def run(self) -> Any:
        """
        Main execution method.
        
        Returns:
            AgentOutput or dict with ranking results
        """
        print("📊 Opportunity Ranking Agent starting...")
        
        # Step 1: Load idea blocks
        ideas = self._load_idea_blocks()
        
        if not ideas:
            return self._create_error_output("No ideas found to rank")
        
        print(f"✅ Loaded {len(ideas)} opportunity ideas")
        
        # Step 2: Load weights
        config = self._load_weights()
        weights = config.get('weights', {})
        
        print(f"✅ Loaded {len(weights)} scoring criteria")
        
        # Step 3: Score and rank
        ranked = self._rank_opportunities(ideas, weights, config)
        
        # Step 4: Write outputs
        self._write_outputs(ranked, config)
        
        # Step 5: Return result
        return self._create_agent_output(ranked, config)
    
    def _load_idea_blocks(self) -> List[Dict]:
        """Load idea blocks from JSON file."""
        if not self.ideas_path.exists():
            print(f"⚠️  Ideas file not found: {self.ideas_path}")
            print("💡 Using example ideas...")
            return self._get_example_ideas()
        
        with open(self.ideas_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'ideas' in data:
            return data['ideas']
        else:
            return []
    
    def _get_example_ideas(self) -> List[Dict]:
        """Return example ideas for testing."""
        return [
            {
                "name": "AI Receptionist for Hair Salons",
                "market_size": 7,
                "niche_attractiveness": 8,
                "competitive_edge": 6,
                "personal_fit": 7,
                "resource_requirement": 7,
                "speed_to_mvp": 8,
                "scalability_potential": 7,
                "summary": "AI phone answering for salon bookings and customer queries"
            },
            {
                "name": "Fleet Booking for Golf Clubs",
                "market_size": 6,
                "niche_attractiveness": 7,
                "competitive_edge": 7,
                "personal_fit": 6,
                "resource_requirement": 6,
                "speed_to_mvp": 6,
                "scalability_potential": 6,
                "summary": "Tee time management and member communication system"
            },
            {
                "name": "BI Dashboards for Construction",
                "market_size": 8,
                "niche_attractiveness": 6,
                "competitive_edge": 5,
                "personal_fit": 5,
                "resource_requirement": 4,
                "speed_to_mvp": 5,
                "scalability_potential": 7,
                "summary": "Project tracking and financial dashboards for builders"
            }
        ]
    
    def _load_weights(self) -> Dict:
        """Load weight configuration from YAML."""
        if not self.weights_path.exists():
            print(f"⚠️  Weights file not found: {self.weights_path}")
            print("💡 Using default weights...")
            return {
                'weights': {
                    'market_size': 5,
                    'entry_ease': 4,
                    'personal_fit': 4,
                    'scalability': 3,
                    'speed': 3,
                    'competition': 2,
                    'resource_need': 2
                }
            }
        
        with open(self.weights_path, 'r') as f:
            weights_dict = yaml.safe_load(f)
        
        # Handle both formats: direct dict or nested under 'weights' key
        if 'weights' in weights_dict:
            return weights_dict
        else:
            return {'weights': weights_dict}
    
    def _rank_opportunities(
        self,
        ideas: List[Dict],
        weights: Dict[str, float],
        config: Dict
    ) -> List[Dict]:
        """
        Score and rank all opportunities.
        
        Args:
            ideas: List of idea dicts
            weights: Scoring weights
            config: Full configuration
            
        Returns:
            List of scored and ranked ideas
        """
        scored = []
        
        for idea in ideas:
            # Validate required fields
            if not self._validate_idea(idea, weights):
                print(f"⚠️  Skipping invalid idea: {idea.get('name', 'Unnamed')}")
                continue
            
            # Score the idea using simple weighted scoring
            score, breakdown = weighted_score(idea, weights)
            
            # Apply bonuses if configured
            bonus_applied = self._apply_bonuses(idea, config.get('bonuses', {}))
            if bonus_applied:
                score *= bonus_applied['multiplier']
                breakdown['bonus'] = bonus_applied
            
            # Check risk flags
            risks = self._check_risks(idea, config.get('risk_flags', {}))
            
            # Add to scored list
            scored.append({
                **idea,
                'score': score,
                'score_breakdown': breakdown,
                'risk_flags': risks,
                'scored_at': datetime.now().isoformat()
            })
        
        # Sort by score (highest first)
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    def _validate_idea(self, idea: Dict, weights: Dict[str, float]) -> bool:
        """
        Validate that idea has all required fields.
        
        Args:
            idea: Idea dict
            weights: Required criteria from weights
            
        Returns:
            True if valid, False otherwise
        """
        if 'name' not in idea:
            return False
        
        # Check at least some criteria are present
        criteria_present = sum(1 for criterion in weights.keys() if criterion in idea)
        
        return criteria_present >= len(weights) * 0.5  # At least 50% of criteria
    
    def _apply_bonuses(self, idea: Dict, bonuses: Dict) -> Dict:
        """Apply bonus multipliers based on conditions."""
        for bonus_name, bonus_config in bonuses.items():
            condition = bonus_config.get('condition', '')
            
            # Simple condition evaluation (can be enhanced)
            if self._evaluate_condition(idea, condition):
                return {
                    'name': bonus_name,
                    'multiplier': bonus_config.get('multiplier', 1.0),
                    'description': bonus_config.get('description', '')
                }
        
        return None
    
    def _evaluate_condition(self, idea: Dict, condition: str) -> bool:
        """Evaluate a bonus condition."""
        if not condition:
            return False
        
        # Simple eval (can be enhanced with safer parser)
        try:
            # Replace criterion names with values
            for key, value in idea.items():
                if isinstance(value, (int, float)):
                    condition = condition.replace(key, str(value))
            
            # Evaluate (simple cases only)
            return eval(condition) if 'AND' in condition or '>=' in condition else False
        except:
            return False
    
    def _check_risks(self, idea: Dict, risk_flags: Dict) -> List[str]:
        """Check for risk flags based on configured triggers."""
        risks = []
        
        for risk_name, risk_config in risk_flags.items():
            trigger = risk_config.get('trigger_when', '')
            
            if self._evaluate_condition(idea, trigger):
                risks.append(risk_config.get('message', risk_name))
        
        return risks
    
    def _write_outputs(self, ranked: List[Dict], config: Dict):
        """
        Write JSON and Markdown outputs.
        
        Args:
            ranked: Ranked opportunities
            config: Weight configuration
        """
        # Write JSON
        json_path = self.output_path.parent / "ranked_opportunities.json"
        with open(json_path, 'w') as f:
            json.dump(ranked, f, indent=2)
        
        print(f"💾 JSON saved to {json_path}")
        
        # Write Markdown report
        self._write_markdown_report(ranked, config)
        
        print(f"📄 Report saved to {self.output_path}")
    
    def _write_markdown_report(self, ranked: List[Dict], config: Dict):
        """Generate markdown report."""
        with open(self.output_path, 'w') as f:
            # Header
            f.write(f"# 📈 Opportunity Report — {datetime.now().strftime('%B %Y')}\n\n")
            f.write(f"**Framework:** {config.get('framework', 'Advanced Weighted')}\n")
            f.write(f"**Total Evaluated:** {len(ranked)}\n\n")
            f.write("---\n\n")
            
            # Top 3
            f.write("## 🥇 Top Opportunities\n\n")
            for i, idea in enumerate(ranked[:3], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                f.write(f"{medal} **{i}. {idea['name']}** — Score: {idea['score']:.2f}\n")
                if 'summary' in idea:
                    f.write(f"   - {idea['summary']}\n")
                f.write(f"\n")
            
            f.write("---\n\n")
            
            # Full breakdown
            f.write("## 🔍 Full Breakdown\n\n")
            
            for i, idea in enumerate(ranked, 1):
                f.write(f"### {i}. {idea['name']} (Score: {idea['score']:.2f})\n\n")
                
                if 'summary' in idea:
                    f.write(f"**Summary:** {idea['summary']}\n\n")
                
                # Score breakdown
                if 'score_breakdown' in idea:
                    f.write("**Score Breakdown:**\n")
                    for criterion, score in idea['score_breakdown'].items():
                        if criterion != 'bonus':
                            f.write(f"- {criterion.replace('_', ' ').title()}: {score}\n")
                    f.write("\n")
                
                # Bonuses
                if 'score_breakdown' in idea and 'bonus' in idea['score_breakdown']:
                    bonus = idea['score_breakdown']['bonus']
                    f.write(f"**Bonus Applied:** {bonus['name']} "
                           f"({bonus['multiplier']}x) - {bonus['description']}\n\n")
                
                # Risk flags
                if 'risk_flags' in idea and idea['risk_flags']:
                    f.write("**⚠️ Risk Flags:**\n")
                    for risk in idea['risk_flags']:
                        f.write(f"- {risk}\n")
                    f.write("\n")
                
                f.write("---\n\n")
    
    def _create_agent_output(self, ranked: List[Dict], config: Dict) -> Any:
        """Create AgentOutput for orchestrator."""
        if AgentOutput is None:
            return {'ranked': ranked, 'config': config}
        
        top = ranked[0] if ranked else None
        
        if not top:
            return AgentOutput(
                agent_name="OpportunityRankingAgent",
                decision="skip",
                reasoning="No valid opportunities to rank",
                data_for_next_agent={},
                confidence=0.0,
                flags=["no_input"]
            )
        
        return AgentOutput(
            agent_name="OpportunityRankingAgent",
            decision="approve",
            reasoning=f"Top opportunity: {top['name']} (score: {top['score']:.2f})",
            data_for_next_agent={
                'top_opportunity': top,
                'all_ranked': ranked[:5],  # Top 5
                'scoring_framework': config.get('framework', 'Advanced Weighted')
            },
            confidence=0.85,
            flags=top.get('risk_flags', [])
        )
    
    def _create_error_output(self, error_msg: str) -> Any:
        """Create error output."""
        if AgentOutput is None:
            return {'error': error_msg}
        
        return AgentOutput(
            agent_name="OpportunityRankingAgent",
            decision="skip",
            reasoning=f"Error: {error_msg}",
            data_for_next_agent={},
            confidence=0.0,
            flags=["error"]
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Run from command line."""
    print("\n" + "="*70)
    print("📊 OPPORTUNITY RANKING AGENT - Advanced Weighted Scoring")
    print("="*70 + "\n")
    
    agent = OpportunityRankingAgent()
    result = agent.run()
    
    print("\n" + "="*70)
    print("✅ Ranking Complete!")
    print("="*70)


if __name__ == "__main__":
    main()

