#!/bin/bash
###############################################################################
# Comprehensive Startup Script for Management Team
#
# Features:
# - Dependency checking (Python, Redis, pip packages)
# - Service startup (Redis, API server)
# - Interactive menu with 6 options
# - Error logging to single log file
# - Graceful cleanup on exit
#
# Usage:
#   ./start.sh
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/logs/startup.log"
PID_DIR="/tmp/management_team"

# Ensure directories exist
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$PID_DIR"

# Initialize log file
echo "=== Management Team Startup - $(date) ===" >> "$LOG_FILE"

###############################################################################
# Logging Functions
###############################################################################

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
    echo -e "${RED}❌ $1${NC}"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1" >> "$LOG_FILE"
    echo -e "${GREEN}✅ $1${NC}"
}

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARN: $1" >> "$LOG_FILE"
    echo -e "${YELLOW}⚠️  $1${NC}"
}

###############################################################################
# Cleanup Function
###############################################################################

cleanup() {
    log "Cleaning up..."

    # Kill API server if running
    if [ -f "$PID_DIR/api_server.pid" ]; then
        API_PID=$(cat "$PID_DIR/api_server.pid")
        if kill -0 "$API_PID" 2>/dev/null; then
            log "Stopping API server (PID: $API_PID)"
            kill "$API_PID" 2>/dev/null || true
        fi
        rm -f "$PID_DIR/api_server.pid"
    fi

    # Kill Streamlit if running
    if [ -f "$PID_DIR/streamlit.pid" ]; then
        STREAMLIT_PID=$(cat "$PID_DIR/streamlit.pid")
        if kill -0 "$STREAMLIT_PID" 2>/dev/null; then
            log "Stopping Streamlit (PID: $STREAMLIT_PID)"
            kill "$STREAMLIT_PID" 2>/dev/null || true
        fi
        rm -f "$PID_DIR/streamlit.pid"
    fi

    log "Cleanup complete"
}

# Register cleanup on exit
trap cleanup EXIT INT TERM

###############################################################################
# Dependency Checks
###############################################################################

check_python() {
    log "Checking Python installation..."

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        echo "Please install Python 3.8 or higher"
        return 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION found"
    return 0
}

check_redis() {
    log "Checking Redis..."

    # Check if Redis is running
    if lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "Redis is already running on port 6379"
        return 0
    fi

    # Redis not running - try to start it
    log_info "Redis not running, attempting to start..."

    if [ -f "$SCRIPT_DIR/scripts/start_redis.sh" ]; then
        bash "$SCRIPT_DIR/scripts/start_redis.sh" >> "$LOG_FILE" 2>&1
        sleep 2

        if lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null 2>&1; then
            log_success "Redis started successfully"
            return 0
        else
            log_warn "Could not start Redis - some features may be unavailable"
            return 1
        fi
    else
        log_warn "Redis start script not found - some features may be unavailable"
        return 1
    fi
}

check_packages() {
    log "Checking Python packages..."

    # Check if requirements.txt exists
    if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
        log_error "requirements.txt not found"
        return 1
    fi

    # Try importing key packages
    if python3 -c "import fastapi, streamlit, anthropic, supabase" 2>/dev/null; then
        log_success "All required packages installed"
        return 0
    else
        log_warn "Some packages may be missing"
        echo ""
        read -p "Install/update packages now? (y/N): " install_choice

        if [[ "$install_choice" =~ ^[Yy]$ ]]; then
            log "Installing packages from requirements.txt..."
            pip install -r "$SCRIPT_DIR/requirements.txt" >> "$LOG_FILE" 2>&1
            log_success "Packages installed"
            return 0
        else
            log_warn "Skipping package installation"
            return 1
        fi
    fi
}

check_env() {
    log "Checking environment configuration..."

    if [ ! -f "$SCRIPT_DIR/config/.env" ]; then
        log_warn ".env file not found"

        if [ -f "$SCRIPT_DIR/config/.env.example" ]; then
            echo ""
            echo "Copy .env.example to .env and configure your API keys:"
            echo "  cp config/.env.example config/.env"
            echo ""
        fi
        return 1
    fi

    log_success "Environment configuration found"
    return 0
}

###############################################################################
# Service Management
###############################################################################

start_api_server() {
    log "Starting API server..."

    # Check if already running
    if [ -f "$PID_DIR/api_server.pid" ]; then
        API_PID=$(cat "$PID_DIR/api_server.pid")
        if kill -0 "$API_PID" 2>/dev/null; then
            log_info "API server already running (PID: $API_PID)"
            return 0
        fi
    fi

    # Start API server in background
    cd "$SCRIPT_DIR"
    PYTHONPATH=. python3 dashboard/api_server.py >> "$LOG_FILE" 2>&1 &
    API_PID=$!
    echo "$API_PID" > "$PID_DIR/api_server.pid"

    # Wait for startup
    sleep 2

    if kill -0 "$API_PID" 2>/dev/null; then
        log_success "API server started (PID: $API_PID)"
        return 0
    else
        log_error "API server failed to start"
        return 1
    fi
}

start_dashboard() {
    log "Starting Streamlit dashboard..."

    # Check if already running
    if [ -f "$PID_DIR/streamlit.pid" ]; then
        STREAMLIT_PID=$(cat "$PID_DIR/streamlit.pid")
        if kill -0 "$STREAMLIT_PID" 2>/dev/null; then
            log_info "Dashboard already running (PID: $STREAMLIT_PID)"
            return 0
        fi
    fi

    # Start Streamlit in background
    cd "$SCRIPT_DIR"
    streamlit run dashboard/streamlit_dashboard.py >> "$LOG_FILE" 2>&1 &
    STREAMLIT_PID=$!
    echo "$STREAMLIT_PID" > "$PID_DIR/streamlit.pid"

    log_success "Dashboard started (PID: $STREAMLIT_PID)"
    log_info "Dashboard will open in your browser at http://localhost:8501"
    return 0
}

###############################################################################
# Main Menu
###############################################################################

show_menu() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           Management Team - Idea Validation               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "What would you like to do today?"
    echo ""
    echo "  1) 💬 Work on new idea (guided conversation)"
    echo "  2) 🚀 Work on new idea (expert mode - fast input)"
    echo "  3) 📂 Continue existing project"
    echo "  4) ⚙️  Run full pipeline (all research agents)"
    echo "  5) 📊 Open dashboard only"
    echo "  6) 🔍 System status"
    echo "  7) 🚪 Exit"
    echo ""
}

run_interactive_workflow() {
    local mode="$1"

    log "Starting interactive workflow in $mode mode"

    cd "$SCRIPT_DIR"

    if [ "$mode" = "expert" ]; then
        python3 cli/interactive_workflow.py --expert
    else
        python3 cli/interactive_workflow.py
    fi
}

run_full_pipeline() {
    log "Starting full pipeline"

    cd "$SCRIPT_DIR"
    python3 cli/manage.py run
}

show_status() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "SYSTEM STATUS"
    echo "═══════════════════════════════════════════════════════════"
    echo ""

    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo -e "${GREEN}✅${NC} Python: $PYTHON_VERSION"
    else
        echo -e "${RED}❌${NC} Python: Not installed"
    fi

    # Redis
    if lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Redis: Running on port 6379"
    else
        echo -e "${YELLOW}⚠️${NC}  Redis: Not running"
    fi

    # API Server
    if [ -f "$PID_DIR/api_server.pid" ]; then
        API_PID=$(cat "$PID_DIR/api_server.pid")
        if kill -0 "$API_PID" 2>/dev/null; then
            echo -e "${GREEN}✅${NC} API Server: Running (PID: $API_PID)"
        else
            echo -e "${YELLOW}⚠️${NC}  API Server: Not running"
        fi
    else
        echo -e "${YELLOW}⚠️${NC}  API Server: Not running"
    fi

    # Dashboard
    if [ -f "$PID_DIR/streamlit.pid" ]; then
        STREAMLIT_PID=$(cat "$PID_DIR/streamlit.pid")
        if kill -0 "$STREAMLIT_PID" 2>/dev/null; then
            echo -e "${GREEN}✅${NC} Dashboard: Running (PID: $STREAMLIT_PID)"
        else
            echo -e "${YELLOW}⚠️${NC}  Dashboard: Not running"
        fi
    else
        echo -e "${YELLOW}⚠️${NC}  Dashboard: Not running"
    fi

    # Environment
    if [ -f "$SCRIPT_DIR/config/.env" ]; then
        echo -e "${GREEN}✅${NC} Environment: Configured"
    else
        echo -e "${YELLOW}⚠️${NC}  Environment: .env file missing"
    fi

    echo ""
    echo "Log file: $LOG_FILE"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    # Banner
    clear
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║           Management Team - Starting Up...                ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    # Run dependency checks
    log "=== Dependency Checks ==="

    check_python || exit 1
    check_redis
    check_packages
    check_env

    # Start core services
    log "=== Starting Services ==="
    echo ""

    start_api_server

    # Show menu
    while true; do
        show_menu
        read -p "Enter your choice [1-7]: " choice

        case $choice in
            1)
                run_interactive_workflow "guided"
                ;;
            2)
                run_interactive_workflow "expert"
                ;;
            3)
                log "Resume project selected"
                echo ""
                read -p "Enter project ID: " project_id
                python3 cli/interactive_workflow.py --resume "$project_id"
                ;;
            4)
                run_full_pipeline
                ;;
            5)
                start_dashboard
                echo ""
                echo "Dashboard running at http://localhost:8501"
                echo "Press Ctrl+C to stop"
                wait
                ;;
            6)
                show_status
                ;;
            7)
                log "User chose to exit"
                echo ""
                echo "Goodbye! 👋"
                exit 0
                ;;
            *)
                echo ""
                echo "Invalid choice. Please enter 1-7."
                ;;
        esac
    done
}

# Run main
main
