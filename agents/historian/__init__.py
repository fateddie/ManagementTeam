"""
Historian Agent - Project snapshot utility sub-agent.

WHY: Lightweight, LLM-readable project memory. Better than Git diffs for
understanding what changed and why across sessions.
"""

from agents.historian.historian import HistorianAgent

__all__ = ["HistorianAgent"]
