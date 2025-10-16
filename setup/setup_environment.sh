#!/usr/bin/env bash
# ===============================================================
# AI MANAGEMENT TEAM – ENVIRONMENT SETUP SCRIPT
# Version: 1.0
# Maintainer: Founder (Rob)
# Date: 2025-10-08
#
# Purpose:
#   Initialize a consistent, Claude-Code-compatible development
#   environment for the AI Management-Team project.
#   Creates virtual environment, installs dependencies,
#   sets up folder hierarchy, and prepares config files.
# ===============================================================

# ------------- CONFIG ------------- #
PYTHON_VERSION="3.11"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
BASE_FOLDERS=(
  "src"
  "src/agents"
  "src/utils"
  "memory"
  "logs"
  "data/project_proposals"
  "data/market_data"
  "data/reports"
  "docs/system/archive"
  "config"
  "dashboards/api"
  "dashboards/ui"
  "dashboards/static"
  "tests"
  "scripts"
)
# ---------------------------------- #

echo "🚀 Setting up AI Management Team development environment..."

# Step 1️⃣ — Create directories
for dir in "${BASE_FOLDERS[@]}"; do
  mkdir -p "$dir"
done
echo "📁 Directory structure created."

# Step 2️⃣ — Initialize Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "🐍 Creating Python virtual environment in $VENV_DIR..."
  python${PYTHON_VERSION} -m venv $VENV_DIR 2>/dev/null || python -m venv $VENV_DIR
else
  echo "🔁 Virtual environment already exists, skipping creation."
fi

# Step 3️⃣ — Activate environment
source $VENV_DIR/bin/activate
echo "✅ Virtual environment activated."

# Step 4️⃣ — Install dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
  echo "📦 Installing dependencies from $REQUIREMENTS_FILE..."
  pip install --upgrade pip
  pip install -r $REQUIREMENTS_FILE
else
  echo "⚠️ No requirements.txt found — creating a default one."
  cat > requirements.txt <<'EOF'
# Core dependencies
requests
pandas
numpy
pyyaml
python-dotenv
# Optional future tools
slack_sdk
chromadb
fastapi
EOF
  pip install -r requirements.txt
fi

# Step 5️⃣ — Create .env file template
if [ ! -f "config/.env" ]; then
  echo "🧾 Creating .env template in config/.env..."
  cat > config/.env <<'EOF'
# ENVIRONMENT VARIABLES (edit values before running)
SLACK_WEBHOOK_URL=""
CLAUDE_API_KEY=""
PROJECT_NAME="AI_Management_Team"
EOF
else
  echo "🔁 .env file already exists, skipping."
fi

# Step 6️⃣ — Create .gitignore if missing
if [ ! -f ".gitignore" ]; then
  echo "⚙️ Creating .gitignore..."
  cat > .gitignore <<'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.env
.venv/
.envrc
# OS
.DS_Store
Thumbs.db
# Project
memory/*.json
logs/
EOF
fi

# Step 7️⃣ — Touch placeholder README files
if [ ! -f "README.md" ]; then
  echo "🧩 Creating project README.md..."
  cat > README.md <<'EOF'
# AI Management Team – Claude Code Project
Initialized via setup_environment.sh
See /docs/system/ for governance, orchestration, and decision documentation.
EOF
fi

# Step 8️⃣ — Set permissions
chmod -R 755 src scripts
chmod 600 config/.env

# Step 9️⃣ — Summary
echo ""
echo "🎉 Environment setup complete!"
echo "→ Activate your environment:  source ${VENV_DIR}/bin/activate"
echo "→ Next step: Run scripts/init_management_team.py to seed docs/system/"
echo ""
echo "🧠 Tip: Add dependencies with 'pip install <package>' then run 'pip freeze > requirements.txt'"
echo "=============================================================="

