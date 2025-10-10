# ==============================================
# file: /ManagementTeam/dashboards/planner_dashboard.py
# ==============================================
"""
Planner Agent Dashboard with Status + Timeline
---------------------------------------------
Enhanced Streamlit dashboard providing real-time visibility into
Planner Agent execution, progress tracking, duration metrics, and file inspection.

Run with:
    streamlit run /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/dashboards/planner_dashboard.py
"""

import streamlit as st
from pathlib import Path
import time
import json
import re
import pandas as pd
from datetime import datetime

LOG_PATH = Path("/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/logs/planner_trace.log")
PROJECTS_DIR = Path("/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/projects")

st.set_page_config(page_title="Planner Agent Dashboard", layout="wide")
st.title("🧭 Planner Agent Oversight Dashboard")
st.markdown("*Real-time monitoring with step tracking and timeline visualization*")

# Sidebar controls
st.sidebar.header("⚙️ Control Panel")
refresh_rate = st.sidebar.slider("Auto-refresh interval (seconds)", 2, 30, 5)
selected_project = st.sidebar.text_input("Project name", "management-layer")
show_logs = st.sidebar.checkbox("Show live logs", value=True)
show_outputs = st.sidebar.checkbox("Show generated files", value=True)
show_timeline = st.sidebar.checkbox("Show execution timeline", value=True)

st.sidebar.markdown("---")
st.sidebar.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def read_last_lines(path: Path, num_lines: int = 200) -> str:
    """Read the last N lines from the log file."""
    if not path.exists():
        return "No log file found. Run the Planner Agent to start logging."
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()[-num_lines:]
        return "".join(lines)
    except Exception as e:
        return f"Error reading log: {e}"


def list_project_files(project: str) -> list[Path]:
    """List all files in a project's planning directory."""
    base = PROJECTS_DIR / project / "planning"
    if not base.exists():
        return []
    return sorted(base.glob("*"))


def read_file(path: Path) -> str:
    """Read a file safely."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading {path.name}: {e}"


def parse_step_status(log_text: str) -> dict:
    """
    Detect step completion and error states from log text.
    Returns a dictionary mapping step names to status indicators.
    """
    steps = {
        "STEP 1": "Parsing",
        "STEP 2": "Gap Analysis",
        "STEP 3": "Templates",
        "STEP 4": "Prepare Data",
        "STEP 5": "YAML Plan",
        "STEP 6": "Roadmap",
        "STEP 7": "Scaffold",
        "STEP 8": "Reflection",
        "STEP 9": "Summary",
    }
    
    # Initialize all steps as pending
    status_map = {v: "⚪ Pending" for v in steps.values()}

    # Mark steps as active if mentioned in logs
    for line in log_text.splitlines():
        for key, step_name in steps.items():
            if key in line:
                status_map[step_name] = "🟡 Active"
        
        # Mark as complete if success indicators found
        if any(word in line.lower() for word in ["created successfully", "written", "completed", "✓", "✅"]):
            for step_name in steps.values():
                if step_name.lower() in line.lower():
                    status_map[step_name] = "🟢 Complete"
        
        # Mark as error if failure indicators found
        if any(word in line.lower() for word in ["error", "failed", "❌"]):
            for step_name in steps.values():
                if step_name.lower() in line.lower():
                    status_map[step_name] = "🔴 Error"
    
    return status_map


def parse_timeline(log_text: str) -> pd.DataFrame:
    """
    Parse timestamps and steps from logs to show step durations.
    Returns a pandas DataFrame with timestamp, step, and duration information.
    """
    # Match lines with timestamps and STEP markers
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(STEP \d+:.*?)$", re.MULTILINE)
    entries = pattern.findall(log_text)
    
    if not entries:
        return pd.DataFrame()
    
    records = []
    for ts, step in entries:
        try:
            ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            records.append({"timestamp": ts_dt, "step": step})
        except ValueError:
            continue

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df.sort_values("timestamp", inplace=True)
    
    # Calculate duration between steps
    df["duration"] = df["timestamp"].diff().dt.total_seconds().fillna(0)
    df["duration"] = df["duration"].apply(lambda x: round(x, 2))
    
    return df


def calculate_metrics(log_text: str, files: list[Path]) -> dict:
    """Calculate summary metrics from logs and generated files."""
    metrics = {
        "total_steps": 9,
        "completed_steps": 0,
        "files_generated": len(files),
        "warnings": 0,
        "errors": 0,
        "total_duration": 0
    }
    
    # Count completed steps
    step_status = parse_step_status(log_text)
    metrics["completed_steps"] = sum(1 for status in step_status.values() if "🟢" in status)
    
    # Count warnings and errors
    for line in log_text.splitlines():
        if "[WARNING]" in line or "⚠️" in line:
            metrics["warnings"] += 1
        if "[ERROR]" in line or "🔴" in line or "❌" in line:
            metrics["errors"] += 1
    
    # Calculate total duration
    timeline_df = parse_timeline(log_text)
    if not timeline_df.empty:
        metrics["total_duration"] = round(timeline_df["duration"].sum(), 2)
    
    return metrics


# --------------------------------------------------
# Main display loop
# --------------------------------------------------
while True:
    # Read and parse logs
    log_text = read_last_lines(LOG_PATH, 200)
    step_status = parse_step_status(log_text)
    timeline_df = parse_timeline(log_text)
    files = list_project_files(selected_project)
    metrics = calculate_metrics(log_text, files)
    
    # Summary Metrics Row
    st.subheader("📊 Summary Metrics")
    metric_cols = st.columns(6)
    
    with metric_cols[0]:
        st.metric("Steps Complete", f"{metrics['completed_steps']}/{metrics['total_steps']}")
    with metric_cols[1]:
        st.metric("Files Generated", metrics['files_generated'])
    with metric_cols[2]:
        st.metric("Total Duration", f"{metrics['total_duration']}s")
    with metric_cols[3]:
        st.metric("Warnings", metrics['warnings'], 
                 delta="⚠️" if metrics['warnings'] > 0 else None)
    with metric_cols[4]:
        st.metric("Errors", metrics['errors'],
                 delta="🔴" if metrics['errors'] > 0 else None,
                 delta_color="inverse" if metrics['errors'] > 0 else "normal")
    with metric_cols[5]:
        progress_pct = int((metrics['completed_steps'] / metrics['total_steps']) * 100)
        st.metric("Progress", f"{progress_pct}%")
    
    st.markdown("---")
    
    # Progress Overview - Step Status
    st.subheader("⚙️ Planner Agent Progress")
    st.caption("Real-time step execution status")
    
    # Display steps in a grid
    step_cols = st.columns(len(step_status))
    for i, (step, status) in enumerate(step_status.items()):
        with step_cols[i]:
            # Determine color based on status
            if "🟢" in status:
                color = "#28a745"  # Green
            elif "🟡" in status:
                color = "#ffc107"  # Yellow
            elif "🔴" in status:
                color = "#dc3545"  # Red
            else:
                color = "#6c757d"  # Gray
            
            st.markdown(
                f"""
                <div style='text-align:center; padding:10px; border-radius:5px; background-color:{color}22;'>
                    <b>{step}</b><br>
                    <span style='color:{color}; font-size:24px;'>{status}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown("---")
    
    # Timeline Visualization
    if show_timeline and not timeline_df.empty:
        st.subheader("⏱️ Execution Timeline")
        st.caption("Step-by-step execution duration")
        
        # Create clean step labels
        timeline_df["step_label"] = timeline_df["step"].apply(lambda s: s.split(":")[1].strip() if ":" in s else s)
        
        # Create bar chart
        chart_data = timeline_df[["step_label", "duration"]].copy()
        chart_data = chart_data[chart_data["duration"] > 0]  # Filter out zero durations
        
        if not chart_data.empty:
            chart_data.set_index("step_label", inplace=True)
            st.bar_chart(chart_data["duration"])
            
            # Show detailed table
            with st.expander("📋 Detailed Timeline"):
                display_df = timeline_df[["step", "timestamp", "duration"]].copy()
                display_df["timestamp"] = display_df["timestamp"].dt.strftime("%H:%M:%S")
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("Execution timeline will appear as steps complete...")
    
    st.markdown("---")
    
    # Logs Section
    if show_logs:
        st.subheader("📜 Live Planner Agent Logs")
        st.caption("Real-time log output from the Planner Agent")
        
        # Color-code log levels
        log_display = log_text
        st.text_area("Log Output", log_display, height=300, key="log_display")
        
        # Download logs button
        if LOG_PATH.exists():
            col1, col2 = st.columns([3, 1])
            with col2:
                st.download_button(
                    label="📥 Download Logs",
                    data=LOG_PATH.read_text(encoding="utf-8"),
                    file_name=f"planner_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                    mime="text/plain"
                )
    
    st.markdown("---")
    
    # Outputs Section
    if show_outputs:
        st.subheader(f"📁 Generated Files: **{selected_project}**")
        st.caption(f"Project artifacts in /projects/{selected_project}/planning/")
        
        if files:
            # Create tabs for each file
            file_tabs = st.tabs([f.name for f in files])
            
            for tab, file_path in zip(file_tabs, files):
                with tab:
                    content = read_file(file_path)
                    
                    # Determine language for syntax highlighting
                    if file_path.suffix == ".yaml":
                        language = "yaml"
                    elif file_path.suffix == ".json":
                        language = "json"
                    elif file_path.suffix == ".md":
                        language = "markdown"
                    else:
                        language = "text"
                    
                    st.code(content, language=language)
                    
                    # File info and download
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.caption(f"Size: {file_path.stat().st_size} bytes | Modified: {datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
                    with col3:
                        st.download_button(
                            label="📥 Download",
                            data=content,
                            file_name=file_path.name,
                            mime="text/plain",
                            key=f"download_{file_path.name}"
                        )
        else:
            st.info(f"No files found for project '{selected_project}'. Run the Planner Agent to generate artifacts.")
            st.code(
                f'python scripts/run_planner.py "{selected_project}" "Your project description"',
                language="bash"
            )
    
    # Footer
    st.markdown("---")
    st.caption("🤖 AI Management Layer System | Planner Agent Dashboard v1.1")
    
    # Auto-refresh controls
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh Now"):
            st.rerun()
    
    # Wait and rerun
    st.sidebar.write(f"⏳ Auto-refresh in {refresh_rate} seconds...")
    time.sleep(refresh_rate)
    st.rerun()
