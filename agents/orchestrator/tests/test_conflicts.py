"""
test_conflicts.py
Phase 9 — Conflict Resolution Tests
---------------------------------------------------------
Unit tests for agent protocol, voting, and conflict resolution.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_protocol import (
    AgentOutput, 
    aggregate_outputs, 
    create_skip_output,
    DECISION_ENUM
)
import pytest


class TestAgentOutput:
    """Test AgentOutput dataclass functionality."""
    
    def test_create_valid_output(self):
        """Test creating a valid agent output."""
        output = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test reasoning",
            data_for_next_agent={"key": "value"},
            confidence=0.8
        )
        
        assert output.agent_name == "TestAgent"
        assert output.decision == "approve"
        assert output.confidence == 0.8
        assert output.validate()
    
    def test_invalid_decision(self):
        """Test that invalid decisions raise errors."""
        with pytest.raises(AssertionError):
            output = AgentOutput(
                agent_name="TestAgent",
                decision="invalid_decision",
                reasoning="Test",
                data_for_next_agent={}
            )
            output.validate()
    
    def test_invalid_confidence(self):
        """Test that invalid confidence raises errors."""
        with pytest.raises(AssertionError):
            output = AgentOutput(
                agent_name="TestAgent",
                decision="approve",
                reasoning="Test",
                data_for_next_agent={},
                confidence=1.5  # Invalid
            )
            output.validate()
    
    def test_has_concerns(self):
        """Test concern detection."""
        output1 = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent={},
            flags=["risk1", "risk2"]
        )
        assert output1.has_concerns()
        
        output2 = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent={}
        )
        assert not output2.has_concerns()
    
    def test_needs_escalation(self):
        """Test escalation detection."""
        # Low confidence
        output1 = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent={},
            confidence=0.5
        )
        assert output1.needs_escalation(threshold=0.7)
        
        # Has concerns
        output2 = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent={},
            confidence=0.9,
            flags=["concern"]
        )
        assert output2.needs_escalation(threshold=0.7)
        
        # High confidence, no concerns
        output3 = AgentOutput(
            agent_name="TestAgent",
            decision="approve",
            reasoning="Test",
            data_for_next_agent={},
            confidence=0.9
        )
        assert not output3.needs_escalation(threshold=0.7)


class TestAggregation:
    """Test output aggregation and voting."""
    
    def test_unanimous_approval(self):
        """Test unanimous approval."""
        outputs = [
            AgentOutput("Agent1", "approve", "Good", {}, 0.9),
            AgentOutput("Agent2", "approve", "Good", {}, 0.8),
            AgentOutput("Agent3", "approve", "Good", {}, 0.85)
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["consensus_decision"] == "approve"
        assert result["total_confidence"] > 0.8
        assert not result["needs_escalation"]  # High confidence, no disagreement
    
    def test_disagreement_escalation(self):
        """Test that disagreements trigger escalation."""
        outputs = [
            AgentOutput("Agent1", "approve", "Good", {}, 0.9),
            AgentOutput("Agent2", "reject", "Bad", {}, 0.9),
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["needs_escalation"]  # Disagreement present
        assert len(result["votes"]) == 2  # Two different votes
    
    def test_weighted_voting(self):
        """Test weighted voting."""
        outputs = [
            AgentOutput("StrategyAgent", "approve", "Good", {}, 0.9),
            AgentOutput("DocumentationAgent", "reject", "Bad", {}, 0.9),
        ]
        
        weights = {
            "StrategyAgent": 2.0,
            "DocumentationAgent": 0.5
        }
        
        result = aggregate_outputs(outputs, weights)
        
        # Strategy agent should win due to higher weight
        assert result["consensus_decision"] == "approve"
    
    def test_low_confidence_escalation(self):
        """Test that low confidence triggers escalation."""
        outputs = [
            AgentOutput("Agent1", "approve", "Uncertain", {}, 0.5),
            AgentOutput("Agent2", "approve", "Uncertain", {}, 0.6),
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["total_confidence"] < 0.7
        assert result["needs_escalation"]
    
    def test_flagged_concerns_escalation(self):
        """Test that flagged concerns trigger escalation."""
        outputs = [
            AgentOutput("Agent1", "approve", "Good", {}, 0.9, ["cost_risk"]),
            AgentOutput("Agent2", "approve", "Good", {}, 0.9),
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["needs_escalation"]
        assert "cost_risk" in result["flagged_concerns"]
    
    def test_empty_outputs(self):
        """Test handling of empty output list."""
        result = aggregate_outputs([])
        
        assert result["consensus_decision"] == "skip"
        assert result["needs_escalation"]
        assert "No agent outputs" in result["reason"]
    
    def test_skip_votes(self):
        """Test handling of skip votes."""
        outputs = [
            AgentOutput("Agent1", "skip", "Not implemented", {}, 1.0),
            AgentOutput("Agent2", "approve", "Good", {}, 0.9),
        ]
        
        result = aggregate_outputs(outputs)
        
        # Approve should win (only substantive vote)
        assert result["consensus_decision"] in ["approve", "skip"]


class TestConflictScenarios:
    """Test real-world conflict scenarios."""
    
    def test_high_stakes_decision(self):
        """Test high-stakes decision with disagreement."""
        outputs = [
            AgentOutput("StrategyAgent", "approve", "Strategic fit", {}, 0.95),
            AgentOutput("FinancialAgent", "reject", "Cost concerns", {}, 0.90, ["budget_exceeded"]),
            AgentOutput("TechnicalArchitectAgent", "conditional", "Technical risks", {}, 0.75, ["complexity_risk"]),
        ]
        
        weights = {
            "StrategyAgent": 0.30,
            "FinancialAgent": 0.20,
            "TechnicalArchitectAgent": 0.30
        }
        
        result = aggregate_outputs(outputs, weights)
        
        # Should escalate due to disagreement and flags
        assert result["needs_escalation"]
        assert len(result["votes"]) == 3  # Three different positions
        assert "budget_exceeded" in result["flagged_concerns"]
    
    def test_consensus_with_concerns(self):
        """Test consensus decision with minor concerns."""
        outputs = [
            AgentOutput("Agent1", "approve", "Good", {}, 0.85, ["timeline_risk"]),
            AgentOutput("Agent2", "approve", "Good", {}, 0.90),
            AgentOutput("Agent3", "approve", "Good", {}, 0.88),
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["consensus_decision"] == "approve"
        # Should still escalate due to flagged concern
        assert result["needs_escalation"]
        assert "timeline_risk" in result["flagged_concerns"]
    
    def test_strong_consensus_high_confidence(self):
        """Test strong consensus with high confidence."""
        outputs = [
            AgentOutput("Agent1", "approve", "Excellent", {}, 0.95),
            AgentOutput("Agent2", "approve", "Excellent", {}, 0.92),
            AgentOutput("Agent3", "approve", "Excellent", {}, 0.93),
            AgentOutput("Agent4", "approve", "Excellent", {}, 0.94),
        ]
        
        result = aggregate_outputs(outputs)
        
        assert result["consensus_decision"] == "approve"
        assert result["total_confidence"] > 0.9
        # Should not need escalation - strong consensus
        assert not result["needs_escalation"]


class TestSkipOutputs:
    """Test skip output helper."""
    
    def test_create_skip_output(self):
        """Test creating skip outputs."""
        output = create_skip_output("OldAgent", "Legacy system")
        
        assert output.agent_name == "OldAgent"
        assert output.decision == "skip"
        assert output.confidence == 1.0
        assert "Legacy system" in output.reasoning


# ==============================================
# Test Runner
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 CONFLICT RESOLUTION TESTS - PHASE 9")
    print("=" * 70 + "\n")
    
    # Run tests manually
    test_output = TestAgentOutput()
    test_agg = TestAggregation()
    test_scenarios = TestConflictScenarios()
    test_skip = TestSkipOutputs()
    
    tests_run = 0
    tests_passed = 0
    
    test_classes = [
        ("AgentOutput", test_output, [
            "test_create_valid_output",
            "test_has_concerns",
            "test_needs_escalation"
        ]),
        ("Aggregation", test_agg, [
            "test_unanimous_approval",
            "test_disagreement_escalation",
            "test_weighted_voting",
            "test_low_confidence_escalation",
            "test_flagged_concerns_escalation",
            "test_empty_outputs"
        ]),
        ("Conflict Scenarios", test_scenarios, [
            "test_high_stakes_decision",
            "test_consensus_with_concerns",
            "test_strong_consensus_high_confidence"
        ]),
        ("Skip Outputs", test_skip, [
            "test_create_skip_output"
        ])
    ]
    
    for class_name, test_instance, test_methods in test_classes:
        print(f"\n📋 Testing {class_name}:")
        for method_name in test_methods:
            tests_run += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"   ✅ {method_name}")
                tests_passed += 1
            except Exception as e:
                print(f"   ❌ {method_name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 TEST RESULTS: {tests_passed}/{tests_run} passed")
    print("=" * 70 + "\n")
    
    if tests_passed == tests_run:
        print("🎉 ALL TESTS PASSED!\n")
        sys.exit(0)
    else:
        print(f"⚠️  {tests_run - tests_passed} test(s) failed\n")
        sys.exit(1)

