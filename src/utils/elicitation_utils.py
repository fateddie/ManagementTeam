# ==============================================
# file: /ManagementTeam/src/utils/elicitation_utils.py
# ==============================================
from __future__ import annotations
from typing import Dict


def questions_markdown(gaps: Dict[str, str]) -> str:
    """
    Generate a markdown document with questions about missing information.
    
    Args:
        gaps: Dictionary mapping field names to gap descriptions
        
    Returns:
        Markdown-formatted string with questions
    """
    if not gaps:
        return "# ❓ Missing Information\n\nNo gaps detected. You can proceed.\n"
    lines = ["# ❓ Missing Information", "", "The Planner Agent identified missing or unclear information:", ""]
    for key, reason in gaps.items():
        lines.append(f"- [ ] **{key}** — {reason}")
    lines.append("")
    lines.append("Once complete, rerun the Planner Agent to regenerate the plan.")
    return "\n".join(lines)

