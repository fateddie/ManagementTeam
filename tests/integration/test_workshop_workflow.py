"""
test_workshop_workflow.py

Integration Tests for Complete Idea-to-Project Workflow
Phase 2 Day 7 - Integration Testing

Purpose:
    Verify complete workflow integration from raw idea to workshop completion

Why integration tests:
    - Unit tests verify individual components
    - Integration tests verify components work together
    - Critical for ensuring data flows correctly between agents
    - Validates real-world usage scenarios

Test Coverage:
    - Refinement → Workshop data flow
    - Workshop → Future agents data format
    - Complete end-to-end workflow
    - Error handling and graceful degradation

Created: 2025-01-XX
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.refinement_agent.refinement_agent import RefinementAgent
from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
from core.base_agent import AgentContext
from core.cache import Cache


class TestWorkshopWorkflow(unittest.TestCase):
    """Integration tests for workshop workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_idea = "AI-powered productivity assistant for entrepreneurs"
        
    def test_refinement_to_workshop_flow(self):
        """
        Test data flow from RefinementAgent to WorkshopAgent.
        
        Why: Validates that workshop can consume refinement output
        """
        # Create context
        context = AgentContext(
            session_id="test_integration_001",
            inputs={"raw_idea": self.test_idea},
            cache=None,
            shared_data={}
        )
        
        # Step 1: Refinement
        refinement_agent = RefinementAgent()
        refinement_output = refinement_agent.execute(context)
        context.shared_data["RefinementAgent"] = refinement_output
        
        # Verify refinement output
        self.assertIsNotNone(refinement_output)
        self.assertEqual(refinement_output.agent_name, "RefinementAgent")
        self.assertIn("refined_idea", refinement_output.data_for_next_agent)
        
        # Step 2: Workshop
        workshop_agent = IterativeWorkshopAgent()
        
        # Verify workshop can validate inputs
        self.assertTrue(workshop_agent.validate_inputs(context))
        
        # Execute workshop
        workshop_output = workshop_agent.execute(context)
        
        # Verify workshop output
        self.assertIsNotNone(workshop_output)
        self.assertEqual(workshop_output.agent_name, "IterativeWorkshopAgent")
        self.assertIn("evolved_idea", workshop_output.data_for_next_agent)
        self.assertIn("viability_score", workshop_output.data_for_next_agent)
        self.assertIn("workshop_history", workshop_output.data_for_next_agent)
        
        print(f"\n✅ Integration Test Passed!")
        print(f"   Refined idea: {refinement_output.data_for_next_agent.get('title', 'N/A')}")
        print(f"   Workshop viability: {workshop_output.data_for_next_agent.get('viability_score', 'N/A')}/50")
    
    def test_workshop_output_format(self):
        """
        Test that workshop output is properly formatted for downstream agents.
        
        Why: Validates that future agents (Vertical, Ranking) can consume workshop data
        """
        # Create minimal context with mock refined data
        context = AgentContext(
            session_id="test_format_001",
            inputs={"raw_idea": self.test_idea},
            cache=None,
            shared_data={}
        )
        
        # Add mock refinement output
        mock_refined = {
            "title": "Test Idea",
            "description": "Test description",
            "target_customer": "Test customers",
            "value_proposition": "Test value",
            "niche": "Test niche"
        }
        
        from core.agent_protocol import AgentOutput as MockOutput
        context.shared_data["RefinementAgent"] = MockOutput(
            agent_name="RefinementAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent=mock_refined,
            confidence=0.8
        )
        
        # Execute workshop
        workshop_agent = IterativeWorkshopAgent()
        workshop_output = workshop_agent.execute(context)
        workshop_data = workshop_output.data_for_next_agent
        
        # Verify required fields for downstream agents
        required_fields = ["evolved_idea", "viability_score", "improvement", "workshop_history", "recommendation"]
        for field in required_fields:
            self.assertIn(field, workshop_data, f"Missing required field: {field}")
        
        # Verify workshop history structure
        history = workshop_data["workshop_history"]
        self.assertIn("round_1", history)
        self.assertIn("round_2", history)
        self.assertIn("round_3", history)
        
        print(f"\n✅ Output Format Test Passed!")
        print(f"   All required fields present for downstream agents")
    
    def test_workshop_without_refinement(self):
        """
        Test workshop fails gracefully without refinement data.
        
        Why: Validates error handling when dependencies aren't met
        """
        context = AgentContext(
            session_id="test_error_001",
            inputs={"raw_idea": self.test_idea},
            cache=None,
            shared_data={}  # No RefinementAgent output
        )
        
        workshop_agent = IterativeWorkshopAgent()
        
        # Should fail validation
        self.assertFalse(workshop_agent.validate_inputs(context))
        
        print(f"\n✅ Error Handling Test Passed!")
        print(f"   Workshop correctly requires RefinementAgent dependency")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 WORKSHOP WORKFLOW - Integration Tests")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
