"""
config.py
Dashboard configuration settings
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directories
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RESULTS_DIR = PROJECT_ROOT / "results"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
AGENTS_DIR = PROJECT_ROOT / "agents"
DASHBOARD_RUNS_DIR = PROJECT_ROOT / "dashboard" / "runs"

# Ensure directories exist
OUTPUTS_DIR.mkdir(exist_ok=True, parents=True)
RESULTS_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
LOGS_DIR.mkdir(exist_ok=True, parents=True)
DASHBOARD_RUNS_DIR.mkdir(exist_ok=True, parents=True)

# API Settings
API_HOST = "127.0.0.1"
API_PORT = 8000

# Polling interval (seconds)
POLL_INTERVAL = 2

# Agent list (from Phase 1.1)
AGENTS = [
    {
        "name": "StrategyAgent",
        "path": "agents/strategy_agent/strategy_agent.py",
        "dependencies": [],
        "description": "Converts PRD into structured strategy YAML"
    },
    {
        "name": "TechnicalArchitectAgent",
        "path": "agents/technical_architect/architect_agent.py",
        "dependencies": ["StrategyAgent"],
        "description": "Converts strategy into technical design"
    },
    {
        "name": "PlanningAgent",
        "path": "src/agents/planning_agent_v2.py",
        "dependencies": ["StrategyAgent", "TechnicalArchitectAgent"],
        "description": "Generates unified project plan and roadmap"
    },
    {
        "name": "DocumentationAgent",
        "path": "agents/documentation_agent/documentation_agent.py",
        "dependencies": ["PlanningAgent"],
        "description": "Compiles PRD and technical specs"
    },
    {
        "name": "ReportingAgent",
        "path": "agents/reporting_agent/reporting_agent.py",
        "dependencies": ["DocumentationAgent"],
        "description": "Generates validation reports and archives"
    },
    {
        "name": "VerticalAgent",
        "path": "agents/vertical_agent/vertical_agent.py",
        "dependencies": [],
        "description": "Evaluates business verticals using RICE scoring"
    },
    {
        "name": "RefinementAgent",
        "path": "agents/refinement_agent/refinement_agent.py",
        "dependencies": [],
        "description": "Refines vague ideas into clear concepts"
    },
    {
        "name": "OpportunityRankingAgent",
        "path": "agents/opportunity_ranking/opportunity_ranking_agent.py",
        "dependencies": ["VerticalAgent"],
        "description": "Advanced weighted scoring for opportunities"
    },
    {
        "name": "Orchestrator",
        "path": "agents/orchestrator/orchestrator.py",
        "dependencies": [],
        "description": "Runs full agent pipeline"
    }
]

# File extensions to monitor
MONITORED_EXTENSIONS = [".yaml", ".yml", ".json", ".md", ".txt", ".csv"]

# Log level
LOG_LEVEL = "INFO"
