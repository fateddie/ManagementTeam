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
        files_to_review = context.inputs.get('files', [])

        # Combine all review content
        review_content = f"{plan}\n{code_diff}\n{implementation}"

        # 1. Check for security vulnerabilities
        security_risks = self._check_security(review_content, files_to_review)

        # 2. Identify performance bottlenecks
        performance_risks = self._check_performance(review_content, files_to_review)

        # 3. Find edge cases
        edge_case_risks = self._check_edge_cases(review_content, files_to_review)

        # 4. Look for failure modes
        reliability_risks = self._check_reliability(review_content, files_to_review)

        # 5. Combine and rank risks
        all_risks = security_risks + performance_risks + edge_case_risks + reliability_risks
        ranked_risks = self._rank_risks(all_risks)

        # 6. Generate overall recommendation
        recommendation, reasoning = self._generate_recommendation(ranked_risks)

        review = {
            'timestamp': datetime.now().isoformat(),
            'change_type': change_type,
            'risks': ranked_risks[:10],  # Top 10 risks
            'overall_recommendation': recommendation,
            'reasoning': reasoning,
            'confidence': self._calculate_confidence(ranked_risks),
            'summary': f'Found {len(ranked_risks)} potential risks ({sum(1 for r in ranked_risks if r["severity"] == "critical")} critical)'
        }

        return AgentOutput(
            agent_name=self.name,
            decision="review_complete",
            reasoning=reasoning,
            data_for_next_agent=review,
            confidence=review['confidence'],
            metadata={
                'execution_mode': 'interactive',
                'artifact_type': 'adversarial_review',
                'risk_count': len(ranked_risks),
                'critical_count': sum(1 for r in ranked_risks if r['severity'] == 'critical')
            }
        )

    def _check_security(self, content: str, files: List[str]) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities."""
        risks = []
        content_lower = content.lower()

        # SQL injection patterns
        sql_patterns = [
            ('sql', 'execute', 'SQL injection risk if using string concatenation'),
            ('query', '+', 'String concatenation in query - use parameterized queries'),
            ('format(', 'sql', 'SQL query formatting - potential injection risk'),
        ]

        for pattern1, pattern2, description in sql_patterns:
            if pattern1 in content_lower and pattern2 in content_lower:
                risks.append({
                    'severity': 'critical',
                    'category': 'security',
                    'description': description,
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Use parameterized queries or ORM with parameter binding',
                    'impact': 'Could allow unauthorized database access or data modification'
                })

        # Authentication/Authorization
        auth_patterns = [
            ('password', 'plain', 'Plaintext password handling'),
            ('token', 'hardcode', 'Hardcoded authentication token'),
            ('api_key', '=', 'Hardcoded API key'),
            ('auth', 'skip', 'Authentication bypass'),
        ]

        for pattern1, pattern2, description in auth_patterns:
            if pattern1 in content_lower and pattern2 in content_lower:
                risks.append({
                    'severity': 'critical',
                    'category': 'security',
                    'description': description,
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Use environment variables, secrets management, or secure credential storage',
                    'impact': 'Could expose credentials or allow unauthorized access'
                })

        # XSS patterns
        if 'html' in content_lower and 'user' in content_lower:
            if 'sanitize' not in content_lower and 'escape' not in content_lower:
                risks.append({
                    'severity': 'high',
                    'category': 'security',
                    'description': 'Potential XSS vulnerability - user input in HTML without sanitization',
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Sanitize user input before rendering in HTML',
                    'impact': 'Could allow malicious scripts to execute in user browsers'
                })

        return risks

    def _check_performance(self, content: str, files: List[str]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        risks = []
        content_lower = content.lower()

        # N+1 query pattern
        if 'for' in content_lower and 'query' in content_lower:
            risks.append({
                'severity': 'medium',
                'category': 'performance',
                'description': 'Potential N+1 query problem - querying inside loop',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Use batch queries, joins, or eager loading',
                'impact': 'Could cause slow response times and high database load'
            })

        # Large data loading
        if 'all()' in content_lower or 'fetchall' in content_lower:
            risks.append({
                'severity': 'medium',
                'category': 'performance',
                'description': 'Loading all records without pagination',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Implement pagination or streaming',
                'impact': 'Could cause memory issues with large datasets'
            })

        # Synchronous blocking
        if 'sleep' in content_lower or 'wait' in content_lower:
            if 'async' not in content_lower:
                risks.append({
                    'severity': 'low',
                    'category': 'performance',
                    'description': 'Synchronous blocking operation',
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Consider async/await for non-blocking operations',
                    'impact': 'Could block event loop or reduce throughput'
                })

        return risks

    def _check_edge_cases(self, content: str, files: List[str]) -> List[Dict[str, Any]]:
        """Find edge case vulnerabilities."""
        risks = []
        content_lower = content.lower()

        # Null/None handling
        if ('[0]' in content or '.get(' in content_lower) and 'if' not in content_lower[:100]:
            risks.append({
                'severity': 'medium',
                'category': 'reliability',
                'description': 'Missing null/None check before access',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Add null checks or use safe navigation operators',
                'impact': 'Could cause NullPointerException or AttributeError'
            })

        # Division by zero
        if '/' in content and 'zero' not in content_lower:
            risks.append({
                'severity': 'low',
                'category': 'reliability',
                'description': 'Potential division by zero',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Add check for zero before division',
                'impact': 'Could cause runtime errors'
            })

        # Empty collection
        if 'list' in content_lower and '[0]' in content:
            risks.append({
                'severity': 'medium',
                'category': 'reliability',
                'description': 'Accessing first element without checking if collection is empty',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Check collection length before accessing elements',
                'impact': 'Could cause IndexError on empty collections'
            })

        return risks

    def _check_reliability(self, content: str, files: List[str]) -> List[Dict[str, Any]]:
        """Look for failure modes and reliability issues."""
        risks = []
        content_lower = content.lower()

        # Network errors
        if ('http' in content_lower or 'api' in content_lower or 'request' in content_lower):
            if 'try' not in content_lower and 'except' not in content_lower:
                risks.append({
                    'severity': 'high',
                    'category': 'reliability',
                    'description': 'Network request without error handling',
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Add try/except for network errors, implement retries',
                    'impact': 'Could cause crashes on network failures'
                })

        # Timeout handling
        if ('request' in content_lower or 'fetch' in content_lower) and 'timeout' not in content_lower:
            risks.append({
                'severity': 'medium',
                'category': 'reliability',
                'description': 'Missing timeout for external requests',
                'location': 'Unknown - pattern detected in review content',
                'suggested_fix': 'Add timeout parameter to prevent indefinite waits',
                'impact': 'Could cause hanging requests'
            })

        # Race conditions
        if 'thread' in content_lower or 'async' in content_lower:
            if 'lock' not in content_lower and 'mutex' not in content_lower:
                risks.append({
                    'severity': 'high',
                    'category': 'reliability',
                    'description': 'Potential race condition in concurrent code',
                    'location': 'Unknown - pattern detected in review content',
                    'suggested_fix': 'Use locks, mutexes, or atomic operations for shared state',
                    'impact': 'Could cause data corruption or inconsistent state'
                })

        return risks

    def _rank_risks(self, risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank risks by severity."""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        return sorted(risks, key=lambda r: severity_order.get(r['severity'], 4))

    def _generate_recommendation(self, ranked_risks: List[Dict[str, Any]]) -> tuple:
        """Generate overall recommendation and reasoning."""
        if not ranked_risks:
            return 'proceed', 'No significant risks identified. Safe to proceed.'

        critical_count = sum(1 for r in ranked_risks if r['severity'] == 'critical')
        high_count = sum(1 for r in ranked_risks if r['severity'] == 'high')

        if critical_count > 0:
            return 'stop', f'Found {critical_count} critical risk(s). Address these before proceeding.'
        elif high_count > 2:
            return 'revise', f'Found {high_count} high-severity risks. Recommend addressing before proceeding.'
        elif high_count > 0:
            return 'proceed', f'Found {high_count} high-severity risk(s), but safe to proceed with caution.'
        else:
            return 'proceed', f'Found {len(ranked_risks)} low/medium risks. Safe to proceed.'

    def _calculate_confidence(self, risks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on risk analysis."""
        if not risks:
            return 0.5  # Medium confidence - could be clean or could have missed issues

        # Higher confidence when we find specific risks (shows analysis worked)
        base_confidence = 0.7
        risk_bonus = min(0.2, len(risks) * 0.02)  # Up to 0.2 bonus for finding risks
        return min(0.95, base_confidence + risk_bonus)

    async def execute_async(self, context: AgentContext) -> AgentOutput:
        """
        Async version of execute for non-blocking operation.

        WHY: Code analysis can be compute-intensive, async allows
        other agents to continue working during review.
        """
        # TODO: Implement async adversarial review
        # For now, just call sync version
        return self.execute(context)
