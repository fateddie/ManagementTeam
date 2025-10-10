# ==============================================
# file: /ManagementTeam/src/utils/template_utils.py
# ==============================================
from __future__ import annotations
import re
from typing import Dict, Any

# Simple {{ var }} replacement so we don't require Jinja at bootstrap.
_VAR = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def fill_template(template_text: str, data: Dict[str, Any]) -> str:
    """
    Fill a template with data using simple {{ variable }} syntax.
    
    Args:
        template_text: Template string with {{ variable }} placeholders
        data: Dictionary of values to substitute
        
    Returns:
        Filled template string
    """
    def _rep(m: re.Match[str]) -> str:
        key = m.group(1)
        val = data.get(key, "")
        # Render simple tables for milestones if found
        if key == "milestones" and isinstance(val, list):
            # For markdown templates that expect a table, create rows
            rows = []
            for ms in val:
                rows.append(
                    f"| {ms.get('id','')} | {ms.get('name','')} | {ms.get('description','')} | {ms.get('duration','')} | {ms.get('deps','—')} | {ms.get('status','Pending')} |"
                )
            return "\n".join(rows)
        return str(val)
    return _VAR.sub(_rep, template_text)

