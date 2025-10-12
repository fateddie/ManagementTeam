# AI Management Team – Claude Code Project

**Version:** 4.0 - With AI Refinement & Advanced Scoring  
**Date:** 2025-10-12  
**Owner:** Rob Freyne  
**Repository:** https://github.com/fateddie/ManagementTeam  
**Status:** 🟢 Production Ready - All 15 Phases Complete

---

## 🎯 Quick Start

### Using CLI (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Run full 10-agent pipeline
python cli/manage.py run

# Or run new workflow: Vague Idea → Refined → Scored → Project
python scripts/run_refine_and_score.py "AI Call Catcher"
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

### **New: Idea-to-Project System** (Phases 12-15)
1. **RefinementAgent** - Turns vague ideas into clear concepts (AI-powered)
2. **VerticalAgent** - Evaluates & scores ideas (RICE/ICE)
3. **OpportunityRankingAgent** - Advanced 7-criteria weighted scoring
4. **StrategicPlannerAgent** - Decides what to build (with human approval)

### **Core Planning System** (Phases 1-11)
3. **StrategyAgent** - Strategic planning & goal extraction
4. **TechnicalArchitectAgent** - System architecture & design
5. **StrategyAgent** - Strategic planning & goal extraction
6. **TechnicalArchitectAgent** - System architecture & design
7. **PlanningAgent** - Unified planning & roadmapping
8. **ResearchAgent** - AI-powered validation (Perplexity)
9. **DocumentationAgent** - Professional documentation generation
10. **ReportingAgent** - Quality control & validation

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

- ✅ **10 AI Agents** - Complete workflow automation
- ✅ **Vague-Idea-to-Project Pipeline** - Refine, evaluate, decide, build in minutes
- ✅ **AI-Powered Refinement** - Turn vague ideas into clear concepts
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
- **COMPLETE_SYSTEM_FLOW.md** - Full pipeline explanation
- **PROJECT_INDEX.md** - Navigation hub for all documentation
- **FINAL_SYSTEM_STATUS.md** - Complete system overview
- **outputs/PHASE_*_SUMMARY.md** - All 15 phase summaries
- **docs/system/PRD.md** - Product requirements
- **docs/system/CI_CD_SETUP.md** - GitHub Actions setup

### **New Agent Documentation:**
- **agents/refinement_agent/** - AI-powered idea refinement
- **agents/vertical_agent/README.md** - Business idea evaluator (RICE/ICE)
- **agents/opportunity_ranking/** - Advanced 7-criteria scoring
- **agents/strategic_planner/README.md** - Strategic decision maker
- **dashboards/VERTICAL_DASHBOARD_README.md** - Vertical scoring dashboard
- **streamlit_app/app.py** - Refinement & scoring dashboard

---

**Maintained by:** AI Management Team  
**Last Updated:** 2025-10-12  
**All 15 Phases:** ✅ Complete (11 core + 4 enhancements)
