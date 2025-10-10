"""
ORCHESTRATOR v1.0
Author: Founder (Rob)

Purpose:
    Coordinate agent workflow for the AI Management Team.
    • Loads & updates persistent memory automatically
    • Executes agents sequentially according to system_context.yaml
    • Logs reasoning and results for Founder oversight
    • Designed for expansion (Slack, dashboard, vector memory)

Dependencies:
    memory_manager.py
    management_team_rules.yaml
    agent_definitions.yaml
    system_context.yaml
"""

import os
import sys
import json
import datetime

# Add parent directory to path to import from src/utils
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.memory_manager import (
    load_memory,
    update_memory,
    add_project_record,
    print_memory_summary
)

# ------------------------------------------------------------------ #
# CONFIG
# ------------------------------------------------------------------ #
BASE_LOG_DIR = "logs"
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# later phases can parse these YAMLs dynamically
AGENT_ORDER = [
    "strategy_agent",
    "financial_agent",
    "technical_architect",
    "operations_agent",
    "data_agent"
]

# ------------------------------------------------------------------ #
# CORE ORCHESTRATOR CLASS
# ------------------------------------------------------------------ #
class Orchestrator:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.session_log = os.path.join(
            BASE_LOG_DIR, f"{datetime.date.today()}_{project_name}.jsonl"
        )

    # ---------------------------------------------- #
    # UTILITIES
    # ---------------------------------------------- #
    def _log(self, entry: dict):
        """Append a structured event to today's log file."""
        with open(self.session_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _simulate_agent_run(self, agent_name: str, context: dict) -> dict:
        """
        Simulate Claude agent output.
        Replace this placeholder with actual Claude Code invocation.
        """
        reasoning = f"{agent_name} evaluated {self.project_name} with context: {context}"
        result = {
            "decision": "approved" if "strategy" in agent_name else "reviewed",
            "score": round(3.5 + 0.5 * (hash(agent_name) % 3), 2),
            "reasoning": reasoning
        }
        return result

    # ---------------------------------------------- #
    # MAIN EXECUTION FLOW
    # ---------------------------------------------- #
    def run(self):
        print(f"\n🚀 Starting orchestration for project: {self.project_name}\n")

        for agent in AGENT_ORDER:
            # 1️⃣ Load agent memory
            memory = load_memory(agent)
            self._log({"event": "memory_loaded", "agent": agent, "memory": memory})
            print(f"→ Loaded memory for {agent}")

            # 2️⃣ Run agent logic (placeholder)
            result = self._simulate_agent_run(agent, memory)
            self._log({"event": "agent_result", "agent": agent, "result": result})
            print(f"✅ {agent} completed with decision: {result['decision']} (score {result['score']})")

            # 3️⃣ Update agent memory
            add_project_record(
                agent,
                self.project_name,
                result["decision"],
                notes=result["reasoning"]
            )
            update_memory(agent, {"last_decision_score": result["score"]})
            self._log({"event": "memory_updated", "agent": agent})
            print(f"💾 Memory updated for {agent}")

        print("\n🎯 All agents completed. Memory persisted.\n")
        self._log({"event": "orchestration_complete", "project": self.project_name})
        print("🧠 Final Memory Summary:")
        for agent in AGENT_ORDER:
            print_memory_summary(agent)


# ------------------------------------------------------------------ #
# RUN DEMO
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    orchestrator = Orchestrator("AI_Receptionist")
    orchestrator.run()

