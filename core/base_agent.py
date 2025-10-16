"""
base_agent.py
Phase 1.1 – BaseAgent Abstract Class
---------------------------------------------------------
Standardized interface for all agents in the Management Team system.

Purpose:
    - Define consistent contract for agent execution
    - Enable dependency tracking for parallel execution
    - Enforce AgentOutput protocol compliance
    - Provide shared context for inter-agent communication

Design Pattern: Abstract Base Class (ABC)

Created: 2025-10-13
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from core.agent_protocol import AgentOutput
from core.cache import Cache


@dataclass
class AgentContext:
    """
    Shared execution context passed to all agents.

    Purpose:
        - Provides session-level information (session_id)
        - Gives access to input files/data
        - Shares cache for performance optimization
        - Allows agents to access outputs from upstream agents

    Attributes:
        session_id: Unique identifier for this pipeline execution
        inputs: Dictionary of input files/data (PRD, ideas, etc.)
        cache: Cache instance for storing/retrieving agent outputs
        shared_data: Results from previously-executed agents

    Example:
        context = AgentContext(
            session_id="20251013_142305",
            inputs={"prd_path": "./docs/PRD.md"},
            cache=Cache(),
            shared_data={}
        )

        # Later, after StrategyAgent runs:
        context.shared_data["StrategyAgent"] = AgentOutput(...)

        # TechnicalArchitect can access strategy results:
        strategy_output = context.shared_data.get("StrategyAgent")
        if strategy_output:
            strategy_data = strategy_output.data_for_next_agent
    """
    session_id: str
    inputs: Dict[str, Any]
    cache: Optional[Cache] = None
    shared_data: Dict[str, AgentOutput] = field(default_factory=dict)

    def get_agent_output(self, agent_name: str) -> Optional[AgentOutput]:
        """
        Safely retrieve output from a previously-executed agent.

        Args:
            agent_name: Name of the agent whose output to retrieve

        Returns:
            AgentOutput if agent has executed, None otherwise
        """
        return self.shared_data.get(agent_name)

    def get_agent_data(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the data_for_next_agent from a previously-executed agent.

        Args:
            agent_name: Name of the agent whose data to retrieve

        Returns:
            Dictionary of agent data, or None if not found
        """
        output = self.get_agent_output(agent_name)
        return output.data_for_next_agent if output else None


class BaseAgent(ABC):
    """
    Abstract base class that all agents must inherit from.

    Purpose:
        - Enforces consistent interface across all agents
        - Enables type-safe orchestration
        - Supports dependency-based execution ordering
        - Ensures AgentOutput protocol compliance

    Required Methods:
        - name: Property returning agent name
        - dependencies: Property returning list of required upstream agents
        - execute: Main execution method that processes inputs and returns output

    Optional Methods:
        - validate_inputs: Check if inputs are valid before execution

    Design Pattern: Template Method Pattern
        - Base class defines algorithm structure (validate → execute)
        - Subclasses implement specific steps

    Example Implementation:
        class MyCustomAgent(BaseAgent):
            @property
            def name(self) -> str:
                return "MyCustomAgent"

            @property
            def dependencies(self) -> List[str]:
                return ["StrategyAgent"]  # Runs after StrategyAgent

            def validate_inputs(self, context: AgentContext) -> bool:
                # Optional: validate before execution
                required_file = context.inputs.get("my_file")
                return required_file is not None

            def execute(self, context: AgentContext) -> AgentOutput:
                # Access upstream agent data
                strategy_data = context.get_agent_data("StrategyAgent")

                # Process...
                result = self._do_work(strategy_data)

                # Return standardized output
                return AgentOutput(
                    agent_name=self.name,
                    decision="approve",
                    reasoning="Processed successfully",
                    data_for_next_agent=result,
                    confidence=0.9
                )
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the agent's name for logging and tracking.

        Must be unique across all agents in the system.
        Used for dependency resolution and result storage.

        Returns:
            String identifier (e.g., "StrategyAgent", "PlanningAgent")
        """
        pass

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """
        Return list of agent names this agent depends on.

        Defines execution order - this agent will only run after
        all dependencies have completed successfully.

        Returns:
            List of agent names (empty list if no dependencies)

        Examples:
            return []  # Runs first (no dependencies)
            return ["StrategyAgent"]  # Waits for StrategyAgent
            return ["StrategyAgent", "TechnicalArchitectAgent"]  # Waits for both
        """
        pass

    @abstractmethod
    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Main execution method - implement agent's core logic here.

        This is where your agent does its work:
        - Read inputs from context.inputs
        - Access upstream agent outputs from context.shared_data
        - Process data (call LLMs, analyze files, etc.)
        - Return structured AgentOutput

        Args:
            context: Shared execution context with inputs and upstream results

        Returns:
            AgentOutput with decision, reasoning, data, and confidence

        Raises:
            Any exceptions during execution (will be caught by orchestrator)
        """
        pass

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Optional: Validate inputs before execution.

        Override this method to check that required inputs exist
        and are valid before running expensive operations.

        Args:
            context: Execution context to validate

        Returns:
            True if inputs are valid, False otherwise

        Example:
            def validate_inputs(self, context: AgentContext) -> bool:
                prd_path = context.inputs.get("prd_path")
                if not prd_path:
                    return False
                return Path(prd_path).exists()
        """
        return True  # Default: assume inputs are valid

    def __repr__(self) -> str:
        """String representation for debugging."""
        deps = ", ".join(self.dependencies) if self.dependencies else "none"
        return f"{self.__class__.__name__}(name={self.name}, dependencies=[{deps}])"


# ==============================================
# Helper Functions
# ==============================================

def validate_agent_interface(agent: Any) -> bool:
    """
    Check if an object properly implements the BaseAgent interface.

    Useful for runtime validation when loading agents dynamically.

    Args:
        agent: Object to validate

    Returns:
        True if agent implements BaseAgent interface correctly

    Example:
        if validate_agent_interface(my_agent):
            print("Agent is valid!")
        else:
            print("Agent missing required methods")
    """
    required_attrs = ["name", "dependencies", "execute"]

    for attr in required_attrs:
        if not hasattr(agent, attr):
            return False

    # Check if it's actually a BaseAgent subclass
    if not isinstance(agent, BaseAgent):
        return False

    return True


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🧪 BASE AGENT - Phase 1.1 Test")
    print("=" * 70 + "\n")

    # Test 1: Cannot instantiate abstract class
    print("Test 1: Cannot instantiate BaseAgent directly")
    try:
        agent = BaseAgent()
        print("   ❌ FAIL: Should not allow instantiation")
    except TypeError as e:
        print(f"   ✅ PASS: {e}")

    # Test 2: Must implement abstract methods
    print("\nTest 2: Subclass must implement required methods")

    class IncompleteAgent(BaseAgent):
        """Missing implementations"""
        pass

    try:
        agent = IncompleteAgent()
        print("   ❌ FAIL: Should require method implementations")
    except TypeError as e:
        print(f"   ✅ PASS: {e}")

    # Test 3: Valid implementation
    print("\nTest 3: Valid agent implementation")

    class ValidAgent(BaseAgent):
        @property
        def name(self) -> str:
            return "ValidAgent"

        @property
        def dependencies(self) -> List[str]:
            return ["StrategyAgent"]

        def execute(self, context: AgentContext) -> AgentOutput:
            return AgentOutput(
                agent_name=self.name,
                decision="approve",
                reasoning="Test agent",
                data_for_next_agent={"status": "ok"},
                confidence=0.9
            )

    try:
        agent = ValidAgent()
        print(f"   ✅ PASS: Created {agent}")
        print(f"   Name: {agent.name}")
        print(f"   Dependencies: {agent.dependencies}")
    except Exception as e:
        print(f"   ❌ FAIL: {e}")

    # Test 4: AgentContext
    print("\nTest 4: AgentContext functionality")

    context = AgentContext(
        session_id="test_session",
        inputs={"prd": "test.md"},
        shared_data={}
    )

    # Add mock agent output
    mock_output = AgentOutput(
        agent_name="StrategyAgent",
        decision="approve",
        reasoning="Test",
        data_for_next_agent={"goals": ["goal1", "goal2"]},
        confidence=0.85
    )
    context.shared_data["StrategyAgent"] = mock_output

    # Retrieve it
    retrieved = context.get_agent_data("StrategyAgent")
    if retrieved and "goals" in retrieved:
        print("   ✅ PASS: AgentContext stores and retrieves data")
        print(f"   Retrieved: {retrieved}")
    else:
        print("   ❌ FAIL: AgentContext not working")

    # Test 5: Validate agent interface
    print("\nTest 5: Agent interface validation")
    if validate_agent_interface(agent):
        print("   ✅ PASS: Agent interface is valid")
    else:
        print("   ❌ FAIL: Agent interface validation failed")

    print("\n" + "=" * 70)
    print("✅ BASE AGENT TESTS COMPLETE")
    print("=" * 70 + "\n")
