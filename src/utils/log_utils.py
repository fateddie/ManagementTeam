# ==============================================
# file: /ManagementTeam/src/utils/log_utils.py
# ==============================================
from __future__ import annotations
import logging
import sys
from pathlib import Path

LOG_PATH = Path("/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/logs/planner_trace.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("PlannerAgent")
