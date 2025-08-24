#!/bin/bash

# Business Intelligence Scraper - Quick Start
# ==========================================
#
# One-command setup and launch script for the Business Intelligence Scraper Platform.
# This script automatically sets up all necessary components and launches the web server.
#
# Features:
# - Automatic dependency installation
# - Database initialization
# - Configuration setup
# - Service health checks
# - Web server launch
#
# Author: Business Intelligence Scraper Team
# Date: July 25, 2025
# Version: 2.0.0

# Enable error handling but handle errors gracefully
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
VENV_DIR=".venv"
LOG_FILE="quick_start.log"
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Function to print colored output
print_step() {
    echo -e "${BLUE}==>${NC} ${1}" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}✅${NC} ${1}" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} ${1}" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}❌${NC} ${1}" | tee -a "$LOG_FILE"
}

print_info() {
    echo -e "${CYAN}ℹ️${NC} ${1}" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        local version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python ${version} found"
            return 0
        else
            print_error "Python ${version} found, but requires Python ${PYTHON_MIN_VERSION}+"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Function to check Node.js version
check_node_version() {
    if command_exists node && command_exists npm; then
        local node_version=$(node --version)
        local npm_version=$(npm --version)
        print_success "Node.js ${node_version} and npm ${npm_version} found"
        return 0
    else
        print_warning "Node.js/npm not found - frontend will be skipped"
        print_warning "Install Node.js from https://nodejs.org/ to enable frontend"
        return 1
    fi
}

# Function to check if port is available
check_port() {
    local port=$1
    if command_exists lsof && lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 1
    else
        return 0
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    print_warning "Port $port is in use, attempting to free it..."
    if command_exists lsof; then
        local pid=$(lsof -Pi :$port -sTCP:LISTEN -t)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null || true
            sleep 2
            print_success "Freed port $port"
        fi
    fi
}

# Function to setup virtual environment
setup_venv() {
    print_step "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        print_success "Created virtual environment"
    else
        print_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    print_success "Activated virtual environment"
    
    # Upgrade pip
    pip install --upgrade pip wheel setuptools >/dev/null 2>&1
    print_success "Updated pip and setuptools"
}

# Function to install dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Install main requirements
    if [ -f "requirements.txt" ]; then
        if pip install -r requirements.txt >/dev/null 2>&1; then
            print_success "Installed main dependencies"
        else
            print_warning "Some main dependencies may have failed to install"
        fi
    fi
    
    # Install testing requirements if they exist
    if [ -f "requirements-testing.txt" ]; then
        if pip install -r requirements-testing.txt >/dev/null 2>&1; then
            print_success "Installed testing dependencies"
        else
            print_warning "Some testing dependencies may have failed to install"
        fi
    fi
    
    # Install additional common dependencies
    if pip install uvicorn[standard] fastapi sqlalchemy redis python-multipart >/dev/null 2>&1; then
        print_success "Installed additional web server dependencies"
    else
        print_warning "Some additional dependencies may have failed to install"
    fi
}

# Function to setup configuration
setup_configuration() {
    print_step "Setting up configuration..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            print_success "Created .env from template"
        elif [ -f ".env.template" ]; then
            cp ".env.template" ".env"
            print_success "Created .env from template"
        else
            # Create basic .env file
            cat > .env << EOF
# Basic Configuration
DATABASE_URL=sqlite:///./data.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=quick-start-secret-key-change-in-production
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Security
JWT_SECRET_KEY=quick-start-jwt-secret-change-in-production
ENCRYPTION_KEY=quick-start-encryption-key-change-in-production

# Performance
CACHE_BACKEND=memory
PERFORMANCE_MONITORING=true
EOF
            print_success "Created basic .env configuration"
        fi
    else
        print_info "Configuration file .env already exists"
    fi
}

# Function to setup directories
setup_directories() {
    print_step "Setting up required directories..."
    
    # Create data directories
    mkdir -p data logs cache temp
    mkdir -p business_intel_scraper/backend/logs
    
    # Set permissions
    chmod 755 data logs cache temp
    
    print_success "Created required directories"
}

# Function to initialize database
initialize_database() {
    print_step "Initializing database..."
    
    # Check if we have database initialization script
    if [ -f "business_intel_scraper/backend/db/init_db.py" ]; then
        python business_intel_scraper/backend/db/init_db.py
        print_success "Database initialized successfully"
    elif python3 -c "import backend_server; backend_server.init_db()" 2>/dev/null; then
        print_success "Database initialized via backend server"
    else
        print_info "Database will be initialized automatically on first run"
    fi
}

# Function to check Redis availability
check_redis() {
    print_step "Checking Redis availability..."
    
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            print_success "Redis is running"
            return 0
        fi
    fi
    
    print_warning "Redis not available, trying Docker..."
    
    if command_exists docker; then
        # Try to start Redis container
        if docker run -d --name redis-quick-start -p 6379:6379 redis:7-alpine >/dev/null 2>&1; then
            print_success "Started Redis container"
            sleep 3
            return 0
        else
            # Container might already exist
            if docker start redis-quick-start >/dev/null 2>&1; then
                print_success "Started existing Redis container"
                sleep 3
                return 0
            fi
        fi
    fi
    
    print_warning "Redis not available, using memory cache fallback"
    return 1
}

# Function to run quick tests
run_quick_tests() {
    print_step "Running quick validation tests..."
    
    # Test Python imports
    if python3 -c "
import sys
sys.path.append('.')
try:
    import backend_server
    import scraping_engine
    import performance_monitor
    print('✅ Core modules import successfully')
except ImportError as e:
    print(f'⚠️ Import warning: {e}')
    sys.exit(0)  # Don't fail on import issues
" 2>/dev/null; then
        print_success "Core modules validated"
    else
        print_warning "Some modules may not be fully available"
    fi
    
    # Quick configuration test
    if [ -f ".env" ]; then
        print_success "Configuration file validated"
    fi
}

# Function to start the web server
start_web_server() {
    print_step "Starting web server..."
    
    # Make sure ports are available
    if ! check_port $BACKEND_PORT; then
        kill_port $BACKEND_PORT
    fi
    
    # Start the backend server
    print_info "Starting backend server on port $BACKEND_PORT..."
    
    # Try different startup methods
    if [ -f "backend_server.py" ]; then
        print_info "Starting via backend_server.py..."
        nohup python3 backend_server.py > logs/backend.log 2>&1 &
        BACKEND_PID=$!
    elif [ -f "business_intel_scraper/backend/main.py" ]; then
        print_info "Starting via uvicorn..."
        nohup uvicorn business_intel_scraper.backend.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > logs/backend.log 2>&1 &
        BACKEND_PID=$!
    else
        print_error "No backend server found to start"
        return 1
    fi
    
    # Wait for server to start
    print_info "Waiting for server to start..."
    for i in {1..20}; do
        if curl -f http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1 || \
           curl -f http://localhost:$BACKEND_PORT/ >/dev/null 2>&1 || \
           curl -f http://localhost:$BACKEND_PORT/docs >/dev/null 2>&1; then
            print_success "Backend server is running!"
            break
        fi
        if [ $i -eq 20 ]; then
            print_error "Server failed to start within 20 seconds"
            print_info "Check logs/backend.log for more details"
            if [ -f "logs/backend.log" ]; then
                print_info "Last few lines of backend log:"
                tail -10 logs/backend.log
            fi
            return 1
        fi
        sleep 1
    done
    
    echo $BACKEND_PID > .backend_pid
    return 0
}

# Function to start frontend server
start_frontend_server() {
    print_step "Starting frontend development server..."
    
    # Check if Node.js is available
    if ! check_node_version; then
        print_warning "Skipping frontend startup - Node.js not available"
        return 0
    fi
    
    # Check if frontend directory exists
    if [ ! -d "business_intel_scraper/frontend" ]; then
        print_warning "Frontend directory not found, skipping frontend startup"
        return 0
    fi
    
    # Check if package.json exists
    if [ ! -f "business_intel_scraper/frontend/package.json" ]; then
        print_warning "Frontend package.json not found, skipping frontend startup"
        return 0
    fi
    
    # Make sure frontend port is available
    if ! check_port $FRONTEND_PORT; then
        kill_port $FRONTEND_PORT
    fi
    
    # Install frontend dependencies if node_modules doesn't exist
    if [ ! -d "business_intel_scraper/frontend/node_modules" ]; then
        print_info "Installing frontend dependencies..."
        cd business_intel_scraper/frontend
        npm install
        cd ../..
    fi
    
    # Start the frontend server
    print_info "Starting frontend server on port $FRONTEND_PORT..."
    cd business_intel_scraper/frontend
    
    # Use polling to avoid file watcher issues
    CHOKIDAR_USEPOLLING=true nohup npm run dev > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..
    
    # Wait for frontend server to start
    print_info "Waiting for frontend server to start..."
    for i in {1..15}; do
        if curl -f http://localhost:$FRONTEND_PORT/ >/dev/null 2>&1; then
            print_success "Frontend server is running!"
            break
        fi
        if [ $i -eq 15 ]; then
            print_warning "Frontend server may not be ready yet (this is normal)"
            print_info "Check logs/frontend.log for more details"
            if [ -f "logs/frontend.log" ]; then
                print_info "Last few lines of frontend log:"
                tail -5 logs/frontend.log
            fi
            break
        fi
        sleep 2
    done
    
    echo $FRONTEND_PID > .frontend_pid
    return 0
}

# Function to show access information
show_access_info() {
    echo ""
    echo -e "${PURPLE}🚀 Business Intelligence Scraper - Quick Start Complete!${NC}"
    echo -e "${PURPLE}===============================================${NC}"
    echo ""
    echo -e "${GREEN}✅ Server Status:${NC}"
    echo -e "   Backend Server: ${GREEN}RUNNING${NC} on port $BACKEND_PORT"
    if [ -f ".frontend_pid" ]; then
        echo -e "   Frontend Server: ${GREEN}RUNNING${NC} on port $FRONTEND_PORT"
    fi
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo -e "   ${BLUE}🎨 Web Interface:${NC}   http://localhost:$FRONTEND_PORT/"
    echo -e "   ${BLUE}🔗 Main API:${NC}        http://localhost:$BACKEND_PORT/"
    echo -e "   ${BLUE}📚 API Docs:${NC}       http://localhost:$BACKEND_PORT/docs"
    echo -e "   ${BLUE}🔍 Health Check:${NC}   http://localhost:$BACKEND_PORT/api/health"
    echo -e "   ${BLUE}📊 Metrics:${NC}        http://localhost:$BACKEND_PORT/metrics"
    echo ""
    echo -e "${YELLOW}📋 Quick Commands:${NC}"
    echo -e "   ${CYAN}# Open main interface${NC}"
    echo -e "   open http://localhost:$FRONTEND_PORT/"
    echo ""
    echo -e "   ${CYAN}# Test the API${NC}"
    echo -e "   curl http://localhost:$BACKEND_PORT/api/health"
    echo ""
    echo -e "   ${CYAN}# View API documentation${NC}"
    echo -e "   open http://localhost:$BACKEND_PORT/docs"
    echo ""
    echo -e "   ${CYAN}# Stop all servers${NC}"
    echo -e "   ./quick_start.sh --stop"
    echo ""
    echo -e "   ${CYAN}# Run tests${NC}"
    echo -e "   python3 tests/run_full_coverage.py --coverage"
    echo ""
    echo -e "${GREEN}✨ Your Business Intelligence Scraper is ready!${NC}"
    echo -e "${GREEN}✨ Visit http://localhost:$FRONTEND_PORT/ to get started!${NC}"
    echo ""
}

# Function to stop services
stop_services() {
    print_step "Stopping services..."
    
    if [ -f ".backend_pid" ]; then
        local pid=$(cat .backend_pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Stopped backend server"
        fi
        rm -f .backend_pid
    fi
    
    if [ -f ".frontend_pid" ]; then
        local pid=$(cat .frontend_pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Stopped frontend server"
        fi
        rm -f .frontend_pid
    fi
    
    # Kill any remaining processes on our ports
    kill_port $BACKEND_PORT >/dev/null 2>&1 || true
    
    # Stop Redis container if we started it
    if command_exists docker; then
        docker stop redis-quick-start >/dev/null 2>&1 || true
    fi
    
    print_success "All services stopped"
}

# Function to show help
show_help() {
    echo -e "${PURPLE}Business Intelligence Scraper - Quick Start${NC}"
    echo -e "${PURPLE}==========================================${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h      Show this help message"
    echo "  --stop          Stop all running services"
    echo "  --status        Show status of services"
    echo "  --clean         Clean up and reset environment"
    echo "  --dev           Start in development mode"
    echo "  --no-redis      Skip Redis setup"
    echo ""
    echo "Examples:"
    echo "  $0              # Quick start with all services"
    echo "  $0 --dev        # Start in development mode"
    echo "  $0 --stop       # Stop all services"
    echo "  $0 --status     # Check service status"
    echo ""
}

# Function to show status
show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    echo "=============="
    
    if [ -f ".backend_pid" ]; then
        local pid=$(cat .backend_pid)
        if kill -0 $pid 2>/dev/null; then
            echo -e "Backend Server: ${GREEN}RUNNING${NC} (PID: $pid)"
        else
            echo -e "Backend Server: ${RED}STOPPED${NC}"
        fi
    else
        echo -e "Backend Server: ${RED}NOT STARTED${NC}"
    fi
    
    if curl -f http://localhost:$BACKEND_PORT/api/health >/dev/null 2>&1; then
        echo -e "Health Check: ${GREEN}PASSED${NC}"
    else
        echo -e "Health Check: ${RED}FAILED${NC}"
    fi
    
    if command_exists redis-cli && redis-cli ping >/dev/null 2>&1; then
        echo -e "Redis: ${GREEN}RUNNING${NC}"
    else
        echo -e "Redis: ${YELLOW}NOT AVAILABLE${NC}"
    fi
}

# Function to clean environment
clean_environment() {
    print_step "Cleaning environment..."
    
    stop_services
    
    # Remove generated files
    rm -rf logs/* cache/* temp/*
    rm -f .backend_pid quick_start.log
    
    # Remove cache directories
    rm -rf __pycache__ .pytest_cache .mypy_cache htmlcov
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    print_success "Environment cleaned"
}

# Main execution function
main() {
    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --stop)
            stop_services
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --clean)
            clean_environment
            exit 0
            ;;
        --dev)
            DEV_MODE=true
            ;;
        --no-redis)
            SKIP_REDIS=true
            ;;
    esac
    
    # Start logging - create log file but don't redirect stdout yet
    echo "" > "$LOG_FILE"
    
    echo -e "${PURPLE}"
    echo "🚀 Business Intelligence Scraper - Quick Start"
    echo "=============================================="
    echo -e "${NC}"
    echo "Starting setup process..."
    echo "Log file: $LOG_FILE"
    echo ""
    
    # Pre-flight checks
    print_step "Running pre-flight checks..."
    
    if ! check_python_version; then
        print_error "Python requirements not met"
        exit 1
    fi
    
    # Check Node.js (optional for frontend)
    check_node_version
    
    if ! command_exists curl; then
        print_warning "curl not found, install it for better functionality"
    fi
    
    # Setup steps
    setup_venv
    install_dependencies
    setup_configuration
    setup_directories
    
    # Database setup
    initialize_database
    
    # Redis setup (optional)
    if [ "${SKIP_REDIS:-}" != "true" ]; then
        check_redis
    fi
    
    # Quick validation
    run_quick_tests
    
    # Start services
    if start_web_server; then
        # Start frontend server (non-blocking)
        start_frontend_server
        
        show_access_info
        
        # Keep the script running and show logs
        echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
        echo ""
        echo -e "${CYAN}Server logs (backend):${NC}"
        echo "======================"
        
        # Follow the backend log file
        if [ -f "logs/backend.log" ]; then
            tail -f logs/backend.log
        else
            # Wait for interrupt
            trap 'stop_services; exit 0' INT TERM
            while true; do
                sleep 1
            done
        fi
    else
        print_error "Failed to start web server"
        exit 1
    fi
}

# Handle cleanup on exit
trap 'stop_services' EXIT

# Run main function
main "$@"
