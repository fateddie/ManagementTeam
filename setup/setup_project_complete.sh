#!/usr/bin/env bash
# ===============================================================
# COMPREHENSIVE PROJECT SETUP SCRIPT
# Version: 2.0 - Production Grade
# Maintainer: Robert Freyne
# Date: 2025-10-17
#
# Purpose:
#   Complete automated setup for Python projects with:
#   - Virtual environment
#   - Code quality tools (Black, Ruff, pre-commit)
#   - Testing framework (pytest)
#   - Environment configuration
#   - Development best practices
#
# Usage:
#   ./setup/setup_project_complete.sh
#
# Features:
#   ✅ Python virtual environment
#   ✅ All dependencies (production + dev)
#   ✅ Code formatting (Black, Ruff)
#   ✅ Pre-commit hooks
#   ✅ Testing framework (pytest)
#   ✅ Environment validation
#   ✅ Git configuration
# ===============================================================

set -e  # Exit on error

# ------------- COLORS ------------- #
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ------------- CONFIG ------------- #
PYTHON_VERSION="3.11"
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
REQUIREMENTS_DEV_FILE="requirements-dev.txt"

# ------------- FUNCTIONS ------------- #

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# ------------- MAIN SCRIPT ------------- #

print_header "🚀 COMPREHENSIVE PROJECT SETUP"

# Step 1️⃣ — Check prerequisites
print_info "Step 1/10: Checking prerequisites..."

# Check for Python
if check_command python3; then
    PYTHON_CMD="python3"
    PYTHON_VERSION_INSTALLED=$($PYTHON_CMD --version | cut -d' ' -f2)
    print_success "Python found: $PYTHON_VERSION_INSTALLED"
else
    print_error "Python 3 not found. Please install Python 3.11 or later."
    exit 1
fi

# Check for pip
if check_command pip3 || check_command pip; then
    print_success "pip found"
else
    print_error "pip not found. Please install pip."
    exit 1
fi

# Check for git
if check_command git; then
    print_success "Git found"
else
    print_warning "Git not found. Some features will be disabled."
fi

# Step 2️⃣ — Create/verify virtual environment
print_info "Step 2/10: Setting up Python virtual environment..."

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists at $VENV_DIR"
    read -p "Do you want to recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Virtual environment recreated"
    else
        print_info "Using existing virtual environment"
    fi
else
    print_info "Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Step 3️⃣ — Activate virtual environment
print_info "Step 3/10: Activating virtual environment..."

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    print_success "Virtual environment activated"
else
    print_error "Could not find activation script"
    exit 1
fi

# Step 4️⃣ — Upgrade pip
print_info "Step 4/10: Upgrading pip..."
python -m pip install --upgrade pip --quiet
print_success "pip upgraded"

# Step 5️⃣ — Install production dependencies
print_info "Step 5/10: Installing production dependencies..."

if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE" --quiet
    print_success "Production dependencies installed"
else
    print_warning "requirements.txt not found, skipping production dependencies"
fi

# Step 6️⃣ — Install development dependencies
print_info "Step 6/10: Installing development dependencies..."

if [ -f "$REQUIREMENTS_DEV_FILE" ]; then
    pip install -r "$REQUIREMENTS_DEV_FILE" --quiet
    print_success "Development dependencies installed (black, ruff, pytest, pre-commit)"
else
    print_warning "requirements-dev.txt not found"
    print_info "Installing essential dev tools manually..."
    pip install black ruff pytest pytest-cov pre-commit --quiet
    print_success "Essential dev tools installed"
fi

# Step 7️⃣ — Configure environment variables
print_info "Step 7/10: Configuring environment variables..."

if [ ! -f "config/.env" ] && [ -f "config/.env.example" ]; then
    print_info "Creating config/.env from template..."
    cp config/.env.example config/.env
    print_success "config/.env created - EDIT THIS FILE WITH YOUR API KEYS"
    print_warning "Remember to edit config/.env with your actual API keys!"
elif [ -f "config/.env" ]; then
    print_success "config/.env already exists"
else
    print_warning "No .env.example found, skipping environment setup"
fi

# Step 8️⃣ — Set up pre-commit hooks
print_info "Step 8/10: Setting up pre-commit hooks..."

if [ -f ".pre-commit-config.yaml" ] && check_command git && [ -d ".git" ]; then
    if check_command pre-commit; then
        pre-commit install --quiet
        print_success "Pre-commit hooks installed (will run on every commit)"
        print_info "Run 'pre-commit run --all-files' to check all files now"
    else
        print_warning "pre-commit not found, skipping git hooks"
    fi
else
    if [ ! -f ".pre-commit-config.yaml" ]; then
        print_warning "No .pre-commit-config.yaml found"
    elif [ ! -d ".git" ]; then
        print_warning "Not a git repository, skipping pre-commit"
    fi
fi

# Step 9️⃣ — Validate environment configuration
print_info "Step 9/10: Validating environment..."

if [ -f "scripts/validate_environment.py" ]; then
    if python scripts/validate_environment.py > /dev/null 2>&1; then
        print_success "Environment validation passed"
    else
        print_warning "Environment validation found some issues"
        print_info "Run 'python scripts/validate_environment.py' for details"
    fi
elif [ -f "config/env_manager.py" ]; then
    if python -c "from config.env_manager import get_config; get_config()" > /dev/null 2>&1; then
        print_success "Config manager validated"
    else
        print_warning "Config manager found some issues"
        print_info "Run 'python -m config.env_manager' for details"
    fi
else
    print_warning "No validation script found, skipping"
fi

# Step 🔟 — Final summary
print_header "✨ SETUP COMPLETE"

echo -e "${GREEN}Your project is ready for development!${NC}\n"

echo -e "${CYAN}📋 Next Steps:${NC}"
echo -e "  1. ${YELLOW}Edit config/.env${NC} with your API keys"
echo -e "  2. ${YELLOW}source venv/bin/activate${NC} to activate environment"
echo -e "  3. ${YELLOW}python -m config.env_manager${NC} to validate configuration"
echo -e "  4. ${YELLOW}pytest tests/${NC} to run tests"
echo -e "  5. ${YELLOW}pre-commit run --all-files${NC} to check code quality"

echo -e "\n${CYAN}🛠️  Installed Tools:${NC}"
echo -e "  • Python $(python --version | cut -d' ' -f2)"
echo -e "  • pip $(pip --version | cut -d' ' -f2)"
if check_command black; then
    echo -e "  • Black $(black --version | cut -d' ' -f2)"
fi
if check_command ruff; then
    echo -e "  • Ruff $(ruff --version | cut -d' ' -f2)"
fi
if check_command pytest; then
    echo -e "  • pytest $(pytest --version | cut -d' ' -f2)"
fi
if check_command pre-commit; then
    echo -e "  • pre-commit $(pre-commit --version | cut -d' ' -f2)"
fi

echo -e "\n${CYAN}📚 Documentation:${NC}"
echo -e "  • README.md - Project overview"
echo -e "  • PROJECT_SETUP_TEMPLATE.md - Setup guide"
echo -e "  • config/.env.example - Environment variables reference"

echo -e "\n${CYAN}🎯 Quick Commands:${NC}"
echo -e "  ${BLUE}Format code:${NC}        black ."
echo -e "  ${BLUE}Lint code:${NC}          ruff check ."
echo -e "  ${BLUE}Fix lint issues:${NC}    ruff check --fix ."
echo -e "  ${BLUE}Run tests:${NC}          pytest"
echo -e "  ${BLUE}Test coverage:${NC}      pytest --cov"
echo -e "  ${BLUE}Run pre-commit:${NC}     pre-commit run --all-files"

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Happy Coding!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
