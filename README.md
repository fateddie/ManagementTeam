# AI Management Team – Claude Code Project

**Version:** 2.0 - With Agent Protocol & Conflict Resolution  
**Date:** 2025-10-11  
**Owner:** Rob Freyne  
**Repository:** https://github.com/fateddie/ManagementTeam  
**Status:** 🟢 Production Ready - All 9 Phases Complete

---

## 🎯 Quick Start

### Using CLI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run full 6-agent pipeline
python cli/manage.py run

# Run validation tests
python cli/manage.py validate

# Check system status
python cli/manage.py status

# List all commands
python cli/manage.py list
```

### Traditional Method

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Run orchestrator directly
python agents/orchestrator/orchestrator.py
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

1. **StrategyAgent** - Strategic planning & goal extraction
2. **TechnicalArchitectAgent** - System architecture & design
3. **PlanningAgent** - Unified planning & roadmapping
4. **ResearchAgent** - AI-powered validation (Perplexity)
5. **DocumentationAgent** - Professional documentation generation
6. **ReportingAgent** - Quality control & validation

### 🔗 Agent Protocol (Phase 9)

All agents now use standardized `AgentOutput` protocol:
- **Structured communication** between agents
- **Weighted voting** for conflict resolution
- **Human escalation** for complex decisions
- **Audit trail** for all decisions
- **Configurable policies** via YAML

---

## 🚀 Next Steps

1. **Quick Start:** `python cli/manage.py run`
2. **Configure API Keys:** Add to `config/.env` (see `config/.env.example`)
3. **Run Tests:** `python cli/manage.py validate`
4. **Check Status:** `python cli/manage.py status`
5. **View Decisions:** Check `outputs/decisions/` for agent decisions

## 📊 System Features

- ✅ **6 AI Agents** - Complete workflow automation
- ✅ **CLI Interface** - User-friendly commands
- ✅ **CI/CD Integration** - GitHub Actions automated
- ✅ **Agent Protocol** - Standardized communication
- ✅ **Conflict Resolution** - Intelligent voting system
- ✅ **Automated Testing** - 100% test coverage
- ✅ **Quality Control** - Automated validation

## 📚 Key Documentation

- **SYSTEM_100_PERCENT_COMPLETE.md** - Complete system overview
- **QUICK_START.md** - Fast setup guide
- **docs/system/CI_CD_SETUP.md** - GitHub Actions setup
- **docs/system/PRD.md** - Product requirements
- **outputs/PHASE_*_SUMMARY.md** - Phase completion summaries

---

**Maintained by:** AI Management Team  
**Last Updated:** 2025-10-11  
**All 9 Phases:** ✅ Complete
