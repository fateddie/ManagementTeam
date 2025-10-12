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
    Returns the top candidate + full ranked list + proactive suggestions.
    
    Args:
        ideas: List of dicts with keys: name, reach, impact, confidence, effort
        framework: "RICE" or "ICE"
        
    Returns:
        Dict with top_choice, all_ranked, summary, and proactive_notes
        
    Example:
        ideas = [
            {"name": "Golf Courses", "reach": 6, "impact": 7, "confidence": 8, "effort": 4},
            {"name": "Car Garages", "reach": 7, "impact": 8, "confidence": 7, "effort": 3},
        ]
        result = run_vertical_agent(ideas)
    """
    # Step 1: Validate inputs
    validation_result = _validate_inputs(ideas)
    if validation_result:
        return validation_result
    
    # Step 2: Score and rank all verticals
    ranked = score_all_verticals(ideas, framework)
    
    # Step 3: Generate recommendation
    recommendation = get_recommendation(ranked)
    
    # Step 4: Add proactive suggestions
    proactive_notes = _generate_proactive_suggestions(ranked[0] if ranked else None, ranked)
    recommendation['proactive_notes'] = proactive_notes
    
    # Step 5: Write recommendation to file
    _write_recommendation_file(recommendation, framework)
    
    return recommendation


def _validate_inputs(ideas: List[Dict]) -> Dict:
    """
    Validate that all verticals have required RICE inputs.
    
    Args:
        ideas: List of vertical dicts
        
    Returns:
        Error dict if validation fails, None if valid
    """
    required_fields = ['name', 'reach', 'impact', 'confidence', 'effort']
    missing_data = []
    
    for idea in ideas:
        if not idea.get('name'):
            missing_data.append("(unnamed vertical)")
            continue
            
        missing_fields = [
            field for field in required_fields 
            if field not in idea or idea[field] is None
        ]
        
        if missing_fields:
            missing_data.append(f"{idea['name']} (missing: {', '.join(missing_fields)})")
    
    if missing_data:
        return {
            "error": "Missing scoring inputs for some verticals",
            "missing": missing_data,
            "action": "Please complete the RICE inputs for all verticals (reach, impact, confidence, effort).",
            "top_choice": None,
            "all_ranked": [],
            "summary": "⚠️ Unable to evaluate - incomplete data"
        }
    
    return None


def _generate_proactive_suggestions(top: Dict, all_ranked: List[Dict]) -> List[str]:
    """
    Generate proactive suggestions based on scoring analysis.
    
    Args:
        top: Top-ranked vertical
        all_ranked: All scored verticals
        
    Returns:
        List of actionable suggestions
    """
    if not top:
        return ["⚠️ No verticals provided for evaluation"]
    
    suggestions = []
    
    # Analyze confidence
    if top['confidence'] < 6:
        suggestions.append(
            f"🔍 Confidence is moderate ({top['confidence']}/10) for '{top['name']}'. "
            f"Consider: market validation, competitor research, or customer interviews."
        )
    elif top['confidence'] < 4:
        suggestions.append(
            f"⚠️ Low confidence ({top['confidence']}/10) for '{top['name']}'. "
            f"High risk - conduct thorough market research before proceeding."
        )
    
    # Analyze reach
    if top['reach'] < 5:
        suggestions.append(
            f"📣 Reach is limited ({top['reach']}/10) for '{top['name']}'. "
            f"Consider: partnerships with industry associations, local directories, or vertical-specific platforms."
        )
    elif top['reach'] < 3:
        suggestions.append(
            f"⚠️ Very limited reach ({top['reach']}/10) for '{top['name']}'. "
            f"This is a niche market - ensure unit economics support smaller scale."
        )
    
    # Analyze impact
    if top['impact'] < 6:
        suggestions.append(
            f"💡 Impact is moderate ({top['impact']}/10) for '{top['name']}'. "
            f"Look for ways to increase value: additional features, integrations, or premium tiers."
        )
    
    # Analyze effort
    if top['effort'] > 6:
        suggestions.append(
            f"⚠️ High effort ({top['effort']}/10) for '{top['name']}'. "
            f"Consider: breaking into MVP phases, starting with core features only, or testing with pilot customers."
        )
    elif top['effort'] > 8:
        suggestions.append(
            f"🚨 Very high effort ({top['effort']}/10) for '{top['name']}'. "
            f"Strongly recommend MVP approach - identify absolute minimum viable features first."
        )
    
    # Analyze score vs alternatives
    if len(all_ranked) > 1:
        second = all_ranked[1]
        score_diff = top['score'] - second['score']
        
        if score_diff < 10:
            suggestions.append(
                f"⚖️ Close call: '{top['name']}' (score: {top['score']}) vs '{second['name']}' (score: {second['score']}). "
                f"Consider running both as quick experiments to see which gains traction."
            )
        elif score_diff > 50:
            suggestions.append(
                f"🎯 Clear winner: '{top['name']}' scores significantly higher than alternatives. "
                f"Strong signal to proceed with this vertical."
            )
    
    # Overall recommendation
    if top['score'] > 100:
        suggestions.append(
            f"✅ Strong opportunity overall (RICE: {top['score']}). "
            f"Ready for strategy planning phase."
        )
    elif top['score'] < 50:
        suggestions.append(
            f"⚠️ Lower overall score (RICE: {top['score']}). "
            f"Proceed cautiously or revisit scoring assumptions."
        )
    
    # Default if no issues
    if not suggestions:
        suggestions.append(
            f"✅ No immediate blockers detected for '{top['name']}'. "
            f"Ready for planning phase - move to Strategy Agent."
        )
    
    return suggestions


def _write_recommendation_file(recommendation: Dict, framework: str = "RICE"):
    """
    Write recommendation to markdown file for easy reference.
    
    Args:
        recommendation: Full recommendation dict
        framework: Scoring framework used
    """
    from datetime import datetime
    
    output_dir = Path("./outputs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "recommendation.md"
    
    top = recommendation.get('top_choice')
    if not top:
        return
    
    with open(output_file, "w") as f:
        # Header
        f.write("# 🧠 Vertical Agent Recommendation\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Framework:** {framework}\n\n")
        f.write("---\n\n")
        
        # Top Choice
        f.write("## 🏆 Top Project\n\n")
        f.write(f"**{top['name']}**\n\n")
        f.write(f"- **{framework} Score:** {top['score']}\n")
        f.write(f"- **Reach:** {top['reach']}/10\n")
        f.write(f"- **Impact:** {top['impact']}/10\n")
        f.write(f"- **Confidence:** {top['confidence']}/10\n")
        f.write(f"- **Effort:** {top['effort']}/10\n")
        
        if 'description' in top:
            f.write(f"\n**Description:** {top['description']}\n")
        
        f.write("\n---\n\n")
        
        # Proactive Notes
        f.write("## 🤖 Proactive Insights\n\n")
        proactive_notes = recommendation.get('proactive_notes', [])
        
        if proactive_notes:
            for i, note in enumerate(proactive_notes, start=1):
                f.write(f"{i}. {note}\n\n")
        else:
            f.write("✅ No immediate blockers detected.\n\n")
        
        # Alternatives
        alternatives = recommendation.get('alternatives', [])
        if alternatives:
            f.write("---\n\n")
            f.write("## 🥈 Alternative Options\n\n")
            for i, alt in enumerate(alternatives, start=1):
                f.write(f"{i}. **{alt['name']}** - Score: {alt['score']}\n")
            f.write("\n")
        
        # Full Ranking
        all_ranked = recommendation.get('all_ranked', [])
        if all_ranked and len(all_ranked) > 1:
            f.write("---\n\n")
            f.write("## 📊 Full Ranking\n\n")
            f.write("| Rank | Vertical | Score | Reach | Impact | Confidence | Effort |\n")
            f.write("|------|----------|-------|-------|--------|------------|--------|\n")
            for i, vertical in enumerate(all_ranked, start=1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
                f.write(
                    f"| {medal} {i} | {vertical['name']} | {vertical['score']} | "
                    f"{vertical['reach']} | {vertical['impact']} | {vertical['confidence']} | "
                    f"{vertical['effort']} |\n"
                )
            f.write("\n")
        
        # Next Steps
        f.write("---\n\n")
        f.write("## 🚀 Next Steps\n\n")
        f.write("1. **Review** the proactive insights above\n")
        f.write("2. **Address** any red flags or concerns\n")
        f.write("3. **Feed** this recommendation to the Strategy Agent\n")
        f.write("4. **Begin** detailed planning for the chosen vertical\n\n")
        
        # Footer
        f.write("---\n\n")
        f.write(f"*Generated by Vertical Agent - {framework} Framework*\n")
        f.write(f"*Management Team AI System*\n")
    
    print(f"📄 Recommendation saved to {output_file}")


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
