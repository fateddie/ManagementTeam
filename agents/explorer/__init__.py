"""
Explorer Agent - File/code mapping utility sub-agent.

WHY: Helps locate relevant code/files quickly to minimize context load.
Runs silently in background when task involves >2 files or >150 LOC.
"""

from agents.explorer.explorer import ExplorerAgent

__all__ = ["ExplorerAgent"]
