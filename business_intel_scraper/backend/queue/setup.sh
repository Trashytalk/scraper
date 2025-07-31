#!/bin/bash

# Queue System Setup Script
# Comprehensive setup for the distributed crawling queue system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
QUEUE_DIR="$PROJECT_ROOT/business_intel_scraper/backend/queue"

# Default values
BACKEND="redis"
ENVIRONMENT="development"
DOCKER_COMPOSE=false
INSTALL_DEPS=true
INIT_DB=true
START_SERVICES=false
INTERACTIVE=true

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "  Business Intelligence Scraper"
    echo "  Distributed Queue System Setup"
    echo "=============================================="
    echo -e "${NC}"
}

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -b, --backend BACKEND      Queue backend (redis|kafka|sqs|memory) [default: redis]
    -e, --environment ENV      Environment (development|testing|production) [default: development]
    -d, --docker              Use Docker Compose for services
    -s, --start               Start services after setup
    --no-deps                 Skip dependency installation
    --no-db                   Skip database initialization
    --non-interactive         Run without prompts
    -h, --help                Show this help message

Examples:
    $0                                    # Interactive setup with Redis
    $0 -b kafka -e production -d -s     # Production Kafka setup with Docker
    $0 -b memory --no-deps --non-interactive  # Memory backend, no deps, no prompts

EOF
}

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -b|--backend)
            BACKEND="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--docker)
            DOCKER_COMPOSE=true
            shift
            ;;
        -s|--start)
            START_SERVICES=true
            shift
            ;;
        --no-deps)
            INSTALL_DEPS=false
            shift
            ;;
        --no-db)
            INIT_DB=false
            shift
            ;;
        --non-interactive)
            INTERACTIVE=false
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate backend
case $BACKEND in
    redis|kafka|sqs|memory)
        ;;
    *)
        error "Invalid backend: $BACKEND. Must be one of: redis, kafka, sqs, memory"
        ;;
esac

# Validate environment
case $ENVIRONMENT in
    development|testing|production)
        ;;
    *)
        error "Invalid environment: $ENVIRONMENT. Must be one of: development, testing, production"
        ;;
esac

check_requirements() {
    log "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not installed"
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    required_version="3.8"
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        error "Python 3.8+ is required, found: $python_version"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        error "pip3 is required but not installed"
    fi
    
    # Check Docker if needed
    if [ "$DOCKER_COMPOSE" = true ]; then
        if ! command -v docker &> /dev/null; then
            error "Docker is required but not installed"
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            error "Docker Compose is required but not installed"
        fi
    fi
    
    # Check backend-specific requirements
    case $BACKEND in
        redis)
            if [ "$DOCKER_COMPOSE" = false ] && ! command -v redis-server &> /dev/null; then
                warn "Redis server not found. Will use Docker or remote Redis."
            fi
            ;;
        kafka)
            if [ "$DOCKER_COMPOSE" = false ]; then
                warn "Kafka not found locally. Will use Docker or remote Kafka."
            fi
            ;;
        sqs)
            log "SQS backend selected - AWS credentials required"
            ;;
        memory)
            log "Memory backend selected - no external services required"
            ;;
    esac
    
    log "System requirements check complete"
}

install_dependencies() {
    if [ "$INSTALL_DEPS" = false ]; then
        log "Skipping dependency installation"
        return
    fi
    
    log "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install base requirements
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    fi
    
    # Install consolidated requirements if available
    if [ -f "requirements-consolidated.txt" ]; then
        pip3 install -r requirements-consolidated.txt
    fi
    
    # Install backend-specific dependencies
    case $BACKEND in
        redis)
            pip3 install redis>=4.5.0 hiredis>=2.2.0
            ;;
        kafka)
            pip3 install kafka-python>=2.0.0
            ;;
        sqs)
            pip3 install boto3>=1.26.0 botocore>=1.29.0
            ;;
    esac
    
    # Install CLI and monitoring dependencies
    pip3 install rich>=13.0.0 click>=8.0.0 pyyaml>=6.0
    
    # Install OCR dependencies
    pip3 install pytesseract>=0.3.10 Pillow>=9.0.0 pdf2image>=3.1.0
    
    log "Dependencies installed successfully"
}

setup_configuration() {
    log "Setting up configuration..."
    
    CONFIG_FILE="$QUEUE_DIR/config.${ENVIRONMENT}.yaml"
    
    # Create configuration directory
    mkdir -p "$QUEUE_DIR"
    
    # Generate configuration file
    cat > "$CONFIG_FILE" << EOF
# Queue System Configuration - $ENVIRONMENT
queue_backend: $BACKEND
environment: $ENVIRONMENT
debug: $([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false")

# Worker Configuration
crawl:
  num_crawl_workers: $([ "$ENVIRONMENT" = "production" ] && echo "10" || echo "5")
  crawl_delay: $([ "$ENVIRONMENT" = "production" ] && echo "1.0" || echo "0.5")
  timeout: 30.0
  max_retries: 3
  max_depth: 3
  max_pages_per_domain: 1000

parse:
  num_parse_workers: $([ "$ENVIRONMENT" = "production" ] && echo "5" || echo "3")
  parse_timeout: 60.0
  enable_ocr: true
  ocr_engines: ["tesseract"]

# Database Configuration
database:
  url: postgresql://user:password@localhost:5432/business_intel
  pool_size: 5
  max_overflow: 10

# Storage Configuration
storage:
  type: s3
  endpoint: http://localhost:9000
  access_key: minioadmin
  secret_key: minioadmin
  bucket: business-intel-storage

# Monitoring Configuration
monitoring:
  enable_metrics: true
  log_level: $([ "$ENVIRONMENT" = "development" ] && echo "DEBUG" || echo "INFO")
  enable_health_checks: true

# Security Configuration
security:
  enable_auth: $([ "$ENVIRONMENT" = "production" ] && echo "true" || echo "false")
  rate_limit_enabled: true
EOF

    # Add backend-specific configuration
    case $BACKEND in
        redis)
            cat >> "$CONFIG_FILE" << EOF

# Redis Configuration
redis:
  url: redis://localhost:6379/0
  max_connections: 20
  socket_timeout: 30.0
EOF
            ;;
        kafka)
            cat >> "$CONFIG_FILE" << EOF

# Kafka Configuration
kafka:
  bootstrap_servers: localhost:9092
  group_id: queue-workers-$ENVIRONMENT
  topic_config:
    num_partitions: $([ "$ENVIRONMENT" = "production" ] && echo "12" || echo "6")
    replication_factor: 1
EOF
            ;;
        sqs)
            cat >> "$CONFIG_FILE" << EOF

# SQS Configuration
sqs:
  region_name: us-west-2
  queue_prefix: queue-system-$ENVIRONMENT
  visibility_timeout: 300
  enable_fifo: false
EOF
            ;;
    esac
    
    log "Configuration saved to: $CONFIG_FILE"
}

setup_database() {
    if [ "$INIT_DB" = false ]; then
        log "Skipping database initialization"
        return
    fi
    
    log "Setting up database..."
    
    # Check if PostgreSQL is available
    if command -v psql &> /dev/null; then
        log "Initializing PostgreSQL database..."
        
        # Create database if it doesn't exist
        createdb business_intel 2>/dev/null || true
        
        # Run initialization script
        if [ -f "$QUEUE_DIR/init-db.sql" ]; then
            psql -d business_intel -f "$QUEUE_DIR/init-db.sql"
            log "Database initialized successfully"
        else
            warn "Database initialization script not found"
        fi
    elif [ "$DOCKER_COMPOSE" = true ]; then
        log "Database will be initialized via Docker Compose"
    else
        warn "PostgreSQL not found. Database initialization skipped."
        warn "Please ensure PostgreSQL is available or use Docker Compose"
    fi
}

setup_docker_services() {
    if [ "$DOCKER_COMPOSE" = false ]; then
        return
    fi
    
    log "Setting up Docker services..."
    
    COMPOSE_FILE="$QUEUE_DIR/docker-compose.queue.yml"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
    fi
    
    cd "$QUEUE_DIR"
    
    # Create Docker network
    docker network create queue-network 2>/dev/null || true
    
    # Start core services based on backend
    case $BACKEND in
        redis)
            log "Starting Redis services..."
            docker-compose -f docker-compose.queue.yml up -d redis-queue redis-commander
            ;;
        kafka)
            log "Starting Kafka services..."
            docker-compose -f docker-compose.queue.yml up -d zookeeper kafka kafka-ui
            ;;
        sqs)
            log "SQS backend - no local services needed"
            ;;
        memory)
            log "Memory backend - no external services needed"
            ;;
    esac
    
    # Start supporting services
    log "Starting supporting services..."
    docker-compose -f docker-compose.queue.yml up -d postgres minio
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 10
    
    # Verify services
    case $BACKEND in
        redis)
            docker-compose -f docker-compose.queue.yml exec redis-queue redis-cli ping || warn "Redis not responding"
            ;;
        kafka)
            # Wait a bit more for Kafka
            sleep 20
            ;;
    esac
    
    log "Docker services started successfully"
}

start_queue_system() {
    if [ "$START_SERVICES" = false ]; then
        return
    fi
    
    log "Starting queue system..."
    
    CONFIG_FILE="$QUEUE_DIR/config.${ENVIRONMENT}.yaml"
    
    cd "$PROJECT_ROOT"
    
    # Start queue API
    log "Starting queue API..."
    python3 -m business_intel_scraper.backend.queue.api --config "$CONFIG_FILE" &
    API_PID=$!
    
    # Start workers
    log "Starting workers..."
    python3 -m business_intel_scraper.backend.queue.worker --type crawl --config "$CONFIG_FILE" &
    CRAWL_PID=$!
    
    python3 -m business_intel_scraper.backend.queue.worker --type parse --config "$CONFIG_FILE" &
    PARSE_PID=$!
    
    # Wait a moment for startup
    sleep 5
    
    # Check if processes are running
    if kill -0 $API_PID 2>/dev/null; then
        log "Queue API started (PID: $API_PID)"
    else
        error "Failed to start queue API"
    fi
    
    if kill -0 $CRAWL_PID 2>/dev/null; then
        log "Crawl worker started (PID: $CRAWL_PID)"
    else
        warn "Failed to start crawl worker"
    fi
    
    if kill -0 $PARSE_PID 2>/dev/null; then
        log "Parse worker started (PID: $PARSE_PID)"
    else
        warn "Failed to start parse worker"
    fi
    
    log "Queue system is running!"
    log "API: http://localhost:8001"
    if [ "$BACKEND" = "redis" ]; then
        log "Redis Commander: http://localhost:8082"
    elif [ "$BACKEND" = "kafka" ]; then
        log "Kafka UI: http://localhost:8083"
    fi
    log "MinIO Console: http://localhost:9001"
    
    # Save PIDs for cleanup
    echo "$API_PID $CRAWL_PID $PARSE_PID" > "$QUEUE_DIR/.pids"
    
    log "PIDs saved to $QUEUE_DIR/.pids for cleanup"
}

interactive_setup() {
    if [ "$INTERACTIVE" = false ]; then
        return
    fi
    
    echo
    echo -e "${BLUE}Interactive Setup${NC}"
    echo "Current configuration:"
    echo "  Backend: $BACKEND"
    echo "  Environment: $ENVIRONMENT"
    echo "  Docker Compose: $DOCKER_COMPOSE"
    echo "  Start Services: $START_SERVICES"
    echo
    
    read -p "Continue with this configuration? [Y/n]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
    
    # Additional setup options
    echo
    echo "Additional setup options:"
    
    if [ "$BACKEND" = "sqs" ]; then
        echo
        echo "AWS SQS Configuration:"
        read -p "AWS Region [us-west-2]: " aws_region
        aws_region=${aws_region:-us-west-2}
        
        echo "Note: Ensure AWS credentials are configured via:"
        echo "  - AWS CLI: aws configure"
        echo "  - Environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
        echo "  - IAM role (if running on EC2)"
    fi
    
    echo
    read -p "Create sample configuration files? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Create sample seed URLs file
        cat > "$PROJECT_ROOT/sample-seeds.txt" << EOF
https://example.com
https://business-directory.com
https://company-registry.gov
EOF
        log "Sample seed URLs created: $PROJECT_ROOT/sample-seeds.txt"
        
        # Create sample job configuration
        cat > "$PROJECT_ROOT/sample-job.json" << EOF
{
    "job_id": "sample-job-001",
    "job_name": "Sample Crawl Job",
    "description": "A sample crawling job for testing",
    "max_depth": 2,
    "max_pages": 100,
    "crawl_delay": 1.0,
    "urls": [
        "https://example.com",
        "https://business-directory.com"
    ]
}
EOF
        log "Sample job configuration created: $PROJECT_ROOT/sample-job.json"
    fi
}

run_tests() {
    if [ "$INTERACTIVE" = false ]; then
        return
    fi
    
    echo
    read -p "Run basic system tests? [Y/n]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        log "Running basic tests..."
        
        cd "$PROJECT_ROOT"
        
        # Test imports
        python3 -c "
from business_intel_scraper.backend.queue import create_queue_manager, QueueBackend
from business_intel_scraper.backend.queue.config import QueueSystemConfig
print('✓ Queue system imports successful')
"
        
        # Test configuration
        python3 -c "
from business_intel_scraper.backend.queue.config import get_${ENVIRONMENT}_config
config = get_${ENVIRONMENT}_config()
errors = config.validate()
if errors:
    print('✗ Configuration validation failed:')
    for error in errors:
        print(f'  - {error}')
    exit(1)
else:
    print('✓ Configuration validation passed')
"
        
        log "Basic tests completed successfully"
    fi
}

cleanup_on_exit() {
    if [ -f "$QUEUE_DIR/.pids" ]; then
        log "Cleaning up processes..."
        PIDS=$(cat "$QUEUE_DIR/.pids")
        for pid in $PIDS; do
            kill $pid 2>/dev/null || true
        done
        rm -f "$QUEUE_DIR/.pids"
    fi
}

# Set up cleanup on exit
trap cleanup_on_exit EXIT

# Main setup sequence
main() {
    print_header
    
    interactive_setup
    
    check_requirements
    
    install_dependencies
    
    setup_configuration
    
    setup_database
    
    setup_docker_services
    
    start_queue_system
    
    run_tests
    
    echo
    log "Queue system setup completed successfully!"
    echo
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Check system status: python3 -m business_intel_scraper.backend.queue.cli system health"
    echo "2. View queue statistics: python3 -m business_intel_scraper.backend.queue.cli monitor stats"
    echo "3. Add seed URLs: python3 -m business_intel_scraper.backend.queue.cli seed add --job-id test-job https://example.com"
    echo "4. Monitor workers: python3 -m business_intel_scraper.backend.queue.cli worker list"
    echo
    echo "Configuration file: $QUEUE_DIR/config.${ENVIRONMENT}.yaml"
    echo "Documentation: See README.md and docs/ directory"
    echo
    
    if [ "$START_SERVICES" = true ]; then
        echo -e "${YELLOW}Services are running in the background.${NC}"
        echo "To stop services: pkill -f queue || docker-compose -f $QUEUE_DIR/docker-compose.queue.yml down"
        echo
        echo "Press Ctrl+C to stop all services and exit"
        
        # Wait for interrupt
        while true; do
            sleep 60
        done
    fi
}

# Run main function
main "$@"
