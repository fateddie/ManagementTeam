# Dashboard - Quick Reference

**For full documentation, see [dashboard/README.md](dashboard/README.md)**

---

## One-Command Start

```bash
./dashboard/start_dashboard.sh
```

Press `Ctrl+C` to stop.

---

## What You Get

**Dashboard UI:** http://localhost:8501
- Start/stop agents with buttons
- View logs in real-time  
- Browse/edit output files
- See dependency graph
- Track confidence scores

**API Backend:** http://localhost:8000
- REST endpoints for agent control
- Interactive docs at /docs

---

## Installation

```bash
pip install -r dashboard/requirements.txt
```

---

## Documentation

- **DASHBOARD_SETUP.md** (this file) - Quick reference
- **dashboard/QUICKSTART.md** - Detailed usage guide with workflows
- **dashboard/README.md** - Complete system explanation with architecture

---

## Common Tasks

**Start an agent:**
1. Open http://localhost:8501
2. Click "▶️ Start" on agent card
3. Watch status change to 🟢 RUNNING

**View logs:**
1. Click "📝 Logs" in sidebar
2. Select agent from dropdown
3. Enable auto-refresh for live updates

**Edit files:**
1. Click "📁 Files" in sidebar
2. Click file in tree view
3. Edit in text area
4. Click "💾 Save"

---

## Troubleshooting

**"API server not running":**
```bash
./dashboard/start_dashboard.sh
```

**Port already in use:**
```bash
./dashboard/stop_dashboard.sh
./dashboard/start_dashboard.sh
```

**Agent stuck on RUNNING:**
- Check logs for errors
- Click "⏹ Stop" then "▶️ Start"

---

## Files Created

```
dashboard/
├── start_dashboard.sh      # Startup script (one command)
├── stop_dashboard.sh       # Force stop script
├── api_server.py           # FastAPI backend
├── streamlit_dashboard.py  # Streamlit UI
├── QUICKSTART.md          # Detailed guide
└── README.md              # Complete docs
```

---

**Ready?** Run: `./dashboard/start_dashboard.sh` 🚀
