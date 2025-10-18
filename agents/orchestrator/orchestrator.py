"""
orchestrator.py
Phase 1.5 – Management-Team-Ready Orchestrator
Phase 1.1 Update – Standardized BaseAgent Interface
"""

import importlib
import yaml
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set

# Phase 1.1: Import BaseAgent components
from core.base_agent import BaseAgent, AgentContext
from core.cache import Cache

# Phase 16: Import ProjectMemory for persistent storage
from core.project_memory import ProjectMemory


class Orchestrator:
    """
    Plugin-based orchestrator that coordinates agents from YAML registry.
    
    Success Criteria:
    ✅ Executes Planning and Research Agents
    ✅ Skips missing/inactive agents gracefully
    ✅ Generates session summary and logs
    ✅ Supports future agent plugins without refactor
    """
    
    def __init__(self, registry_path="./agents/orchestrator/agent_registry.yaml", project_id=None):
        """Initialize orchestrator with agent registry."""
        self.registry_path = registry_path
        self.log_path = "./logs/orchestrator.log"
        self.results = {}
        self.session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.project_id = project_id or f"project_{self.session_id}"
        self.logger = self._init_logger()
        self.agents = self._load_agents()

        # Phase 16: Initialize persistent memory (optional - graceful failure)
        self.memory = self._init_memory()

        # Project Context: Initialize context tracker (optional - graceful failure)
        self.context_tracker = self._init_context_tracker()

    def _init_logger(self):
        """Setup logging to file."""
        Path("logs").mkdir(exist_ok=True)
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format="%(asctime)s | %(message)s"
        )
        logger = logging.getLogger("orchestrator")
        logger.info(f"Session start {self.session_id}")
        return logger

    def _load_agents(self):
        """Load active agents from registry."""
        with open(self.registry_path, "r") as f:
            registry = yaml.safe_load(f)
        
        agents = []
        for a in sorted(registry["agents"], key=lambda x: x["stage"]):
            if not a.get("active", False):
                self.logger.info(f"{a['name']} SKIPPED (inactive)")
                continue
            
            try:
                module_path, class_name = a["path"].split(":")
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name)
                agents.append(cls())
                self.logger.info(f"{a['name']} loaded")
            except Exception as e:
                self.logger.error(f"Failed to load {a['name']}: {e}")
        
        return agents

    def run_cycle(self):
        """
        Execute all active agents in sequence.

        Phase 1.1 Changes:
            - Removed method guessing (hasattr checks)
            - All agents now use standardized execute(context)
            - Created AgentContext for shared data
            - Validate inputs before execution
            - Store AgentOutput in shared context
        """
        self.logger.info("Cycle start")
        print(f"🔄 Starting orchestration cycle (Phase 1.1)...\n")

        # Phase 1.1: Create shared execution context
        context = AgentContext(
            session_id=self.session_id,
            inputs=self._load_inputs(),
            cache=self._init_cache(),
            shared_data={}
        )

        for agent in self.agents:
            name = agent.name if isinstance(agent, BaseAgent) else agent.__class__.__name__
            self.logger.info(f"Running {name}")
            print(f"▶️  {name}...")

            try:
                # Phase 1.1: Validate inputs first
                if isinstance(agent, BaseAgent):
                    if not agent.validate_inputs(context):
                        raise ValueError(f"Input validation failed for {name}")

                # Phase 16: Publish agent start event
                if self.memory:
                    self.memory.publish_event("agent_started", {
                        "agent": name,
                        "project_id": self.project_id,
                        "session_id": self.session_id
                    })

                # Phase 1.1: Standardized execution
                if isinstance(agent, BaseAgent):
                    result = agent.execute(context)
                    # Validate AgentOutput
                    result.validate()
                    # Store in shared context for downstream agents
                    context.shared_data[name] = result

                    # Phase 16: Store in persistent memory
                    if self.memory:
                        self.memory.store_project(
                            project_id=self.project_id,
                            stage=name,
                            data=result.data_for_next_agent
                        )
                else:
                    # Legacy agents (not yet migrated)
                    print(f"   ⚠️  {name} not migrated to BaseAgent yet")
                    result = self._run_legacy_agent(agent)

                self.results[name] = result
                self.logger.info(f"{name} completed")

                # Phase 16: Publish agent completion event
                if self.memory:
                    self.memory.publish_event("agent_completed", {
                        "agent": name,
                        "project_id": self.project_id,
                        "session_id": self.session_id,
                        "confidence": getattr(result, 'confidence', None)
                    })

                # Project Context: Log agent activity to timeline
                if self.context_tracker:
                    self.context_tracker.log_activity(
                        project_id=self.project_id,
                        activity=f"{name} completed",
                        agent_name=name,
                        activity_type="agent_run",
                        metadata={
                            "session_id": self.session_id,
                            "confidence": getattr(result, 'confidence', None),
                            "decision": getattr(result, 'decision', None)
                        }
                    )

                    # If agent made a decision, record it
                    if hasattr(result, 'decision') and hasattr(result, 'reasoning'):
                        self.context_tracker.record_decision(
                            project_id=self.project_id,
                            decision=result.decision,
                            rationale=result.reasoning,
                            agent_name=name,
                            confidence=getattr(result, 'confidence', None)
                        )

                # Display confidence if available
                if hasattr(result, 'confidence'):
                    print(f"   ✅ Complete (confidence: {result.confidence:.2f})\n")
                else:
                    print(f"   ✅ Complete\n")

            except NotImplementedError as e:
                self.logger.info(f"{name} SKIPPED – {e}")
                print(f"   ⏭️  Skipped: {e}\n")
                self.results[name] = {"status": "skipped", "reason": str(e)}

            except Exception as e:
                self.results[name] = {"error": str(e)}
                self.logger.error(f"{name} failed: {e}")
                print(f"   ❌ Failed: {e}\n")

        self._write_summary()
        self.logger.info("Cycle complete")

    async def run_cycle_async(self, enable_parallel: bool = True):
        """
        Execute agents with async/await and optional parallel execution.

        Phase 17: Async orchestration with parallel stage execution.

        Features:
            - Non-blocking I/O operations
            - Parallel execution of independent agents (same stage)
            - Better resource utilization
            - 2-5x faster for I/O-bound workloads

        Args:
            enable_parallel: If True, agents in same stage run in parallel

        Example:
            orchestrator = Orchestrator()
            await orchestrator.run_cycle_async(enable_parallel=True)
        """
        self.logger.info("Async cycle start")
        print(f"🔄 Starting async orchestration cycle (Phase 17)...\n")
        if enable_parallel:
            print("⚡ Parallel execution: ENABLED\n")

        # Create shared execution context
        context = AgentContext(
            session_id=self.session_id,
            inputs=self._load_inputs(),
            cache=self._init_cache(),
            shared_data={}
        )

        if enable_parallel:
            # Group agents by stage for parallel execution
            stages = self._group_agents_by_stage()
            total_stages = len(stages)

            for stage_num, stage_agents in enumerate(stages, 1):
                print(f"📍 Stage {stage_num}/{total_stages} ({len(stage_agents)} agents)")

                # Run all agents in this stage in parallel
                tasks = []
                for agent in stage_agents:
                    task = self._execute_agent_async(agent, context)
                    tasks.append(task)

                # Wait for all agents in stage to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for agent, result in zip(stage_agents, results):
                    name = agent.name if isinstance(agent, BaseAgent) else agent.__class__.__name__

                    if isinstance(result, Exception):
                        self.results[name] = {"error": str(result)}
                        self.logger.error(f"{name} failed: {result}")
                        print(f"   ❌ {name}: Failed - {result}\n")
                    else:
                        self.results[name] = result
                        self.logger.info(f"{name} completed")

                        if hasattr(result, 'confidence'):
                            print(f"   ✅ {name}: Complete (confidence: {result.confidence:.2f})\n")
                        else:
                            print(f"   ✅ {name}: Complete\n")

                print()  # Blank line between stages
        else:
            # Sequential async execution
            for agent in self.agents:
                name = agent.name if isinstance(agent, BaseAgent) else agent.__class__.__name__
                print(f"▶️  {name}...")

                try:
                    result = await self._execute_agent_async(agent, context)
                    self.results[name] = result
                    self.logger.info(f"{name} completed")

                    if hasattr(result, 'confidence'):
                        print(f"   ✅ Complete (confidence: {result.confidence:.2f})\n")
                    else:
                        print(f"   ✅ Complete\n")

                except Exception as e:
                    self.results[name] = {"error": str(e)}
                    self.logger.error(f"{name} failed: {e}")
                    print(f"   ❌ Failed: {e}\n")

        self._write_summary()
        self.logger.info("Async cycle complete")

    async def _execute_agent_async(self, agent: BaseAgent, context: AgentContext):
        """
        Execute a single agent asynchronously.

        Phase 17: Handles validation, execution, memory storage, and event publishing.
        """
        name = agent.name if isinstance(agent, BaseAgent) else agent.__class__.__name__

        # Validate inputs
        if isinstance(agent, BaseAgent):
            if not agent.validate_inputs(context):
                raise ValueError(f"Input validation failed for {name}")

        # Publish start event
        if self.memory:
            self.memory.publish_event("agent_started", {
                "agent": name,
                "project_id": self.project_id,
                "session_id": self.session_id
            })

        # Execute agent (async)
        if isinstance(agent, BaseAgent):
            result = await agent.execute_async(context)
            result.validate()
            context.shared_data[name] = result

            # Store in persistent memory
            if self.memory:
                self.memory.store_project(
                    project_id=self.project_id,
                    stage=name,
                    data=result.data_for_next_agent
                )
        else:
            # Legacy agents (run in thread pool)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_legacy_agent, agent)

        # Publish completion event
        if self.memory:
            self.memory.publish_event("agent_completed", {
                "agent": name,
                "project_id": self.project_id,
                "session_id": self.session_id,
                "confidence": getattr(result, 'confidence', None)
            })

        return result

    def _group_agents_by_stage(self) -> List[List[BaseAgent]]:
        """
        Group agents by their dependencies for parallel execution.

        Phase 17: Agents with same dependencies can run in parallel.

        Returns:
            List of stages, where each stage is a list of agents that can run in parallel

        Example:
            Stage 0: [AgentA, AgentB]  # No dependencies, run in parallel
            Stage 1: [AgentC]          # Depends on AgentA
            Stage 2: [AgentD, AgentE]  # Both depend on AgentC, run in parallel
        """
        stages: List[List[BaseAgent]] = []
        processed: Set[str] = set()
        remaining = list(self.agents)

        while remaining:
            # Find agents whose dependencies have been satisfied
            ready = []
            for agent in remaining:
                if not isinstance(agent, BaseAgent):
                    ready.append(agent)
                    continue

                deps = set(agent.dependencies)
                if deps.issubset(processed):
                    ready.append(agent)

            if not ready:
                # Circular dependency or missing dependencies
                self.logger.error(f"Circular dependency detected in agents: {[a.name for a in remaining]}")
                break

            # Add this stage
            stages.append(ready)

            # Mark as processed
            for agent in ready:
                if isinstance(agent, BaseAgent):
                    processed.add(agent.name)
                remaining.remove(agent)

        return stages

    def _load_inputs(self):
        """Load input files for agents."""
        return {
            "prd_path": "./projects/swing-fx-trading-assistant/docs/trading_strategy_prd.md"
        }

    def _init_memory(self):
        """
        Initialize persistent memory system (Phase 16).
        Gracefully falls back if Redis is unavailable.
        """
        try:
            memory = ProjectMemory()
            self.logger.info("✅ Persistent memory connected (Redis)")
            print("🧠 Persistent memory: ENABLED")
            return memory
        except ConnectionError as e:
            self.logger.warning(f"⚠️  Persistent memory unavailable: {e}")
            print("⚠️  Persistent memory: DISABLED (Redis not running)")
            print("   Start Redis: ./scripts/start_redis.sh")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️  Memory initialization failed: {e}")
            return None

    def _init_context_tracker(self):
        """
        Initialize project context tracker for managing project status,
        milestones, decisions, and timeline.

        Gracefully falls back if database is unavailable.
        """
        try:
            from core.project_context import ProjectContext
            context_tracker = ProjectContext()
            self.logger.info("✅ Project context tracker initialized")
            print("📋 Project context tracking: ENABLED")
            return context_tracker
        except ConnectionError as e:
            self.logger.warning(f"⚠️  Context tracker unavailable: {e}")
            print("⚠️  Project context: DISABLED (Database error)")
            return None
        except Exception as e:
            self.logger.warning(f"⚠️  Context tracker initialization failed: {e}")
            print(f"⚠️  Project context: DISABLED ({e})")
            return None

    def _init_cache(self):
        """Initialize cache for performance optimization."""
        try:
            return Cache()
        except Exception:
            return None

    def _run_legacy_agent(self, agent):
        """
        Fallback for agents not yet migrated to BaseAgent.
        Phase 1.1: This method will be removed once all agents are migrated.
        """
        if hasattr(agent, 'run_cycle'):
            return agent.run_cycle()
        elif hasattr(agent, 'run'):
            return agent.run()
        elif hasattr(agent, 'execute'):
            return agent.execute()
        else:
            raise NotImplementedError(f"Agent {agent.__class__.__name__} has no execution method")

    def _write_summary(self):
        """Generate session summary from template."""
        Path("outputs").mkdir(exist_ok=True)
        
        template_path = Path("./agents/orchestrator/templates/session_summary_template.md")
        
        if template_path.exists():
            template = template_path.read_text()
        else:
            template = "# Session {{session_id}}\n\n{{combined_results}}\n"
        
        # Build agent table
        table_lines = []
        for name, v in self.results.items():
            status = 'OK' if 'error' not in str(v) else 'FAIL'
            error_msg = v.get('error', '–') if isinstance(v, dict) else '–'
            table_lines.append(f"| {name} | {status} | {error_msg} |")
        
        agent_table = "\n".join(table_lines)

        # Convert AgentOutput to dict for JSON serialization
        results_serializable = {}
        for name, result in self.results.items():
            if hasattr(result, '__dict__'):
                results_serializable[name] = result.__dict__
            else:
                results_serializable[name] = result

        combined = json.dumps(results_serializable, indent=2, default=str)
        
        # Simple template replacement
        filled = template.replace("{{session_id}}", self.session_id) \
                        .replace("{{combined_results}}", combined) \
                        .replace("{{log_path}}", self.log_path) \
                        .replace("{% for agent in agents %}", "") \
                        .replace("{% endfor %}", "") \
                        .replace("{{agent_table}}", agent_table)
        
        # Remove any remaining template syntax
        import re
        filled = re.sub(r'\{\{[^}]+\}\}', '', filled)
        filled = re.sub(r'\{%[^%]+%\}', '', filled)
        
        out_path = Path(f"./outputs/session_summary_{self.session_id}.md")
        out_path.write_text(filled)
        
        self.logger.info(f"Summary written to {out_path}")
        print(f"✅ Summary saved: {out_path}")


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 70)
    print("🎭 ORCHESTRATOR v2.2 - PHASE 17")
    print("Management-Team with Async/Await & Parallel Execution")
    print("=" * 70 + "\n")

    # Check for async flag
    use_async = "--async" in sys.argv
    enable_parallel = "--parallel" in sys.argv or "--async" in sys.argv

    o = Orchestrator()

    if use_async:
        print("⚡ Running in ASYNC mode with parallel execution\n")
        asyncio.run(o.run_cycle_async(enable_parallel=enable_parallel))
    else:
        print("📍 Running in SYNC mode (sequential)\n")
        print("💡 Tip: Use --async for 2-5x faster execution\n")
        o.run_cycle()

    print("\n" + "=" * 70)
    print("✅ ORCHESTRATION COMPLETE")
    print("=" * 70 + "\n")

