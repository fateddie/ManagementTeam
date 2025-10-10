# 📁 PROJECT FILE STRUCTURE – AI MANAGEMENT TEAM SYSTEM

**Version:** 1.1  
**Maintainer:** Founder (Rob)  
**Date:** 2025-10-10  
**Status:** Updated for AI Management Layer architecture

---

## 🎯 PURPOSE

This document defines and maintains the standardized **directory and file structure** for the AI Management-Team project (Claude Code environment).  
It ensures consistent organization, discoverability, and scalability across all future enhancements (agents, dashboards, integrations, etc.).

---

## 🧩 TOP-LEVEL OVERVIEW

```
ManagementTeam/
├── .venv/                          # Python virtual environment (gitignored)
├── .gitignore                      # Git ignore rules
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── setup_environment.sh            # Environment setup (macOS/Linux)
├── setup_environment.bat           # Environment setup (Windows)
│
├── config/                         # Configuration files
│   ├── .env                        # Environment variables (gitignored)
│   ├── global.yaml                 # System-wide configuration
│   ├── mem0.yaml                   # Mem0 memory configuration
│   ├── neo4j.yaml                  # Neo4j configuration (Phase 2)
│   ├── logging.yaml                # Logging configuration
│   └── templates/                  # Project templates
│       ├── project_plan.yaml
│       ├── roadmap.md
│       ├── milestones.json
│       ├── missing_info.md
│       ├── folder_structure.json
│       └── project_readme.md
│
├── claude/                         # Claude AI configuration
│   ├── config.yaml                 # Claude behavior settings
│   ├── environment.sh              # Environment setup script
│   └── cursor_rules.md             # Cursor AI rules
│
├── src/                            # Core application logic
│   ├── agents/                     # Agent implementation files
│   └── utils/                      # Utility modules
│       └── memory_manager.py       # Persistent memory system
│
├── scripts/                        # Executable scripts
│   ├── init_management_team.py     # Project initialization
│   └── orchestrator.py             # Agent workflow coordinator
│
├── docs/                           # Documentation
│   └── system/                     # System governance & architecture
│       ├── README_management_team.md
│       ├── management_team_charter_v1.0.md
│       ├── management_team_rules.yaml
│       ├── management_team_agent_definitions.yaml
│       ├── system_context.yaml
│       ├── change_log.md
│       ├── project_progress_plan.md
│       ├── orchestrator_README.md
│       ├── orchestrator_extensions.md
│       ├── TDR_index.md
│       ├── file_structure.md       # This file
│       └── archive/                # Superseded versions
│
├── memory/                         # Persistent agent memory (JSON)
│   ├── strategy_agent.json
│   ├── financial_agent.json
│   ├── technical_architect.json
│   ├── operations_agent.json
│   └── data_agent.json
│
├── logs/                           # Activity logs (JSONL format)
│   └── YYYY-MM-DD_ProjectName.jsonl
│
├── data/                           # Project data and reports
│   ├── project_proposals/          # New project specs
│   ├── market_data/                # Market research
│   ├── reports/                    # Generated reports
│   │   ├── strategy_report_*.md
│   │   ├── financial_review_*.md
│   │   ├── architecture_review_*.md
│   │   ├── operations_plan_*.md
│   │   └── performance_report_*.md
│   ├── raw/                        # Raw data files
│   ├── processed/                  # Processed data
│   └── exports/                    # Exported data
│
├── projects/                       # Scaffolded projects by Planner Agent
│   └── <project_name>/             # Individual project folders
│       ├── planning/
│       ├── docs/
│       ├── control/
│       ├── environment/
│       ├── memory/
│       ├── src/
│       ├── tests/
│       ├── data/
│       ├── logs/
│       └── README.md
│
├── dashboards/                     # Dashboard & API (future)
│   ├── api/                        # FastAPI backend
│   ├── ui/                         # React frontend
│   └── static/                     # Static assets
│
└── tests/                          # Test files
    ├── test_memory_manager.py
    ├── test_orchestrator.py
    └── test_agents/
```

---

## 🧠 DIRECTORY DETAILS

### 📂 `src/` – Core Application Logic

**Purpose:** Contains all core Python modules and agent implementations.

```
src/
├── agents/                         # Individual agent implementations
│   ├── __init__.py
│   ├── strategy_agent.py           # Market positioning & prioritization
│   ├── financial_agent.py          # ROI validation & budgeting
│   ├── technical_architect.py      # Architecture & compliance
│   ├── operations_agent.py         # Execution planning
│   └── data_agent.py               # Performance metrics & learning
│
└── utils/                          # Shared utilities
    ├── __init__.py
    ├── memory_manager.py           # JSON-based persistent memory
    ├── yaml_loader.py              # YAML config parsing (future)
    ├── slack_notifier.py           # Slack integration (future)
    └── vector_memory.py            # ChromaDB integration (future)
```

**Key Files:**

- `memory_manager.py` ✅ - Handles agent state persistence
- Agent files 🕓 - Individual agent logic (to be implemented)

---

### 📂 `scripts/` – Executable Scripts

**Purpose:** Standalone scripts for initialization, orchestration, and automation.

```
scripts/
├── init_management_team.py         # Initialize new project governance
├── orchestrator.py                 # Main workflow coordinator
├── maintenance_tasks.py            # Weekly cleanup & validation
├── run_daily_summary.py            # Daily performance summary (future)
└── backup_memory.py                # Memory backup utility (future)
```

**Key Files:**

- `init_management_team.py` ✅ - Creates governance files
- `orchestrator.py` ✅ - Coordinates agent workflow

**Usage:**

```bash
python scripts/init_management_team.py "ProjectName"
python scripts/orchestrator.py
```

---

### 📂 `docs/system/` – System Governance & Architecture

**Purpose:** Central repository for all governance, decision-making rules, and architectural documentation.

```
docs/system/
├── README_management_team.md               # System usage guide
├── management_team_charter_v1.0.md         # Mission, values, principles
├── management_team_rules.yaml              # Decision criteria & weights
├── management_team_agent_definitions.yaml  # Agent behaviors & specs
├── system_context.yaml                     # Workflow orchestration
├── system_architecture.md                  # System architecture overview
├── change_log.md                           # Update history
├── project_progress_plan.md                # Development roadmap
├── orchestrator_README.md                  # Orchestrator documentation
├── orchestrator_extensions.md              # Extension guide
├── TDR_index.md                            # Technology decision records
├── file_structure.md                       # This file
├── claude.md                               # Claude working guidelines
├── PRD.md                                  # Complete Product Requirements Document ✨NEW
├── PRD_summary.md                          # Product requirements summary
├── PROJECT_SUMMARY.md                      # Comprehensive project overview
├── planner_agent_spec.md                   # Planner Agent specification ✨NEW
├── planner_agent_templates.md              # Planner Agent templates ✨NEW
├── setup_completion_summary.md             # Setup completion summary ✨NEW
│
├── archive/                                # Historical versions
│   ├── management_team_charter_v0.9.md
│   └── superseded_decisions/
│
└── templates/                              # Reusable templates
    ├── TDR_template.md
    ├── agent_template.py
    └── report_template.md
```

**Key Files:**

- `management_team_charter_v1.0.md` ✅ - Core governance
- `management_team_rules.yaml` ✅ - Decision framework
- `system_context.yaml` ✅ - Workflow configuration
- `TDR_index.md` ✅ - Technology decisions

---

### 📂 `memory/` – Persistent Agent Memory

**Purpose:** JSON-based storage for each agent's state, history, and preferences.

```
memory/
├── strategy_agent.json
├── financial_agent.json
├── technical_architect.json
├── operations_agent.json
├── data_agent.json
└── shared_context.json              # Cross-agent shared state (future)
```

**JSON Structure:**

```json
{
  "agent": "strategy_agent",
  "last_updated": "2025-10-08T14:30:00",
  "project_history": [
    {
      "date": "2025-10-08",
      "project": "AI_Receptionist",
      "decision": "approved",
      "notes": "Strong ROI, market fit confirmed"
    }
  ],
  "preferences": {},
  "notes": [],
  "last_decision_score": 4.3
}
```

**Managed By:** `src/utils/memory_manager.py`

---

### 📂 `logs/` – Activity Logs

**Purpose:** Structured logs of all orchestrator runs and agent activities.

```
logs/
├── 2025-10-08_AI_Receptionist.jsonl
├── 2025-10-09_CRM_Integration.jsonl
└── archive/
    └── 2025-09/
```

**Log Format (JSONL):**

```jsonl
{"event": "memory_loaded", "agent": "strategy_agent", "memory": {...}}
{"event": "agent_result", "agent": "strategy_agent", "result": {...}}
{"event": "memory_updated", "agent": "strategy_agent"}
{"event": "orchestration_complete", "project": "AI_Receptionist"}
```

**Managed By:** `scripts/orchestrator.py`

---

### 📂 `data/` – Project Data & Reports

**Purpose:** Input specifications and generated reports.

```
data/
├── project_proposals/              # New project specifications
│   ├── ai_receptionist.yaml
│   ├── crm_integration.yaml
│   └── template.yaml
│
├── market_data/                    # Market research & trends
│   ├── smb_automation_trends.csv
│   └── competitor_analysis.md
│
├── reports/                        # Agent-generated reports
│   ├── strategy/
│   │   └── strategy_report_2025-10-08.md
│   ├── financial/
│   │   └── financial_review_2025-10-08.md
│   ├── technical/
│   │   └── architecture_review_2025-10-08.md
│   ├── operations/
│   │   └── operations_plan_2025-10-08.md
│   └── data/
│       └── performance_report_2025-10-08.md
│
├── raw/                            # Raw data files ✨NEW
├── processed/                      # Processed/transformed data ✨NEW
└── exports/                        # Exported data ✨NEW
```

---

### 📂 `dashboards/` – Dashboard & API (Future)

**Purpose:** Web-based interface for monitoring and interaction.

```
dashboards/
├── api/                            # FastAPI backend
│   ├── main.py                     # API entry point
│   ├── routes/
│   │   ├── agents.py
│   │   ├── projects.py
│   │   └── logs.py
│   └── models/
│       └── schemas.py
│
├── ui/                             # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.tsx
│   ├── package.json
│   └── public/
│
└── static/                         # Static assets
    ├── css/
    ├── js/
    └── images/
```

**Status:** 🕓 Planned for v1.2

---

### 📂 `config/` – Configuration Files

**Purpose:** System-wide configuration files and project templates.

```
config/
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Template for .env
├── global.yaml                     # System-wide settings ✨NEW
├── mem0.yaml                       # Mem0 memory configuration ✨NEW
├── neo4j.yaml                      # Neo4j settings (Phase 2) ✨NEW
├── logging.yaml                    # Logging configuration ✨NEW
└── templates/                      # Project scaffolding templates ✨NEW
    ├── project_plan.yaml           # Project plan template
    ├── roadmap.md                  # Roadmap template
    ├── milestones.json             # Milestones template
    ├── missing_info.md             # Missing info prompt template
    ├── folder_structure.json       # Folder structure definition
    └── project_readme.md           # Project README template
```

**Key Configuration Files:**

- `global.yaml` - Paths, logging levels, agent settings, security, performance
- `mem0.yaml` - Memory system configuration, policies, retention
- `neo4j.yaml` - Graph database settings for Phase 2 migration
- `logging.yaml` - Structured logging with formatters and handlers

**Environment Variables:**

```bash
# config/.env
SLACK_WEBHOOK_URL=""
CLAUDE_API_KEY=""
MEM0_API_KEY=""
NEO4J_URI=""
NEO4J_USERNAME=""
NEO4J_PASSWORD=""
PROJECT_NAME="AI_Management_Team"
ENVIRONMENT="development"
```

---

### 📂 `claude/` – Claude AI Configuration

**Purpose:** Define Claude's behavior, context awareness, and development guidelines.

```
claude/
├── config.yaml                     # Claude configuration settings
├── environment.sh                  # Environment setup script ✨NEW
└── cursor_rules.md                 # Cursor AI rules & standards ✨NEW
```

**Configuration Structure:**

```yaml
version: 1.0
project_name: "AI Management-Team"
context_dirs: # Directories for context
  - docs/system
  - src
always_load: # Files to read before updates
  - management_team_charter_v1.0.md
  - management_team_rules.yaml
coding_style: # Code standards
  python_version: "3.11"
  max_line_length: 88
```

**New Files:**

- `environment.sh` - Automated environment setup with virtual env
- `cursor_rules.md` - Coding standards, principles, and agent development rules

**Related Files:**

- `docs/system/claude.md` - Detailed working guidelines
- `logs/claude_activity.log` - Claude action log (future)

---

### 📂 `projects/` – Scaffolded Projects ✨NEW

**Purpose:** Contains individual projects created by the Planner Agent.

```
projects/
└── <project_name>/                 # Auto-generated project folder
    ├── planning/                   # Project planning artifacts
    │   ├── project_plan.yaml
    │   ├── roadmap.md
    │   ├── milestones.json
    │   └── missing_info.md
    ├── docs/                       # Project documentation
    │   ├── README.md
    │   ├── PRD.md
    │   ├── tech_spec.md
    │   └── diagrams/
    ├── control/                    # Claude/Cursor control files
    │   ├── Claude.md
    │   ├── Rules.md
    │   └── ProgressLog.md
    ├── environment/                # Project environment
    │   ├── environment.sh
    │   ├── requirements.txt
    │   └── .env.example
    ├── memory/                     # Project-specific memory
    │   ├── context.json
    │   └── decisions.json
    ├── src/                        # Source code
    ├── tests/                      # Tests
    ├── data/                       # Project data
    │   ├── raw/
    │   ├── processed/
    │   └── exports/
    ├── logs/                       # Project logs
    └── README.md                   # Project overview
```

**Management:**

- Created by: `src/agents/planner_agent.py`
- Template source: `/config/templates/`
- Tracked in: Mem0 memory system

---

### 📂 `tests/` – Test Suite

**Purpose:** Unit and integration tests.

```
tests/
├── __init__.py
├── test_memory_manager.py
├── test_orchestrator.py
├── test_agents/
│   ├── test_strategy_agent.py
│   ├── test_financial_agent.py
│   └── test_data_agent.py
└── fixtures/
    ├── sample_memory.json
    └── sample_project.yaml
```

**Status:** 🔜 To be implemented

---

## 🔒 GITIGNORE RULES

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.env
.venv/
.envrc

# OS
.DS_Store
Thumbs.db

# Project-specific
memory/*.json
logs/
*.jsonl

# IDE
.vscode/
.idea/
*.swp

# Data
data/market_data/*.csv
data/reports/*.pdf
```

---

## 📋 FILE NAMING CONVENTIONS

### General Rules

- **Lowercase with underscores:** `memory_manager.py`, `strategy_agent.py`
- **Dates in ISO format:** `YYYY-MM-DD` (e.g., `2025-10-08_AI_Receptionist.jsonl`)
- **Version numbers:** `v1.0`, `v1.1`, `v2.0`

### Specific Patterns

| Type        | Pattern                   | Example                            |
| ----------- | ------------------------- | ---------------------------------- |
| Agent files | `{agent_name}.py`         | `strategy_agent.py`                |
| Reports     | `{type}_report_{date}.md` | `strategy_report_2025-10-08.md`    |
| Logs        | `{date}_{project}.jsonl`  | `2025-10-08_AI_Receptionist.jsonl` |
| Memory      | `{agent_name}.json`       | `strategy_agent.json`              |
| Config      | `{purpose}_config.yaml`   | `slack_config.yaml`                |
| TDRs        | `TDR_{id}_{topic}.md`     | `TDR_001_json_memory.md`           |

---

## 🔄 MAINTENANCE & UPDATES

### When to Update This Document

- Adding new directories or major file categories
- Changing file naming conventions
- Restructuring project organization
- Adding new subsystems (e.g., dashboards, integrations)

### Update Process

1. Modify `file_structure.md`
2. Update version number and date
3. Log change in `change_log.md`
4. Communicate to team via Slack (when implemented)

---

## 📚 RELATED DOCUMENTATION

- `README_management_team.md` - System usage guide
- `project_progress_plan.md` - Development roadmap
- `orchestrator_README.md` - Orchestrator details
- `TDR_index.md` - Technology decisions

---

## 🎓 QUICK REFERENCE

### Where to Find...

| What              | Location                                              |
| ----------------- | ----------------------------------------------------- |
| Agent memory      | `/memory/{agent_name}.json`                           |
| Execution logs    | `/logs/{date}_{project}.jsonl`                        |
| Governance rules  | `/docs/system/management_team_rules.yaml`             |
| Agent definitions | `/docs/system/management_team_agent_definitions.yaml` |
| Generated reports | `/data/reports/`                                      |
| Project proposals | `/data/project_proposals/`                            |
| Setup script      | `./setup_environment.sh`                              |
| Orchestrator      | `./scripts/orchestrator.py`                           |

### Common Commands

**macOS/Linux:**

```bash
# Initialize environment
./setup_environment.sh

# Initialize project
python scripts/init_management_team.py "ProjectName"

# Run orchestrator
source .venv/bin/activate
python scripts/orchestrator.py

# Check agent memory
cat memory/strategy_agent.json | python -m json.tool

# View recent logs
tail -f logs/$(ls -t logs/ | head -1)
```

**Windows:**

```batch
REM Initialize environment
setup_environment.bat

REM Initialize project
python scripts\init_management_team.py "ProjectName"

REM Run orchestrator
.venv\Scripts\activate
python scripts\orchestrator.py

REM Check agent memory
type memory\strategy_agent.json | python -m json.tool

REM View recent logs
type logs\*.jsonl
```

---

## 📝 Document Change Log

### Version 1.1 (2025-10-10)

- ✨ Added comprehensive configuration system (`config/global.yaml`, `mem0.yaml`, `neo4j.yaml`, `logging.yaml`)
- ✨ Added project templates system (`config/templates/`)
- ✨ Added Claude environment setup and Cursor rules
- ✨ Added `projects/` directory for scaffolded projects
- ✨ Added new documentation (PRD.md, planner_agent_spec.md, planner_agent_templates.md, setup_completion_summary.md)
- ✨ Added data subdirectories (raw/, processed/, exports/)
- Updated architecture to support AI Management Layer system

### Version 1.0 (2025-10-08)

- Initial structure for AI Management Team system
- Core agent framework
- Basic documentation and governance

---

**Version:** 1.1  
**Last Updated:** 2025-10-10  
**Next Review:** 2026-01-10  
**Maintainer:** Founder (Rob)
