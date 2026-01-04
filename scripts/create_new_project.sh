#!/bin/bash
# ==============================================
# Create New Project from Universal Template
# ==============================================
# Creates a new project with standardized structure and best practices
#
# Usage:
#   ./scripts/create_new_project.sh my-new-project
#   ./scripts/create_new_project.sh my-new-project --path /custom/location

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==============================================
# Parse Arguments
# ==============================================
if [ $# -lt 1 ]; then
    echo -e "${RED}❌ Error: Project name required${NC}"
    echo "Usage: $0 <project-name> [--path /custom/location]"
    echo ""
    echo "Examples:"
    echo "  $0 my-ai-assistant"
    echo "  $0 my-ai-assistant --path /Users/me/projects"
    exit 1
fi

PROJECT_NAME=$1
CUSTOM_PATH=""

# Parse optional --path argument
if [ $# -gt 1 ] && [ "$2" == "--path" ] && [ -n "$3" ]; then
    CUSTOM_PATH=$3
fi

# Determine project location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MANAGEMENT_TEAM_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -n "$CUSTOM_PATH" ]; then
    PROJECT_ROOT="$CUSTOM_PATH/$PROJECT_NAME"
else
    PROJECT_ROOT="$MANAGEMENT_TEAM_ROOT/projects/$PROJECT_NAME"
fi

TEMPLATE_DIR="$MANAGEMENT_TEAM_ROOT/config/templates/universal"

# ==============================================
# Validation
# ==============================================
echo -e "${BLUE}🔍 Validating...${NC}"

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo -e "${RED}❌ Error: Universal template directory not found${NC}"
    echo "   Expected: $TEMPLATE_DIR"
    exit 1
fi

# Check if project already exists
if [ -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Error: Project directory already exists${NC}"
    echo "   Location: $PROJECT_ROOT"
    echo "   Use a different name or delete the existing directory"
    exit 1
fi

# Validate project name (alphanumeric, dashes, underscores)
if ! [[ "$PROJECT_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo -e "${RED}❌ Error: Invalid project name${NC}"
    echo "   Project name must contain only letters, numbers, dashes, and underscores"
    exit 1
fi

# ==============================================
# Create Project Structure
# ==============================================
echo -e "${BLUE}📁 Creating project structure...${NC}"

mkdir -p "$PROJECT_ROOT"/{config,docs,src,tests,scripts,data,logs}
mkdir -p "$PROJECT_ROOT"/data/{raw,processed,cache}

echo -e "${GREEN}   ✅ Created directory structure${NC}"

# ==============================================
# Copy Universal Templates
# ==============================================
echo -e "${BLUE}📄 Copying universal templates...${NC}"

# env_manager.py
cp "$TEMPLATE_DIR/env_manager_template.py" "$PROJECT_ROOT/config/env_manager.py"
echo -e "${GREEN}   ✅ config/env_manager.py${NC}"

# .env.example
cp "$TEMPLATE_DIR/.env.example" "$PROJECT_ROOT/config/.env.example"
echo -e "${GREEN}   ✅ config/.env.example${NC}"

# .gitignore
cp "$TEMPLATE_DIR/.gitignore" "$PROJECT_ROOT/.gitignore"
echo -e "${GREEN}   ✅ .gitignore${NC}"

# PRINCIPLES.md
cp "$TEMPLATE_DIR/PRINCIPLES.md" "$PROJECT_ROOT/docs/"
echo -e "${GREEN}   ✅ docs/PRINCIPLES.md${NC}"

# CLAUDE.md
cp "$TEMPLATE_DIR/CLAUDE.md" "$PROJECT_ROOT/docs/"
echo -e "${GREEN}   ✅ docs/CLAUDE.md${NC}"

# validate_env.py
cp "$TEMPLATE_DIR/validate_env.py" "$PROJECT_ROOT/scripts/"
chmod +x "$PROJECT_ROOT/scripts/validate_env.py"
echo -e "${GREEN}   ✅ scripts/validate_env.py${NC}"

# pyproject.toml
cp "$TEMPLATE_DIR/pyproject.toml" "$PROJECT_ROOT/"
echo -e "${GREEN}   ✅ pyproject.toml${NC}"

# pytest.ini
cp "$TEMPLATE_DIR/pytest.ini" "$PROJECT_ROOT/"
echo -e "${GREEN}   ✅ pytest.ini${NC}"

# requirements-dev.txt
cp "$TEMPLATE_DIR/requirements-dev.txt" "$PROJECT_ROOT/"
echo -e "${GREEN}   ✅ requirements-dev.txt${NC}"

# setup_venv.sh
cp "$TEMPLATE_DIR/setup_venv.sh" "$PROJECT_ROOT/scripts/"
chmod +x "$PROJECT_ROOT/scripts/setup_venv.sh"
echo -e "${GREEN}   ✅ scripts/setup_venv.sh${NC}"

# setup.sh (master setup)
cp "$TEMPLATE_DIR/setup.sh" "$PROJECT_ROOT/scripts/"
chmod +x "$PROJECT_ROOT/scripts/setup.sh"
echo -e "${GREEN}   ✅ scripts/setup.sh${NC}"

# ==============================================
# Customize Templates
# ==============================================
echo -e "${BLUE}🔧 Customizing templates...${NC}"

# Update PROJECT_NAME in .env.example
sed -i.bak "s/PROJECT_NAME=MyProject/PROJECT_NAME=$PROJECT_NAME/g" "$PROJECT_ROOT/config/.env.example"
rm "$PROJECT_ROOT/config/.env.example.bak"

# Update PROJECT_ROOT in .env.example
sed -i.bak "s|PROJECT_ROOT=/path/to/your/project|PROJECT_ROOT=$PROJECT_ROOT|g" "$PROJECT_ROOT/config/.env.example"
rm "$PROJECT_ROOT/config/.env.example.bak"

# Update PROJECT_NAME in pyproject.toml
sed -i.bak "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$PROJECT_ROOT/pyproject.toml"
rm "$PROJECT_ROOT/pyproject.toml.bak"

echo -e "${GREEN}   ✅ Updated project-specific values${NC}"

# ==============================================
# Create Initial Files
# ==============================================
echo -e "${BLUE}📝 Creating initial files...${NC}"

# Create README.md
cat > "$PROJECT_ROOT/README.md" << EOF
# $PROJECT_NAME

**Status:** In Development
**Created:** $(date +%Y-%m-%d)

## 🎯 Purpose

[Describe what this project does]

## 🚀 Quick Start

\`\`\`bash
# 1. Set up environment
cp config/.env.example config/.env
nano config/.env  # Add your credentials

# 2. Validate configuration
python scripts/validate_env.py

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python src/main.py
\`\`\`

## 📚 Documentation

- [Setup Guide](docs/SETUP.md)
- [System Principles](docs/PRINCIPLES.md)
- [Claude Guidelines](docs/CLAUDE.md)

## 🏗️ Project Structure

\`\`\`
$PROJECT_NAME/
├── config/              # Configuration and credentials
│   ├── env_manager.py   # Centralized credential management
│   ├── .env.example     # Environment template
│   └── .env             # Your credentials (gitignored)
├── src/                 # Source code
├── tests/               # Unit and integration tests
├── scripts/             # Utility scripts
├── data/                # Data files
│   ├── raw/             # Original data
│   ├── processed/       # Cleaned data
│   └── cache/           # Cached results
├── logs/                # Application logs
└── docs/                # Documentation
\`\`\`

## 🔐 Security

- ✅ Credentials managed via \`config/env_manager.py\`
- ✅ \`config/.env\` is gitignored
- ✅ No hardcoded secrets in code
- ✅ Validation on startup

## 📋 TODO

- [ ] Configure \`config/.env\` with credentials
- [ ] Implement core functionality
- [ ] Add tests
- [ ] Update this README

---

🤖 Generated with [Universal Project Template](https://github.com/your-org/management-team)
EOF

echo -e "${GREEN}   ✅ README.md${NC}"

# Create requirements.txt
cat > "$PROJECT_ROOT/requirements.txt" << EOF
# Core dependencies
python-dotenv>=1.0.0

# Add your project dependencies here
# Example:
# openai>=1.0.0
# anthropic>=0.18.0
# requests>=2.28.0
EOF

echo -e "${GREEN}   ✅ requirements.txt${NC}"

# Create main.py stub
mkdir -p "$PROJECT_ROOT/src"
cat > "$PROJECT_ROOT/src/main.py" << EOF
#!/usr/bin/env python3
"""
Main entry point for $PROJECT_NAME
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.env_manager import get_config


def main():
    """Main application logic"""
    # Load and validate configuration
    config = get_config()

    print(f"🚀 Starting {config.project_name}...")
    print(f"   Environment: {config.environment}")
    print(f"   Debug: {config.debug}")

    # TODO: Implement your application logic here

    print("✅ Done!")


if __name__ == "__main__":
    main()
EOF

chmod +x "$PROJECT_ROOT/src/main.py"
echo -e "${GREEN}   ✅ src/main.py${NC}"

# Create __init__.py files
touch "$PROJECT_ROOT/src/__init__.py"
touch "$PROJECT_ROOT/tests/__init__.py"

# ==============================================
# Initialize Git
# ==============================================
echo -e "${BLUE}🔧 Initializing git repository...${NC}"

cd "$PROJECT_ROOT"
git init -q
git add .
git commit -q -m "Initial commit from universal template

Created with ManagementTeam universal template system.
Includes:
- Centralized credential management (env_manager.py)
- System principles (PRINCIPLES.md)
- AI assistant guidelines (CLAUDE.md)
- Security best practices (.gitignore)
- Validation scripts

🤖 Generated with [Universal Project Template]"

echo -e "${GREEN}   ✅ Git repository initialized${NC}"

# ==============================================
# Success Summary
# ==============================================
echo ""
echo -e "${GREEN}=" | awk '{s=sprintf("%70s",""); gsub(/ /,"=",$0); print}'${NC}
echo -e "${GREEN}✅ SUCCESS - Project created!${NC}"
echo -e "${GREEN}=" | awk '{s=sprintf("%70s",""); gsub(/ /,"=",$0); print}'${NC}
echo ""
echo -e "${BLUE}📁 Project Location:${NC}"
echo "   $PROJECT_ROOT"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "   1. cd $PROJECT_ROOT"
echo "   2. ./scripts/setup.sh  # Complete automated setup"
echo "   3. source venv/bin/activate"
echo "   4. nano config/.env  # Add your credentials"
echo "   5. python src/main.py"
echo ""
echo -e "${BLUE}🧪 Development Commands:${NC}"
echo "   • Run tests: pytest"
echo "   • Format code: black ."
echo "   • Lint code: ruff check ."
echo "   • Type check: mypy src/"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - Setup Guide: docs/PRINCIPLES.md"
echo "   - Claude Guide: docs/CLAUDE.md"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure config/.env before running!${NC}"
echo ""
