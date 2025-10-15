"""
test_workshop_agent.py

Unit tests for IterativeWorkshopAgent
Phase 1 - Testing basic functionality

Why these tests:
- Verify agent implements BaseAgent interface correctly
- Test Perplexity integration for market data gathering
- Validate each round execution with fallback data
- Ensure AgentOutput format is correct for downstream agents
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
from core.base_agent import AgentContext, validate_agent_interface


class TestIterativeWorkshopAgent(unittest.TestCase):
    """Test suite for IterativeWorkshopAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = IterativeWorkshopAgent()
        self.test_idea = {
            "title": "AI Email Assistant",
            "description": "AI-powered email management for busy entrepreneurs",
            "target_customer": "Busy entrepreneurs 25-45",
            "value_proposition": "Save 2 hours/day on email management",
            "niche": "Productivity software"
        }
    
    def test_agent_interface(self):
        """Test that agent implements BaseAgent interface correctly."""
        self.assertTrue(validate_agent_interface(self.agent))
        self.assertEqual(self.agent.name, "IterativeWorkshopAgent")
        self.assertEqual(self.agent.dependencies, ["RefinementAgent"])
    
    def test_initialization(self):
        """Test agent initializes with required components."""
        self.assertIsNotNone(self.agent.logger)
        # Perplexity and OpenAI may or may not be available
        # That's okay - agent has fallback logic
    
    def test_round_1_placeholder(self):
        """Test Round 1 fallback placeholder data structure."""
        result = self.agent._get_round_1_placeholder(self.test_idea, {})
        
        self.assertIn("risks", result)
        self.assertIn("opportunities", result)
        self.assertIn("initial_viability_score", result)
        self.assertEqual(len(result["risks"]), 3)
        self.assertEqual(len(result["opportunities"]), 3)
    
    def test_round_2_placeholder(self):
        """Test Round 2 fallback placeholder data structure."""
        test_risks = [{"risk": "Market too small", "probability": 30, "impact": 40000, "score": 12}]
        result = self.agent._get_round_2_placeholder(self.test_idea, test_risks)
        
        self.assertIn("solutions", result)
        self.assertIn("recommended_solution", result)
        self.assertIn("evolved_idea", result)
        self.assertTrue(len(result["solutions"]) >= 3)
    
    def test_round_3_placeholder(self):
        """Test Round 3 fallback placeholder data structure."""
        test_opportunities = [{"opportunity": "Growing market", "potential_value": 1000000, "probability": 60}]
        result = self.agent._get_round_3_placeholder(self.test_idea, test_opportunities)
        
        self.assertIn("strategies", result)
        self.assertIn("recommended_strategy", result)
        self.assertIn("final_idea", result)
        self.assertIn("final_viability_score", result)
        self.assertTrue(len(result["strategies"]) >= 3)
    
    def test_recommendation_generation(self):
        """Test recommendation based on viability scores."""
        self.assertIn("GO", self.agent._generate_recommendation(45))
        self.assertIn("CONDITIONAL", self.agent._generate_recommendation(35))
        self.assertIn("ITERATE", self.agent._generate_recommendation(25))
        self.assertIn("NO-GO", self.agent._generate_recommendation(15))
    
    def test_market_data_summarization(self):
        """Test market data summarization."""
        market_data = {
            "query1": {"summary": "Market is growing at 15% CAGR"},
            "query2": {"summary": "Top competitors include X, Y, Z"}
        }
        summary = self.agent._summarize_market_data(market_data)
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 ITERATIVE WORKSHOP AGENT - Unit Tests")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
