# Dashboard Quick Start Guide

## Installation (2 minutes)

### Step 1: Install Dependencies

```bash
# From project root
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam

# Install dashboard requirements
pip install -r dashboard/requirements.txt
```

**WHY:** Dashboard needs FastAPI, Streamlit, and other libraries that aren't in your base agent requirements.

---

## Running the Dashboard (30 seconds)

### **EASY WAY (Recommended):** One-Command Startup

```bash
# From project root - starts everything automatically
./dashboard/start_dashboard.sh
```

**WHY:** This script:
- ✅ Checks dependencies are installed
- ✅ Starts API server in background
- ✅ Waits for API to be ready
- ✅ Starts Streamlit dashboard
- ✅ Opens browser automatically
- ✅ Cleans up on exit (Ctrl+C)

**You should see:**
```
==================================================
🤖 Agent Monitoring Dashboard Startup
==================================================

📋 Checking dependencies...
✅ Dependencies OK

🚀 Starting API server (backend)...
⏳ Waiting for API to start...
✅ API server ready (PID: 12345)

==================================================
✅ Backend Running
==================================================
📍 API:  http://localhost:8000
📖 Docs: http://localhost:8000/docs

==================================================
🎨 Starting Dashboard (frontend)...
==================================================

The dashboard will open in your browser automatically.
Press Ctrl+C to stop both API and dashboard
```

**To stop everything:** Press `Ctrl+C` in the terminal

---

### **MANUAL WAY:** Two Terminals (Alternative)

If you prefer to run API and dashboard separately:

**Terminal 1: API Server**
```bash
python dashboard/api_server.py
```

**Terminal 2: Dashboard**
```bash
streamlit run dashboard/streamlit_dashboard.py
```

**WHY USE MANUAL WAY?**
- See API logs in real-time (startup script hides them)
- Debug API issues separately from UI
- Restart one without restarting the other

---

### **Stopping the Dashboard**

**If using startup script:** Press `Ctrl+C`

**If processes stuck:** Run cleanup script
```bash
./dashboard/stop_dashboard.sh
```

**WHY:** Kills any orphaned processes on ports 8000 and 8501

---

## Using the Dashboard

### Overview Page (Default)

**What you see:**
- Summary metrics (Total/Running/Completed/Failed agents)
- Agent status cards with:
  - 🟢 Green = Currently running
  - ✅ Green check = Completed successfully
  - ❌ Red X = Failed
  - ⚪ White = Idle (not run yet)
- Start/Stop buttons for each agent
- Quick link to logs

**What to do:**
1. **Start an agent:** Click "▶️ Start" on any agent card
2. **Watch it run:** Status updates every 2 seconds automatically
3. **View logs:** Click "📋 Logs" to see output

**PRO TIP:** Enable "🔄 Auto-refresh" to see live updates!

---

### Logs Page

**What you see:**
- Dropdown to select agent
- Two tabs:
  - **Output (stdout):** Normal agent output
  - **Errors (stderr):** Error messages and warnings

**What to do:**
1. Select agent from dropdown
2. Watch logs stream in real-time (if auto-refresh enabled)
3. Scroll through to find errors or debug info

**WHY SEPARATE TABS:** stdout vs stderr is standard in Unix/Linux. Most normal output goes to stdout, errors to stderr. Separating them makes errors easier to spot.

---

### Files Page

**What you see:**
- Left panel: Directory tree of `outputs/`, `results/`, `data/`
- Right panel: File viewer/editor

**What to do:**
1. **Click folder** (📁) to expand it
2. **Click file** (📄) to view its contents
3. **Edit content** in text area
4. **Click "💾 Save"** to save changes

**USE CASES:**
- **Quick fixes:** Fix typo in generated YAML without leaving dashboard
- **Config tweaks:** Adjust agent settings and re-run
- **Output review:** Check what agents generated

**WARNING:** Saving overwrites the file immediately. No undo!

---

### Dependency Graph Page

**What you see:**
- Textual representation of agent dependencies
- Shows execution order (Level 0, 1, 2, etc.)

**WHY IT MATTERS:**
- Understand which agents block others
- Identify longest critical path (bottleneck)
- Plan parallel execution (Phase 2)

**EXAMPLE:**
```
Level 0: StrategyAgent runs first
Level 1: TechnicalArchitect waits for Strategy to finish
Level 2: Planning waits for both Strategy + Technical
```

If Strategy fails, everything downstream also fails!

---

## Common Workflows

### Workflow 1: Run Full Pipeline

1. Go to **Overview** page
2. Scroll to **Orchestrator** card
3. Click "▶️ Start"
4. Watch agents run in sequence
5. Check **Logs** if any fail

**TIME:** 3-10 minutes depending on agents

---

### Workflow 2: Debug Single Agent

1. Go to **Overview** page
2. Click "▶️ Start" on problematic agent
3. Switch to **Logs** page
4. Select that agent from dropdown
5. Enable auto-refresh
6. Watch output to find error

**TIP:** stderr tab shows errors. Look there first!

---

### Workflow 3: Quick Config Edit

1. Go to **Files** page
2. Navigate to config file (e.g., `outputs/strategy_plan.yaml`)
3. Edit content in text area
4. Click "💾 Save"
5. Go to **Overview**
6. Stop and restart affected agent

**USE CASE:** Agent generated bad config, need to fix and re-run downstream agents

---

### Workflow 4: Monitor Long-Running Agent

1. Start agent from **Overview**
2. **Disable** "🔄 Auto-refresh" checkbox
3. Read current logs
4. **Enable** auto-refresh when done reading
5. Let it update automatically

**WHY:** Auto-refresh disrupts reading. Disable to freeze view, enable to resume live updates.

---

## Troubleshooting

### Problem: "API server not running" error

**Symptom:** Red banner at top of dashboard

**Solution:**
```bash
# Make sure Terminal 1 is running:
python dashboard/api_server.py

# You should see: "🚀 Starting Agent Monitoring API..."
```

**WHY:** Dashboard can't function without API server. API must start first.

---

### Problem: Agent stuck on "RUNNING" forever

**Possible causes:**

**1. Agent waiting for input:**
```python
# Bad: Agent waits forever for user to type
raw_idea = input("Enter idea: ")
```
**Fix:** Modify agent to accept arguments instead

**2. Agent is actually working:**
- LLM calls take 5-30 seconds
- File processing takes time
- Be patient!

**3. Agent crashed but not detected:**
- Check logs for errors
- Click "⏹ Stop" then "▶️ Start" to restart

---

### Problem: Can't see logs

**Symptom:** Logs page shows "No output yet"

**Possible causes:**

**1. Agent hasn't printed anything yet:**
- Wait 5-10 seconds
- Some agents are quiet at start

**2. Output buffering:**
- Python buffers print() statements
- Agent may have printed, but not flushed

**Fix in agent code:**
```python
# Before
print("Starting...")

# After
print("Starting...", flush=True)  # Forces immediate output
```

**3. Agent redirected output elsewhere:**
- Check `logs/` directory for files
- Some agents log to files, not stdout

---

### Problem: File edits don't take effect

**Symptom:** Changed file, agent still uses old version

**Cause:** Agent already loaded file at startup

**Solution:**
1. Edit file in dashboard
2. Click "💾 Save"
3. Go to Overview
4. Click "⏹ Stop" on agent
5. Click "▶️ Start" on agent

**WHY:** Python loads files once. Must restart process to reload.

---

## Advanced Tips

### Tip 1: Check API Docs

```
Open: http://localhost:8000/docs
```

**WHY:** FastAPI auto-generates interactive API documentation. You can test endpoints directly without the dashboard.

**USE CASE:** Dashboard broken? Test API directly to isolate issue.

---

### Tip 2: View Session History

```bash
# From project root
ls -la dashboard/runs/

# Each folder is a session (format: YYYYMMDD_HHMMSS)
# Inside: JSON files with execution metadata
```

**WHY:** Every agent run is logged. Review past executions to spot patterns.

**USE CASE:** "Agent worked yesterday, fails today. What changed?"

---

### Tip 3: Monitor from Another Computer

```bash
# Find your local IP
ifconfig | grep inet

# Access dashboard from another device:
http://192.168.1.X:8501
```

**WHY:** Streamlit serves on local network. Can monitor from phone/tablet.

**USE CASE:** Run long pipeline, monitor progress from couch!

---

### Tip 4: Run Multiple Dashboards

```bash
# Terminal 1: API (only need one)
python dashboard/api_server.py

# Terminal 2: Dashboard 1
streamlit run dashboard/streamlit_dashboard.py

# Terminal 3: Dashboard 2 (different port)
streamlit run dashboard/streamlit_dashboard.py --server.port 8502
```

**WHY:** Multiple team members can monitor same agents.

---

## What's Next?

After you're comfortable with the dashboard:

1. **Try running Orchestrator** - Full pipeline execution
2. **Experiment with file editing** - Quick config tweaks
3. **Monitor confidence scores** - Spot low-quality decisions
4. **Review session history** - Learn from past runs

---

## Quick Reference

### Ports
- **API Server:** http://localhost:8000
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

### Files Created by Agents
- **outputs/** - Main agent outputs (YAML, MD)
- **results/** - Scoring results, reports
- **data/** - Refined ideas, opportunity data
- **logs/** - Log files (if agents log to files)

### Session History
- **dashboard/runs/{session_id}/** - Execution metadata (JSON)

### Key Concepts
- **Polling:** Dashboard checks API every 2 seconds
- **Subprocesses:** Agents run independently, can be stopped
- **REST API:** Dashboard talks to agents via HTTP
- **Session ID:** Groups related agent runs (format: YYYYMMDD_HHMMSS)

---

**You're ready to go!** 🚀

Start the API server, start the dashboard, and click "▶️ Start" on an agent to see it in action.
