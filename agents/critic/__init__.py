"""
Critic Agent - Adversarial review sub-agent.

WHY: Before executing risky changes, have a second set of eyes review
the plan adversarially to identify risks, edge cases, and failure modes.
"""

from agents.critic.critic import CriticAgent

__all__ = ["CriticAgent"]
