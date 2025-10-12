# AI Management Team – Claude Code Project

**Version:** 3.0 - With Vertical & Strategic Planning  
**Date:** 2025-10-12  
**Owner:** Rob Freyne  
**Repository:** https://github.com/fateddie/ManagementTeam  
**Status:** 🟢 Production Ready - All 13 Phases Complete

---

## 🎯 Quick Start

### Using CLI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run full 8-agent pipeline
python cli/manage.py run

# Or run new workflow: Idea → Decision → Project
python scripts/run_vertical_agent.py inputs/ideas.json
python scripts/run_strategic_planner.py

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

### **New: Business Vertical System** (Phases 12-13)
1. **VerticalAgent** - Evaluates & scores business ideas (RICE/ICE)
2. **StrategicPlannerAgent** - Decides what to build next (with human approval)

### **Core Planning System** (Phases 1-11)
3. **StrategyAgent** - Strategic planning & goal extraction
4. **TechnicalArchitectAgent** - System architecture & design
5. **PlanningAgent** - Unified planning & roadmapping
6. **ResearchAgent** - AI-powered validation (Perplexity)
7. **DocumentationAgent** - Professional documentation generation
8. **ReportingAgent** - Quality control & validation

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

- ✅ **8 AI Agents** - Complete workflow automation
- ✅ **Idea-to-Project Pipeline** - Evaluate, decide, build in minutes
- ✅ **Human-in-the-Loop** - Approval gates for strategic decisions
- ✅ **RICE/ICE Scoring** - Business vertical evaluation
- ✅ **Interactive Dashboard** - Streamlit visualization
- ✅ **CLI Interface** - User-friendly commands
- ✅ **CI/CD Integration** - GitHub Actions automated
- ✅ **Agent Protocol** - Standardized communication
- ✅ **Conflict Resolution** - Intelligent voting system
- ✅ **Performance Optimization** - Caching & parallel execution
- ✅ **Automated Testing** - 100% test coverage
- ✅ **Quality Control** - Automated validation

## 📚 Key Documentation

- **QUICK_START.md** - ⭐ Start here! Complete workflow guide
- **PROJECT_INDEX.md** - Navigation hub for all documentation
- **FINAL_SYSTEM_STATUS.md** - Complete system overview
- **DOCUMENTATION_STATUS.md** - Documentation audit
- **outputs/PHASE_*_SUMMARY.md** - All 13 phase summaries
- **docs/system/PRD.md** - Product requirements
- **docs/system/CI_CD_SETUP.md** - GitHub Actions setup

### **New Agent Documentation:**
- **agents/vertical_agent/README.md** - Business idea evaluator
- **agents/strategic_planner/README.md** - Strategic decision maker
- **dashboards/VERTICAL_DASHBOARD_README.md** - Interactive dashboard

---

**Maintained by:** AI Management Team  
**Last Updated:** 2025-10-12  
**All 13 Phases:** ✅ Complete (11 core + 2 enhancements)
