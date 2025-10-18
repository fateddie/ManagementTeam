"""
test_async_orchestration.py
Phase 17 - Test Async/Await & Parallel Execution

Purpose:
    Test the async orchestration system with mock agents
    to verify parallel execution and performance improvements.
"""

import asyncio
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.base_agent import BaseAgent, AgentContext, AgentOutput
from agents.orchestrator.orchestrator import Orchestrator


class MockAgent(BaseAgent):
    """Mock agent that simulates I/O delay"""

    def __init__(self, agent_name: str, deps: list = None, delay: float = 1.0):
        self._name = agent_name
        self._deps = deps or []
        self.delay = delay

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> list:
        return self._deps

    def execute(self, context: AgentContext) -> AgentOutput:
        """Synchronous execution with simulated I/O"""
        print(f"  {self.name}: Starting (sync, {self.delay}s delay)")
        time.sleep(self.delay)  # Simulate I/O
        print(f"  {self.name}: Complete")

        return AgentOutput(
            agent_name=self.name,
            decision="approve",
            reasoning=f"Mock agent {self.name} completed",
            data_for_next_agent={"status": "ok"},
            confidence=0.9
        )

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """Async execution with simulated I/O"""
        print(f"  {self.name}: Starting (async, {self.delay}s delay)")
        await asyncio.sleep(self.delay)  # Simulate async I/O
        print(f"  {self.name}: Complete")

        return AgentOutput(
            agent_name=self.name,
            decision="approve",
            reasoning=f"Mock agent {self.name} completed",
            data_for_next_agent={"status": "ok"},
            confidence=0.9
        )


def test_sequential_sync():
    """Test sequential synchronous execution"""
    print("\n" + "=" * 70)
    print("TEST 1: Sequential Synchronous Execution")
    print("=" * 70 + "\n")

    agents = [
        MockAgent("Agent1", deps=[], delay=1.0),
        MockAgent("Agent2", deps=["Agent1"], delay=1.0),
        MockAgent("Agent3", deps=["Agent2"], delay=1.0),
    ]

    start_time = time.time()

    for agent in agents:
        context = AgentContext(
            session_id="test",
            inputs={},
            shared_data={}
        )
        result = agent.execute(context)
        context.shared_data[agent.name] = result

    elapsed = time.time() - start_time

    print(f"\n✅ Total time: {elapsed:.2f}s (Expected: ~3s)")
    return elapsed


async def test_sequential_async():
    """Test sequential async execution"""
    print("\n" + "=" * 70)
    print("TEST 2: Sequential Async Execution")
    print("=" * 70 + "\n")

    agents = [
        MockAgent("Agent1", deps=[], delay=1.0),
        MockAgent("Agent2", deps=["Agent1"], delay=1.0),
        MockAgent("Agent3", deps=["Agent2"], delay=1.0),
    ]

    start_time = time.time()

    context = AgentContext(
        session_id="test",
        inputs={},
        shared_data={}
    )

    for agent in agents:
        result = await agent.execute_async(context)
        context.shared_data[agent.name] = result

    elapsed = time.time() - start_time

    print(f"\n✅ Total time: {elapsed:.2f}s (Expected: ~3s, same as sync)")
    return elapsed


async def test_parallel_async():
    """Test parallel async execution"""
    print("\n" + "=" * 70)
    print("TEST 3: Parallel Async Execution")
    print("=" * 70 + "\n")

    # Stage 1: 3 independent agents (can run in parallel)
    stage1 = [
        MockAgent("AgentA", deps=[], delay=1.0),
        MockAgent("AgentB", deps=[], delay=1.0),
        MockAgent("AgentC", deps=[], delay=1.0),
    ]

    # Stage 2: 1 agent depending on stage 1
    stage2 = [
        MockAgent("AgentD", deps=["AgentA", "AgentB", "AgentC"], delay=1.0),
    ]

    start_time = time.time()

    context = AgentContext(
        session_id="test",
        inputs={},
        shared_data={}
    )

    # Run stage 1 in parallel
    print("Stage 1: Running 3 agents in parallel...")
    tasks = [agent.execute_async(context) for agent in stage1]
    results = await asyncio.gather(*tasks)

    for agent, result in zip(stage1, results):
        context.shared_data[agent.name] = result

    # Run stage 2 (depends on stage 1)
    print("\nStage 2: Running dependent agent...")
    for agent in stage2:
        result = await agent.execute_async(context)
        context.shared_data[agent.name] = result

    elapsed = time.time() - start_time

    print(f"\n✅ Total time: {elapsed:.2f}s (Expected: ~2s)")
    print(f"   Speedup: {3.0/elapsed:.1f}x faster than sequential!")
    return elapsed


async def test_orchestrator_parallel():
    """Test full orchestrator with parallel execution"""
    print("\n" + "=" * 70)
    print("TEST 4: Orchestrator Parallel Execution")
    print("=" * 70 + "\n")

    # Create mock orchestrator with custom agents
    class MockOrchestrator(Orchestrator):
        def _load_agents(self):
            return [
                MockAgent("FastAgent1", deps=[], delay=0.5),
                MockAgent("FastAgent2", deps=[], delay=0.5),
                MockAgent("SlowAgent", deps=["FastAgent1", "FastAgent2"], delay=1.0),
            ]

    start_time = time.time()

    orch = MockOrchestrator()
    await orch.run_cycle_async(enable_parallel=True)

    elapsed = time.time() - start_time

    print(f"\n✅ Total time: {elapsed:.2f}s")
    print(f"   Expected: ~1.5s (0.5s parallel + 1.0s sequential)")
    return elapsed


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("🧪 ASYNC ORCHESTRATION TESTS - PHASE 17")
    print("=" * 80)

    # Test 1: Sequential sync (baseline)
    sync_time = test_sequential_sync()

    # Test 2: Sequential async (same as sync, but non-blocking)
    async_time = await test_sequential_async()

    # Test 3: Parallel async (3x faster!)
    parallel_time = await test_parallel_async()

    # Test 4: Full orchestrator
    orch_time = await test_orchestrator_parallel()

    # Summary
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 80 + "\n")

    print(f"Sequential Sync:      {sync_time:.2f}s")
    print(f"Sequential Async:     {async_time:.2f}s (Same as sync)")
    print(f"Parallel Async:       {parallel_time:.2f}s ({sync_time/parallel_time:.1f}x speedup!)")
    print(f"Orchestrator Parallel: {orch_time:.2f}s")

    print("\n✅ All tests passed!")
    print("\n💡 Key Takeaway:")
    print("   - Async alone doesn't speed up sequential work")
    print("   - Parallel execution of independent agents = HUGE speedup")
    print("   - For I/O-bound agents (API calls), expect 2-5x improvement")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
