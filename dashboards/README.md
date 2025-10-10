# 🧭 Planner Agent Dashboard

## Overview

The **Planner Agent Dashboard** provides real-time visibility into the AI Management Layer's planning workflow. It allows you to monitor agent execution, review logs, inspect generated files, and track project metrics.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
streamlit run dashboards/planner_dashboard.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

---

## 📊 Features

### Real-Time Log Monitoring

- **Live Log Streaming**: View the last 60 lines of planner agent logs
- **Log Statistics**: Track INFO, WARNING, and ERROR counts
- **Download Logs**: Export full log files for offline analysis

### Project Metrics

- **Files Generated**: Count of artifacts created by the Planner Agent
- **Gaps Detected**: Number of information gaps identified
- **Last Modified**: Timestamp of most recent project activity
- **Status Indicators**: Visual feedback on project readiness

### Generated File Inspection

- **Tabbed File Viewer**: Browse all generated files (YAML, JSON, Markdown)
- **Syntax Highlighting**: Language-specific formatting
- **Download Files**: Export individual project artifacts
- **Multi-Project Support**: Switch between different projects

### Auto-Refresh

- **Configurable Refresh Rate**: 2-30 second intervals
- **Manual Refresh**: On-demand update button
- **Live Status**: Real-time activity monitoring

---

## 🎛️ Control Panel

### Sidebar Controls

| Control | Description | Default |
|---------|-------------|---------|
| **Auto-refresh interval** | Time between automatic updates | 5 seconds |
| **Select Project** | Choose project to monitor | First available |
| **Show live logs** | Toggle log display | ON |
| **Show generated files** | Toggle file viewer | ON |
| **Show metrics** | Toggle metrics panel | ON |

---

## 📁 Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  🧭 Planner Agent Oversight Dashboard                   │
├─────────────────────────────────┬───────────────────────┤
│ 📜 Live Planner Agent Logs      │ 📊 Project Metrics    │
│                                  │                       │
│ [Log Statistics Bar]             │ Files Generated: 4    │
│                                  │ Gaps Detected: 2      │
│ [Log Output Area]                │ Last Modified: ...    │
│                                  │                       │
│ [Download Full Log Button]       │ Status: ⚠️            │
├─────────────────────────────────┴───────────────────────┤
│ 📁 Generated Files                                       │
│                                                          │
│ [File Tabs: project_plan.yaml | roadmap.md | ...]       │
│                                                          │
│ [File Content with Syntax Highlighting]                 │
│                                                          │
│ [Download Button]                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Use Cases

### 1. Monitor Planner Agent Execution

Run the dashboard while executing the Planner Agent:

```bash
# Terminal 1: Run the dashboard
streamlit run dashboards/planner_dashboard.py

# Terminal 2: Execute the Planner Agent
python scripts/run_planner.py "new-project" "Build a trading bot"
```

Watch real-time logs and see files appear as they're generated.

### 2. Review Completed Projects

- Select a project from the dropdown
- Review all generated artifacts
- Check for information gaps
- Download files for external processing

### 3. Debug Issues

- Monitor log output for errors
- Track WARNING messages
- Identify where the agent workflow failed
- Export logs for detailed analysis

### 4. Track Multiple Projects

- Switch between projects using the sidebar
- Compare metrics across different projects
- Monitor project evolution over time

---

## 📝 Log Format

The dashboard reads logs from:
```
/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/logs/planner_trace.log
```

Log format:
```
YYYY-MM-DD HH:MM:SS,mmm [LEVEL] message
```

Example:
```
2025-10-10 14:23:45,123 [INFO] 🚀 Initializing Planner Agent for project: trading-bot
2025-10-10 14:23:45,456 [INFO] 🔍 STEP 1: Parsing user description.
2025-10-10 14:23:45,789 [WARNING] ⚠️  Found 2 information gaps: ['milestones', 'stakeholders']
```

---

## 🎨 Color Coding

- **🟢 Green**: Success messages, completed steps
- **🟡 Yellow**: Warnings, information gaps
- **🔴 Red**: Errors, failed operations
- **🔵 Blue**: Informational messages

---

## 🛠️ Configuration

### Customize Refresh Rate

Adjust in the sidebar or modify the default in `planner_dashboard.py`:

```python
refresh_rate = st.sidebar.slider("Auto-refresh interval (seconds)", 2, 30, 5)
                                                                        # ↑ Default
```

### Change Log Display Lines

Modify the `num_lines` parameter:

```python
log_text = read_last_lines(LOG_PATH, 60)  # Display last 60 lines
                                          # Increase for more history
```

### Customize Paths

Update paths at the top of `planner_dashboard.py`:

```python
LOG_PATH = Path("/path/to/your/logs/planner_trace.log")
PROJECTS_DIR = Path("/path/to/your/projects")
```

---

## 🚨 Troubleshooting

### Dashboard won't start

```bash
# Ensure Streamlit is installed
pip install streamlit

# Check Python version (3.8+ required)
python --version
```

### No logs appearing

```bash
# Verify log file exists
ls -la /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/logs/

# Run Planner Agent to generate logs
python scripts/run_planner.py "test-project" "Test description"
```

### Projects not showing

```bash
# Check projects directory
ls -la /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/projects/

# Create a test project
python src/agents/planner_agent.py
```

### Dashboard performance issues

- Increase refresh interval (10+ seconds)
- Reduce log display lines
- Close unnecessary browser tabs

---

## 🔗 Integration

### With Planner Agent

The dashboard automatically reads:
- Logs from `src/utils/log_utils.py`
- Project files from `projects/<project_name>/planning/`
- Summary reports from `summary_report.json`

### With Other Tools

Export data for external analysis:
- Download logs → Import into log analyzers
- Download JSON → Process with custom scripts
- Download YAML → Validate with external tools

---

## 📚 Related Documentation

- **Planner Agent Spec**: `docs/system/planner_agent_spec.md`
- **Configuration Guide**: `config/global.yaml`
- **Logging Configuration**: `config/logging.yaml`
- **Project Structure**: `docs/system/file_structure.md`

---

## 🎯 Future Enhancements

- [ ] Add historical trend graphs
- [ ] Export metrics to CSV
- [ ] Real-time notifications for errors
- [ ] Multi-agent dashboard (expand to other agents)
- [ ] Project comparison view
- [ ] Custom alert thresholds

---

**Version**: 1.0  
**Last Updated**: 2025-10-10  
**Maintainer**: Rob Freyne

