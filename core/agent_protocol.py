"""
agent_protocol.py
Phase 9 — AgentOutput Protocol & Conflict Resolution
---------------------------------------------------------
Standardized protocol for inter-agent communication and decision-making.

Purpose:
    - Defines AgentOutput dataclass for standardized agent responses
    - Provides validation and serialization
    - Enables conflict resolution through weighted voting
    - Supports human escalation for low-confidence decisions
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
from datetime import datetime

# Valid decision types
DECISION_ENUM = {"approve", "reject", "conditional", "skip"}


@dataclass
class AgentOutput:
    """
    Standardized output format for all agents in the Management Team system.
    
    Attributes:
        agent_name: Name of the agent producing output
        decision: approve | reject | conditional | skip
        reasoning: Human-readable explanation of decision
        data_for_next_agent: Structured data to pass to downstream agents
        confidence: Decision confidence (0.0 - 1.0)
        flags: Optional warnings or concerns
        timestamp: When output was created
        metadata: Additional agent-specific metadata
    """
    agent_name: str
    decision: str
    reasoning: str
    data_for_next_agent: Dict[str, Any]
    confidence: float = 1.0
    flags: Optional[List[str]] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize optional fields and set timestamp."""
        if self.flags is None:
            self.flags = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def validate(self) -> bool:
        """
        Validate the agent output.
        
        Returns:
            True if valid
            
        Raises:
            AssertionError if validation fails
        """
        assert self.decision in DECISION_ENUM, (
            f"Invalid decision: {self.decision}. "
            f"Must be one of: {', '.join(DECISION_ENUM)}"
        )
        assert 0.0 <= self.confidence <= 1.0, (
            f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
        )
        assert isinstance(self.data_for_next_agent, dict), (
            "data_for_next_agent must be a dictionary"
        )
        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation of AgentOutput
        """
        self.validate()
        return asdict(self)

    def save_yaml(self, out_dir: str = "./outputs/decisions") -> str:
        """
        Save agent output to YAML file.
        
        Args:
            out_dir: Directory to save decision files
            
        Returns:
            Path to saved file
        """
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = Path(out_dir) / f"{self.agent_name}_decision_{ts}.yaml"
        
        # Save with readable formatting
        content = yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
            default_flow_style=False
        )
        path.write_text(content, encoding='utf-8')
        
        return str(path)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentOutput':
        """
        Create AgentOutput from dictionary.
        
        Args:
            data: Dictionary containing agent output data
            
        Returns:
            AgentOutput instance
        """
        return cls(**data)

    @classmethod
    def from_yaml(cls, path: str) -> 'AgentOutput':
        """
        Load AgentOutput from YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            AgentOutput instance
        """
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def has_concerns(self) -> bool:
        """Check if output has any flags/concerns."""
        return bool(self.flags)

    def needs_escalation(self, threshold: float = 0.7) -> bool:
        """
        Check if decision needs human escalation based on confidence.
        
        Args:
            threshold: Minimum confidence required (default 0.7)
            
        Returns:
            True if confidence below threshold or has concerns
        """
        return self.confidence < threshold or self.has_concerns()

    def __repr__(self) -> str:
        """String representation."""
        flags_str = f", flags={len(self.flags)}" if self.flags else ""
        return (
            f"AgentOutput(agent={self.agent_name}, "
            f"decision={self.decision}, "
            f"confidence={self.confidence:.2f}{flags_str})"
        )


def create_skip_output(agent_name: str, reason: str = "Not implemented") -> AgentOutput:
    """
    Helper to create a skip output for agents not yet implementing the protocol.
    
    Args:
        agent_name: Name of the agent
        reason: Reason for skipping
        
    Returns:
        AgentOutput with decision='skip'
    """
    return AgentOutput(
        agent_name=agent_name,
        decision="skip",
        reasoning=reason,
        data_for_next_agent={},
        confidence=1.0
    )


def aggregate_outputs(
    outputs: List[AgentOutput],
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Aggregate multiple agent outputs using weighted voting.
    
    Args:
        outputs: List of AgentOutput instances
        weights: Optional dict mapping agent_name to weight (default: equal weights)
        
    Returns:
        Dictionary with aggregated results including:
        - consensus_decision: Most voted decision
        - total_confidence: Weighted average confidence
        - votes: Breakdown of votes
        - needs_escalation: Boolean
    """
    if not outputs:
        return {
            "consensus_decision": "skip",
            "total_confidence": 0.0,
            "votes": {},
            "needs_escalation": True,
            "reason": "No agent outputs provided"
        }
    
    # Default to equal weights
    if weights is None:
        weights = {out.agent_name: 1.0 for out in outputs}
    
    # Count weighted votes
    vote_scores = {}
    total_weight = 0.0
    weighted_confidence = 0.0
    
    for output in outputs:
        weight = weights.get(output.agent_name, 1.0)
        total_weight += weight
        
        # Accumulate votes
        decision = output.decision
        vote_scores[decision] = vote_scores.get(decision, 0.0) + weight
        
        # Accumulate weighted confidence
        weighted_confidence += output.confidence * weight
    
    # Determine consensus
    consensus_decision = max(vote_scores, key=vote_scores.get) if vote_scores else "skip"
    avg_confidence = weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    # Check if escalation needed
    needs_escalation = (
        avg_confidence < 0.7 or
        any(out.has_concerns() for out in outputs) or
        len(vote_scores) > 1  # Disagreement
    )
    
    return {
        "consensus_decision": consensus_decision,
        "total_confidence": round(avg_confidence, 2),
        "votes": vote_scores,
        "needs_escalation": needs_escalation,
        "participating_agents": [out.agent_name for out in outputs],
        "flagged_concerns": [
            flag for out in outputs for flag in (out.flags or [])
        ]
    }


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🔗 AGENT PROTOCOL - PHASE 9")
    print("=" * 70 + "\n")
    
    # Create sample output
    output = AgentOutput(
        agent_name="StrategyAgent",
        decision="approve",
        reasoning="Strategic goals align with business objectives",
        data_for_next_agent={"goals": ["goal1", "goal2"], "priority": "high"},
        confidence=0.95,
        flags=[]
    )
    
    print(f"Created: {output}")
    print(f"\nValidation: {'✅ Passed' if output.validate() else '❌ Failed'}")
    print(f"Needs escalation: {output.needs_escalation()}")
    
    # Save to file
    saved_path = output.save_yaml()
    print(f"\n📁 Saved to: {saved_path}")
    
    # Test aggregation
    outputs = [
        AgentOutput("Agent1", "approve", "Good", {}, 0.9),
        AgentOutput("Agent2", "approve", "Good", {}, 0.8),
        AgentOutput("Agent3", "conditional", "Concerns", {}, 0.6, ["cost_risk"])
    ]
    
    result = aggregate_outputs(outputs)
    print(f"\n📊 Aggregation Result:")
    print(f"   Consensus: {result['consensus_decision']}")
    print(f"   Confidence: {result['total_confidence']}")
    print(f"   Escalation needed: {result['needs_escalation']}")
    
    print("\n" + "=" * 70)
    print("✅ PROTOCOL TEST COMPLETE")
    print("=" * 70)

