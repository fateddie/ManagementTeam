# ==============================================
# file: /ManagementTeam/src/utils/parser_utils.py
# ==============================================
from __future__ import annotations
import re
from datetime import date
from typing import Dict, Any, List

# Extremely lightweight extractor; replace with a proper NLP pipeline later.


def extract_entities(description: str, defaults: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Extract structured entities from a free-text project description.
    
    Args:
        description: Free-text project description
        defaults: Default values to merge into the result
        
    Returns:
        Dictionary of extracted entities
    """
    defaults = defaults or {}
    out: Dict[str, Any] = {**defaults}
    out["summary"] = description.strip()
    out["date_created"] = out.get("date_created") or date.today().isoformat()

    # naive milestone capture: lines like "M1: Name (3 days)"
    ms: List[Dict[str, Any]] = []
    for line in description.splitlines():
        m = re.match(r"^(M\d+)\s*:\s*(.*?)\s*\(([^)]+)\)", line.strip())
        if m:
            ms.append({"id": m.group(1), "name": m.group(2), "duration": m.group(3)})
    if ms:
        out["milestones"] = ms
    return out


def identify_gaps(entities: Dict[str, Any]) -> Dict[str, str]:
    """
    Identify missing or incomplete information in extracted entities.
    
    Args:
        entities: Dictionary of extracted entities
        
    Returns:
        Dictionary mapping field names to gap descriptions
    """
    gaps: Dict[str, str] = {}
    required = ["title", "summary"]
    for k in required:
        if not entities.get(k):
            gaps[k] = "Missing required field"
    # Optional but useful
    if "milestones" not in entities:
        gaps["milestones"] = "No milestones found; add at least 3"
    return gaps

