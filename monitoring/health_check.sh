#!/bin/bash
# Production Health Check Script
# Business Intelligence Scraper Platform v2.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
DB_NAME="${DB_NAME:-business_intel_scraper_prod}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"

# Logging
LOG_FILE="monitoring/health_check.log"
mkdir -p monitoring

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}🔍 PRODUCTION HEALTH CHECK${NC}"
    echo -e "${BLUE}================================${NC}"
    echo "Platform: Business Intelligence Scraper Platform v2.0.0"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Host: $(hostname)"
    echo ""
}

check_service() {
    local service_name="$1"
    local check_command="$2"
    local expected_result="$3"
    
    echo -n "Checking $service_name... "
    
    if result=$(eval "$check_command" 2>/dev/null); then
        if [[ "$result" == *"$expected_result"* ]] || [[ -z "$expected_result" ]]; then
            echo -e "${GREEN}✅ OK${NC}"
            log "SUCCESS: $service_name is healthy"
            return 0
        else
            echo -e "${YELLOW}⚠️ DEGRADED${NC} (unexpected response: $result)"
            log "WARNING: $service_name is degraded - $result"
            return 1
        fi
    else
        echo -e "${RED}❌ FAILED${NC}"
        log "ERROR: $service_name is unhealthy"
        return 2
    fi
}

check_api_endpoint() {
    local endpoint="$1"
    local expected_status="${2:-200}"
    
    local url="${API_BASE_URL}${endpoint}"
    local response=$(curl -s -w "%{http_code}" -o /tmp/health_response "$url" 2>/dev/null || echo "000")
    
    if [[ "$response" == "$expected_status" ]]; then
        if [[ -f /tmp/health_response ]]; then
            local content=$(cat /tmp/health_response 2>/dev/null)
            if command -v jq >/dev/null 2>&1 && echo "$content" | jq . >/dev/null 2>&1; then
                local status=$(echo "$content" | jq -r '.status // "unknown"' 2>/dev/null)
                echo "API ${endpoint}: ${status}"
            else
                echo "API ${endpoint}: OK"
            fi
        else
            echo "API ${endpoint}: OK"
        fi
        rm -f /tmp/health_response
        return 0
    else
        echo "API ${endpoint}: HTTP $response"
        rm -f /tmp/health_response
        return 1
    fi
}

check_database_connection() {
    if command -v psql >/dev/null 2>&1; then
        local result=$(psql "$DATABASE_URL" -c "SELECT 1;" -t 2>/dev/null | tr -d ' \n' || echo "failed")
        if [[ "$result" == "1" ]]; then
            echo "Database: Connected"
            return 0
        fi
    fi
    
    # Fallback: try with python
    if command -v python3 >/dev/null 2>&1; then
        local result=$(python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('Connected')
except:
    print('Failed')
" 2>/dev/null || echo "Failed")
        echo "Database: $result"
        [[ "$result" == "Connected" ]] && return 0
    fi
    
    echo "Database: Failed"
    return 1
}

check_redis_connection() {
    if command -v redis-cli >/dev/null 2>&1; then
        local result=$(redis-cli -u "$REDIS_URL" ping 2>/dev/null || echo "failed")
        if [[ "$result" == "PONG" ]]; then
            echo "Redis: Connected"
            return 0
        fi
    fi
    
    # Fallback: try with python
    if command -v python3 >/dev/null 2>&1; then
        local result=$(python3 -c "
import redis
try:
    r = redis.from_url('$REDIS_URL')
    r.ping()
    print('Connected')
except:
    print('Failed')
" 2>/dev/null || echo "Failed")
        echo "Redis: $result"
        [[ "$result" == "Connected" ]] && return 0
    fi
    
    echo "Redis: Failed"
    return 1
}

check_system_resources() {
    echo "System Resources:"
    
    # CPU usage
    if command -v top >/dev/null 2>&1; then
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'u' -f1 || echo "unknown")
        echo "  CPU Usage: ${cpu_usage}%"
    fi
    
    # Memory usage
    if command -v free >/dev/null 2>&1; then
        local memory_info=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        echo "  Memory Usage: ${memory_info}%"
    fi
    
    # Disk usage
    if command -v df >/dev/null 2>&1; then
        local disk_usage=$(df / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
        echo "  Disk Usage: ${disk_usage}%"
    fi
    
    # Load average
    if [[ -f /proc/loadavg ]]; then
        local load_avg=$(cat /proc/loadavg | awk '{print $1}')
        echo "  Load Average: $load_avg"
    fi
}

check_docker_services() {
    if command -v docker >/dev/null 2>&1; then
        echo "Docker Services:"
        
        # Check if docker-compose services are running
        if [[ -f docker-compose.production-v3.yml ]]; then
            local services=$(docker-compose -f docker-compose.production-v3.yml ps --services 2>/dev/null || echo "")
            if [[ -n "$services" ]]; then
                while IFS= read -r service; do
                    local status=$(docker-compose -f docker-compose.production-v3.yml ps "$service" 2>/dev/null | tail -n +3 | awk '{print $4}' || echo "unknown")
                    if [[ "$status" == "Up" ]]; then
                        echo -e "  ${service}: ${GREEN}Running${NC}"
                    else
                        echo -e "  ${service}: ${RED}$status${NC}"
                    fi
                done <<< "$services"
            else
                echo "  No docker-compose services found"
            fi
        fi
        
        # Check individual containers
        local containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || echo "")
        if [[ -n "$containers" ]] && [[ "$containers" != "NAMES	STATUS" ]]; then
            echo "  Running Containers:"
            echo "$containers" | tail -n +2 | while IFS=$'\t' read -r name status; do
                if [[ "$status" == Up* ]]; then
                    echo -e "    ${name}: ${GREEN}$status${NC}"
                else
                    echo -e "    ${name}: ${RED}$status${NC}"
                fi
            done
        fi
    fi
}

generate_health_report() {
    local exit_code="$1"
    local status="HEALTHY"
    
    if [[ $exit_code -eq 1 ]]; then
        status="DEGRADED"
    elif [[ $exit_code -eq 2 ]]; then
        status="UNHEALTHY"
    fi
    
    # Create JSON report
    cat > monitoring/health_report.json << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platform": "Business Intelligence Scraper Platform v2.0.0",
  "overall_status": "$status",
  "exit_code": $exit_code,
  "host": "$(hostname)",
  "checks": {
    "api_health": "$api_status",
    "database": "$db_status", 
    "redis": "$redis_status",
    "frontend": "$frontend_status"
  },
  "uptime": "$(uptime -p 2>/dev/null || echo 'unknown')",
  "load_average": "$(cat /proc/loadavg 2>/dev/null | awk '{print $1}' || echo 'unknown')"
}
EOF

    echo ""
    echo -e "${BLUE}📊 HEALTH CHECK SUMMARY${NC}"
    echo "========================="
    echo "Overall Status: $status"
    echo "Report saved to: monitoring/health_report.json"
    echo "Log file: $LOG_FILE"
}

main() {
    print_header
    
    local exit_code=0
    
    echo -e "${BLUE}🌐 Service Health Checks${NC}"
    echo "-------------------------"
    
    # API Health Check
    if check_service "Backend API" "check_api_endpoint '/health'" ""; then
        api_status="healthy"
    else
        api_status="unhealthy"
        exit_code=2
    fi
    
    # Database Check
    if check_service "Database" "check_database_connection" "Connected"; then
        db_status="healthy"
    else
        db_status="unhealthy"
        exit_code=2
    fi
    
    # Redis Check
    if check_service "Redis Cache" "check_redis_connection" "Connected"; then
        redis_status="healthy"
    else
        redis_status="degraded"
        [[ $exit_code -eq 0 ]] && exit_code=1
    fi
    
    # Frontend Check
    echo -n "Checking Frontend... "
    frontend_response=$(curl -s -I "$FRONTEND_URL" | head -1 | awk '{print $2}' 2>/dev/null || echo "000")
    if [[ "$frontend_response" =~ ^2[0-9][0-9]$ ]]; then
        echo -e "${GREEN}✅ OK${NC}"
        frontend_status="healthy"
        log "SUCCESS: Frontend is healthy"
    else
        echo -e "${YELLOW}⚠️ DEGRADED${NC} (HTTP $frontend_response)"
        frontend_status="degraded"
        log "WARNING: Frontend is degraded - HTTP $frontend_response"
        [[ $exit_code -eq 0 ]] && exit_code=1
    fi
    
    echo ""
    echo -e "${BLUE}📊 System Status${NC}"
    echo "----------------"
    check_system_resources
    
    echo ""
    echo -e "${BLUE}🐳 Docker Status${NC}"
    echo "----------------"
    check_docker_services
    
    echo ""
    echo -e "${BLUE}🔍 API Endpoints${NC}"
    echo "----------------"
    
    # Check specific API endpoints
    endpoints=("/health" "/docs" "/api/auth/login")
    for endpoint in "${endpoints[@]}"; do
        check_api_endpoint "$endpoint" >/dev/null 2>&1
        local status=$?
        if [[ $status -eq 0 ]]; then
            echo -e "  ${endpoint}: ${GREEN}✅ OK${NC}"
        else
            echo -e "  ${endpoint}: ${RED}❌ FAILED${NC}"
        fi
    done
    
    generate_health_report $exit_code
    
    exit $exit_code
}

# Run the health check
main "$@"
