"""
critic.py
Critic Agent - Adversarial review sub-agent.
---------------------------------------------------------

WHY: Even well-intentioned plans have blind spots. The Critic provides
adversarial review before execution, identifying security vulnerabilities,
performance bottlenecks, edge cases, and failure modes that optimistic
planning might miss.

TRIGGER RULES (any):
    - Risky changes (auth, payments, credentials)
    - Security-impacting diffs
    - Integration with money/sensitive data
    - Major refactors or architectural changes
    - User explicitly requests review

OUTPUT:
    - Top 10 risks ranked by severity
    - Suggested fixes for each risk
    - Overall recommendation (proceed/revise/stop)
    - Stored as sub-agent artifact in ProjectContext (queryable by dashboard)

EXECUTION MODE: Interactive (explains plan, gets user approval)

Created: 2025-10-18 (Phase 1 - Sub-Agent Unification)
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

logger = logging.getLogger(__name__)


class CriticAgent(BaseAgent):
    """
    Critic Agent - Adversarial review of plans and code.

    WHY: Catch risks, vulnerabilities, and edge cases before they
    become production issues. Runs interactively with user approval.
    """

    @property
    def name(self) -> str:
        """Agent identifier for registry and logging."""
        return "CriticAgent"

    @property
    def dependencies(self) -> List[str]:
        """
        No dependencies - can review any plan/code independently.

        WHY: Critic is called ad-hoc when risky changes are detected,
        not part of sequential workflow.
        """
        return []

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that we have something to review.

        WHY: Need either a plan, code diff, or implementation details.
        """
        plan = context.inputs.get('plan')
        code_diff = context.inputs.get('code_diff')
        implementation = context.inputs.get('implementation')

        if not any([plan, code_diff, implementation]):
            logger.warning(f"{self.name}: No plan, code_diff, or implementation provided")
            return False

        return True

    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Perform adversarial review of plan/code.

        WHY: Identify risks and failure modes before execution,
        enabling safer implementations.

        Args:
            context: Contains plan, code_diff, or implementation details

        Returns:
            AgentOutput with risk analysis and recommendations
        """
        logger.info(f"{self.name}: Starting adversarial review...")

        plan = context.inputs.get('plan', '')
        code_diff = context.inputs.get('code_diff', '')
        implementation = context.inputs.get('implementation', '')
        change_type = context.inputs.get('change_type', 'general')

        # TODO: Implement actual adversarial review logic
        # 1. Parse plan/code to understand what's being changed
        # 2. Check for security vulnerabilities (SQL injection, XSS, auth bypass, etc.)
        # 3. Identify performance bottlenecks (N+1 queries, memory leaks, etc.)
        # 4. Find edge cases (null handling, empty arrays, race conditions, etc.)
        # 5. Look for failure modes (network errors, timeout handling, etc.)
        # 6. Rank risks by severity (critical > high > medium > low)
        # 7. Suggest specific fixes for each risk
        # 8. Provide overall recommendation (proceed/revise/stop)

        review = {
            'timestamp': datetime.now().isoformat(),
            'change_type': change_type,
            'risks': [
                # Example risk structure:
                # {
                #     'severity': 'critical',  # critical, high, medium, low
                #     'category': 'security',   # security, performance, reliability, maintainability
                #     'description': 'SQL injection vulnerability in user input',
                #     'location': 'line 42 in user_service.py',
                #     'suggested_fix': 'Use parameterized queries instead of string concatenation',
                #     'impact': 'Could allow unauthorized database access'
                # }
            ],
            'overall_recommendation': 'proceed',  # proceed, revise, stop
            'reasoning': 'TODO: Implement adversarial review logic',
            'confidence': 0.0,  # Low confidence until implemented
            'summary': 'Adversarial review skeleton ready for implementation'
        }

        return AgentOutput(
            agent_name=self.name,
            decision="review_complete",
            reasoning="Adversarial review skeleton ready for implementation",
            data_for_next_agent=review,
            confidence=1.0,  # High confidence in placeholder structure
            metadata={
                'execution_mode': 'interactive',
                'artifact_type': 'adversarial_review',
                'risk_count': len(review['risks'])
            }
        )

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: Code analysis can be compute-intensive, async allows
        other agents to continue working during review.
        """
        # TODO: Implement async adversarial review
        # For now, just call sync version
        return self.execute(context)
