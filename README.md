# AI Management Team – Claude Code Project

**Version:** 1.0  
**Date:** 2025-10-08  
**Owner:** Founder (Rob)

---

## 🎯 Quick Start

### macOS/Linux

```bash
# Initialize environment
./setup_environment.sh

# Activate virtual environment
source .venv/bin/activate

# Run orchestrator
python scripts/orchestrator.py
```

### Windows

```batch
REM Initialize environment
setup_environment.bat

REM Activate virtual environment
.venv\Scripts\activate

REM Run orchestrator
python scripts\orchestrator.py
```

---

## 📚 Documentation

See `/docs/system/` for complete governance, orchestration, and decision documentation:

- **README_management_team.md** - System usage guide
- **management_team_charter_v1.0.md** - Mission, values, governance
- **management_team_rules.yaml** - Decision criteria & weights
- **file_structure.md** - Complete file organization
- **orchestrator_README.md** - Orchestrator documentation
- **project_progress_plan.md** - Development roadmap

---

## 🏗️ Project Structure

```
ManagementTeam/
├── docs/system/          # Governance & architecture
├── src/                  # Core application logic
├── scripts/              # Orchestrator & utilities
├── memory/               # Agent persistent memory
├── logs/                 # Execution logs
├── data/                 # Projects & reports
└── config/               # Environment variables
```

---

## 🤖 AI Management Team Agents

1. **Strategy Agent** - Market positioning & prioritization
2. **Financial Agent** - ROI validation & budgeting
3. **Technical Architect** - Architecture & compliance
4. **Operations Agent** - Execution planning
5. **Data Agent** - Performance metrics & learning

---

## 🚀 Next Steps

1. Review `/docs/system/README_management_team.md`
2. Initialize a project: `python scripts/init_management_team.py "ProjectName"`
3. Configure `/config/.env` with your API keys
4. Run the orchestrator: `python scripts/orchestrator.py`

---

**Maintained by:** Strategy Agent (under Founder review)  
**Last Updated:** 2025-10-08
