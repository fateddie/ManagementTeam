"""
streamlit_dashboard.py
Real-Time Agent Monitoring Dashboard

PURPOSE & REASONING:
-------------------
This dashboard solves the problem of "blind execution" - when agents run,
you have no visibility into what they're doing until they finish (or crash).

WHY WE NEED THIS:
1. Development & Debugging: See which agent is stuck, where errors occur
2. Confidence Monitoring: Track confidence scores to spot low-quality decisions
3. Dependency Understanding: Visualize which agents wait for others
4. File Management: Quickly view/edit outputs without terminal commands
5. Real-Time Feedback: Know immediately when something goes wrong

WHY STREAMLIT:
- Fast to build (2-3 hours vs 5+ for React)
- Python-only (no JS knowledge needed)
- Auto-refresh built-in (via st.experimental_rerun)
- Already familiar (you have existing Streamlit dashboards)

ARCHITECTURE:
This is the "VIEW" layer. It polls the FastAPI "CONTROLLER" layer
every 2 seconds, which manages the "MODEL" layer (agents running as subprocesses).
Classic MVC pattern keeps concerns separated.
"""

import streamlit as st
import requests
import time
import json
from pathlib import Path
from datetime import datetime

# WHY: Import after setting page config to avoid Streamlit warnings
st.set_page_config(
    page_title="Agent Monitor",
    page_icon="🤖",
    layout="wide",  # WHY: Wide layout shows more data without scrolling
    initial_sidebar_state="expanded"
)

# ============================================================================
# Configuration
# ============================================================================

# WHY: Hardcoded for simplicity. Could be env vars for production.
API_URL = "http://127.0.0.1:8000"
POLL_INTERVAL = 2  # seconds - WHY: Balance between responsiveness and CPU usage

# WHY: Initialize session state to persist data across refreshes
if "last_update" not in st.session_state:
    st.session_state.last_update = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None


# ============================================================================
# Helper Functions
# ============================================================================

def check_api_connection():
    """
    Check if API server is running.

    WHY: Fail fast with clear error message instead of confusing timeout errors.
    REASONING: Users need to know to start the API server first.
    """
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_agent_status():
    """
    Fetch status of all agents from API.

    WHY: Centralized data fetching makes it easy to add caching/error handling.
    RETURNS: List of agent status dicts or empty list on error.
    """
    try:
        response = requests.get(f"{API_URL}/api/agents/status", timeout=5)
        if response.status_code == 200:
            return response.json().get("status", [])
    except:
        pass
    return []


def start_agent(agent_name):
    """
    Start an agent via API.

    WHY: UI shouldn't know HOW to start agents, just trigger the action.
    This keeps the dashboard decoupled from agent implementation details.
    """
    try:
        response = requests.post(f"{API_URL}/api/agents/{agent_name}/start", timeout=5)
        return response.status_code == 200
    except:
        return False


def stop_agent(agent_name):
    """Stop a running agent via API."""
    try:
        response = requests.post(f"{API_URL}/api/agents/{agent_name}/stop", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_agent_logs(agent_name, lines=100):
    """
    Fetch recent log lines for an agent.

    WHY: Limited to last N lines to avoid memory issues with long-running agents.
    REASONING: Users care most about recent output, not ancient history.
    """
    try:
        response = requests.get(f"{API_URL}/api/agents/{agent_name}/logs?lines={lines}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"stdout": [], "stderr": []}


def get_file_tree():
    """Fetch file tree from API."""
    try:
        response = requests.get(f"{API_URL}/api/files/tree", timeout=5)
        if response.status_code == 200:
            return response.json().get("tree", [])
    except:
        pass
    return []


def read_file(path):
    """Read file contents from API."""
    try:
        response = requests.get(f"{API_URL}/api/files/content?path={path}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None


def write_file(path, content):
    """Write file contents via API."""
    try:
        response = requests.put(
            f"{API_URL}/api/files/content?path={path}",
            json={"content": content},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False


# ============================================================================
# UI Components
# ============================================================================

def render_agent_card(agent_status):
    """
    Render a single agent status card.

    WHY: Cards provide at-a-glance status with visual hierarchy.
    DESIGN: Color-coded status (green=running, gray=idle, red=failed)
    makes it immediately obvious what's happening.
    """
    name = agent_status.get("agent_name", "Unknown")
    is_running = agent_status.get("is_running", False)
    status = agent_status.get("status", "idle")

    # WHY: Color coding for instant visual feedback
    if is_running:
        status_color = "🟢"
        status_text = "RUNNING"
    elif status == "completed":
        status_color = "✅"
        status_text = "COMPLETED"
    elif status == "failed":
        status_color = "❌"
        status_text = "FAILED"
    elif status == "stopped":
        status_color = "⏸️"
        status_text = "STOPPED"
    else:
        status_color = "⚪"
        status_text = "IDLE"

    # Create card with columns for layout
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(f"### {status_color} {name}")
        st.caption(f"Status: **{status_text}**")

        # WHY: Show metadata when available to give context
        if agent_status.get("metadata"):
            confidence = agent_status["metadata"].get("confidence")
            if confidence:
                st.caption(f"🎯 Confidence: {confidence}")

    with col2:
        # WHY: Start/stop buttons for direct control
        if is_running:
            if st.button("⏹ Stop", key=f"stop_{name}"):
                if stop_agent(name):
                    st.success(f"Stopped {name}")
                    st.rerun()
        else:
            if st.button("▶️ Start", key=f"start_{name}"):
                if start_agent(name):
                    st.success(f"Started {name}")
                    st.rerun()

    with col3:
        # WHY: Quick link to logs for debugging
        if st.button("📋 Logs", key=f"logs_{name}"):
            st.session_state.selected_agent_logs = name

    # WHY: Show timing info to spot slow agents
    if agent_status.get("start_time"):
        st.caption(f"Started: {agent_status['start_time'][:19]}")
    if agent_status.get("end_time"):
        st.caption(f"Ended: {agent_status['end_time'][:19]}")

    st.divider()


def render_file_tree(tree, level=0):
    """
    Recursively render file tree.

    WHY: Tree structure matches mental model of file system.
    REASONING: Users already understand folders contain files,
    so we mirror that familiar structure.

    DESIGN NOTE: Using indentation for folders instead of nested expanders
    to avoid Streamlit's nested expander limitation.
    """
    indent = "　" * level  # Using full-width space for indentation
    
    for item in tree:
        if item["type"] == "directory":
            # WHY: Simple text for directories with indentation
            # REASONING: Avoids nested expander issue while showing hierarchy
            st.markdown(f"{indent}📁 **{item['name']}/**")
            if item.get("children"):
                render_file_tree(item["children"], level + 1)
        else:
            # WHY: Clickable files for easy viewing
            # REASONING: Button makes it clear the file is interactive
            if st.button(
                f"{indent}📄 {item['name']}",
                key=f"file_{item['path']}",
                help=f"Size: {item['size']} bytes | Modified: {item['modified'][:19]}"
            ):
                st.session_state.selected_file = item["path"]


# ============================================================================
# Pages
# ============================================================================

def page_overview():
    """
    Overview page - Main dashboard.

    WHY: Single-screen overview lets users see everything at once.
    DESIGN PRINCIPLE: Most important info (agent status) at top,
    less critical info (recent files) at bottom.
    """
    st.title("🤖 Agent Monitor - Overview")

    # WHY: Check API first - fail fast if it's down
    if not check_api_connection():
        st.error("⚠️ API server not running! Start it with: `python dashboard/api_server.py`")
        return

    # Auto-refresh toggle
    # WHY: Let users disable auto-refresh to read logs without interruption
    st.session_state.auto_refresh = st.checkbox(
        "🔄 Auto-refresh (every 2s)",
        value=st.session_state.auto_refresh,
        help="Disable to freeze the view while reading logs"
    )

    st.markdown("---")

    # Fetch agent status
    agents = get_agent_status()

    if not agents:
        st.warning("No agents found. Check API connection.")
        return

    # WHY: Show summary metrics for quick health check
    col1, col2, col3, col4 = st.columns(4)
    running = sum(1 for a in agents if a.get("is_running"))
    completed = sum(1 for a in agents if a.get("status") == "completed")
    failed = sum(1 for a in agents if a.get("status") == "failed")

    col1.metric("Total Agents", len(agents))
    col2.metric("Running", running)
    col3.metric("Completed", completed)
    col4.metric("Failed", failed)

    st.markdown("---")

    # Render agent cards
    st.subheader("📊 Agent Status")
    for agent in agents:
        render_agent_card(agent)

    # WHY: Auto-refresh using Streamlit's rerun mechanism
    if st.session_state.auto_refresh:
        time.sleep(POLL_INTERVAL)
        st.rerun()


def page_logs():
    """
    Logs page - View agent output.

    WHY: Separate page keeps overview clean, gives more space for logs.
    DESIGN: Split view (agent list + log viewer) is standard dev tool pattern.
    """
    st.title("📝 Agent Logs")

    if not check_api_connection():
        st.error("⚠️ API server not running!")
        return

    agents = get_agent_status()

    # WHY: Dropdown for agent selection - cleaner than tabs for 9+ agents
    agent_names = [a["agent_name"] for a in agents]
    selected = st.selectbox("Select Agent", agent_names)

    if selected:
        logs = get_agent_logs(selected, lines=200)

        # WHY: Tabs separate stdout/stderr - developers expect this separation
        tab1, tab2 = st.tabs(["📤 Output (stdout)", "⚠️ Errors (stderr)"])

        with tab1:
            stdout = logs.get("stdout", [])
            if stdout:
                # WHY: Code block preserves formatting and enables copy-paste
                st.code("\n".join(stdout), language="text")
            else:
                st.info("No output yet")

        with tab2:
            stderr = logs.get("stderr", [])
            if stderr:
                st.code("\n".join(stderr), language="text")
            else:
                st.success("No errors")

        # WHY: Auto-refresh for live tail-f experience
        if st.checkbox("🔄 Auto-refresh logs", value=True):
            time.sleep(2)
            st.rerun()


def page_files():
    """
    Agent-centric file browser with workflow visualization.

    WHY: Users want to understand the workflow process by seeing which agents produce which files.
    REASONING: 3-column layout shows (1) workflow timeline, (2) agent outputs, (3) file preview.
    This makes the idea-to-project pipeline visible and understandable.

    NEW FEATURES:
    - Workflow progress timeline showing completed stages
    - Agent-grouped file view (see what each agent produced)
    - Enhanced preview with syntax highlighting
    - Search and filter across all agent outputs
    """
    st.title("📁 Agent File Explorer")

    if not check_api_connection():
        st.error("⚠️ API server not running!")
        st.info("Start the API server: `python dashboard/api_server.py`")
        return

    # Search and filter controls
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search files", placeholder="Type to filter filenames...")
    with col_filter:
        agent_filter = st.selectbox(
            "Filter by Agent",
            ["All Agents", "RefinementAgent", "IterativeWorkshopAgent", "VerticalAgent",
             "StrategyAgent", "TechnicalArchitectAgent", "PlanningAgent",
             "DocumentationAgent", "ReportingAgent", "TrendResearchAgent"]
        )

    st.markdown("---")

    # 3-column layout: Timeline | Agent Outputs | File Preview
    col1, col2, col3 = st.columns([1, 1.5, 2])

    with col1:
        render_workflow_timeline()

    with col2:
        render_agent_outputs(search_query, agent_filter)

    with col3:
        render_file_preview_enhanced()


def render_workflow_timeline():
    """
    Show workflow progress as a vertical timeline.

    WHY: Users need to see which stages are complete and what's next.
    REASONING: Timeline view is intuitive for sequential processes.
    """
    st.subheader("🔄 Workflow Progress")

    try:
        response = requests.get(f"{API_URL}/api/workflow/status", timeout=5)
        if response.status_code != 200:
            st.error("Failed to load workflow status")
            return

        workflow_data = response.json().get("workflow", [])

        # Calculate overall progress
        total_stages = len(workflow_data)
        completed_stages = sum(1 for stage in workflow_data if stage.get("complete", False))
        progress_pct = (completed_stages / total_stages * 100) if total_stages > 0 else 0

        st.progress(progress_pct / 100, text=f"{completed_stages}/{total_stages} stages complete")
        st.caption(f"{progress_pct:.0f}% Complete")
        st.markdown("---")

        # Timeline
        for stage in workflow_data:
            is_complete = stage.get("complete", False)
            stage_name = stage.get("name", "Unknown")
            description = stage.get("description", "")
            outputs = stage.get("outputs", [])

            # Stage indicator
            if is_complete:
                icon = "✅"
                status_text = "Complete"
                status_color = "green"
            else:
                icon = "⏸️"
                status_text = "Pending"
                status_color = "gray"

            with st.expander(f"{icon} {stage_name}", expanded=False):
                st.caption(description)
                if outputs:
                    st.caption(f"📄 {len(outputs)} file(s)")
                    for output in outputs[:3]:  # Show first 3
                        st.caption(f"  • {Path(output).name}")
                    if len(outputs) > 3:
                        st.caption(f"  • ... and {len(outputs) - 3} more")
                else:
                    st.caption("_No outputs yet_")

    except Exception as e:
        st.error(f"Error loading workflow: {str(e)}")
        st.caption("Make sure API server is running")


def render_agent_outputs(search_query: str = "", agent_filter: str = "All Agents"):
    """
    Show files grouped by the agent that created them.

    WHY: Users want to see what each agent produces.
    REASONING: Agent-centric view makes it clear which agent does what.
    """
    st.subheader("🤖 Agent Outputs")

    try:
        response = requests.get(f"{API_URL}/api/files/by-agent", timeout=5)
        if response.status_code != 200:
            st.error("Failed to load agent files")
            return

        agent_files = response.json().get("agents", {})

        # Apply agent filter
        if agent_filter != "All Agents":
            agent_files = {agent_filter: agent_files.get(agent_filter, [])}

        # Count total files
        total_files = sum(len(files) for files in agent_files.values())
        if search_query:
            st.caption(f"🔍 Searching {total_files} files...")
        else:
            st.caption(f"📊 {total_files} total files")

        st.markdown("---")

        # Render each agent's files
        for agent_name, files in agent_files.items():
            if not files:
                continue  # Skip agents with no files

            # Apply search filter
            if search_query:
                files = [f for f in files if search_query.lower() in f["name"].lower()]

            if not files:
                continue  # Skip if search filtered everything out

            # Agent section
            agent_emoji = {
                "RefinementAgent": "✨",
                "IterativeWorkshopAgent": "🎯",
                "VerticalAgent": "📊",
                "StrategyAgent": "🎓",
                "TechnicalArchitectAgent": "🏗️",
                "PlanningAgent": "📝",
                "DocumentationAgent": "📚",
                "ReportingAgent": "📈",
                "TrendResearchAgent": "🔍",
                "Unknown": "❓"
            }.get(agent_name, "🤖")

            with st.expander(f"{agent_emoji} {agent_name} ({len(files)})", expanded=(agent_filter != "All Agents")):
                for file in files:
                    file_name = file["name"]
                    file_path = file["path"]
                    file_ext = file.get("extension", "")

                    # File type icon
                    ext_icon = {
                        ".md": "📄",
                        ".json": "📋",
                        ".yaml": "⚙️",
                        ".yml": "⚙️",
                        ".py": "🐍",
                        ".txt": "📝"
                    }.get(file_ext, "📄")

                    # File button
                    if st.button(f"{ext_icon} {file_name}", key=f"file_{file_path}", use_container_width=True):
                        st.session_state.selected_file = file_path
                        st.rerun()

                    # Show modification time
                    modified_time = datetime.fromtimestamp(file["modified"]).strftime("%Y-%m-%d %H:%M")
                    st.caption(f"  Modified: {modified_time}")

    except Exception as e:
        st.error(f"Error loading agent files: {str(e)}")


def render_file_preview_enhanced():
    """
    Enhanced file preview with syntax highlighting and metadata.

    WHY: Better reading experience, especially for code/JSON/YAML files.
    REASONING: Syntax highlighting makes content easier to understand.
    """
    st.subheader("📖 File Preview")

    if not st.session_state.selected_file:
        st.info("← Select a file to preview")
        st.markdown("""
        **How to use:**
        1. Check workflow progress in the timeline
        2. Browse agent outputs to see what each agent produced
        3. Click any file to preview/edit
        """)
        return

    file_path = st.session_state.selected_file
    st.caption(f"📄 `{file_path}`")

    file_data = read_file(file_path)

    if not file_data or "error" in file_data:
        st.error(f"Could not read file: {file_data.get('error', 'Unknown error')}")
        return

    content = file_data.get("content", "")
    file_ext = file_data.get("extension", "")
    file_size = file_data.get("size", 0)
    file_modified = file_data.get("modified", "")

    # File metadata
    col_meta1, col_meta2, col_meta3 = st.columns(3)
    with col_meta1:
        st.metric("Size", f"{file_size:,} bytes")
    with col_meta2:
        st.metric("Type", file_ext or "text")
    with col_meta3:
        st.metric("Modified", file_modified[:10] if file_modified else "Unknown")

    st.markdown("---")

    # Tabs for different views
    tab_preview, tab_edit = st.tabs(["👁️ Preview", "✏️ Edit"])

    with tab_preview:
        # Syntax-highlighted preview
        if file_ext in [".json", ".yaml", ".yml"]:
            # Pretty-print JSON/YAML
            try:
                if file_ext == ".json":
                    parsed = json.loads(content)
                    st.json(parsed)
                else:
                    st.code(content, language="yaml")
            except:
                st.code(content)
        elif file_ext == ".py":
            st.code(content, language="python")
        elif file_ext == ".md":
            st.markdown(content)
        else:
            st.text(content)

    with tab_edit:
        # Editable text area
        edited_content = st.text_area(
            "Edit Content",
            value=content,
            height=400,
            key="file_content_edit"
        )

        col_save, col_cancel = st.columns([1, 4])
        with col_save:
            if st.button("💾 Save", use_container_width=True):
                if write_file(file_path, edited_content):
                    st.success("✅ File saved!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Save failed")
        with col_cancel:
            if st.button("🔄 Reload", use_container_width=True):
                st.rerun()


def page_changelog():
    """
    Changelog viewer - displays project version history.

    WHY: Developers need to understand what changed and why
    REASONING: Changelog in dashboard = no context switching to find version info
    BENEFITS: See full project evolution, jump to specific versions, understand migrations
    """
    st.title("📋 Changelog")

    if not check_api_connection():
        st.error("⚠️ API server not running!")
        return

    # WHY: Read CHANGELOG.md from project root
    # REASONING: Single source of truth for version history
    changelog_path = "CHANGELOG.md"
    file_data = read_file(changelog_path)

    if file_data and "content" in file_data:
        content = file_data["content"]

        # WHY: Show metadata at top
        st.caption(f"📄 Last updated: {file_data['modified'][:19]} | Size: {file_data['size']} bytes")
        st.markdown("---")

        # WHY: Extract versions for quick navigation
        # REASONING: Long changelogs are hard to navigate - version menu helps
        import re
        version_pattern = r'^##\s+\[([^\]]+)\]'
        versions = re.findall(version_pattern, content, re.MULTILINE)

        if versions:
            st.sidebar.markdown("### 📌 Versions")
            selected_version = st.sidebar.radio(
                "Jump to version",
                ["All"] + versions,
                help="Quick navigation to specific version"
            )

            # Filter content if specific version selected
            if selected_version != "All":
                # Extract content for selected version
                # WHY: Focus on relevant section, not entire history
                version_section = re.search(
                    rf'(##\s+\[{re.escape(selected_version)}\].*?)(?=##\s+\[|\Z)',
                    content,
                    re.DOTALL
                )
                if version_section:
                    content = f"# Changelog\n\n{version_section.group(1)}"

        # WHY: Render as markdown for proper formatting
        # REASONING: Changelog uses markdown syntax (headers, lists, code blocks)
        st.markdown(content)

        # WHY: Auto-refresh option for active development
        if st.sidebar.checkbox("🔄 Auto-refresh changelog", value=False):
            time.sleep(5)  # Longer interval - changelog changes less frequently
            st.rerun()
    else:
        st.warning(f"📋 Changelog not available")
        st.info("""
        **How to create CHANGELOG.md:**

        The changelog file may have been moved or deleted. You can:

        1. **Restore from archive:**
           ```bash
           cp docs/archive/CHANGELOG.md ./CHANGELOG.md
           ```

        2. **Create a new one** in the project root with version history

        3. **Use automated generation:**
           ```bash
           git log --oneline > CHANGELOG.md
           ```
        """)

        # Show available documentation instead
        st.markdown("### 📚 Available Documentation")
        alt_docs = ["docs/system/change_log.md", "README.md", "docs/setup/QUICK_START.md"]

        for doc in alt_docs:
            doc_data = read_file(doc)
            if doc_data and "content" in doc_data:
                with st.expander(f"📄 {doc}"):
                    st.markdown(doc_data["content"][:1000] + "...")
                    if st.button(f"View full {doc}", key=doc):
                        st.markdown(doc_data["content"])


def page_graph():
    """
    Dependency graph visualization.

    WHY: Visual graph shows which agents block others - critical for debugging delays.
    REASONING: Text list of dependencies is hard to parse; graph is instant comprehension.
    """
    st.title("🔗 Agent Dependency Graph")

    st.info("🚧 Dependency graph visualization coming soon!")
    st.markdown("""
    **For now, here's the textual representation:**

    ```
    Level 0 (Parallel):
    ├─ StrategyAgent (no dependencies)
    ├─ RefinementAgent (no dependencies)
    └─ VerticalAgent (no dependencies)

    Level 1:
    ├─ TechnicalArchitectAgent (waits for StrategyAgent)
    └─ OpportunityRankingAgent (waits for VerticalAgent)

    Level 2:
    └─ PlanningAgent (waits for StrategyAgent + TechnicalArchitectAgent)

    Level 3:
    └─ DocumentationAgent (waits for PlanningAgent)

    Level 4:
    └─ ReportingAgent (waits for DocumentationAgent) [runs last]
    ```

    **WHY THIS MATTERS:**
    - Level 0 agents can run simultaneously (parallel execution in Phase 2)
    - If StrategyAgent fails, TechnicalArchitect and Planning can't run
    - Longest path (Strategy→Technical→Planning→Docs→Reporting) determines total time
    """)


# ============================================================================
# Page: Project Context
# ============================================================================

def page_project_context():
    """
    Project Context page for managing project status, milestones, and decisions.

    WHY: Users need a centralized place to track project progress, deadlines,
    action points, and decision rationale without searching through files.

    FEATURES:
    - View all projects with deadline status
    - Track milestones and action points
    - Record decision rationale
    - View recent activity timeline
    - Add notes (issues, successes, ideas)
    """
    st.title("📋 Project Context")

    # Check API connection
    if not check_api_connection():
        st.error("❌ API server is not running. Start it with: `python dashboard/api_server.py`")
        return

    # Fetch projects
    try:
        response = requests.get(f"{API_URL}/api/context/projects")
        if response.status_code == 503:
            st.warning("⚠️ Project context tracking is not available. Database may be unavailable.")
            st.info("The context tracking system extends `data/test_ideas.db` with project management tables.")
            return
        elif response.status_code != 200:
            st.error(f"Failed to fetch projects: {response.text}")
            return

        projects = response.json().get("projects", [])
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return

    # Tabs for different views
    tabs = st.tabs(["📊 Overview", "🎯 Milestones & Actions", "🧭 Decisions", "📝 Notes & Timeline", "🔄 Workflow Progress"])

    # ========================================================================
    # Tab 1: Overview - Project list and deadline status
    # ========================================================================
    with tabs[0]:
        st.subheader("Projects Overview")

        col1, col2 = st.columns([2, 1])

        with col1:
            if not projects:
                st.info("No projects yet. Create your first project below!")
            else:
                for project in projects:
                    with st.expander(f"📁 {project['name']} ({project['status'].upper()})"):
                        st.write(f"**Description:** {project.get('description', 'No description')}")
                        st.write(f"**Priority:** {project.get('priority', 'medium').upper()}")
                        st.write(f"**Progress:** {project.get('progress_percent', 0)}%")

                        # Deadline status
                        if project.get('target_date'):
                            try:
                                deadline_response = requests.get(f"{API_URL}/api/context/projects/{project['id']}/deadline")
                                if deadline_response.status_code == 200:
                                    deadline = deadline_response.json()

                                    if deadline['is_overdue']:
                                        st.error(f"🔴 OVERDUE by {abs(deadline['days_remaining'])} days")
                                    elif deadline['days_remaining'] <= 3:
                                        st.warning(f"🟡 Due in {deadline['days_remaining']} days")
                                    else:
                                        st.success(f"🟢 {deadline['days_remaining']} days remaining")
                            except:
                                pass
                        else:
                            st.info("No deadline set")

                        # Quick actions
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button(f"View Details", key=f"view_{project['id']}"):
                                st.session_state.selected_project = project['id']
                        with col_b:
                            new_status = st.selectbox(
                                "Change Status",
                                ["planning", "active", "paused", "completed", "cancelled"],
                                index=["planning", "active", "paused", "completed", "cancelled"].index(project['status']),
                                key=f"status_{project['id']}"
                            )
                            if st.button(f"Update", key=f"update_status_{project['id']}"):
                                try:
                                    update_response = requests.put(
                                        f"{API_URL}/api/context/projects/{project['id']}/status",
                                        params={"status": new_status}
                                    )
                                    if update_response.status_code == 200:
                                        st.success("Status updated!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update: {e}")
                        with col_c:
                            new_progress = st.number_input(
                                "Progress %",
                                0, 100,
                                project.get('progress_percent', 0),
                                key=f"progress_{project['id']}"
                            )
                            if st.button(f"Set", key=f"set_progress_{project['id']}"):
                                try:
                                    update_response = requests.put(
                                        f"{API_URL}/api/context/projects/{project['id']}/status",
                                        params={"status": project['status'], "progress_percent": new_progress}
                                    )
                                    if update_response.status_code == 200:
                                        st.success("Progress updated!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update: {e}")

        with col2:
            st.markdown("### Create New Project")
            with st.form("create_project"):
                name = st.text_input("Project Name*", placeholder="AI Dashboard MVP")
                description = st.text_area("Description", placeholder="Build a Streamlit dashboard for monitoring agents")
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=1)
                deadline = st.date_input("Deadline (optional)", value=None)
                tags = st.text_input("Tags (comma-separated)", placeholder="dashboard,ai,mvp")

                if st.form_submit_button("Create Project"):
                    if name:
                        try:
                            tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
                            deadline_str = deadline.isoformat() if deadline else None

                            create_response = requests.post(
                                f"{API_URL}/api/context/projects",
                                params={
                                    "name": name,
                                    "description": description,
                                    "priority": priority,
                                    "deadline": deadline_str,
                                    "tags": tags_list
                                }
                            )

                            if create_response.status_code == 200:
                                st.success(f"✅ Created project: {name}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Failed to create project: {create_response.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Please enter a project name")

    # ========================================================================
    # Tab 2: Milestones & Actions
    # ========================================================================
    with tabs[1]:
        st.subheader("Milestones & Action Points")

        if not projects:
            st.info("Create a project first to add milestones and actions.")
            return

        # Project selector
        selected_project = st.selectbox(
            "Select Project",
            projects,
            format_func=lambda p: p['name'],
            key="milestones_project"
        )

        if selected_project:
            project_id = selected_project['id']

            col1, col2 = st.columns(2)

            # Milestones column
            with col1:
                st.markdown("#### 🎯 Milestones")

                try:
                    milestones_response = requests.get(f"{API_URL}/api/context/projects/{project_id}/milestones")
                    if milestones_response.status_code == 200:
                        milestones = milestones_response.json().get("milestones", [])

                        if milestones:
                            for milestone in milestones:
                                status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}.get(milestone['status'], "")
                                st.write(f"{status_icon} **{milestone['name']}** ({milestone['status']})")
                                if milestone.get('description'):
                                    st.caption(milestone['description'])
                                if milestone.get('target_date'):
                                    st.caption(f"📅 Target: {milestone['target_date']}")
                                st.divider()
                        else:
                            st.info("No milestones yet")
                except Exception as e:
                    st.error(f"Failed to load milestones: {e}")

                # Add milestone form
                with st.expander("➕ Add Milestone"):
                    with st.form("add_milestone"):
                        m_name = st.text_input("Milestone Name*")
                        m_description = st.text_area("Description")
                        m_target = st.date_input("Target Date")
                        m_order = st.number_input("Order", 0, 100, 0)

                        if st.form_submit_button("Add Milestone"):
                            if m_name:
                                try:
                                    add_response = requests.post(
                                        f"{API_URL}/api/context/projects/{project_id}/milestones",
                                        params={
                                            "name": m_name,
                                            "description": m_description,
                                            "target_date": m_target.isoformat() if m_target else None,
                                            "order": m_order
                                        }
                                    )
                                    if add_response.status_code == 200:
                                        st.success("Milestone added!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {add_response.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.warning("Please enter milestone name")

            # Action points column
            with col2:
                st.markdown("#### ✅ Action Points")

                try:
                    actions_response = requests.get(f"{API_URL}/api/context/projects/{project_id}/actions")
                    if actions_response.status_code == 200:
                        actions = actions_response.json().get("actions", [])

                        # Filter controls
                        filter_status = st.selectbox(
                            "Filter by status",
                            ["all", "todo", "in_progress", "done", "blocked"],
                            key="action_filter"
                        )

                        filtered_actions = actions if filter_status == "all" else [a for a in actions if a['status'] == filter_status]

                        if filtered_actions:
                            for action in filtered_actions:
                                priority_icon = {"low": "🔵", "medium": "🟡", "high": "🟠", "urgent": "🔴"}.get(action['priority'], "")
                                status_icon = {"todo": "⏸️", "in_progress": "▶️", "done": "✅", "blocked": "🚫", "cancelled": "❌"}.get(action['status'], "")

                                st.write(f"{priority_icon} {status_icon} **{action['title']}**")
                                if action.get('description'):
                                    st.caption(action['description'])
                                if action.get('due_date'):
                                    st.caption(f"📅 Due: {action['due_date']}")

                                # Status update
                                new_action_status = st.selectbox(
                                    "Status",
                                    ["todo", "in_progress", "done", "blocked", "cancelled"],
                                    index=["todo", "in_progress", "done", "blocked", "cancelled"].index(action['status']),
                                    key=f"action_status_{action['id']}"
                                )
                                if st.button(f"Update Status", key=f"update_action_{action['id']}"):
                                    try:
                                        update_response = requests.put(
                                            f"{API_URL}/api/context/actions/{action['id']}/status",
                                            params={"status": new_action_status}
                                        )
                                        if update_response.status_code == 200:
                                            st.success("Updated!")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")

                                st.divider()
                        else:
                            st.info("No action points yet")
                except Exception as e:
                    st.error(f"Failed to load actions: {e}")

                # Add action form
                with st.expander("➕ Add Action Point"):
                    with st.form("add_action"):
                        a_title = st.text_input("Action Title*")
                        a_description = st.text_area("Description")
                        a_priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=1)
                        a_due = st.date_input("Due Date")

                        if st.form_submit_button("Add Action"):
                            if a_title:
                                try:
                                    add_response = requests.post(
                                        f"{API_URL}/api/context/projects/{project_id}/actions",
                                        params={
                                            "title": a_title,
                                            "description": a_description,
                                            "priority": a_priority,
                                            "due_date": a_due.isoformat() if a_due else None
                                        }
                                    )
                                    if add_response.status_code == 200:
                                        st.success("Action added!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {add_response.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.warning("Please enter action title")

    # ========================================================================
    # Tab 3: Decisions
    # ========================================================================
    with tabs[2]:
        st.subheader("🧭 Decision Rationale")

        if not projects:
            st.info("Create a project first to record decisions.")
            return

        # Project selector
        selected_project = st.selectbox(
            "Select Project",
            projects,
            format_func=lambda p: p['name'],
            key="decisions_project"
        )

        if selected_project:
            project_id = selected_project['id']

            try:
                decisions_response = requests.get(f"{API_URL}/api/context/projects/{project_id}/decisions")
                if decisions_response.status_code == 200:
                    decisions = decisions_response.json().get("decisions", [])

                    if decisions:
                        for decision in decisions:
                            with st.expander(f"📌 {decision['decision']} ({decision['created_at'][:10]})"):
                                st.markdown(f"**Rationale:** {decision['rationale']}")

                                if decision.get('alternatives'):
                                    try:
                                        alternatives = json.loads(decision['alternatives'])
                                        st.markdown(f"**Alternatives Considered:** {', '.join(alternatives)}")
                                    except:
                                        pass

                                if decision.get('context'):
                                    st.markdown(f"**Context:** {decision['context']}")

                                if decision.get('agent_name'):
                                    st.caption(f"🤖 Decided by: {decision['agent_name']}")

                                if decision.get('confidence'):
                                    st.progress(decision['confidence'], text=f"Confidence: {decision['confidence']:.0%}")
                    else:
                        st.info("No decisions recorded yet. Agents automatically record their decisions during execution.")
            except Exception as e:
                st.error(f"Failed to load decisions: {e}")

    # ========================================================================
    # Tab 4: Notes & Timeline
    # ========================================================================
    with tabs[3]:
        st.subheader("📝 Notes & Activity Timeline")

        if not projects:
            st.info("Create a project first to add notes.")
            return

        # Project selector
        selected_project = st.selectbox(
            "Select Project",
            projects,
            format_func=lambda p: p['name'],
            key="notes_project"
        )

        if selected_project:
            project_id = selected_project['id']

            col1, col2 = st.columns([2, 1])

            # Timeline column
            with col1:
                st.markdown("#### 📅 Recent Activity")

                days = st.slider("Days to show", 1, 30, 7)

                try:
                    timeline_response = requests.get(
                        f"{API_URL}/api/context/projects/{project_id}/timeline",
                        params={"days": days, "limit": 50}
                    )
                    if timeline_response.status_code == 200:
                        activities = timeline_response.json().get("activity", [])

                        if activities:
                            for activity in activities:
                                activity_icon = {
                                    "agent_run": "🤖",
                                    "milestone_completed": "🎯",
                                    "action_completed": "✅",
                                    "status_change": "🔄",
                                    "note": "📝",
                                    "decision": "🧭"
                                }.get(activity['activity_type'], "📍")

                                timestamp = datetime.fromisoformat(activity['created_at']).strftime("%Y-%m-%d %H:%M")
                                st.write(f"{activity_icon} **{timestamp}** - {activity['activity']}")

                                if activity.get('agent_name'):
                                    st.caption(f"   Agent: {activity['agent_name']}")
                        else:
                            st.info("No activity in the selected timeframe")
                except Exception as e:
                    st.error(f"Failed to load timeline: {e}")

            # Notes column
            with col2:
                st.markdown("#### 📝 Notes")

                # Add note form
                with st.expander("➕ Add Note"):
                    with st.form("add_note"):
                        note_type = st.selectbox("Type", ["issue", "success", "idea", "learning", "general"])
                        note_title = st.text_input("Title*")
                        note_content = st.text_area("Content*")

                        if st.form_submit_button("Add Note"):
                            if note_title and note_content:
                                try:
                                    add_response = requests.post(
                                        f"{API_URL}/api/context/projects/{project_id}/notes",
                                        params={
                                            "note_type": note_type,
                                            "title": note_title,
                                            "content": note_content
                                        }
                                    )
                                    if add_response.status_code == 200:
                                        st.success("Note added!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {add_response.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.warning("Please fill in title and content")

                # Display notes
                try:
                    notes_response = requests.get(f"{API_URL}/api/context/projects/{project_id}/notes")
                    if notes_response.status_code == 200:
                        notes = notes_response.json().get("notes", [])

                        note_type_filter = st.selectbox(
                            "Filter by type",
                            ["all", "issue", "success", "idea", "learning", "general"],
                            key="note_filter"
                        )

                        filtered_notes = notes if note_type_filter == "all" else [n for n in notes if n['note_type'] == note_type_filter]

                        if filtered_notes:
                            for note in filtered_notes:
                                note_icon = {
                                    "issue": "🐛",
                                    "success": "🎉",
                                    "idea": "💡",
                                    "learning": "📚",
                                    "general": "📝"
                                }.get(note['note_type'], "📝")

                                st.markdown(f"{note_icon} **{note['title']}**")
                                st.caption(note['content'])
                                st.caption(f"Added: {note['created_at'][:10]}")
                                st.divider()
                        else:
                            st.info("No notes yet")
                except Exception as e:
                    st.error(f"Failed to load notes: {e}")

    # ========================================================================
    # Tab 5: Workflow Progress - Conversational workflow tracking
    # ========================================================================
    with tabs[4]:
        st.subheader("🔄 Workflow Progress")

        st.markdown("""
        Track progress through the conversational idea validation workflow.
        See which steps are complete, current data, and confidence scores.
        """)

        if not selected_project:
            st.info("👈 Select a project to view workflow progress")
            return

        project_id = selected_project['id']

        try:
            # Try to load workflow state from project metadata
            project_response = requests.get(f"{API_URL}/api/context/projects/{project_id}")
            if project_response.status_code != 200:
                st.error("Failed to load project data")
                return

            project_data = project_response.json()
            metadata = project_data.get('metadata', {})
            workflow_state = metadata.get('workflow_state')

            if not workflow_state:
                st.info("No workflow progress yet. Start the interactive workflow:")
                st.code(f"python cli/interactive_workflow.py --resume {project_id}")
                return

            # Extract workflow data
            current_step = workflow_state.get('current_step')
            completed_steps = workflow_state.get('completed_steps', [])
            collected_data = workflow_state.get('collected_data', {})
            step_scores = workflow_state.get('step_scores', {})
            started_at = workflow_state.get('started_at')
            updated_at = workflow_state.get('updated_at')

            # Progress bar
            steps = ["step_1_refinement", "step_2_pain_discovery", "step_3_market_sizing", "step_4_competitive_landscape"]
            completed_count = len(completed_steps)
            total_steps = len(steps)
            progress_pct = (completed_count / total_steps) if total_steps > 0 else 0

            st.progress(progress_pct)
            st.caption(f"Progress: {completed_count}/{total_steps} steps complete ({progress_pct*100:.0f}%)")

            if started_at:
                st.caption(f"Started: {started_at}")
            if updated_at:
                st.caption(f"Last updated: {updated_at}")

            st.markdown("---")

            # Step-by-step status
            step_names = {
                "step_1_refinement": "💬 Step 1: Idea Refinement",
                "step_2_pain_discovery": "🔍 Step 2: Pain Discovery",
                "step_3_market_sizing": "📊 Step 3: Market Sizing",
                "step_4_competitive_landscape": "⚔️ Step 4: Competitive Analysis"
            }

            for step_key in steps:
                step_name = step_names.get(step_key, step_key)

                # Determine status
                if step_key in completed_steps:
                    status_icon = "✅"
                    status_text = "Completed"
                    status_color = "green"
                elif step_key == current_step:
                    status_icon = "🔄"
                    status_text = "In Progress"
                    status_color = "orange"
                else:
                    status_icon = "⏳"
                    status_text = "Pending"
                    status_color = "gray"

                # Show step
                with st.expander(f"{status_icon} {step_name} - {status_text}"):
                    if step_key in step_scores:
                        score_data = step_scores[step_key]
                        score = score_data.get('score', 0)
                        completed_at = score_data.get('completed_at', '')
                        summary = score_data.get('summary', '')

                        # Confidence bar
                        filled = int(score * 10)
                        empty = 10 - filled
                        confidence_bar = '█' * filled + '░' * empty

                        st.markdown(f"**Confidence:** [{confidence_bar}] {score*100:.0f}%")

                        if completed_at:
                            st.caption(f"Completed: {completed_at}")

                        if summary:
                            st.markdown("**Summary:**")
                            st.caption(summary)

                    elif step_key == current_step:
                        st.info("Currently working on this step...")

                    else:
                        st.caption("Not started yet")

            st.markdown("---")

            # Collected data
            if collected_data:
                st.markdown("### 📋 Collected Data")

                for field_name, value in collected_data.items():
                    st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
                    st.write(value)
                    st.markdown("")
            else:
                st.info("No data collected yet")

            # Actions
            st.markdown("---")
            st.markdown("### 🎯 Actions")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Continue Workflow:**")
                st.code(f"python cli/interactive_workflow.py --resume {project_id}")

            with col2:
                st.markdown("**Run Research:**")
                st.code(f"python cli/manage.py run --project {project_id}")

        except Exception as e:
            st.error(f"Error loading workflow progress: {e}")
            import traceback
            st.code(traceback.format_exc())


# ============================================================================
# Main App
# ============================================================================

def main():
    """
    Main app entry point.

    WHY: Sidebar navigation is Streamlit standard for multi-page apps.
    DESIGN: Order pages by usage frequency (Overview most common, Changelog/Graph least).

    ENHANCEMENTS:
    - Added Changelog page for version history
    - Improved navigation with clear page icons
    """
    st.sidebar.title("🤖 Agent Monitor")
    st.sidebar.markdown("---")

    # Page navigation
    # WHY: Group related pages together
    # REASONING: Overview/Logs/Files are operational tools, Project Context for project management, Changelog/Graph are reference
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Overview", "📋 Project Context", "📝 Logs", "📁 Files", "📖 Changelog", "🔗 Dependency Graph"],
        help="Select a page"
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("💡 **Tip:** Enable auto-refresh on Overview to see live updates")
    st.sidebar.caption("📋 **Project Context:** Track status, milestones, decisions")
    st.sidebar.caption("⚙️ **API:** http://localhost:8000")

    # WHY: Route to appropriate page function
    if page == "🏠 Overview":
        page_overview()
    elif page == "📋 Project Context":
        page_project_context()
    elif page == "📝 Logs":
        page_logs()
    elif page == "📁 Files":
        page_files()
    elif page == "📖 Changelog":
        page_changelog()
    elif page == "🔗 Dependency Graph":
        page_graph()


if __name__ == "__main__":
    main()
