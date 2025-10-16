#!/bin/bash
# stop_dashboard.sh
# Safely stops all dashboard processes
#
# PURPOSE:
# Kills API server and Streamlit processes if startup script didn't clean up properly
#
# USAGE:
#   ./dashboard/stop_dashboard.sh
#
# WHY THIS EXISTS:
# - If you killed terminal instead of pressing Ctrl+C, processes may still run
# - Useful if API port is stuck or you want to force stop
# - Safer than manually finding and killing PIDs

echo "🛑 Stopping Agent Monitoring Dashboard..."
echo ""

# Kill API server (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔴 Killing API server (port 8000)..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    echo "✅ API server stopped"
else
    echo "⚪ API server not running"
fi

# Kill Streamlit (port 8501)
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔴 Killing Streamlit dashboard (port 8501)..."
    lsof -ti:8501 | xargs kill -9 2>/dev/null || true
    echo "✅ Streamlit stopped"
else
    echo "⚪ Streamlit not running"
fi

# Clean up PID file
if [ -f /tmp/dashboard_api.pid ]; then
    rm /tmp/dashboard_api.pid
    echo "✅ Cleaned up PID file"
fi

echo ""
echo "✅ All dashboard processes stopped"
