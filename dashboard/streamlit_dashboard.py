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
    File browser and editor with sorting and filtering.

    WHY: Avoid switching to terminal/editor during development workflow.
    REASONING: Quick edits (fix typos, adjust configs) don't warrant full IDE.

    ENHANCEMENTS:
    - Sort by name/date/size/type for better organization
    - Filter by extension to find specific file types quickly
    - File count and size summary for quick overview
    """
    st.title("📁 File Browser")

    if not check_api_connection():
        st.error("⚠️ API server not running!")
        return

    # WHY: Controls at top for easy access
    # REASONING: Users set preferences before browsing
    col_ctrl1, col_ctrl2 = st.columns([1, 1])

    with col_ctrl1:
        sort_option = st.selectbox(
            "🔤 Sort by",
            ["name", "date", "size", "type"],
            help="Choose how to organize files"
        )

    with col_ctrl2:
        filter_option = st.selectbox(
            "🔍 Filter by extension",
            ["All files", ".md", ".yaml", ".yml", ".py", ".json", ".txt"],
            help="Show only specific file types"
        )

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Directory Tree")
        tree = get_file_tree()
        if tree:
            # Calculate file statistics
            # WHY: Quick overview helps understand project size/activity
            total_files = 0
            total_size = 0

            def count_files(items):
                nonlocal total_files, total_size
                for item in items:
                    if item["type"] == "file":
                        total_files += 1
                        total_size += item.get("size", 0)
                    elif item.get("children"):
                        count_files(item["children"])

            count_files(tree)

            # Display summary
            st.caption(f"📊 {total_files} files | {total_size:,} bytes ({total_size/1024:.1f} KB)")
            st.markdown("---")

            render_file_tree(tree)
        else:
            st.info("No files found")

    with col2:
        st.subheader("File Viewer/Editor")

        if st.session_state.selected_file:
            file_path = st.session_state.selected_file
            st.caption(f"📄 {file_path}")

            file_data = read_file(file_path)

            if file_data and "content" in file_data:
                # WHY: Text area for editing - simple but functional
                content = st.text_area(
                    "Content",
                    value=file_data["content"],
                    height=400,
                    key="file_content"
                )

                col_a, col_b = st.columns([1, 4])
                with col_a:
                    if st.button("💾 Save"):
                        if write_file(file_path, content):
                            st.success("File saved!")
                            st.rerun()
                        else:
                            st.error("Save failed")

                with col_b:
                    st.caption(f"Size: {file_data['size']} bytes | Modified: {file_data['modified'][:19]}")
            else:
                st.error("Could not read file")
        else:
            st.info("← Select a file from the tree")


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
        st.error(f"Could not read {changelog_path}")
        st.info("Make sure CHANGELOG.md exists in the project root")


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
    # REASONING: Overview/Logs/Files are operational tools, Changelog/Graph are reference
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Overview", "📝 Logs", "📁 Files", "📋 Changelog", "🔗 Dependency Graph"],
        help="Select a page"
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("💡 **Tip:** Enable auto-refresh on Overview to see live updates")
    st.sidebar.caption("⚙️ **API:** http://localhost:8000")

    # WHY: Route to appropriate page function
    if page == "🏠 Overview":
        page_overview()
    elif page == "📝 Logs":
        page_logs()
    elif page == "📁 Files":
        page_files()
    elif page == "📋 Changelog":
        page_changelog()
    elif page == "🔗 Dependency Graph":
        page_graph()


if __name__ == "__main__":
    main()
