#!/bin/bash
# Monitoring System Startup Script
# Business Intelligence Scraper Platform v2.0.0

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✓ $1"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠ $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✗ $1"
}

# Configuration
MONITORING_DIR="$PROJECT_ROOT/monitoring"
MONITORING_CONFIG="$MONITORING_DIR/config.json"
MONITORING_SCRIPT="$PROJECT_ROOT/monitoring_system.py"
HEALTH_CHECK_SCRIPT="$MONITORING_DIR/health_check.sh"
PID_FILE="$MONITORING_DIR/monitoring.pid"
LOG_FILE="$MONITORING_DIR/monitoring.log"

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
        exit 1
    fi
    success "Python 3 found: $(python3 --version)"
    
    # Check required directories
    mkdir -p "$MONITORING_DIR"
    mkdir -p "$MONITORING_DIR/logs"
    mkdir -p "$MONITORING_DIR/data"
    
    # Check configuration file
    if [[ ! -f "$MONITORING_CONFIG" ]]; then
        error "Configuration file not found: $MONITORING_CONFIG"
        exit 1
    fi
    success "Configuration file found"
    
    # Check monitoring script
    if [[ ! -f "$MONITORING_SCRIPT" ]]; then
        error "Monitoring script not found: $MONITORING_SCRIPT"
        exit 1
    fi
    success "Monitoring script found"
    
    # Make health check script executable
    if [[ -f "$HEALTH_CHECK_SCRIPT" ]]; then
        chmod +x "$HEALTH_CHECK_SCRIPT"
        success "Health check script is executable"
    else
        warning "Health check script not found: $HEALTH_CHECK_SCRIPT"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Check if virtual environment exists
    if [[ -d "$PROJECT_ROOT/venv" ]]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        success "Activated virtual environment"
    else
        warning "No virtual environment found, using system Python"
    fi
    
    # Install required packages
    REQUIRED_PACKAGES=(
        "psutil"
        "requests"
        "psycopg2-binary"
        "redis"
        "fastapi"
        "uvicorn"
        "jinja2"
        "python-multipart"
    )
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            success "$package is already installed"
        else
            log "Installing $package..."
            pip install "$package" || {
                error "Failed to install $package"
                exit 1
            }
            success "Installed $package"
        fi
    done
}

# Function to check if monitoring is already running
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Function to start monitoring
start_monitoring() {
    log "Starting monitoring system..."
    
    if check_running; then
        warning "Monitoring system is already running (PID: $(cat "$PID_FILE"))"
        return 0
    fi
    
    # Activate virtual environment if it exists
    if [[ -d "$PROJECT_ROOT/venv" ]]; then
        source "$PROJECT_ROOT/venv/bin/activate"
    fi
    
    # Start monitoring in background
    cd "$PROJECT_ROOT"
    nohup python3 "$MONITORING_SCRIPT" > "$LOG_FILE" 2>&1 &
    local monitoring_pid=$!
    
    # Save PID
    echo "$monitoring_pid" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$monitoring_pid" > /dev/null 2>&1; then
        success "Monitoring system started successfully (PID: $monitoring_pid)"
        log "Log file: $LOG_FILE"
        log "PID file: $PID_FILE"
        return 0
    else
        error "Monitoring system failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop monitoring
stop_monitoring() {
    log "Stopping monitoring system..."
    
    if ! check_running; then
        warning "Monitoring system is not running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    kill "$pid" 2>/dev/null || {
        error "Failed to stop monitoring system (PID: $pid)"
        return 1
    }
    
    # Wait for process to stop
    local timeout=10
    while ps -p "$pid" > /dev/null 2>&1 && [[ $timeout -gt 0 ]]; do
        sleep 1
        ((timeout--))
    done
    
    if ps -p "$pid" > /dev/null 2>&1; then
        warning "Force killing monitoring system..."
        kill -9 "$pid" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    success "Monitoring system stopped"
}

# Function to restart monitoring
restart_monitoring() {
    log "Restarting monitoring system..."
    stop_monitoring
    sleep 2
    start_monitoring
}

# Function to show status
show_status() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        success "Monitoring system is running (PID: $pid)"
        
        # Show process info
        if command -v ps &> /dev/null; then
            log "Process info:"
            ps -p "$pid" -o pid,ppid,cmd,etime,pcpu,pmem 2>/dev/null || true
        fi
        
        # Show recent log entries
        if [[ -f "$LOG_FILE" ]]; then
            log "Recent log entries:"
            tail -n 5 "$LOG_FILE" 2>/dev/null || true
        fi
        
        # Run health check if available
        if [[ -x "$HEALTH_CHECK_SCRIPT" ]]; then
            log "Running health check..."
            "$HEALTH_CHECK_SCRIPT" --quiet || true
        fi
    else
        warning "Monitoring system is not running"
    fi
}

# Function to show logs
show_logs() {
    if [[ -f "$LOG_FILE" ]]; then
        log "Monitoring system logs:"
        tail -f "$LOG_FILE"
    else
        warning "Log file not found: $LOG_FILE"
    fi
}

# Function to run health check
run_health_check() {
    if [[ -x "$HEALTH_CHECK_SCRIPT" ]]; then
        log "Running health check..."
        "$HEALTH_CHECK_SCRIPT" "$@"
    else
        error "Health check script not found or not executable: $HEALTH_CHECK_SCRIPT"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    log "Validating configuration..."
    
    if python3 -c "
import json
import sys
try:
    with open('$MONITORING_CONFIG', 'r') as f:
        config = json.load(f)
    print('✓ Configuration file is valid JSON')
    
    # Check required sections
    required_sections = ['monitoring', 'services', 'intervals', 'thresholds', 'alerts']
    for section in required_sections:
        if section in config:
            print(f'✓ Section \"{section}\" found')
        else:
            print(f'✗ Missing required section: {section}')
            sys.exit(1)
    
    print('✓ Configuration validation passed')
except Exception as e:
    print(f'✗ Configuration validation failed: {e}')
    sys.exit(1)
"; then
        success "Configuration is valid"
    else
        error "Configuration validation failed"
        exit 1
    fi
}

# Function to show help
show_help() {
    cat << EOF
Business Intelligence Scraper Platform - Monitoring System Control

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    start           Start the monitoring system
    stop            Stop the monitoring system  
    restart         Restart the monitoring system
    status          Show monitoring system status
    logs            Show and follow monitoring logs
    health          Run health check
    validate        Validate configuration
    install         Install dependencies
    help            Show this help message

Options:
    --quiet         Suppress verbose output
    --force         Force operation (for stop/start)

Examples:
    $0 start                    # Start monitoring
    $0 status                   # Check status
    $0 health --json            # Run health check with JSON output
    $0 logs                     # Follow logs
    $0 restart                  # Restart monitoring

Files:
    Configuration:  $MONITORING_CONFIG
    Script:         $MONITORING_SCRIPT
    Health Check:   $HEALTH_CHECK_SCRIPT
    PID File:       $PID_FILE
    Log File:       $LOG_FILE

EOF
}

# Main execution
main() {
    local command="${1:-help}"
    
    case "$command" in
        start)
            check_prerequisites
            start_monitoring
            ;;
        stop)
            stop_monitoring
            ;;
        restart)
            check_prerequisites
            restart_monitoring
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        health)
            shift
            run_health_check "$@"
            ;;
        validate)
            validate_config
            ;;
        install)
            check_prerequisites
            install_dependencies
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
