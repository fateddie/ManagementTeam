"""
Sub-Agent Coordinator - Hybrid silent/interactive execution model.

WHY: Balances automation (silent background tasks) with transparency
(conversational approval for research). Unifies Cursor sub-agent rules
with project's conversational workflow philosophy.

REASONING:
- Silent agents (Explorer, Historian) run without blocking user
- Interactive agents (Research, Critic) explain plan and get approval
- All artifacts stored in ProjectContext (not .history/ files)
- Quality metrics tracked for continuous improvement
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from pathlib import Path

from core.project_context import ProjectContext
from core.explorer_agent import ExplorerAgent
from core.historian_agent import HistorianAgent
from core.critic_agent import CriticAgent
from core.research_documenter import ResearchDocumenter

logger = logging.getLogger(__name__)


class SubAgentCoordinator:
    """
    Coordinates sub-agent execution with hybrid silent/interactive model.

    Two execution modes:
    1. SILENT: Background execution with progress updates
    2. INTERACTIVE: Conversational explanation + user approval

    WHY TWO MODES:
    - Silent for utility tasks (file mapping, checkpoints)
    - Interactive for research/analysis requiring context
    """

    # Sub-agent classification
    SILENT_AGENTS = [
        'ExplorerAgent',      # File/code mapping
        'HistorianAgent',     # Project snapshots
    ]

    INTERACTIVE_AGENTS = [
        'ResearchDocumenter', # Deep API/library research
        'CriticAgent',        # Adversarial plan review
        'AlignmentAgent',     # Preference checking
    ]

    def __init__(self, project_id: str, session_id: str, verbose: bool = True):
        """
        Initialize sub-agent coordinator.

        Args:
            project_id: Current project ID
            session_id: Current session ID
            verbose: Show progress messages (default: True)
        """
        self.project_id = project_id
        self.session_id = session_id
        self.verbose = verbose
        self.context = ProjectContext()

        # Instantiate agents
        self.explorer = ExplorerAgent()
        self.historian = HistorianAgent()
        self.critic = CriticAgent()
        self.research_documenter = ResearchDocumenter()

        # Metrics tracking
        self.execution_metrics = {}

    def execute_agent(
        self,
        agent_name: str,
        agent_context: Dict[str, Any],
        agent_callable: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute sub-agent based on its execution mode.

        Args:
            agent_name: Name of sub-agent to execute
            agent_context: Context/parameters for agent
            agent_callable: Function to call for execution

        Returns:
            Dict with agent output and metadata

        WHY: Single entry point enforces consistency and metrics tracking
        """
        start_time = datetime.now()

        try:
            # Determine execution mode
            if agent_name in self.SILENT_AGENTS:
                result = self._silent_execution(agent_name, agent_context, agent_callable)
            elif agent_name in self.INTERACTIVE_AGENTS:
                result = self._interactive_execution(agent_name, agent_context, agent_callable)
            else:
                # Unknown agent - default to interactive (safer)
                logger.warning(f"Unknown agent {agent_name}, defaulting to interactive mode")
                result = self._interactive_execution(agent_name, agent_context, agent_callable)

            # Track metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self._record_metrics(agent_name, execution_time, result.get('success', False))

            # Store artifact in ProjectContext
            self._store_artifact(agent_name, result)

            return result

        except Exception as e:
            logger.error(f"Sub-agent {agent_name} failed: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'agent_name': agent_name
            }

    def _silent_execution(
        self,
        agent_name: str,
        agent_context: Dict[str, Any],
        agent_callable: Optional[Callable]
    ) -> Dict[str, Any]:
        """
        Silent background execution with brief progress update.

        WHY: Don't interrupt user flow for utility tasks
        """
        if self.verbose:
            print(f"🔍 {agent_name} running in background...")

        # Use actual agent if agent_callable not provided
        if agent_callable:
            result = agent_callable(agent_context)
        elif agent_name == 'ExplorerAgent':
            result = self.explorer.explore(agent_context)
        elif agent_name == 'HistorianAgent':
            result = self.historian.create_snapshot(agent_context)
        else:
            logger.warning(f"No implementation for silent agent: {agent_name}")
            result = {'success': True, 'message': 'Placeholder execution'}

        if self.verbose and result.get('success'):
            summary = result.get('summary', 'Complete')
            print(f"✓ {agent_name}: {summary}")

        return result

    def _interactive_execution(
        self,
        agent_name: str,
        agent_context: Dict[str, Any],
        agent_callable: Optional[Callable]
    ) -> Dict[str, Any]:
        """
        Interactive execution with explanation and user approval.

        WHY: Research and analysis require user understanding and context
        """
        # Explain what agent will do
        print(f"\n{'='*60}")
        print(f"📋 {agent_name}")
        print(f"{'='*60}\n")

        # Show plan
        plan = self._generate_agent_plan(agent_name, agent_context)
        print(plan)

        # Get user approval
        print(f"\n{'─'*60}")
        print("Proceed with this sub-agent?")
        print("  1) Yes, run it")
        print("  2) Skip this sub-agent")
        print("  3) Adjust parameters")
        print()

        choice = input("Choice [1-3]: ").strip()

        if choice == '2':
            return {
                'success': False,
                'skipped': True,
                'agent_name': agent_name,
                'reason': 'User skipped'
            }

        elif choice == '3':
            print("\n📝 Parameter adjustments:")
            adjustments = input("What would you like to change? → ").strip()
            agent_context['user_adjustments'] = adjustments

        # Execute agent
        print(f"\n🚀 Running {agent_name}...\n")

        # Use actual agent if agent_callable not provided
        if agent_callable:
            result = agent_callable(agent_context)
        elif agent_name == 'ResearchDocumenter':
            result = self.research_documenter.research(agent_context)
        elif agent_name == 'CriticAgent':
            result = self.critic.review(agent_context)
        else:
            logger.warning(f"No implementation for interactive agent: {agent_name}")
            result = {'success': True, 'message': 'Placeholder execution'}

        # Show conversational summary
        if result.get('success'):
            print(f"\n✅ {agent_name} complete!")
            if result.get('summary'):
                print(f"\n{result['summary']}\n")

        return result

    def _generate_agent_plan(self, agent_name: str, context: Dict[str, Any]) -> str:
        """Generate human-readable plan for what agent will do."""

        plans = {
            'ResearchDocumenter': f"""
I'll research documentation for: {context.get('topic', 'unknown')}

📍 **What I'll do:**
   • Search official documentation
   • Check GitHub issues and examples
   • Look for known pitfalls

🎯 **What you'll get:**
   • Capabilities and constraints summary
   • Minimal working example
   • 5-step integration plan with citations
            """,

            'CriticAgent': f"""
I'll review the plan adversarially to find risks.

📍 **What I'll check:**
   • Security vulnerabilities
   • Performance bottlenecks
   • Edge cases and failure modes

🎯 **What you'll get:**
   • Top 10 risks ranked by severity
   • Suggested fixes for each
   • Overall recommendation (proceed/revise/stop)
            """,
        }

        return plans.get(agent_name, f"Execute {agent_name} with provided context")

    def _store_artifact(self, agent_name: str, result: Dict[str, Any]):
        """
        Store sub-agent artifact in ProjectContext.

        WHY: Centralized storage enables dashboard viewing and querying.
        Replaces file-based .history/ approach from Cursor rules.
        """
        try:
            self.context.record_subagent_artifact(
                project_id=self.project_id,
                session_id=self.session_id,
                subagent_name=agent_name,
                artifact_type=result.get('artifact_type', 'execution'),
                data=result,
                metadata={
                    'execution_mode': 'silent' if agent_name in self.SILENT_AGENTS else 'interactive',
                    'timestamp': datetime.now().isoformat(),
                    'success': result.get('success', False)
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store artifact for {agent_name}: {e}")

    def _record_metrics(self, agent_name: str, execution_time: float, success: bool):
        """Track execution metrics for quality monitoring."""
        if agent_name not in self.execution_metrics:
            self.execution_metrics[agent_name] = {
                'total_runs': 0,
                'successful_runs': 0,
                'total_time_sec': 0,
                'avg_time_sec': 0
            }

        metrics = self.execution_metrics[agent_name]
        metrics['total_runs'] += 1
        metrics['total_time_sec'] += execution_time
        metrics['avg_time_sec'] = metrics['total_time_sec'] / metrics['total_runs']

        if success:
            metrics['successful_runs'] += 1

        # Store in ProjectContext for dashboard
        try:
            self.context.update_metadata(
                project_id=self.project_id,
                session_id=self.session_id,
                metadata={f'subagent_metrics_{agent_name}': metrics}
            )
        except Exception as e:
            logger.warning(f"Failed to store metrics: {e}")

    def get_agent_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """Get execution metrics for sub-agents."""
        if agent_name:
            return self.execution_metrics.get(agent_name, {})
        return self.execution_metrics

    def is_silent_agent(self, agent_name: str) -> bool:
        """Check if agent runs silently."""
        return agent_name in self.SILENT_AGENTS

    def is_interactive_agent(self, agent_name: str) -> bool:
        """Check if agent requires user interaction."""
        return agent_name in self.INTERACTIVE_AGENTS


# Convenience function for backward compatibility
def execute_subagent(
    agent_name: str,
    project_id: str,
    session_id: str,
    context: Dict[str, Any],
    agent_callable: Optional[Callable] = None
) -> Dict[str, Any]:
    """
    Execute a sub-agent (convenience wrapper).

    WHY: Simple API for one-off sub-agent execution
    """
    coordinator = SubAgentCoordinator(project_id, session_id)
    return coordinator.execute_agent(agent_name, context, agent_callable)
