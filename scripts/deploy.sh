#!/bin/bash
# Production Deployment Script
# Business Intelligence Scraper - Enterprise Deployment

set -e

# Configuration
COMPOSE_FILE="docker-compose.production-v3.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups"
LOG_FILE="./logs/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        warning "Environment file $ENV_FILE not found, creating template..."
        create_env_template
    fi
    
    success "Prerequisites check completed"
}

# Create environment template
create_env_template() {
    cat > "$ENV_FILE" << EOF
# Production Environment Configuration
# Business Intelligence Scraper

# Database
POSTGRES_USER=bisuser
POSTGRES_PASSWORD=secure_password_change_me
POSTGRES_DB=business_intelligence

# Redis
REDIS_PASSWORD=redis_secure_password

# Application
JWT_SECRET_KEY=production_jwt_secret_change_me
API_SECRET_KEY=production_api_secret_change_me
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# Monitoring
GRAFANA_PASSWORD=admin123

# Build
BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
VERSION=3.0.0
VCS_REF=main

# Logging
LOG_LEVEL=INFO
WORKERS=4
EOF
    warning "Please edit $ENV_FILE with your production values"
}

# Backup existing data
backup_data() {
    if [ "$1" = "--skip-backup" ]; then
        log "Skipping backup as requested"
        return
    fi
    
    log "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup timestamp
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    # Database backup
    if docker ps | grep -q bis_postgres_prod; then
        log "Backing up PostgreSQL database..."
        docker exec bis_postgres_prod pg_dump -U ${POSTGRES_USER:-bisuser} business_intelligence > "$BACKUP_DIR/postgres_backup_$BACKUP_TIMESTAMP.sql"
        success "Database backup created: postgres_backup_$BACKUP_TIMESTAMP.sql"
    fi
    
    # Application data backup
    if docker volume ls | grep -q scraper_app_data; then
        log "Backing up application data..."
        docker run --rm -v scraper_app_data:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/app_data_backup_$BACKUP_TIMESTAMP.tar.gz -C /data .
        success "Application data backup created: app_data_backup_$BACKUP_TIMESTAMP.tar.gz"
    fi
}

# Deploy application
deploy() {
    log "Starting production deployment..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Start services
    log "Starting services..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    health_check
    
    success "Deployment completed successfully!"
}

# Health check
health_check() {
    log "Running health checks..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts"
        
        # Check application health
        if curl -f -s http://localhost:8000/api/health > /dev/null; then
            success "Application health check passed"
            break
        elif [ $attempt -eq $max_attempts ]; then
            error "Health check failed after $max_attempts attempts"
        else
            warning "Health check failed, retrying in 10 seconds..."
            sleep 10
            ((attempt++))
        fi
    done
    
    # Check database connectivity
    if docker exec bis_postgres_prod pg_isready -U ${POSTGRES_USER:-bisuser} > /dev/null 2>&1; then
        success "Database connectivity check passed"
    else
        error "Database connectivity check failed"
    fi
    
    # Check Redis connectivity
    if docker exec bis_redis_prod redis-cli ping > /dev/null 2>&1; then
        success "Redis connectivity check passed"
    else
        warning "Redis connectivity check failed"
    fi
}

# Rollback deployment
rollback() {
    log "Rolling back deployment..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    
    # Restore from backup if available
    if [ -n "$1" ]; then
        log "Restoring from backup: $1"
        # Add restore logic here
    fi
    
    success "Rollback completed"
}

# View logs
view_logs() {
    log "Viewing application logs..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f --tail=100 app
}

# Scale services
scale_services() {
    local app_replicas=${1:-2}
    log "Scaling application to $app_replicas replicas..."
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --scale app=$app_replicas
    
    success "Services scaled successfully"
}

# Cleanup old resources
cleanup() {
    log "Cleaning up old Docker resources..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful!)
    if [ "$1" = "--deep" ]; then
        warning "Performing deep cleanup (removing unused volumes)..."
        docker volume prune -f
    fi
    
    success "Cleanup completed"
}

# Show status
status() {
    log "Current deployment status:"
    
    echo ""
    echo "=== Container Status ==="
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    echo ""
    echo "=== Resource Usage ==="
    docker stats --no-stream
    
    echo ""
    echo "=== Health Checks ==="
    curl -s http://localhost:8000/api/health | jq . 2>/dev/null || echo "Health endpoint not accessible"
}

# Main function
main() {
    # Create log directory
    mkdir -p logs
    
    case "$1" in
        "deploy")
            check_prerequisites
            backup_data "$2"
            deploy
            ;;
        "rollback")
            rollback "$2"
            ;;
        "logs")
            view_logs
            ;;
        "status")
            status
            ;;
        "scale")
            scale_services "$2"
            ;;
        "cleanup")
            cleanup "$2"
            ;;
        "health")
            health_check
            ;;
        "backup")
            backup_data
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|logs|status|scale|cleanup|health|backup}"
            echo ""
            echo "Commands:"
            echo "  deploy [--skip-backup]  - Deploy the application"
            echo "  rollback [backup_file]  - Rollback deployment"
            echo "  logs                    - View application logs"
            echo "  status                  - Show deployment status"
            echo "  scale [replicas]        - Scale application (default: 2)"
            echo "  cleanup [--deep]        - Cleanup Docker resources"
            echo "  health                  - Run health checks"
            echo "  backup                  - Create data backup"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
