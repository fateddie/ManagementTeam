# ⚡ Quick Start Guide - Planner Agent

**1-Page Reference** | Always keep this handy!

---

## 🚀 Common Commands

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

| What           | Path                               |
| -------------- | ---------------------------------- |
| **Projects**   | `/projects/<project-name>/`        |
| **Templates**  | `/config/templates/`               |
| **Logs**       | `/logs/planner_trace.log`          |
| **Dashboard**  | `/dashboards/planner_dashboard.py` |
| **CLI Script** | `/scripts/run_planner.py`          |

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
