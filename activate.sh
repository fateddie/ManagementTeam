#!/bin/bash
# Quick activation script for AI Management Layer System
# Usage: source activate.sh

echo "🚀 Activating AI Management Layer System..."

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH=/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam:$PYTHONPATH

# Set project root
export MANAGEMENT_TEAM_ROOT=/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam

# Load environment variables from central .env file
if [ -f "config/.env" ]; then
    echo "📥 Loading environment variables from config/.env..."
    export $(grep -v '^#' config/.env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  config/.env not found. Copy config/.env.example to config/.env"
fi

echo "✅ Environment ready!"
echo ""
echo "Commands available:"
echo "  python scripts/run_planner.py <name> <description>"
echo "  streamlit run dashboards/planner_dashboard.py"
echo "  python src/agents/planner_agent.py"
echo ""
echo "🔑 API Keys loaded from: config/.env"

