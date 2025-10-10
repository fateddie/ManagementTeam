"""
MEMORY MANAGER v1.0
Author: Strategy Agent / Founder (Rob)

Purpose:
    Provides lightweight persistent memory for AI management agents.
    Each agent stores its state, past decisions, and preferences in JSON format.
    Designed for local use and Claude Code context integration.

Directory Structure:
    /memory/
        strategy_agent.json
        financial_agent.json
        technical_architect.json
        operations_agent.json
        data_agent.json
"""

import os, json, datetime
from typing import Dict, Any

BASE_DIR = "memory"

def _ensure_dir():
    """Create memory directory if it doesn't exist."""
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

def _get_file(agent_name: str) -> str:
    """Return the file path for a given agent."""
    return os.path.join(BASE_DIR, f"{agent_name}.json")

def load_memory(agent_name: str) -> Dict[str, Any]:
    """Load agent memory if available, else return empty template."""
    _ensure_dir()
    file_path = _get_file(agent_name)
    if not os.path.exists(file_path):
        return {
            "agent": agent_name,
            "last_updated": None,
            "project_history": [],
            "preferences": {},
            "notes": []
        }
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_memory(agent_name: str, new_data: Dict[str, Any]):
    """Merge new data and write back to memory file."""
    memory = load_memory(agent_name)
    memory.update(new_data)
    memory["last_updated"] = datetime.datetime.now().isoformat()
    with open(_get_file(agent_name), "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def add_project_record(agent_name: str, project_name: str, decision: str, notes: str = ""):
    """Append a project decision record for an agent."""
    memory = load_memory(agent_name)
    memory.setdefault("project_history", []).append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "project": project_name,
        "decision": decision,
        "notes": notes
    })
    update_memory(agent_name, memory)

def get_recent_projects(agent_name: str, limit: int = 5):
    """Return the most recent project records."""
    memory = load_memory(agent_name)
    history = memory.get("project_history", [])
    return history[-limit:]

def print_memory_summary(agent_name: str):
    """Simple console summary for debugging or Founder review."""
    memory = load_memory(agent_name)
    print(f"\n🧠 MEMORY SUMMARY – {agent_name}")
    print(f"Last Updated: {memory.get('last_updated')}")
    print("Recent Projects:")
    for record in get_recent_projects(agent_name):
        print(f"  - {record['project']} ({record['decision']}) – {record.get('notes', '')}")
    print("\n")

if __name__ == "__main__":
    # Example usage
    agent = "strategy_agent"
    add_project_record(agent, "AI_Receptionist", "approved", "Strong ROI, market fit confirmed")
    print_memory_summary(agent)
