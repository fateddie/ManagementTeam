# ⚡ Quick Start Guide - Management Team AI System

**1-Page Reference** | Always keep this handy!

---

## 🔑 First Time Setup

### Set Up API Keys (One Time Only)

```bash
# 1. Copy the template
cp config/.env.example config/.env

# 2. Edit with your actual keys
nano config/.env
# (Add your PERPLEXITY_API_KEY, etc.)

# 3. Load environment
source activate.sh
```

---

## 🎯 Vertical Agent - Evaluate Business Ideas (NEW!)

### Quick Evaluation (2 Minutes)

```bash
# 1. Create inputs/ideas.json with your business ideas
[
  {
    "name": "AI Receptionist for Hair Salons",
    "reach": 7,
    "impact": 8,
    "confidence": 6,
    "effort": 4
  },
  {
    "name": "Tyre Fitters Booking Bot",
    "reach": 5,
    "impact": 7,
    "confidence": 8,
    "effort": 5
  }
]

# 2. Run evaluation
python scripts/run_vertical_agent.py inputs/ideas.json

# 3. Check outputs/recommendation.md for results
```

**What the scores mean (1-10):**

- **Reach:** How many customers? (Higher = more customers)
- **Impact:** How much value? (Higher = bigger improvement)
- **Confidence:** How sure are you? (Higher = more certain)
- **Effort:** How hard to build? (Lower = easier, better!)

**Options:**

```bash
# Use ICE framework instead
python scripts/run_vertical_agent.py inputs/ideas.json --framework ICE

# Show full ranking
python scripts/run_vertical_agent.py inputs/ideas.json --verbose

# Run with examples
python scripts/run_vertical.py

# Launch interactive dashboard 🆕
streamlit run dashboards/vertical_dashboard.py
```

---

## 🚀 Planner Agent - Common Commands

### Create a New Project

```bash
python scripts/run_planner.py "project-name" "Description of your project"
```

### With Human Oversight

```bash
python scripts/run_planner.py "project-name" "Description" --interactive
```

### Start Dashboard

```bash
streamlit run dashboards/planner_dashboard.py
```

### Run Demo/Test

```bash
python src/agents/planner_agent.py
```

---

## 📁 Important Paths

| What                | Path                               |
| ------------------- | ---------------------------------- |
| **Projects**        | `/projects/<project-name>/`        |
| **Vertical Inputs** | `/inputs/ideas.json`               |
| **Vertical Output** | `/outputs/recommendation.md`       |
| **Templates**       | `/config/templates/`               |
| **Logs**            | `/logs/planner_trace.log`          |
| **Dashboard**       | `/dashboards/planner_dashboard.py` |
| **CLI Scripts**     | `/scripts/run_*.py`                |

---

## 📊 Check Project Status

```bash
# View logs
tail -f logs/planner_trace.log

# List projects
ls -la projects/

# Check specific project
ls -la projects/<project-name>/planning/
```

---

## 🎯 Expected Outputs

Every project creates:

```
/projects/<project-name>/planning/
├── project_plan.yaml       # Main plan
├── roadmap.md              # Timeline
├── missing_info.md         # Gaps to fill
├── reflection_report.md    # AI analysis
└── summary_report.json     # Metrics
```

---

## 🔧 Troubleshooting

### No output generated

```bash
# Check logs
cat logs/planner_trace.log

# Verify templates exist
ls config/templates/
```

### Dashboard won't start

```bash
# Install dependencies
pip install -r requirements.txt

# Check Streamlit
streamlit --version
```

### Permission errors

```bash
# Make script executable
chmod +x scripts/run_planner.py
chmod +x claude/environment.sh
```

---

## 📚 Key Documentation

| Document                            | Purpose                |
| ----------------------------------- | ---------------------- |
| `SYSTEM_READY.md`                   | Full system status     |
| `IMPLEMENTATION_COMPLETE.md`        | Implementation details |
| `docs/system/planner_agent_spec.md` | Agent specification    |
| `dashboards/README.md`              | Dashboard guide        |

---

## ⌨️ Examples

### Trading Bot

```bash
python scripts/run_planner.py \
  "trading-bot" \
  "Build an automated crypto trading bot with ML predictions"
```

### Data Pipeline

```bash
python scripts/run_planner.py \
  "data-pipeline" \
  "Create ETL pipeline for processing customer data"
```

### Web App

```bash
python scripts/run_planner.py \
  "web-dashboard" \
  "Build analytics dashboard with real-time metrics" \
  --interactive
```

---

## 🎛️ Dashboard Controls

- **Refresh Rate:** 2-30 seconds
- **Project Selection:** Text input or dropdown
- **Toggles:** Logs, Files, Timeline
- **Download:** Logs and individual files

---

## ✅ Quick Checklist

Before running:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] In correct directory
- [ ] Templates folder exists
- [ ] **API keys set in `config/.env`** (copy from `config/.env.example`)

After running:

- [ ] Check `/projects/<name>/planning/` for files
- [ ] Review `missing_info.md` for gaps
- [ ] Validate `project_plan.yaml`
- [ ] Read `reflection_report.md`

---

## 🆘 Need Help?

1. **Check logs:** `logs/planner_trace.log`
2. **Read docs:** `docs/system/planner_agent_spec.md`
3. **Run demo:** `python src/agents/planner_agent.py`
4. **View dashboard:** `streamlit run dashboards/planner_dashboard.py`

---

**Version:** 1.1 | **Date:** 2025-10-10 | **Status:** ✅ Ready
