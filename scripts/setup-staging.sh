#!/bin/bash

# ==============================================================================
# Business Intelligence Scraper Platform v3.0.0
# Staging Environment Setup Script
# ==============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STAGING_DIR="/opt/staging/scraper"
STAGING_COMPOSE="docker-compose.staging.yml"
STAGING_ENV=".env.staging"
BACKUP_DIR="/opt/backups/staging"
LOG_FILE="/var/log/staging-setup.log"

# Functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
    log "WARNING: $1"
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log "SUCCESS: $1"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
    log "INFO: $1"
}

check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "git" "openssl" "curl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    success "Prerequisites check completed"
}

create_staging_directories() {
    info "Creating staging directories..."
    
    local directories=(
        "$STAGING_DIR"
        "$BACKUP_DIR"
        "/var/log/scraper"
        "/opt/staging/data"
        "/opt/staging/config"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        chown -R 1000:1000 "$dir"
        chmod 755 "$dir"
    done
    
    success "Staging directories created"
}

generate_staging_config() {
    info "Generating staging configuration..."
    
    # Generate staging environment file
    cat > "$STAGING_DIR/$STAGING_ENV" << EOF
# Business Intelligence Scraper Platform - Staging Environment
# Generated on: $(date)

# Environment
NODE_ENV=staging
ENVIRONMENT=staging
DEBUG=true
LOG_LEVEL=debug

# Security
JWT_SECRET=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 16)
SESSION_SECRET=$(openssl rand -hex 24)

# Database Configuration
POSTGRES_HOST=postgres-staging
POSTGRES_PORT=5432
POSTGRES_DB=scraper_staging
POSTGRES_USER=scraper_staging
POSTGRES_PASSWORD=$(openssl rand -hex 16)
DATABASE_URL=postgresql://scraper_staging:\${POSTGRES_PASSWORD}@postgres-staging:5432/scraper_staging

# Redis Configuration
REDIS_HOST=redis-staging
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -hex 12)
REDIS_URL=redis://:\${REDIS_PASSWORD}@redis-staging:6379/0

# Application Configuration
APP_NAME="Business Intelligence Scraper (Staging)"
APP_VERSION=3.0.0
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000

# Features
ENABLE_AI_FEATURES=true
ENABLE_MONITORING=true
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true

# Monitoring
MONITORING_ENABLED=true
METRICS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=$(openssl rand -hex 12)

# External Services (Staging)
CRAWL_TIMEOUT=60
MAX_CONCURRENT_CRAWLS=5
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Email Configuration (Testing)
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=staging
SMTP_PASSWORD=staging

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=7
EOF

    # Set secure permissions
    chmod 600 "$STAGING_DIR/$STAGING_ENV"
    chown 1000:1000 "$STAGING_DIR/$STAGING_ENV"
    
    success "Staging configuration generated"
}

create_staging_compose() {
    info "Creating staging Docker Compose configuration..."
    
    cat > "$STAGING_DIR/$STAGING_COMPOSE" << 'EOF'
version: '3.8'

services:
  # Backend Application
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: scraper-app-staging
    restart: unless-stopped
    env_file:
      - .env.staging
    ports:
      - "8001:8000"  # Different port for staging
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - postgres-staging
      - redis-staging
    networks:
      - scraper-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Frontend Application
  frontend:
    build:
      context: ./business_intel_scraper/frontend
      dockerfile: Dockerfile
      target: production
    container_name: scraper-frontend-staging
    restart: unless-stopped
    ports:
      - "3001:3000"  # Different port for staging
    environment:
      - REACT_APP_API_URL=http://localhost:8001
      - REACT_APP_ENVIRONMENT=staging
    depends_on:
      - app
    networks:
      - scraper-staging
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL Database
  postgres-staging:
    image: postgres:15-alpine
    container_name: scraper-postgres-staging
    restart: unless-stopped
    env_file:
      - .env.staging
    ports:
      - "5433:5432"  # Different port for staging
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
      - ./business_intel_scraper/database/init:/docker-entrypoint-initdb.d
    networks:
      - scraper-staging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis-staging:
    image: redis:7-alpine
    container_name: scraper-redis-staging
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6380:6379"  # Different port for staging
    volumes:
      - redis_staging_data:/data
    networks:
      - scraper-staging
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Monitoring - Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: scraper-prometheus-staging
    restart: unless-stopped
    ports:
      - "9091:9090"  # Different port for staging
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_staging_data:/prometheus
    networks:
      - scraper-staging
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  # Monitoring - Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: scraper-grafana-staging
    restart: unless-stopped
    ports:
      - "3002:3000"  # Different port for staging
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_staging_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    networks:
      - scraper-staging

  # Email Testing - MailHog
  mailhog:
    image: mailhog/mailhog:latest
    container_name: scraper-mailhog-staging
    restart: unless-stopped
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
    networks:
      - scraper-staging

volumes:
  postgres_staging_data:
    driver: local
  redis_staging_data:
    driver: local
  prometheus_staging_data:
    driver: local
  grafana_staging_data:
    driver: local

networks:
  scraper-staging:
    driver: bridge
    name: scraper-staging-network
EOF

    success "Staging Docker Compose configuration created"
}

setup_monitoring() {
    info "Setting up monitoring configuration..."
    
    # Create monitoring directory
    mkdir -p "$STAGING_DIR/monitoring"
    
    # Prometheus configuration
    cat > "$STAGING_DIR/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'scraper-app'
    static_configs:
      - targets: ['app:8000']
    scrape_interval: 10s
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-staging:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-staging:6379']
    scrape_interval: 30s
EOF

    # Create Grafana provisioning
    mkdir -p "$STAGING_DIR/monitoring/grafana/datasources"
    mkdir -p "$STAGING_DIR/monitoring/grafana/dashboards"
    
    cat > "$STAGING_DIR/monitoring/grafana/datasources/prometheus.yml" << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    success "Monitoring configuration setup completed"
}

deploy_staging() {
    info "Deploying staging environment..."
    
    cd "$STAGING_DIR"
    
    # Pull latest images
    docker-compose -f "$STAGING_COMPOSE" pull
    
    # Build and start services
    docker-compose -f "$STAGING_COMPOSE" up -d --build
    
    # Wait for services to be healthy
    info "Waiting for services to become healthy..."
    sleep 30
    
    # Check service health
    local services=("app" "frontend" "postgres-staging" "redis-staging")
    for service in "${services[@]}"; do
        if docker-compose -f "$STAGING_COMPOSE" ps "$service" | grep -q "Up (healthy)"; then
            success "Service $service is healthy"
        else
            warning "Service $service may not be fully ready"
        fi
    done
    
    success "Staging environment deployed"
}

run_health_checks() {
    info "Running health checks..."
    
    local checks=(
        "http://localhost:8001/health:Backend API"
        "http://localhost:3001:Frontend"
        "http://localhost:3002:Grafana"
        "http://localhost:8025:MailHog"
    )
    
    for check in "${checks[@]}"; do
        local url="${check%:*}"
        local name="${check#*:}"
        
        if curl -f -s "$url" > /dev/null; then
            success "$name is accessible"
        else
            warning "$name is not accessible at $url"
        fi
    done
}

create_staging_backup() {
    info "Creating initial staging backup..."
    
    local backup_name="staging-initial-$(date +%Y%m%d-%H%M%S)"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    mkdir -p "$backup_path"
    
    # Backup database
    docker exec scraper-postgres-staging pg_dump -U scraper_staging scraper_staging > "$backup_path/database.sql"
    
    # Backup Redis data
    docker exec scraper-redis-staging redis-cli --rdb /data/dump.rdb
    docker cp scraper-redis-staging:/data/dump.rdb "$backup_path/"
    
    # Backup configuration
    cp -r "$STAGING_DIR" "$backup_path/config"
    
    # Create backup manifest
    cat > "$backup_path/manifest.json" << EOF
{
    "backup_name": "$backup_name",
    "timestamp": "$(date -Iseconds)",
    "version": "3.0.0",
    "environment": "staging",
    "components": [
        "database",
        "redis",
        "configuration"
    ]
}
EOF

    success "Initial staging backup created: $backup_path"
}

print_staging_info() {
    echo
    echo "==============================================="
    echo "🎉 STAGING ENVIRONMENT SETUP COMPLETE"
    echo "==============================================="
    echo
    echo "📊 Service URLs:"
    echo "   • Backend API:  http://localhost:8001"
    echo "   • Frontend:     http://localhost:3001"
    echo "   • Grafana:      http://localhost:3002"
    echo "   • MailHog:      http://localhost:8025"
    echo "   • Prometheus:   http://localhost:9091"
    echo
    echo "🔑 Default Credentials:"
    echo "   • Grafana: admin / $(grep GRAFANA_ADMIN_PASSWORD "$STAGING_DIR/$STAGING_ENV" | cut -d'=' -f2)"
    echo
    echo "📁 Important Paths:"
    echo "   • Staging Directory: $STAGING_DIR"
    echo "   • Backup Directory:  $BACKUP_DIR"
    echo "   • Log File:         $LOG_FILE"
    echo
    echo "🛠️  Management Commands:"
    echo "   • View logs:        cd $STAGING_DIR && docker-compose -f $STAGING_COMPOSE logs -f"
    echo "   • Restart services: cd $STAGING_DIR && docker-compose -f $STAGING_COMPOSE restart"
    echo "   • Stop staging:     cd $STAGING_DIR && docker-compose -f $STAGING_COMPOSE down"
    echo "   • Start staging:    cd $STAGING_DIR && docker-compose -f $STAGING_COMPOSE up -d"
    echo
    echo "📝 Next Steps:"
    echo "   1. Test all functionality in staging environment"
    echo "   2. Run integration tests"
    echo "   3. Validate performance benchmarks"
    echo "   4. Review security scan results"
    echo "   5. Approve for production deployment"
    echo
    echo "==============================================="
}

main() {
    echo "🚀 Business Intelligence Scraper Platform v3.0.0"
    echo "Staging Environment Setup"
    echo "========================================"
    echo
    
    check_prerequisites
    create_staging_directories
    generate_staging_config
    create_staging_compose
    setup_monitoring
    deploy_staging
    run_health_checks
    create_staging_backup
    print_staging_info
    
    success "Staging environment setup completed successfully!"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
