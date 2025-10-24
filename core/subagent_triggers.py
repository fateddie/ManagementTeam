"""
subagent_triggers.py
Phase 4 - Auto-triggering Logic: Intelligent sub-agent invocation
---------------------------------------------------------

WHY: Manual sub-agent invocation is error-prone and interrupts flow.
Auto-triggering enables proactive assistance - ExplorerAgent maps files
when complexity warrants it, Historian snapshots at key moments, Critic
reviews risky changes, ResearchDocumenter fills knowledge gaps.

DESIGN PRINCIPLES:
1. Conservative defaults - better to under-trigger than over-trigger
2. Clear decision logic - users should understand why agents activated
3. Easy overrides - users can disable/customize any trigger
4. Logging everything - full audit trail of trigger decisions
5. Confidence-based - adapt to uncertainty levels

USAGE:
    engine = SubAgentTriggerEngine()

    # Check if Explorer should run
    if engine.should_invoke_explorer(context):
        # Run ExplorerAgent
        pass

Created: 2025-10-19 (Phase 4 - Sub-Agent Unification)
"""

import logging
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TriggerDecision:
    """
    Represents a trigger decision with reasoning.

    WHY: Transparency - users should understand why agents were invoked
    """
    should_trigger: bool
    agent_name: str
    reason: str
    confidence: float  # How confident are we in this decision (0.0-1.0)
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SubAgentTriggerEngine:
    """
    Decides when to automatically invoke sub-agents.

    RESPONSIBILITIES:
    - Load configuration from config/subagents.yml
    - Evaluate trigger rules based on context
    - Return trigger decisions with reasoning
    - Track trigger metrics for tuning

    TRIGGER TYPES:
    1. Threshold-based: File count, LOC, complexity
    2. Pattern-based: External APIs, security changes
    3. Confidence-based: Low confidence scores
    4. Risk-based: Risky operations detected
    """

    DEFAULT_CONFIG_PATH = Path("config/subagents.yml")

    def __init__(self, config_path: Optional[Path] = None, enabled: bool = True):
        """
        Initialize trigger engine.

        Args:
            config_path: Path to configuration file (default: config/subagents.yml)
            enabled: Enable auto-triggering (default: True)

        WHY: Allow disabling for testing or manual control
        """
        self.enabled = enabled
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config = self._load_config()

        # Track trigger metrics
        self.trigger_history = []

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return self._get_default_config()

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            logger.info(f"Loaded trigger config from {self.config_path}")
            return config

        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file not found."""
        return {
            'defaults': {
                'max_parallel_research': 3,
                'historian_snapshot_loc_threshold': 150,
                'ask_before_overwrite': True
            },
            'triggers': {
                'explorer': {
                    'files_threshold': 2,
                    'loc_threshold': 150,
                    'enabled': True
                },
                'historian': {
                    'on_end_of_block': True,
                    'on_prd_change': True,
                    'modified_loc_threshold': 150,
                    'enabled': True
                },
                'critic': {
                    'on_risky_changes': True,
                    'on_security_impact': True,
                    'on_high_complexity': True,
                    'enabled': True
                },
                'research_documenter': {
                    'require_for_external_api': True,
                    'require_for_major_version_bump': True,
                    'confidence_threshold': 0.6,
                    'enabled': True
                }
            }
        }

    def should_invoke_explorer(self, context: Dict[str, Any]) -> TriggerDecision:
        """
        Decide if ExplorerAgent should be invoked.

        Args:
            context: Dictionary with:
                - files_to_modify: List of file paths
                - estimated_loc: Estimated lines of code
                - task_description: What's being done
                - complexity: Optional complexity score

        Returns:
            TriggerDecision with reasoning

        TRIGGER CONDITIONS:
        - More than N files affected (files_threshold)
        - More than M LOC affected (loc_threshold)
        - High complexity task
        - Unfamiliar codebase area
        """
        if not self.enabled:
            return TriggerDecision(False, "ExplorerAgent", "Auto-triggering disabled", 1.0)

        trigger_config = self.config.get('triggers', {}).get('explorer', {})
        if not trigger_config.get('enabled', True):
            return TriggerDecision(False, "ExplorerAgent", "Explorer triggers disabled in config", 1.0)

        files_to_modify = context.get('files_to_modify', [])
        estimated_loc = context.get('estimated_loc', 0)
        complexity = context.get('complexity', 'medium')

        # Check file threshold
        files_threshold = trigger_config.get('files_threshold', 2)
        if len(files_to_modify) >= files_threshold:
            return TriggerDecision(
                True,
                "ExplorerAgent",
                f"Task affects {len(files_to_modify)} files (threshold: {files_threshold})",
                0.9,
                {'file_count': len(files_to_modify), 'threshold': files_threshold}
            )

        # Check LOC threshold
        loc_threshold = trigger_config.get('loc_threshold', 150)
        if estimated_loc >= loc_threshold:
            return TriggerDecision(
                True,
                "ExplorerAgent",
                f"Task involves ~{estimated_loc} LOC (threshold: {loc_threshold})",
                0.85,
                {'estimated_loc': estimated_loc, 'threshold': loc_threshold}
            )

        # Check complexity
        if complexity in ['high', 'very_high']:
            return TriggerDecision(
                True,
                "ExplorerAgent",
                f"High complexity task ({complexity}) warrants file mapping",
                0.8,
                {'complexity': complexity}
            )

        return TriggerDecision(
            False,
            "ExplorerAgent",
            "Below trigger thresholds - not needed",
            0.7
        )

    def should_invoke_historian(self, context: Dict[str, Any]) -> TriggerDecision:
        """
        Decide if HistorianAgent should be invoked for checkpoint.

        Args:
            context: Dictionary with:
                - modified_loc: Lines of code modified
                - at_end_of_block: Boolean, end of work session
                - prd_changed: Boolean, PRD was modified
                - milestone_reached: Boolean, major milestone

        Returns:
            TriggerDecision with reasoning

        TRIGGER CONDITIONS:
        - End of work block
        - PRD/architecture changed
        - More than N LOC modified
        - Major milestone reached
        """
        if not self.enabled:
            return TriggerDecision(False, "HistorianAgent", "Auto-triggering disabled", 1.0)

        trigger_config = self.config.get('triggers', {}).get('historian', {})
        if not trigger_config.get('enabled', True):
            return TriggerDecision(False, "HistorianAgent", "Historian triggers disabled in config", 1.0)

        modified_loc = context.get('modified_loc', 0)
        at_end_of_block = context.get('at_end_of_block', False)
        prd_changed = context.get('prd_changed', False)
        milestone_reached = context.get('milestone_reached', False)

        # End of work block
        if at_end_of_block and trigger_config.get('on_end_of_block', True):
            return TriggerDecision(
                True,
                "HistorianAgent",
                "End of work block - create snapshot for continuity",
                0.95,
                {'trigger_type': 'end_of_block'}
            )

        # PRD changed
        if prd_changed and trigger_config.get('on_prd_change', True):
            return TriggerDecision(
                True,
                "HistorianAgent",
                "PRD changed - snapshot critical project state",
                0.9,
                {'trigger_type': 'prd_change'}
            )

        # Milestone reached
        if milestone_reached:
            return TriggerDecision(
                True,
                "HistorianAgent",
                "Major milestone reached - create checkpoint",
                0.92,
                {'trigger_type': 'milestone'}
            )

        # LOC threshold
        loc_threshold = trigger_config.get('modified_loc_threshold', 150)
        if modified_loc >= loc_threshold:
            return TriggerDecision(
                True,
                "HistorianAgent",
                f"Modified {modified_loc} LOC (threshold: {loc_threshold})",
                0.85,
                {'modified_loc': modified_loc, 'threshold': loc_threshold}
            )

        return TriggerDecision(
            False,
            "HistorianAgent",
            "No snapshot trigger conditions met",
            0.8
        )

    def should_invoke_critic(self, context: Dict[str, Any]) -> TriggerDecision:
        """
        Decide if CriticAgent should review changes.

        Args:
            context: Dictionary with:
                - change_type: Type of change (feature, bugfix, refactor, security, etc.)
                - security_impact: Boolean or score
                - affects_auth: Boolean, touches authentication
                - affects_payments: Boolean, touches payment flow
                - complexity: Complexity level
                - confidence: Confidence in approach

        Returns:
            TriggerDecision with reasoning

        TRIGGER CONDITIONS:
        - Security-impacting changes
        - Authentication or payment changes
        - High complexity
        - Low confidence
        - Risky operations (database schema, API contracts)
        """
        if not self.enabled:
            return TriggerDecision(False, "CriticAgent", "Auto-triggering disabled", 1.0)

        trigger_config = self.config.get('triggers', {}).get('critic', {})
        if not trigger_config.get('enabled', True):
            return TriggerDecision(False, "CriticAgent", "Critic triggers disabled in config", 1.0)

        change_type = context.get('change_type', 'general')
        security_impact = context.get('security_impact', False)
        affects_auth = context.get('affects_auth', False)
        affects_payments = context.get('affects_payments', False)
        complexity = context.get('complexity', 'medium')
        confidence = context.get('confidence', 0.8)

        # Security changes
        if security_impact and trigger_config.get('on_security_impact', True):
            return TriggerDecision(
                True,
                "CriticAgent",
                "Security-impacting changes require adversarial review",
                0.95,
                {'trigger_type': 'security', 'change_type': change_type}
            )

        # Authentication changes
        if affects_auth:
            return TriggerDecision(
                True,
                "CriticAgent",
                "Authentication changes are high-risk - review required",
                0.98,
                {'trigger_type': 'authentication'}
            )

        # Payment changes
        if affects_payments:
            return TriggerDecision(
                True,
                "CriticAgent",
                "Payment flow changes require careful review",
                0.97,
                {'trigger_type': 'payments'}
            )

        # High complexity
        if complexity in ['high', 'very_high'] and trigger_config.get('on_high_complexity', True):
            return TriggerDecision(
                True,
                "CriticAgent",
                f"High complexity ({complexity}) warrants adversarial review",
                0.85,
                {'trigger_type': 'complexity', 'complexity': complexity}
            )

        # Low confidence
        if confidence < 0.7:
            return TriggerDecision(
                True,
                "CriticAgent",
                f"Low confidence ({confidence:.0%}) - review recommended",
                0.8,
                {'trigger_type': 'low_confidence', 'confidence': confidence}
            )

        return TriggerDecision(
            False,
            "CriticAgent",
            "No high-risk factors detected",
            0.75
        )

    def should_invoke_research(self, context: Dict[str, Any]) -> TriggerDecision:
        """
        Decide if ResearchDocumenter should research a topic.

        Args:
            context: Dictionary with:
                - library_name: External library being used
                - api_name: External API being integrated
                - confidence: Confidence in implementation approach
                - major_version_bump: Boolean, major version change
                - unfamiliar_tech: Boolean, new technology

        Returns:
            TriggerDecision with reasoning

        TRIGGER CONDITIONS:
        - External API/library integration
        - Major version bump of dependency
        - Low confidence in approach
        - Unfamiliar technology
        """
        if not self.enabled:
            return TriggerDecision(False, "ResearchDocumenter", "Auto-triggering disabled", 1.0)

        trigger_config = self.config.get('triggers', {}).get('research_documenter', {})
        if not trigger_config.get('enabled', True):
            return TriggerDecision(False, "ResearchDocumenter", "Research triggers disabled in config", 1.0)

        library_name = context.get('library_name')
        api_name = context.get('api_name')
        confidence = context.get('confidence', 0.8)
        major_version_bump = context.get('major_version_bump', False)
        unfamiliar_tech = context.get('unfamiliar_tech', False)

        # External API integration
        if (library_name or api_name) and trigger_config.get('require_for_external_api', True):
            topic = library_name or api_name
            return TriggerDecision(
                True,
                "ResearchDocumenter",
                f"External integration ({topic}) requires documentation research",
                0.9,
                {'trigger_type': 'external_api', 'topic': topic}
            )

        # Major version bump
        if major_version_bump and trigger_config.get('require_for_major_version_bump', True):
            return TriggerDecision(
                True,
                "ResearchDocumenter",
                "Major version bump - research breaking changes and migration",
                0.88,
                {'trigger_type': 'version_bump'}
            )

        # Low confidence threshold
        confidence_threshold = trigger_config.get('confidence_threshold', 0.6)
        if confidence < confidence_threshold:
            return TriggerDecision(
                True,
                "ResearchDocumenter",
                f"Low confidence ({confidence:.0%}) - research recommended (threshold: {confidence_threshold:.0%})",
                0.85,
                {'trigger_type': 'low_confidence', 'confidence': confidence, 'threshold': confidence_threshold}
            )

        # Unfamiliar technology
        if unfamiliar_tech:
            return TriggerDecision(
                True,
                "ResearchDocumenter",
                "Unfamiliar technology - deep research advised",
                0.82,
                {'trigger_type': 'unfamiliar_tech'}
            )

        return TriggerDecision(
            False,
            "ResearchDocumenter",
            "No research trigger conditions met",
            0.7
        )

    def evaluate_all_triggers(self, context: Dict[str, Any]) -> Dict[str, TriggerDecision]:
        """
        Evaluate all trigger rules for given context.

        Args:
            context: Workflow context dictionary

        Returns:
            Dictionary mapping agent_name -> TriggerDecision

        WHY: Convenience method to check all agents at once
        """
        decisions = {
            'ExplorerAgent': self.should_invoke_explorer(context),
            'HistorianAgent': self.should_invoke_historian(context),
            'CriticAgent': self.should_invoke_critic(context),
            'ResearchDocumenter': self.should_invoke_research(context)
        }

        # Log all decisions
        for agent_name, decision in decisions.items():
            if decision.should_trigger:
                logger.info(f"TRIGGER: {agent_name} - {decision.reason}")
                self.trigger_history.append({
                    'agent': agent_name,
                    'triggered': True,
                    'reason': decision.reason,
                    'confidence': decision.confidence,
                    'metadata': decision.metadata
                })
            else:
                logger.debug(f"SKIP: {agent_name} - {decision.reason}")

        return decisions

    def get_triggered_agents(self, context: Dict[str, Any]) -> List[str]:
        """
        Get list of agent names that should be triggered.

        Args:
            context: Workflow context

        Returns:
            List of agent names to invoke

        WHY: Simple interface for orchestrator
        """
        decisions = self.evaluate_all_triggers(context)
        return [
            agent_name
            for agent_name, decision in decisions.items()
            if decision.should_trigger
        ]

    def get_trigger_metrics(self) -> Dict[str, Any]:
        """
        Get metrics on trigger history.

        Returns:
            Dictionary with trigger statistics

        WHY: Helps tune trigger thresholds
        """
        if not self.trigger_history:
            return {'total_triggers': 0}

        total = len(self.trigger_history)
        by_agent = {}

        for trigger in self.trigger_history:
            agent = trigger['agent']
            if agent not in by_agent:
                by_agent[agent] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'reasons': []
                }

            by_agent[agent]['count'] += 1
            by_agent[agent]['reasons'].append(trigger['reason'])

        # Calculate averages
        for agent, stats in by_agent.items():
            agent_triggers = [t for t in self.trigger_history if t['agent'] == agent]
            avg_conf = sum(t['confidence'] for t in agent_triggers) / len(agent_triggers)
            stats['avg_confidence'] = avg_conf

        return {
            'total_triggers': total,
            'by_agent': by_agent
        }

    def reload_config(self):
        """Reload configuration from file."""
        self.config = self._load_config()
        logger.info("Trigger configuration reloaded")

    def disable(self):
        """Disable all auto-triggering."""
        self.enabled = False
        logger.info("Auto-triggering disabled")

    def enable(self):
        """Enable auto-triggering."""
        self.enabled = True
        logger.info("Auto-triggering enabled")

    def __repr__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"<SubAgentTriggerEngine status={status} triggers={len(self.trigger_history)}>"
