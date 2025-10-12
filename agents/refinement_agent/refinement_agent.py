"""
refinement_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Idea Refinement Agent

Takes vague/broad startup ideas and refines them into clear,
niche-ready concepts ready for scoring.

Location: agents/refinement_agent/refinement_agent.py

Phase: 15 - Idea Refinement Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import utilities
from cli.utils.prompts import load_refinement_prompt

# Import OpenAI (use existing API key from config)
try:
    from openai import OpenAI
    from src.utils.config_loader import get_env
except ImportError:
    OpenAI = None
    get_env = None


class RefinementAgent:
    """
    Refines vague business ideas into clear, scoreable concepts.
    
    Flow:
    1. User provides raw idea ("AI Call Catcher")
    2. Agent critiques and asks questions
    3. Agent suggests refinements
    4. Outputs clear concept ("AI Receptionist for Hair Salons")
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        output_path: str = "data/refined/refined_ideas.json"
    ):
        """
        Initialize Refinement Agent.
        
        Args:
            model: OpenAI model to use
            output_path: Where to save refined ideas
        """
        self.model = model
        self.output_path = Path(output_path)
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        if OpenAI and get_env:
            api_key = get_env("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key) if api_key else None
        else:
            self.client = None
    
    def refine_idea(self, raw_idea: str) -> Dict:
        """
        Refine a vague idea into a clear concept.
        
        Args:
            raw_idea: User's raw/vague business idea
            
        Returns:
            Dict with refined idea details
        """
        print(f"\n🔄 Refining idea: '{raw_idea}'...")
        
        if not self.client:
            print("⚠️  OpenAI client not available - using mock refinement")
            return self._mock_refinement(raw_idea)
        
        # Load prompt template
        prompt = load_refinement_prompt(raw_idea)
        
        print("🤖 Sending to LLM for refinement...")
        
        try:
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert startup advisor. Return ONLY valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            # Parse JSON
            refined = json.loads(content)
            
            print("✅ Refinement complete!\n")
            
            return refined
            
        except json.JSONDecodeError as e:
            print(f"❌ LLM returned invalid JSON: {e}")
            print(f"Response was: {content[:200]}...")
            return self._mock_refinement(raw_idea)
        
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return self._mock_refinement(raw_idea)
    
    def _mock_refinement(self, raw_idea: str) -> Dict:
        """Fallback mock refinement for testing."""
        return {
            "original_idea": raw_idea,
            "critique": "This idea needs more specificity about target market and solution approach",
            "clarifying_questions": [
                "What specific industry or vertical?",
                "What is the exact problem being solved?",
                "Who is the ideal first customer?"
            ],
            "suggested_refinements": [
                f"{raw_idea} for Hair Salons - focusing on appointment booking",
                f"{raw_idea} for Dental Practices - focusing on patient communication"
            ],
            "refined_idea": {
                "name": f"{raw_idea} for Hair Salons",
                "niche": "Independent hair salons with 1-3 locations",
                "value_proposition": "Automated phone answering and appointment booking",
                "target_customer": "Salon owners who miss calls during busy hours",
                "unique_angle": "Pre-trained on salon-specific FAQs and terminology"
            },
            "next_steps": [
                "Validate with 5 salon owners",
                "Research existing salon software",
                "Build simple prototype"
            ]
        }
    
    def save_refined_idea(self, refined: Dict, path: str = None) -> str:
        """
        Save refined idea to JSON file (appends).
        
        Args:
            refined: Refined idea dict
            path: Optional custom save path
            
        Returns:
            Path where idea was saved
        """
        file_path = Path(path) if path else self.output_path
        
        existing = []
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    existing = json.load(f)
            except json.JSONDecodeError:
                existing = []
        
        # Add timestamp
        refined['refined_at'] = datetime.now().isoformat()
        
        existing.append(refined)
        
        with open(file_path, 'w') as f:
            json.dump(existing, f, indent=2)
        
        return str(file_path)
    
    def run(self, raw_idea: str) -> Dict:
        """
        Main execution method.
        
        Args:
            raw_idea: Raw business idea string
            
        Returns:
            Refined idea dict
        """
        # Refine the idea
        refined = self.refine_idea(raw_idea)
        
        # Save it
        saved_path = self.save_refined_idea(refined)
        
        print(f"💾 Refined idea saved to {saved_path}")
        
        return refined


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Execution
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Run from command line."""
    print("\n" + "="*70)
    print("🔄 IDEA REFINEMENT AGENT")
    print("="*70 + "\n")
    
    # Get user input
    raw_idea = input("💡 Enter your raw startup idea: ").strip()
    
    if not raw_idea:
        print("❌ No idea provided")
        return
    
    # Run refinement
    agent = RefinementAgent()
    refined = agent.run(raw_idea)
    
    # Display results
    print("\n" + "="*70)
    print("✅ REFINEMENT COMPLETE")
    print("="*70 + "\n")
    
    print("📋 Refined Idea:\n")
    print(json.dumps(refined.get('refined_idea', {}), indent=2))
    
    if 'clarifying_questions' in refined:
        print("\n❓ Clarifying Questions:")
        for i, q in enumerate(refined['clarifying_questions'], 1):
            print(f"   {i}. {q}")
    
    if 'suggested_refinements' in refined:
        print("\n💡 Alternative Refinements:")
        for i, r in enumerate(refined['suggested_refinements'], 1):
            print(f"   {i}. {r}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()

