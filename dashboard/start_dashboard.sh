#!/bin/bash
# start_dashboard.sh
# Startup script for Agent Monitoring Dashboard
#
# PURPOSE:
# This script starts both the API server and Streamlit dashboard in one command.
# Handles background processes, checks for errors, and provides clear status messages.
#
# USAGE:
#   ./dashboard/start_dashboard.sh
#
# WHAT IT DOES:
# 1. Checks if required dependencies are installed
# 2. Starts FastAPI backend server in background
# 3. Waits for API to be ready
# 4. Starts Streamlit dashboard (opens browser automatically)
# 5. On exit (Ctrl+C), cleans up both processes
#
# WHY TWO PROCESSES:
# - API server (backend): Manages agent execution, file operations
# - Streamlit (frontend): Provides visual interface
# - Must run separately so they can communicate via HTTP
# - API can run without UI (useful for automation/testing)

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=================================================="
echo "🤖 Agent Monitoring Dashboard Startup"
echo "=================================================="
echo ""

# WHY: Check dependencies before starting - fail fast with clear message
echo "📋 Checking dependencies..."
if ! python -c "import fastapi, uvicorn, streamlit" 2>/dev/null; then
    echo "❌ Missing dependencies!"
    echo ""
    echo "Please install with:"
    echo "  pip install -r dashboard/requirements.txt"
    echo ""
    exit 1
fi
echo "✅ Dependencies OK"
echo ""

# WHY: Check if already running to avoid port conflicts
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Warning: Port 8000 already in use (API server may be running)"
    echo "   Kill existing process? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        echo "✅ Killed existing process"
    else
        echo "❌ Exiting (port conflict)"
        exit 1
    fi
fi

# WHY: Start API in background so script can continue to Streamlit
echo "🚀 Starting API server (backend)..."
python dashboard/api_server.py > /tmp/dashboard_api.log 2>&1 &
API_PID=$!

# WHY: Save PID to file so we can kill it on exit
echo $API_PID > /tmp/dashboard_api.pid

# WHY: Wait for API to be ready before starting UI
echo "⏳ Waiting for API to start..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API server ready (PID: $API_PID)"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "❌ API server failed to start"
        echo "   Check logs: /tmp/dashboard_api.log"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
done

echo ""
echo "=================================================="
echo "✅ Backend Running"
echo "=================================================="
echo "📍 API:  http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo "📋 Logs: /tmp/dashboard_api.log"
echo "🔧 PID:  $API_PID"
echo ""
echo "=================================================="
echo "🎨 Starting Dashboard (frontend)..."
echo "=================================================="
echo ""
echo "The dashboard will open in your browser automatically."
echo "If not, visit: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both API and dashboard"
echo ""

# WHY: Trap to cleanup on exit - ensures background process is killed
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    if [ -f /tmp/dashboard_api.pid ]; then
        kill $(cat /tmp/dashboard_api.pid) 2>/dev/null || true
        rm /tmp/dashboard_api.pid
    fi
    echo "✅ Cleanup complete"
    exit 0
}
trap cleanup EXIT INT TERM

# WHY: Start Streamlit in foreground so it handles Ctrl+C naturally
# When user presses Ctrl+C, trap above will kill API server
streamlit run dashboard/streamlit_dashboard.py
