#!/bin/bash
# ===============================================
# Variant Exploration System (VES) — Setup Script
# ===============================================
# This script initializes the development environment for Cursor & Claude Code.

echo "🔧 Setting up Variant Exploration System environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install core dependencies
pip install --upgrade pip
pip install pytest jsonschema pandas colorama streamlit

# Set environment variables
export USER="Rob"
export PYTHONPATH=$(pwd)

# Directory check
mkdir -p orchestrator/schema orchestrator/logs orchestrator/state tests reports

echo "✅ Environment setup complete."
echo "Run tests with: pytest -v"
