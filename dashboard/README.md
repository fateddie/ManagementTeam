# Agent Monitoring Dashboard

## The Problem We're Solving

### **Before This Dashboard**
When you ran agents, you had:
- ❌ **No visibility** - Black box execution until completion
- ❌ **No control** - Can't stop runaway agents without `kill` commands
- ❌ **No debugging** - Have to read log files in terminal to understand failures
- ❌ **No file management** - Switch between terminal/editor to check outputs
- ❌ **No real-time feedback** - Wait minutes to discover a typo caused failure

### **After This Dashboard**
Now you have:
- ✅ **Full visibility** - See which agents are running, their status, confidence scores
- ✅ **Direct control** - Start/stop agents with button clicks
- ✅ **Live debugging** - Watch logs stream in real-time, catch errors immediately
- ✅ **Integrated file browser** - View/edit outputs without leaving the dashboard
- ✅ **Instant feedback** - Know within 2 seconds if something goes wrong

---

## Why This Architecture?

### **Design Decision: 3-Tier Architecture**

```
┌─────────────────────────────────────┐
│  PRESENTATION LAYER                 │  ← What you see
│  (streamlit_dashboard.py)           │
│  - UI components                    │
│  - User interactions                │
└──────────────┬──────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────┐
│  API LAYER                          │  ← Business logic
│  (api_server.py)                    │
│  - Route requests                   │
│  - Validate inputs                  │
│  - Coordinate operations            │
└──────────────┬──────────────────────┘
               │ Function calls
┌──────────────▼──────────────────────┐
│  DOMAIN LAYER                       │  ← Core functionality
│  (agent_runner.py, file_manager.py) │
│  - Subprocess management            │
│  - File operations                  │
│  - State tracking                   │
└──────────────┬──────────────────────┘
               │ System calls
┌──────────────▼──────────────────────┐
│  YOUR AGENTS                        │  ← Existing system
│  (All 11 BaseAgent agents)          │
└─────────────────────────────────────┘
```

**WHY 3 TIERS?**

1. **Separation of Concerns**
   - UI logic doesn't know about subprocesses
   - API doesn't know about Streamlit widgets
   - Each layer can be tested independently

2. **Flexibility**
   - Want to swap Streamlit for React? Just replace presentation layer
   - Want to add WebSocket support? Just modify API layer
   - Want to change how agents run? Just update domain layer

3. **Maintainability**
   - Bug in UI? Only touch streamlit_dashboard.py
   - Need new API endpoint? Only touch api_server.py
   - Agent logic change? Only touch agent_runner.py

---

## File-by-File Explanation

### `config.py` - Central Configuration

**PURPOSE:** Single source of truth for all settings

**WHY IT EXISTS:**
- Avoid magic numbers scattered across codebase
- Change settings in one place
- Easy to convert to environment variables later

**KEY DESIGN CHOICES:**
```python
POLL_INTERVAL = 2  # WHY: Balance between responsiveness and CPU
# - 1 second: Too aggressive, wastes resources
# - 5 seconds: Too slow, feels laggy
# - 2 seconds: Sweet spot for development monitoring
```

**AGENTS LIST:**
- Hardcoded agent metadata (name, path, dependencies)
- WHY: Central registry makes it easy to add/remove agents
- ALTERNATIVE: Could auto-discover agents, but explicit list is clearer

---

### `file_manager.py` - File System Operations

**PURPOSE:** Safe, controlled access to project files

**WHY NOT DIRECT FILE ACCESS?**
- **Security:** API can restrict which directories are accessible
- **Validation:** Check file exists before reading (avoid race conditions)
- **Abstraction:** UI doesn't need to know about Path objects
- **Error Handling:** Centralized try/catch for better error messages

**KEY METHODS:**

#### `get_file_tree()`
```python
def get_file_tree(self) -> List[Dict[str, Any]]:
    """Build tree structure of files."""
```
**WHY:** Tree structure matches mental model of file system
**REASONING:** Users understand "folders contain files" intuitively
**PERFORMANCE:** Filters out hidden files (.git, __pycache__) to reduce noise

#### `read_file(relative_path)`
**WHY RELATIVE PATHS?**
- Security: Can't access files outside project root
- Portability: Works on any machine regardless of install location
- Simplicity: Shorter paths in API calls

#### `write_file(relative_path, content)`
**WHY VALIDATION?**
- Prevents writing outside project directory
- Creates parent directories if needed (convenience)
- Returns detailed error messages for debugging

---

### `agent_runner.py` - Subprocess Management

**PURPOSE:** Run agents as subprocesses and capture their output

**WHY SUBPROCESSES INSTEAD OF IMPORTING?**

**Problem with importing:**
```python
from agents.strategy_agent import StrategyAgent
agent = StrategyAgent()
agent.execute(context)  # ❌ Blocks dashboard, can't stop it
```

**Solution with subprocesses:**
```python
proc = subprocess.Popen(["python", "agent.py"])  # ✅ Runs independently
proc.terminate()  # ✅ Can stop it
```

**REASONS:**
1. **Non-blocking:** Dashboard stays responsive while agents run
2. **Isolation:** Agent crash doesn't crash dashboard
3. **Control:** Can start/stop/restart agents on demand
4. **Monitoring:** Capture stdout/stderr separately
5. **Multiple agents:** Run several agents simultaneously

**KEY DESIGN: AgentExecution Dataclass**
```python
@dataclass
class AgentExecution:
    agent_name: str
    session_id: str
    start_time: str
    status: str = "running"  # State machine: running→completed/failed/stopped
```

**WHY DATACLASS?**
- Type hints for safety
- Auto-generates `__init__`, `__repr__`
- `asdict()` for easy JSON serialization

**WHY SESSION_ID?**
- Group related agent runs together
- Allows reviewing past executions
- Format: `YYYYMMDD_HHMMSS` - sortable, human-readable

**KEY METHOD: `_capture_output()`**

Runs in separate thread to avoid blocking:
```python
def _capture_output(self, agent_name, proc):
    """Capture stdout/stderr from process (runs in thread)."""
    for line in proc.stdout:  # WHY: Streaming, not blocking
        execution.stdout_lines.append(line)  # WHY: List, not string (memory efficient)
```

**THREADING RATIONALE:**
- Main thread can respond to API requests
- Background thread tails agent output
- No locks needed (each agent has own execution object)

---

### `api_server.py` - REST API Backend

**PURPOSE:** HTTP interface for dashboard to interact with system

**WHY REST API INSTEAD OF DIRECT FUNCTION CALLS?**

**What we could have done:**
```python
# In streamlit_dashboard.py:
from agent_runner import AgentRunner
runner = AgentRunner()
runner.start_agent("StrategyAgent")  # ❌ Tight coupling
```

**What we did:**
```python
# In streamlit_dashboard.py:
requests.post("http://localhost:8000/api/agents/StrategyAgent/start")  # ✅ Loose coupling
```

**BENEFITS:**
1. **Decoupling:** Streamlit doesn't import agent code
2. **Network-ready:** Easy to move API to different machine later
3. **Language-agnostic:** Could write UI in JavaScript if needed
4. **Standard protocol:** HTTP is universal, well-understood
5. **Testing:** Can test API with curl/Postman without UI

**WHY FASTAPI?**

**Alternatives:**
- Flask: More popular, but older, synchronous-only
- Django: Overkill for simple API
- Raw HTTP: Too much boilerplate

**FastAPI advantages:**
- **Type hints:** `def get_status() -> List[Dict]` generates docs automatically
- **Async:** Can handle multiple requests simultaneously (future-proof)
- **Auto docs:** `/docs` endpoint with interactive API explorer
- **Validation:** Pydantic models catch bad requests early
- **Modern:** Best practices built-in

**ENDPOINT DESIGN:**

```python
@app.get("/api/agents/status")  # WHY: RESTful resource naming
def get_all_agent_status():
    """Get status of all agents."""
    return {"status": runner.get_all_status()}
```

**WHY `/api/` PREFIX?**
- Namespace: Separates API from potential static files
- Convention: Standard in web development
- Versioning: Easy to add `/api/v2/` later

**WHY PLURAL `/agents`?**
- RESTful convention: Collection resources are plural
- Consistency: `/api/agents` (all), `/api/agents/{name}` (one)

**ERROR HANDLING:**
```python
if "error" in result:
    raise HTTPException(status_code=400, detail=result["error"])
```
**WHY HTTPException?**
- FastAPI knows how to format it as JSON error response
- Standard HTTP status codes (400=bad request, 404=not found)
- Client can handle errors consistently

**CORS MIDDLEWARE:**
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```
**WHY:** Streamlit runs on different port (8501) than API (8000)
**REASONING:** Browsers block cross-origin requests by default (security)
**SOLUTION:** CORS headers tell browser "it's okay, we trust each other"

---

### `streamlit_dashboard.py` - User Interface

**PURPOSE:** Visual interface for monitoring and controlling agents

**WHY STREAMLIT?**

**Comparison:**

| Framework | Lines of Code | Build Time | Learning Curve | Real-time Updates |
|-----------|---------------|------------|----------------|-------------------|
| React + Tailwind | ~800 | 5 hours | High (JSX, hooks) | Excellent (WebSocket) |
| **Streamlit** | **~400** | **2 hours** | **Low (just Python)** | **Good (polling)** |
| HTML/JS | ~600 | 4 hours | Medium | Manual (setInterval) |

**REASONING:** You want fast iteration during development/testing

**KEY DESIGN: Session State**
```python
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
```

**WHY SESSION STATE?**
- Streamlit reruns entire script on every interaction
- Without state, variables reset every time
- Session state persists across reruns (like global variables, but safer)

**EXAMPLE:**
```python
# Without session state:
auto_refresh = True  # ❌ Always True on rerun
if st.checkbox("Auto-refresh", auto_refresh):  # Always checked

# With session state:
st.session_state.auto_refresh = st.checkbox("Auto-refresh", st.session_state.auto_refresh)
# ✅ Remembers user's choice
```

**AUTO-REFRESH MECHANISM:**
```python
if st.session_state.auto_refresh:
    time.sleep(2)
    st.experimental_rerun()  # WHY: Triggers full rerun, fetches fresh data
```

**REASONING:**
- `sleep(2)` prevents hammering API every millisecond
- `experimental_rerun()` is Streamlit's way of saying "refresh the page"
- User can disable to freeze view (useful when reading logs)

**COLOR-CODED STATUS:**
```python
if is_running:
    status_color = "🟢"  # WHY: Universal "go" color
elif status == "failed":
    status_color = "❌"  # WHY: Instantly recognizable error indicator
```

**REASONING:**
- Humans process color faster than text
- No need to read "FAILED" when red X communicates it
- Colorblind-friendly: emoji shapes differ too

**FILE TREE DESIGN:**
```python
def render_file_tree(tree, level=0):
    indent = "  " * level  # WHY: Visual hierarchy
    with st.expander(f"📁 {item['name']}", expanded=(level==0)):
        render_file_tree(item['children'], level+1)  # WHY: Recursion for nested structure
```

**REASONING:**
- Recursion naturally handles arbitrary nesting
- Expanders prevent overwhelming UI with hundreds of files
- Top-level expanded by default (common files are at top)

---

## How It All Works Together: Request Flow

### **Example: User Clicks "Start Strategy Agent"**

```
1. USER ACTION
   └─ Click "▶️ Start" button for StrategyAgent

2. STREAMLIT (streamlit_dashboard.py)
   └─ Button click triggers:
      if st.button("▶️ Start"):
          start_agent("StrategyAgent")  # ← Helper function

3. HTTP REQUEST
   └─ Helper function makes POST:
      requests.post("http://localhost:8000/api/agents/StrategyAgent/start")

4. FASTAPI (api_server.py)
   └─ Route matches: @app.post("/api/agents/{agent_name}/start")
   └─ Calls: runner.start_agent("StrategyAgent")

5. AGENT RUNNER (agent_runner.py)
   └─ Looks up agent path: "agents/strategy_agent/strategy_agent.py"
   └─ Starts subprocess: subprocess.Popen(["python", "agents/..."])
   └─ Spawns thread to capture output
   └─ Saves execution metadata to: dashboard/runs/{session_id}/StrategyAgent.json

6. AGENT EXECUTES
   └─ StrategyAgent runs independently
   └─ Prints to stdout (captured by thread)
   └─ Creates outputs: outputs/strategy_plan.yaml

7. STREAMLIT POLLS (every 2 seconds)
   └─ Requests: GET /api/agents/status
   └─ API calls: runner.get_all_status()
   └─ UI updates: Shows "🟢 RUNNING" for StrategyAgent

8. AGENT COMPLETES
   └─ Process exits
   └─ Thread saves final logs
   └─ Status changes: "running" → "completed"

9. USER SEES RESULT
   └─ Next poll shows: "✅ COMPLETED"
   └─ User clicks "📁 Files" → sees strategy_plan.yaml
   └─ User clicks "📋 Logs" → sees full execution trace
```

---

## Design Decisions Explained

### **Why Polling Instead of WebSockets?**

**WebSocket approach:**
```python
# Server pushes updates instantly
websocket.send({"agent": "StrategyAgent", "status": "running"})
```
**Pros:** Instant updates (0ms latency)
**Cons:** More complex, harder to debug, persistent connections

**Polling approach:**
```python
# Client asks every 2 seconds
requests.get("/api/agents/status")
```
**Pros:** Simple, reliable, stateless
**Cons:** 2-second delay (acceptable for development monitoring)

**DECISION:** Polling
**REASONING:**
- Simplicity trumps perfection for internal tools
- 2-second latency is fine (not a trading system)
- Can always add WebSocket later if needed

### **Why Separate API and UI Processes?**

**Could have been single process:**
```python
# In streamlit_dashboard.py:
runner = AgentRunner()
runner.start_agent("StrategyAgent")  # ❌ No API layer
```

**WHY SEPARATE:**
1. **Independence:** API can run without UI (useful for automation/testing)
2. **Scalability:** Can run multiple UI instances, one API
3. **Debugging:** Can curl API directly to isolate UI issues
4. **Future-proofing:** Easy to add mobile app or CLI tool later

### **Why Save Execution Metadata?**

```python
execution_file = session_dir / f"{agent_name}.json"
execution_file.write_text(json.dumps(execution.to_dict()))
```

**WHY:**
- **History:** Review past runs to spot patterns (does StrategyAgent always fail on Fridays?)
- **Debugging:** Reproduce issues by seeing exact command/env
- **Auditing:** Track when agents ran, who started them
- **Analytics:** Analyze execution times over time

**FILE FORMAT CHOICE:**
- JSON: Human-readable, git-friendly, widely supported
- Alternative (SQL): Overkill for simple key-value data
- Alternative (Binary): Faster but opaque

---

## Cost Considerations

### **Token/API Costs: $0**
- ✅ **No LLM calls from dashboard** - pure UI + file I/O
- ✅ **Agent costs unchanged** - dashboard just watches, doesn't modify behavior
- ✅ **Local only** - no cloud hosting fees

### **Performance:**
- **Memory:** <50MB for API server, <100MB for Streamlit
- **CPU:** Negligible (mostly idle, brief spikes during polling)
- **Disk:** ~1KB per agent execution (minimal metadata)

### **Development Time vs Value:**
- **Investment:** 2-3 hours to build
- **Saved per debugging session:** 10-30 minutes (no terminal juggling)
- **ROI:** Pays for itself after ~6 debugging sessions

---

## Troubleshooting Guide

### **Problem: "API server not running"**

**Symptom:** Red error banner in dashboard

**Cause:** FastAPI server isn't started

**Solution:**
```bash
# Terminal 1: Start API
python dashboard/api_server.py

# Wait for: "🚀 Starting Agent Monitoring API..."
# Then: Terminal 2: Start dashboard
streamlit run dashboard/streamlit_dashboard.py
```

**WHY THIS HAPPENS:**
Dashboard makes HTTP requests to localhost:8000. If nothing is listening, requests fail.

---

### **Problem: Agent shows "RUNNING" but no logs**

**Possible causes:**

1. **Agent is hanging (waiting for input)**
   - **Check:** Does agent need user input? (e.g., `input("Enter idea: ")`)
   - **Fix:** Modify agent to accept arguments instead of interactive input

2. **Output buffering**
   - **Check:** Are you using `print()`? Python buffers stdout by default
   - **Fix:** Use `print("...", flush=True)` or run with `python -u`

3. **Agent is working, just slow**
   - **Check:** Is agent calling LLM? API calls take 3-30 seconds
   - **Fix:** Be patient, or add progress indicators to agent code

---

### **Problem: File edits don't take effect**

**Symptom:** Edit file in dashboard, agent still uses old version

**Cause:** Agent already loaded file before your edit

**Solution:**
1. Edit file
2. Restart agent (click Stop, then Start)
3. Agent will load fresh file content

**WHY:** Python loads files at startup. To see edits, must restart process.

---

## Next Steps & Future Enhancements

### **Phase 2: Parallel Execution** (from existing roadmap)
- Use agent dependencies to run independent agents simultaneously
- Dashboard would show multiple agents running at once
- Significantly reduces total pipeline time

### **Potential Enhancements:**

1. **Visual Dependency Graph**
   - Use networkx + graphviz to render interactive graph
   - Click node to see agent details
   - Highlight critical path (longest chain)

2. **Session Comparison**
   - View two runs side-by-side
   - Diff outputs to see what changed
   - Identify which change improved results

3. **Notifications**
   - Browser notification when agent completes
   - Email/Slack alerts for failures
   - Critical for long-running agents

4. **Performance Metrics**
   - Execution time trends over time
   - Confidence score charts
   - Identify slow/unreliable agents

5. **Agent Configuration UI**
   - Edit agent config.yaml from dashboard
   - Adjust weights, thresholds without code
   - A/B test different configurations

---

## Startup Scripts

### **start_dashboard.sh** - One-Command Startup

**PURPOSE:** Start both API and dashboard with a single command

**USAGE:**
```bash
./dashboard/start_dashboard.sh
```

**WHAT IT DOES:**
1. ✅ Checks dependencies installed (`pip install -r requirements.txt`)
2. ✅ Checks port 8000 available (kills existing if needed)
3. ✅ Starts API server in background
4. ✅ Waits for API health check (polls `/health` endpoint)
5. ✅ Starts Streamlit dashboard in foreground
6. ✅ On Ctrl+C: Gracefully shuts down both processes

**WHY BACKGROUND + FOREGROUND?**
- API in background: Runs invisibly, logs to `/tmp/dashboard_api.log`
- Streamlit in foreground: Interactive, Ctrl+C stops it naturally
- Trap handler: Ensures API is killed when Streamlit exits

**ERROR HANDLING:**
- Missing dependencies → Clear install instructions
- Port conflict → Offer to kill existing process
- API won't start → Show log location, exit cleanly

---

### **stop_dashboard.sh** - Force Stop All Processes

**PURPOSE:** Kill dashboard processes if Ctrl+C didn't work

**USAGE:**
```bash
./dashboard/stop_dashboard.sh
```

**WHEN TO USE:**
- Terminal killed instead of Ctrl+C (processes orphaned)
- Port 8000 or 8501 stuck (can't start new instance)
- Debugging (want clean slate)

**WHAT IT DOES:**
1. Finds processes on port 8000 (API) → kills them
2. Finds processes on port 8501 (Streamlit) → kills them
3. Removes PID file (`/tmp/dashboard_api.pid`)
4. Reports what was stopped

**WHY KILL -9?**
- Normal signals may not work on stuck processes
- Force kill ensures cleanup
- Safe because these are local dev servers

---

## Summary: Why This Design?

**Every decision optimizes for:**

1. **Development Speed** (Streamlit over React)
2. **Debuggability** (Detailed logging, clear error messages)
3. **Simplicity** (3 files, 600 lines total, not 3000)
4. **Maintainability** (Separation of concerns, single responsibility)
5. **Cost** ($0 - local only, no cloud services)
6. **Extensibility** (Easy to add features without rewriting)

**The result:**
A professional monitoring dashboard built in 2-3 hours that provides real-time visibility into agent execution, dramatically improving development/debugging workflow with zero ongoing costs.

---

**Questions? Issues?**
- Check logs: `dashboard/runs/{session_id}/` for execution history
- Test API directly: Visit `http://localhost:8000/docs` for interactive API explorer
- Debug Streamlit: Add `st.write(variable)` to inspect values

**Remember:** This dashboard is a *tool for development*. It's not meant to be production infrastructure. Its value is making your life easier during agent development and testing.
