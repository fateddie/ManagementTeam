#!/bin/bash
# ==============================================
# Migrate Existing Project to Universal Standards
# ==============================================
# Updates an existing project with production-grade tooling
# and standardized configuration while preserving custom code
#
# Usage:
#   ./scripts/migrate_project_to_standards.sh /path/to/project
#   ./scripts/migrate_project_to_standards.sh projects/my-project

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
    echo -e "${RED}❌ Error: Project path required${NC}"
    echo "Usage: $0 <project-path>"
    echo ""
    echo "Examples:"
    echo "  $0 projects/my-existing-project"
    echo "  $0 /Users/me/projects/existing-app"
    exit 1
fi

PROJECT_PATH=$1

# Convert to absolute path if relative
if [[ "$PROJECT_PATH" != /* ]]; then
    PROJECT_PATH="$(pwd)/$PROJECT_PATH"
fi

# Get script directory and template location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MANAGEMENT_TEAM_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$MANAGEMENT_TEAM_ROOT/config/templates/universal"

# ==============================================
# Validation
# ==============================================
echo -e "${BLUE}🔍 Validating project...${NC}"

# Check if project exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}❌ Error: Project directory not found${NC}"
    echo "   Path: $PROJECT_PATH"
    exit 1
fi

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo -e "${RED}❌ Error: Universal template directory not found${NC}"
    echo "   Expected: $TEMPLATE_DIR"
    exit 1
fi

# Check if this looks like a Python project
if [ ! -f "$PROJECT_PATH/requirements.txt" ] && [ ! -f "$PROJECT_PATH/pyproject.toml" ]; then
    echo -e "${YELLOW}⚠️  Warning: No requirements.txt or pyproject.toml found${NC}"
    echo "   This may not be a Python project. Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Migration cancelled."
        exit 0
    fi
fi

echo -e "${GREEN}   ✅ Project validated${NC}"
echo -e "${BLUE}   Location: $PROJECT_PATH${NC}"

# ==============================================
# Backup Existing Files
# ==============================================
echo ""
echo -e "${BLUE}💾 Creating backup...${NC}"

BACKUP_DIR="$PROJECT_PATH/.migration-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup files that will be replaced
FILES_TO_BACKUP=(
    "pyproject.toml"
    "pytest.ini"
    "requirements-dev.txt"
    ".gitignore"
    "scripts/setup_venv.sh"
    "scripts/setup.sh"
    "scripts/validate_env.py"
    "docs/PRINCIPLES.md"
    "docs/CLAUDE.md"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$PROJECT_PATH/$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname "$file")"
        cp "$PROJECT_PATH/$file" "$BACKUP_DIR/$file"
        echo -e "${GREEN}   ✅ Backed up $file${NC}"
    fi
done

echo -e "${GREEN}   ✅ Backup created at: $BACKUP_DIR${NC}"

# ==============================================
# Copy Template Files
# ==============================================
echo ""
echo -e "${BLUE}📄 Updating project files...${NC}"

# Ensure directories exist
mkdir -p "$PROJECT_PATH"/{config,docs,scripts,tests,data,logs}
mkdir -p "$PROJECT_PATH"/data/{raw,processed,cache}

# Copy/update template files (preserving existing .env)
echo ""
echo -e "${YELLOW}Production Tooling:${NC}"

# pyproject.toml
if [ -f "$PROJECT_PATH/pyproject.toml" ]; then
    echo -e "${YELLOW}   ⚠️  pyproject.toml exists - merging manually required${NC}"
    cp "$TEMPLATE_DIR/pyproject.toml" "$PROJECT_PATH/pyproject.toml.new"
    echo -e "${BLUE}   📝 Created pyproject.toml.new (review and merge manually)${NC}"
else
    cp "$TEMPLATE_DIR/pyproject.toml" "$PROJECT_PATH/pyproject.toml"
    echo -e "${GREEN}   ✅ pyproject.toml${NC}"
fi

# pytest.ini
if [ -f "$PROJECT_PATH/pytest.ini" ]; then
    echo -e "${YELLOW}   ⚠️  pytest.ini exists - kept existing (new version in backup if you want to compare)${NC}"
else
    cp "$TEMPLATE_DIR/pytest.ini" "$PROJECT_PATH/pytest.ini"
    echo -e "${GREEN}   ✅ pytest.ini${NC}"
fi

# requirements-dev.txt
if [ -f "$PROJECT_PATH/requirements-dev.txt" ]; then
    # Merge dependencies
    cat "$TEMPLATE_DIR/requirements-dev.txt" >> "$PROJECT_PATH/requirements-dev.txt.new"
    echo -e "${YELLOW}   ⚠️  requirements-dev.txt exists - created .new file (review and merge)${NC}"
else
    cp "$TEMPLATE_DIR/requirements-dev.txt" "$PROJECT_PATH/requirements-dev.txt"
    echo -e "${GREEN}   ✅ requirements-dev.txt${NC}"
fi

# .gitignore (merge approach)
if [ -f "$PROJECT_PATH/.gitignore" ]; then
    cat "$TEMPLATE_DIR/.gitignore" >> "$PROJECT_PATH/.gitignore.new"
    echo -e "${YELLOW}   ⚠️  .gitignore exists - created .new file (review and merge)${NC}"
else
    cp "$TEMPLATE_DIR/.gitignore" "$PROJECT_PATH/.gitignore"
    echo -e "${GREEN}   ✅ .gitignore${NC}"
fi

echo ""
echo -e "${YELLOW}Setup Scripts:${NC}"

# setup_venv.sh
cp "$TEMPLATE_DIR/setup_venv.sh" "$PROJECT_PATH/scripts/"
chmod +x "$PROJECT_PATH/scripts/setup_venv.sh"
echo -e "${GREEN}   ✅ scripts/setup_venv.sh${NC}"

# setup.sh
cp "$TEMPLATE_DIR/setup.sh" "$PROJECT_PATH/scripts/"
chmod +x "$PROJECT_PATH/scripts/setup.sh"
echo -e "${GREEN}   ✅ scripts/setup.sh${NC}"

# validate_env.py
if [ ! -f "$PROJECT_PATH/scripts/validate_env.py" ]; then
    cp "$TEMPLATE_DIR/validate_env.py" "$PROJECT_PATH/scripts/"
    chmod +x "$PROJECT_PATH/scripts/validate_env.py"
    echo -e "${GREEN}   ✅ scripts/validate_env.py${NC}"
else
    echo -e "${BLUE}   📝 scripts/validate_env.py already exists (kept)${NC}"
fi

echo ""
echo -e "${YELLOW}Documentation:${NC}"

# PRINCIPLES.md
if [ ! -f "$PROJECT_PATH/docs/PRINCIPLES.md" ]; then
    cp "$TEMPLATE_DIR/PRINCIPLES.md" "$PROJECT_PATH/docs/"
    echo -e "${GREEN}   ✅ docs/PRINCIPLES.md${NC}"
else
    echo -e "${BLUE}   📝 docs/PRINCIPLES.md already exists (kept)${NC}"
fi

# CLAUDE.md
if [ ! -f "$PROJECT_PATH/docs/CLAUDE.md" ]; then
    cp "$TEMPLATE_DIR/CLAUDE.md" "$PROJECT_PATH/docs/"
    echo -e "${GREEN}   ✅ docs/CLAUDE.md${NC}"
else
    echo -e "${BLUE}   📝 docs/CLAUDE.md already exists (kept)${NC}"
fi

echo ""
echo -e "${YELLOW}Environment Management:${NC}"

# env_manager.py (only if config/ directory exists)
if [ -d "$PROJECT_PATH/config" ]; then
    if [ ! -f "$PROJECT_PATH/config/env_manager.py" ]; then
        cp "$TEMPLATE_DIR/env_manager_template.py" "$PROJECT_PATH/config/env_manager.py"
        echo -e "${GREEN}   ✅ config/env_manager.py${NC}"
    else
        echo -e "${BLUE}   📝 config/env_manager.py already exists (kept)${NC}"
    fi

    # .env.example (never overwrite existing)
    if [ ! -f "$PROJECT_PATH/config/.env.example" ]; then
        cp "$TEMPLATE_DIR/.env.example" "$PROJECT_PATH/config/.env.example"
        echo -e "${GREEN}   ✅ config/.env.example${NC}"
    else
        echo -e "${BLUE}   📝 config/.env.example already exists (kept)${NC}"
    fi

    # NEVER touch .env
    if [ -f "$PROJECT_PATH/config/.env" ]; then
        echo -e "${GREEN}   ✅ config/.env preserved (not modified)${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  No config/ directory - skipping env_manager.py${NC}"
fi

# ==============================================
# Extract Project Name
# ==============================================
PROJECT_NAME=$(basename "$PROJECT_PATH")

# Update PROJECT_NAME placeholder if pyproject.toml was created new
if [ -f "$PROJECT_PATH/pyproject.toml" ] && grep -q "{{PROJECT_NAME}}" "$PROJECT_PATH/pyproject.toml" 2>/dev/null; then
    sed -i.bak "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$PROJECT_PATH/pyproject.toml"
    rm -f "$PROJECT_PATH/pyproject.toml.bak"
    echo -e "${GREEN}   ✅ Updated pyproject.toml with project name${NC}"
fi

# ==============================================
# Create __init__.py files if missing
# ==============================================
echo ""
echo -e "${BLUE}📝 Creating __init__.py files...${NC}"

for dir in src tests; do
    if [ -d "$PROJECT_PATH/$dir" ] && [ ! -f "$PROJECT_PATH/$dir/__init__.py" ]; then
        touch "$PROJECT_PATH/$dir/__init__.py"
        echo -e "${GREEN}   ✅ $dir/__init__.py${NC}"
    fi
done

# ==============================================
# Git Status Check
# ==============================================
echo ""
echo -e "${BLUE}🔧 Checking git status...${NC}"

cd "$PROJECT_PATH"
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Git repository detected${NC}"
    echo -e "${BLUE}   💡 Run 'git status' to see changes${NC}"
else
    echo -e "${YELLOW}   ⚠️  Not a git repository${NC}"
    echo -e "${BLUE}   💡 Consider running: git init${NC}"
fi

# ==============================================
# Success Summary
# ==============================================
echo ""
echo -e "${GREEN}=" | awk '{s=sprintf("%70s",""); gsub(/ /,"=",$0); print}'${NC}
echo -e "${GREEN}✅ MIGRATION COMPLETE${NC}"
echo -e "${GREEN}=" | awk '{s=sprintf("%70s",""); gsub(/ /,"=",$0); print}'${NC}
echo ""
echo -e "${BLUE}📁 Project:${NC} $PROJECT_PATH"
echo -e "${BLUE}💾 Backup:${NC} $BACKUP_DIR"
echo ""
echo -e "${BLUE}📋 What Changed:${NC}"
echo "   ✅ Production tooling added (Black, Ruff, Pytest, MyPy)"
echo "   ✅ Setup automation scripts installed"
echo "   ✅ Documentation principles added"
echo "   ✅ Development dependencies configured"
echo ""
echo -e "${BLUE}🔍 Files to Review Manually:${NC}"
if [ -f "$PROJECT_PATH/pyproject.toml.new" ]; then
    echo "   ⚠️  pyproject.toml.new - merge with existing pyproject.toml"
fi
if [ -f "$PROJECT_PATH/requirements-dev.txt.new" ]; then
    echo "   ⚠️  requirements-dev.txt.new - merge with existing requirements-dev.txt"
fi
if [ -f "$PROJECT_PATH/.gitignore.new" ]; then
    echo "   ⚠️  .gitignore.new - merge with existing .gitignore"
fi
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "   1. Review any .new files and merge manually"
echo "   2. cd $PROJECT_PATH"
echo "   3. ./scripts/setup.sh  # Run complete setup"
echo "   4. source venv/bin/activate"
echo "   5. pytest  # Verify tests work"
echo "   6. black . && ruff check .  # Format and lint"
echo ""
echo -e "${BLUE}💡 Optional: Update imports to use env_manager${NC}"
echo "   Replace: os.getenv('API_KEY')"
echo "   With:    from config.env_manager import get_config"
echo "            config = get_config()"
echo "            api_key = config.api_key"
echo ""
echo -e "${YELLOW}⚠️  Original files backed up to:${NC}"
echo "   $BACKUP_DIR"
echo ""
