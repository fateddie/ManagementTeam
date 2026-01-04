# Folder Structure Guide

**Last Updated:** 2025-10-25
**Purpose:** Reference guide for project organization (for both AI and humans)

---

## 📁 Root Directory (Essentials Only - 10 files)

```
ManagementTeam/
├── README.md                # Project overview & quick start
├── pyproject.toml          # Python project configuration
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini              # Test configuration
├── .env                    # Environment variables (git-ignored)
├── .env.example            # Template for .env
├── .gitignore             # Git ignore rules
├── .editorconfig          # Editor settings
└── .pre-commit-config.yaml # Pre-commit hooks config
```

**Philosophy:** Root should only contain essential config files. Everything else organized into logical folders.

---

## 📚 Documentation (docs/)

```
docs/
├── ARCHITECTURE.md         # System architecture & data flow
├── PRINCIPLES.md           # Core principles (transparency, human-in-loop)
├── CLAUDE.md              # Instructions for AI assistants
├── AUDIT_CHECKLIST.md     # Feature verification checklist
├── CHANGELOG.md           # Chronological change history
├── PROJECT_SNAPSHOT.md    # Current state snapshot
├── QUICKSTART.md          # Getting started guide
├── FOLDER_STRUCTURE.md    # This file
├── COST_OPTIMIZATION.md   # HuggingFace cost savings strategy
│
├── setup/                 # Setup guides
│   ├── API_KEYS_SETUP_GUIDE.md
│   ├── DASHBOARD_SETUP.md
│   └── TREND_RESEARCH_QUICKSTART.md
│
└── archive/               # Historical documentation
    └── (older docs preserved for reference)
```

---

## 🧪 Tests (tests/)

```
tests/
├── test_checkpoints.py          # Checkpoint/resume functionality
├── test_collector.py            # Data collection tests
├── test_data_persistence.py     # Data persistence tests
├── test_integration.py          # End-to-end integration tests
├── test_sub_agents.py           # Sub-agent tests
├── test_subagent_triggers.py    # Agent trigger logic tests
│
├── integration/                 # Integration test suites
└── e2e/                         # End-to-end test suites
```

**Run tests:**
```bash
pytest tests/ -v
```

---

## 📊 Data (data/)

**Philosophy:** Separate raw data, reports, and exports. Git-ignore generated files.

```
data/
├── raw/                   # Source data (git-ignored)
│   ├── social_posts.csv              # Collected posts
│   └── social_posts_enriched.csv     # Posts with ICP/urgency/pricing
│
├── reports/              # Generated reports
│   ├── evidence_report.md                  # Human-readable (git-tracked)
│   └── demand_validation_report.json      # Machine-readable (git-ignored)
│
├── exports/              # User exports (git-ignored)
│   ├── data_export.csv
│   └── data_export.xlsx
│
└── cache/               # Performance cache (git-ignored)
    └── embeddings.pt   # Semantic search embeddings cache
```

**Access Patterns:**
```python
# Reading enriched data
df = pd.read_csv("data/raw/social_posts_enriched.csv")

# Generating reports
validator = DemandValidator()  # Defaults to data/raw/social_posts_enriched.csv
validator.export_evidence_report("data/reports/evidence_report.md")
```

---

## 🔧 Source Code (src/)

```
src/
├── analysis/             # Analysis modules
│   └── demand_validator.py    # ICP, features, pricing analysis
│
├── integrations/         # External API integrations
│   ├── reddit_connector.py
│   ├── x_connector.py
│   └── message_collector_v4_enhanced.py
│
├── ml/                   # Machine learning models
│   ├── pain_point_extractor.py   # HuggingFace NER + sentiment
│   ├── topic_clustering.py       # BERTopic
│   └── virality_analyzer.py
│
└── utils/                # Utilities
    ├── config_loader.py
    └── config_utils.py
```

---

## ⚙️ Core (core/)

```
core/
├── workflow_state.py              # Checkpoint/resume system
├── interactive_orchestrator.py    # Main workflow orchestration
├── pain_discovery_analyzer.py     # Pain discovery coordination
├── keyword_generator.py           # Hybrid KeyBERT + GPT keywords
├── idea_critic.py                 # T5 grammar + GPT critique
├── competitive_analyzer.py        # Competitor intelligence
├── ai_conversation_handler.py     # AI conversation management
└── base_agent.py                  # Base agent class
```

---

## 📜 Scripts (scripts/)

```
scripts/
├── export_evidence.py        # Export validation evidence
├── view_posts.py             # View collected posts
├── search_evidence.py        # Semantic search (HuggingFace)
├── update_changelog.py       # Auto-update CHANGELOG (git hook)
├── verify_docs.py            # Verify docs current (git hook)
└── (other utility scripts)
```

**Usage:**
```bash
# Semantic search
python scripts/search_evidence.py "missed calls" --top-k 5

# Export evidence
python scripts/export_evidence.py --format markdown

# View posts by industry
python scripts/view_posts.py --industry dental
```

---

## 🤖 Agents (agents/)

```
agents/
├── refinement_agent/      # AI-powered idea refinement
├── vertical_agent/        # Business vertical scoring (RICE/ICE)
├── opportunity_ranking/   # Multi-criteria ranking
├── strategic_planner/     # Strategic planning
└── (other agents)
```

---

## 🗄️ Archive (archive/)

```
archive/
├── orchestrator_artifacts_phases_0_3/
├── orchestrator_prototype/
├── orchestrator_schema_phases_0_3/
└── claude/  # Old claude folder (not .claude)
```

**Purpose:** Preserve historical artifacts without cluttering active workspace.

---

## 🔄 Other Directories

```
.checkpoints/          # Workflow state checkpoints (git-ignored)
.claude/              # Claude Code settings
.git/                 # Git repository data
.venv/               # Virtual environment (git-ignored)
logs/                # Application logs (git-ignored)
outputs/             # Agent outputs (git-ignored)
```

---

## 🎯 Quick Reference

### Where to find things:

| What | Where |
|------|-------|
| Architecture docs | `docs/ARCHITECTURE.md` |
| Cost optimization | `docs/COST_OPTIMIZATION.md` |
| Core principles | `docs/PRINCIPLES.md` |
| AI instructions | `docs/CLAUDE.md` |
| Collected data | `data/raw/social_posts_enriched.csv` |
| Generated reports | `data/reports/evidence_report.md` |
| Semantic search | `scripts/search_evidence.py` |
| Tests | `tests/` |

### Where to add new files:

| Type | Location |
|------|----------|
| Documentation | `docs/` |
| Tests | `tests/` |
| Source code | `src/` (by category) |
| Core orchestration | `core/` |
| Utility scripts | `scripts/` |
| Agent implementations | `agents/` |

---

**Need to change structure?** Update this file + .gitignore accordingly.
