"""
CriticAgent - Adversarial security and risk review before risky changes

WHY: Catches vulnerabilities, edge cases, and failure modes before they become
production issues. Provides independent review perspective using adversarial
thinking patterns.

AUTO-TRIGGERS:
- Security-impacting changes
- Authentication or payment code modifications
- High complexity tasks
- Low confidence (<0.7)
- Risky operations (database schema, API contracts)

USAGE:
    agent = CriticAgent()
    result = agent.review({
        'change_type': 'security',
        'description': 'Implement JWT authentication',
        'files': ['core/auth.py', 'core/middleware.py'],
        'code_diff': '...'  # Optional
    })

OUTPUT:
    {
        'risks': [...]  # Top 10 risks ranked by severity
        'recommendation': 'proceed' | 'revise' | 'stop',
        'summary': '...',
        '_audit_trail': {...}
    }

Created: 2025-01-04 (Subagent System Implementation)
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CriticAgent:
    """
    Adversarial code review agent focused on security and risk.

    Analyzes code changes through adversarial lens:
    - Security vulnerabilities
    - Edge cases and failure modes
    - Performance bottlenecks
    - Data integrity risks
    - Scalability concerns

    Returns top 10 risks ranked by severity with mitigation suggestions.
    """

    # Risk categories and their severity weights
    RISK_CATEGORIES = {
        'security': {
            'weight': 10,
            'patterns': ['password', 'token', 'api_key', 'secret', 'auth', 'credential', 'jwt', 'session']
        },
        'data_integrity': {
            'weight': 9,
            'patterns': ['sql', 'delete', 'truncate', 'drop', 'update', 'transaction', 'commit']
        },
        'authentication': {
            'weight': 10,
            'patterns': ['login', 'logout', 'authenticate', 'authorize', 'permission', 'role']
        },
        'payment': {
            'weight': 10,
            'patterns': ['payment', 'billing', 'charge', 'stripe', 'invoice', 'transaction']
        },
        'performance': {
            'weight': 6,
            'patterns': ['loop', 'recursive', 'n+1', 'query', 'cache', 'timeout']
        },
        'error_handling': {
            'weight': 7,
            'patterns': ['try', 'except', 'error', 'exception', 'raise', 'assert']
        },
        'concurrency': {
            'weight': 8,
            'patterns': ['thread', 'lock', 'async', 'await', 'race', 'mutex']
        },
        'api_contracts': {
            'weight': 7,
            'patterns': ['api', 'endpoint', 'route', 'request', 'response', 'schema']
        }
    }

    def __init__(self):
        """Initialize CriticAgent."""
        pass

    def review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform adversarial review of planned changes.

        Args:
            context: Review context with:
                - change_type: Type of change (security, feature, refactor, etc.)
                - description: What's being changed
                - files: List of files being modified
                - code_diff: Optional code diff/preview
                - complexity: Complexity level
                - confidence: Confidence in approach

        Returns:
            Dict with risks, recommendation, summary, _audit_trail
        """
        change_type = context.get('change_type', 'general')
        description = context.get('description', 'Unknown changes')
        files = context.get('files', [])

        logger.info(f"🔍 CriticAgent reviewing: {description}")

        # Detect applicable risk categories
        applicable_categories = self._detect_risk_categories(context)

        # Generate risks
        risks = self._generate_risks(context, applicable_categories)

        # Rank risks by severity
        risks = sorted(risks, key=lambda r: r['severity_score'], reverse=True)[:10]

        # Make recommendation
        recommendation = self._make_recommendation(risks, context)

        # Generate summary
        summary = self._generate_summary(risks, recommendation)

        result = {
            'success': True,
            'risks': risks,
            'risk_count': len(risks),
            'recommendation': recommendation['decision'],
            'recommendation_rationale': recommendation['rationale'],
            'summary': summary,
            'artifact_type': 'review',
            '_audit_trail': {
                'generated_at': datetime.now().isoformat(),
                'change_type': change_type,
                'description': description,
                'files_reviewed': len(files),
                'risk_categories_detected': list(applicable_categories.keys()),
                'version': 'v1.0'
            }
        }

        logger.info(f"✅ CriticAgent: {len(risks)} risks identified, recommendation: {recommendation['decision']}")

        return result

    def _detect_risk_categories(self, context: Dict) -> Dict[str, Dict]:
        """Detect which risk categories apply to this change."""
        applicable = {}

        change_type = context.get('change_type', '').lower()
        description = (context.get('description', '') + ' ' + change_type).lower()
        files = context.get('files', [])
        code_diff = context.get('code_diff', '').lower()

        # Combine all text for analysis
        combined_text = f"{description} {' '.join(files)} {code_diff}"

        for category, info in self.RISK_CATEGORIES.items():
            # Check if any patterns match
            matches = [p for p in info['patterns'] if p in combined_text]

            if matches:
                applicable[category] = {
                    'weight': info['weight'],
                    'matched_patterns': matches
                }

        return applicable

    def _generate_risks(self, context: Dict, applicable_categories: Dict) -> List[Dict]:
        """Generate specific risks based on change context."""
        risks = []

        change_type = context.get('change_type', '').lower()
        description = context.get('description', '')
        confidence = context.get('confidence', 0.8)

        # SECURITY RISKS
        if 'security' in applicable_categories:
            risks.append({
                'id': 1,
                'category': 'security',
                'title': 'Credential Exposure Risk',
                'description': 'Security-related changes risk exposing credentials if not properly handled.',
                'severity': 'critical',
                'severity_score': 10,
                'likelihood': 'medium',
                'mitigation': [
                    'Ensure all secrets use environment variables (.env)',
                    'Never log credentials or tokens',
                    'Use secrets management service for production',
                    'Add pre-commit hooks to scan for hardcoded secrets'
                ]
            })

        if 'authentication' in applicable_categories:
            risks.append({
                'id': 2,
                'category': 'authentication',
                'title': 'Authentication Bypass',
                'description': 'Auth changes may introduce bypass vulnerabilities if edge cases not covered.',
                'severity': 'critical',
                'severity_score': 10,
                'likelihood': 'medium',
                'mitigation': [
                    'Test all authentication paths (valid, invalid, edge cases)',
                    'Verify authorization checks applied to all endpoints',
                    'Test session expiry and token revocation',
                    'Add integration tests for auth flows'
                ]
            })

        # DATA INTEGRITY RISKS
        if 'data_integrity' in applicable_categories:
            risks.append({
                'id': 3,
                'category': 'data_integrity',
                'title': 'Data Loss or Corruption',
                'description': 'Database operations risk data loss if transactions not properly handled.',
                'severity': 'critical',
                'severity_score': 9,
                'likelihood': 'medium',
                'mitigation': [
                    'Wrap critical operations in transactions',
                    'Add data validation before writes',
                    'Implement backup/rollback strategy',
                    'Test failure scenarios (connection loss, timeout)'
                ]
            })

        # PAYMENT RISKS
        if 'payment' in applicable_categories:
            risks.append({
                'id': 4,
                'category': 'payment',
                'title': 'Payment Processing Errors',
                'description': 'Payment changes risk charging errors, refund issues, or double-billing.',
                'severity': 'critical',
                'severity_score': 10,
                'likelihood': 'high',
                'mitigation': [
                    'Use idempotency keys for all payment operations',
                    'Test edge cases: network failures, partial payments, refunds',
                    'Add comprehensive logging for audit trail',
                    'Implement retry logic with exponential backoff',
                    'Never store raw credit card data (PCI compliance)'
                ]
            })

        # PERFORMANCE RISKS
        if 'performance' in applicable_categories:
            risks.append({
                'id': 5,
                'category': 'performance',
                'title': 'Performance Degradation',
                'description': 'Changes may introduce performance bottlenecks or N+1 query issues.',
                'severity': 'high',
                'severity_score': 7,
                'likelihood': 'medium',
                'mitigation': [
                    'Profile code for hot paths',
                    'Check for N+1 queries (use select_related/prefetch_related)',
                    'Add indexes for frequently queried fields',
                    'Consider caching for expensive operations',
                    'Load test with realistic data volumes'
                ]
            })

        # ERROR HANDLING RISKS
        if 'error_handling' in applicable_categories:
            risks.append({
                'id': 6,
                'category': 'error_handling',
                'title': 'Unhandled Edge Cases',
                'description': 'Error handling may miss edge cases leading to crashes or data inconsistency.',
                'severity': 'high',
                'severity_score': 7,
                'likelihood': 'high',
                'mitigation': [
                    'Add try/except for all external calls (API, DB, file I/O)',
                    'Handle None/empty cases explicitly',
                    'Validate input before processing',
                    'Test failure scenarios (timeout, malformed data, missing fields)',
                    'Add logging for errors with context'
                ]
            })

        # CONCURRENCY RISKS
        if 'concurrency' in applicable_categories:
            risks.append({
                'id': 7,
                'category': 'concurrency',
                'title': 'Race Conditions',
                'description': 'Concurrent operations risk race conditions or deadlocks if not synchronized.',
                'severity': 'high',
                'severity_score': 8,
                'likelihood': 'medium',
                'mitigation': [
                    'Use locks/mutexes for shared state',
                    'Consider atomic operations (compare-and-swap)',
                    'Test concurrent scenarios (multiple threads/processes)',
                    'Add timeout for lock acquisition',
                    'Document thread-safety assumptions'
                ]
            })

        # API CONTRACT RISKS
        if 'api_contracts' in applicable_categories:
            risks.append({
                'id': 8,
                'category': 'api_contracts',
                'title': 'Breaking API Changes',
                'description': 'API modifications may break existing clients if not versioned properly.',
                'severity': 'high',
                'severity_score': 7,
                'likelihood': 'medium',
                'mitigation': [
                    'Version API endpoints (/v1/, /v2/)',
                    'Deprecate old endpoints before removing',
                    'Document all breaking changes',
                    'Add integration tests for API contracts',
                    'Use schema validation (OpenAPI, JSON Schema)'
                ]
            })

        # GENERAL RISKS (always apply)
        if confidence < 0.7:
            risks.append({
                'id': 9,
                'category': 'implementation',
                'title': 'Low Confidence Implementation',
                'description': f'Low confidence ({confidence:.0%}) increases risk of bugs and incorrect assumptions.',
                'severity': 'high',
                'severity_score': 8,
                'likelihood': 'high',
                'mitigation': [
                    'Research best practices for this pattern',
                    'Review similar implementations in codebase',
                    'Ask for code review from domain expert',
                    'Add comprehensive tests before deploying',
                    'Consider prototyping approach first'
                ]
            })

        if context.get('complexity') in ['high', 'very_high']:
            risks.append({
                'id': 10,
                'category': 'complexity',
                'title': 'High Complexity Maintenance Burden',
                'description': 'Complex code is harder to maintain, test, and debug.',
                'severity': 'medium',
                'severity_score': 6,
                'likelihood': 'high',
                'mitigation': [
                    'Break into smaller, testable functions',
                    'Add extensive documentation and comments',
                    'Consider simplifying approach if possible',
                    'Ensure comprehensive test coverage (>80%)',
                    'Add examples/usage documentation'
                ]
            })

        return risks

    def _make_recommendation(self, risks: List[Dict], context: Dict) -> Dict[str, str]:
        """Make proceed/revise/stop recommendation based on risks."""

        if not risks:
            return {
                'decision': 'proceed',
                'rationale': 'No significant risks identified. Safe to proceed.'
            }

        critical_risks = [r for r in risks if r['severity'] == 'critical']
        high_risks = [r for r in risks if r['severity'] == 'high']

        # STOP if multiple critical risks
        if len(critical_risks) >= 3:
            return {
                'decision': 'stop',
                'rationale': f'{len(critical_risks)} critical risks identified. Recommend redesigning approach to reduce risk.'
            }

        # REVISE if any critical risk or many high risks
        if len(critical_risks) >= 1 or len(high_risks) >= 4:
            return {
                'decision': 'revise',
                'rationale': f'{len(critical_risks)} critical and {len(high_risks)} high-severity risks. Address mitigations before proceeding.'
            }

        # PROCEED with caution
        return {
            'decision': 'proceed',
            'rationale': f'Risks are manageable. Review {len(high_risks)} high-severity mitigations before deploying.'
        }

    def _generate_summary(self, risks: List[Dict], recommendation: Dict) -> str:
        """Generate human-readable summary."""

        critical_count = len([r for r in risks if r['severity'] == 'critical'])
        high_count = len([r for r in risks if r['severity'] == 'high'])
        medium_count = len([r for r in risks if r['severity'] == 'medium'])

        summary = f"**CriticAgent Review Summary**\n\n"
        summary += f"**Risk Analysis:**\n"
        summary += f"- Critical: {critical_count}\n"
        summary += f"- High: {high_count}\n"
        summary += f"- Medium: {medium_count}\n\n"
        summary += f"**Recommendation:** {recommendation['decision'].upper()}\n"
        summary += f"**Rationale:** {recommendation['rationale']}\n\n"

        if risks:
            summary += "**Top 3 Risks:**\n"
            for risk in risks[:3]:
                summary += f"{risk['id']}. **{risk['title']}** ({risk['severity']})\n"
                summary += f"   {risk['description']}\n\n"

        return summary


# Convenience function for direct usage
def review_changes(
    change_type: str,
    description: str,
    files: Optional[List[str]] = None,
    complexity: str = 'medium',
    confidence: float = 0.8
) -> Dict[str, Any]:
    """
    Convenience function to review changes.

    Usage:
        result = review_changes(
            change_type="security",
            description="Implement JWT authentication",
            files=["core/auth.py", "core/middleware.py"],
            complexity="high",
            confidence=0.7
        )
    """
    agent = CriticAgent()
    return agent.review({
        'change_type': change_type,
        'description': description,
        'files': files or [],
        'complexity': complexity,
        'confidence': confidence
    })
