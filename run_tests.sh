#!/bin/bash

# =============================================================================
# Comprehensive Test Execution Script for Business Intelligence Scraper
# =============================================================================
# 
# This script provides comprehensive testing capabilities with multiple
# execution modes, reporting options, and CI/CD integration.
#
# Usage:
#   ./run_tests.sh [OPTIONS] [TEST_CATEGORY]
#
# Test Categories:
#   all         - Run all tests (default)
#   unit        - Run unit tests only
#   integration - Run integration tests only
#   performance - Run performance tests only
#   security    - Run security tests only
#   api         - Run API tests only
#   smoke       - Run smoke tests only
#   fast        - Run fast tests only
#   slow        - Run slow tests only
#
# Options:
#   --coverage  - Generate coverage report
#   --html      - Generate HTML coverage report
#   --xml       - Generate XML coverage report
#   --parallel  - Run tests in parallel
#   --verbose   - Verbose output
#   --quiet     - Minimal output
#   --failfast  - Stop on first failure
#   --profile   - Profile test execution
#   --watch     - Watch mode for development
#   --ci        - CI/CD mode with appropriate settings
#   --help      - Show this help message
#
# Author: Business Intelligence Scraper Team
# Version: 2.0.0
# License: MIT
# =============================================================================

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$PROJECT_ROOT/tests"
VENV_ACTIVATE="$PROJECT_ROOT/venv/bin/activate"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default settings
COVERAGE=false
HTML_REPORT=false
XML_REPORT=false
PARALLEL=false
VERBOSE=false
QUIET=false
FAILFAST=false
PROFILE=false
WATCH=false
CI_MODE=false
TEST_CATEGORY="all"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to show help
show_help() {
    cat << EOF
Business Intelligence Scraper - Comprehensive Test Runner

Usage: $0 [OPTIONS] [TEST_CATEGORY]

Test Categories:
    all         Run all tests (default)
    unit        Run unit tests only
    integration Run integration tests only
    performance Run performance tests only
    security    Run security tests only
    api         Run API tests only
    smoke       Run smoke tests only
    fast        Run fast tests only (< 1 second)
    slow        Run slow tests only (> 1 second)

Options:
    --coverage      Generate coverage report
    --html          Generate HTML coverage report
    --xml           Generate XML coverage report
    --parallel      Run tests in parallel
    --verbose       Verbose output
    --quiet         Minimal output
    --failfast      Stop on first failure
    --profile       Profile test execution
    --watch         Watch mode for development
    --ci            CI/CD mode with appropriate settings
    --help          Show this help message

Examples:
    $0                              # Run all tests
    $0 unit --coverage              # Run unit tests with coverage
    $0 integration --verbose        # Run integration tests verbosely
    $0 security --failfast          # Run security tests, stop on first failure
    $0 performance --profile        # Run performance tests with profiling
    $0 --ci                         # Run in CI/CD mode
    $0 smoke --parallel             # Run smoke tests in parallel

Environment Variables:
    PYTEST_WORKERS    Number of parallel workers (default: auto)
    TEST_TIMEOUT      Test timeout in seconds (default: 300)
    COVERAGE_THRESHOLD Minimum coverage percentage (default: 80)

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --coverage)
                COVERAGE=true
                shift
                ;;
            --html)
                HTML_REPORT=true
                COVERAGE=true
                shift
                ;;
            --xml)
                XML_REPORT=true
                COVERAGE=true
                shift
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --quiet)
                QUIET=true
                shift
                ;;
            --failfast)
                FAILFAST=true
                shift
                ;;
            --profile)
                PROFILE=true
                shift
                ;;
            --watch)
                WATCH=true
                shift
                ;;
            --ci)
                CI_MODE=true
                COVERAGE=true
                XML_REPORT=true
                FAILFAST=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            unit|integration|performance|security|api|smoke|fast|slow|all)
                TEST_CATEGORY="$1"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/pytest.ini" ]]; then
        print_error "pytest.ini not found. Please run from project root."
        exit 1
    fi
    
    # Check if virtual environment exists and activate it
    if [[ -f "$VENV_ACTIVATE" ]]; then
        print_status "Activating virtual environment..."
        source "$VENV_ACTIVATE"
    else
        print_warning "Virtual environment not found at $VENV_ACTIVATE"
        print_status "Using system Python environment"
    fi
    
    # Check if pytest is installed
    if ! command -v pytest &> /dev/null; then
        print_error "pytest is not installed. Please install it:"
        echo "pip install pytest pytest-cov pytest-xdist pytest-mock"
        exit 1
    fi
    
    # Check if required test dependencies are available
    print_status "Checking test dependencies..."
    python -c "import pytest, pytest_cov" 2>/dev/null || {
        print_error "Required test dependencies not found. Installing..."
        pip install pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio
    }
    
    print_success "Prerequisites check completed"
}

# Function to build pytest command
build_pytest_command() {
    local cmd="pytest"
    
    # Add test directory
    cmd="$cmd $TESTS_DIR"
    
    # Add test category markers
    case $TEST_CATEGORY in
        unit)
            cmd="$cmd -m 'unit and not slow'"
            ;;
        integration)
            cmd="$cmd -m 'integration'"
            ;;
        performance)
            cmd="$cmd -m 'performance or slow'"
            ;;
        security)
            cmd="$cmd -m 'security'"
            ;;
        api)
            cmd="$cmd -m 'api'"
            ;;
        smoke)
            cmd="$cmd -m 'smoke'"
            ;;
        fast)
            cmd="$cmd -m 'not slow'"
            ;;
        slow)
            cmd="$cmd -m 'slow'"
            ;;
        all)
            # Run all tests
            ;;
    esac
    
    # Add coverage options
    if [[ "$COVERAGE" == true ]]; then
        cmd="$cmd --cov=business_intel_scraper --cov=. --cov-report=term-missing"
        
        if [[ "$HTML_REPORT" == true ]]; then
            cmd="$cmd --cov-report=html:htmlcov"
        fi
        
        if [[ "$XML_REPORT" == true ]]; then
            cmd="$cmd --cov-report=xml:coverage.xml"
        fi
        
        # Set coverage threshold
        local threshold=${COVERAGE_THRESHOLD:-80}
        cmd="$cmd --cov-fail-under=$threshold"
    fi
    
    # Add parallel execution
    if [[ "$PARALLEL" == true ]]; then
        local workers=${PYTEST_WORKERS:-auto}
        cmd="$cmd -n $workers"
    fi
    
    # Add verbosity options
    if [[ "$VERBOSE" == true ]]; then
        cmd="$cmd -v --tb=long"
    elif [[ "$QUIET" == true ]]; then
        cmd="$cmd -q --tb=line"
    fi
    
    # Add fail fast option
    if [[ "$FAILFAST" == true ]]; then
        cmd="$cmd -x"
    fi
    
    # Add profiling
    if [[ "$PROFILE" == true ]]; then
        cmd="$cmd --durations=20"
    fi
    
    # Add CI-specific options
    if [[ "$CI_MODE" == true ]]; then
        cmd="$cmd --junitxml=test-results.xml --strict-markers --tb=short"
    fi
    
    # Add timeout
    local timeout=${TEST_TIMEOUT:-300}
    cmd="$cmd --timeout=$timeout"
    
    echo "$cmd"
}

# Function to run tests
run_tests() {
    print_header "Running Tests - Category: $TEST_CATEGORY"
    
    # Build and display command
    local pytest_cmd=$(build_pytest_command)
    
    if [[ "$VERBOSE" == true ]]; then
        print_status "Executing: $pytest_cmd"
    fi
    
    # Create reports directory
    mkdir -p "$PROJECT_ROOT/test-reports"
    
    # Set environment variables for testing
    export TESTING=1
    export DATABASE_URL="sqlite:///:memory:"
    export LOG_LEVEL="WARNING"
    
    # Run tests in watch mode or normal mode
    if [[ "$WATCH" == true ]]; then
        print_status "Running in watch mode (press Ctrl+C to stop)..."
        python -m pytest_watch --runner "pytest" -- $pytest_cmd
    else
        # Execute pytest command
        if eval "$pytest_cmd"; then
            print_success "All tests passed!"
            return 0
        else
            print_error "Some tests failed!"
            return 1
        fi
    fi
}

# Function to generate reports
generate_reports() {
    if [[ "$COVERAGE" == true ]]; then
        print_header "Generating Coverage Reports"
        
        # Generate coverage summary
        echo "Coverage Summary:"
        coverage report --show-missing
        
        if [[ "$HTML_REPORT" == true ]]; then
            print_status "HTML coverage report generated: htmlcov/index.html"
            
            # Try to open in browser (if available)
            if command -v xdg-open &> /dev/null; then
                xdg-open "htmlcov/index.html" &>/dev/null &
            elif command -v open &> /dev/null; then
                open "htmlcov/index.html" &>/dev/null &
            fi
        fi
        
        if [[ "$XML_REPORT" == true ]]; then
            print_status "XML coverage report generated: coverage.xml"
        fi
    fi
}

# Function to cleanup
cleanup() {
    print_header "Cleaning Up"
    
    # Remove temporary files
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
    find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove test databases
    rm -f "$PROJECT_ROOT"/*.db-test 2>/dev/null || true
    
    print_status "Cleanup completed"
}

# Function to show summary
show_summary() {
    print_header "Test Execution Summary"
    
    echo "Test Category: $TEST_CATEGORY"
    echo "Coverage Enabled: $COVERAGE"
    echo "Parallel Execution: $PARALLEL"
    echo "CI Mode: $CI_MODE"
    
    if [[ -f "test-results.xml" ]]; then
        print_status "JUnit XML report: test-results.xml"
    fi
    
    if [[ -d "htmlcov" ]]; then
        print_status "HTML coverage report: htmlcov/index.html"
    fi
    
    if [[ -f "coverage.xml" ]]; then
        print_status "XML coverage report: coverage.xml"
    fi
}

# Main execution function
main() {
    print_header "Business Intelligence Scraper - Test Runner"
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    # Check prerequisites
    check_prerequisites
    
    # Run tests
    if run_tests; then
        # Generate reports
        generate_reports
        
        # Show summary
        show_summary
        
        print_success "Test execution completed successfully!"
        exit 0
    else
        print_error "Test execution failed!"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"
