#!/bin/bash

# Production Infrastructure Validation Script
# Business Intelligence Scraper v3.0 - Phase 3 Validation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🚀 Business Intelligence Scraper v3.0${NC}"
echo -e "${BLUE}Phase 3 Production Infrastructure Validation${NC}"
echo "================================================"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
print_test_result() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    
    if [ "$result" = "PASS" ]; then
        echo -e "✅ ${GREEN}$test_name${NC}"
        [ -n "$details" ] && echo -e "   ${details}"
        ((TESTS_PASSED++))
    else
        echo -e "❌ ${RED}$test_name${NC}"
        [ -n "$details" ] && echo -e "   ${RED}$details${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check required files exist
echo -e "\n${YELLOW}📋 Testing File Structure...${NC}"

check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        print_test_result "$description" "PASS"
    else
        print_test_result "$description" "FAIL" "Missing file: $file"
    fi
}

check_file "Dockerfile.production-v3" "Production Dockerfile exists"
check_file "docker-compose.production-v3.yml" "Production Docker Compose exists"
check_file ".github/workflows/production-cicd.yml" "CI/CD Pipeline exists"
check_file "scripts/deploy.sh" "Deployment script exists"
check_file "scripts/backup.sh" "Backup script exists"
check_file "config/production.yaml" "Production config exists"
check_file "PRODUCTION_DEPLOYMENT_GUIDE.md" "Production documentation exists"

# Test 2: Check script permissions
echo -e "\n${YELLOW}🔐 Testing Script Permissions...${NC}"

check_executable() {
    local script="$1"
    local description="$2"
    
    if [ -x "$PROJECT_ROOT/$script" ]; then
        print_test_result "$description" "PASS"
    else
        print_test_result "$description" "FAIL" "Script not executable: $script"
    fi
}

check_executable "scripts/deploy.sh" "Deploy script is executable"
check_executable "scripts/backup.sh" "Backup script is executable"

# Test 3: Validate Docker Compose configuration
echo -e "\n${YELLOW}🐳 Testing Docker Configuration...${NC}"

cd "$PROJECT_ROOT"

if docker-compose -f docker-compose.production-v3.yml config --quiet 2>/dev/null; then
    print_test_result "Docker Compose configuration valid" "PASS"
else
    print_test_result "Docker Compose configuration valid" "FAIL" "Configuration validation failed"
fi

# Test 4: Check deployment script functionality
echo -e "\n${YELLOW}⚙️ Testing Deployment Script...${NC}"

if ./scripts/deploy.sh --help >/dev/null 2>&1; then
    print_test_result "Deployment script help function" "PASS"
else
    print_test_result "Deployment script help function" "FAIL" "Help command failed"
fi

# Test 5: Validate CI/CD workflow syntax
echo -e "\n${YELLOW}🔄 Testing CI/CD Pipeline...${NC}"

if [ -f ".github/workflows/production-cicd.yml" ]; then
    # Basic YAML syntax check
    if python3 -c "import yaml; yaml.safe_load(open('.github/workflows/production-cicd.yml'))" 2>/dev/null; then
        print_test_result "GitHub Actions workflow syntax" "PASS"
    else
        print_test_result "GitHub Actions workflow syntax" "FAIL" "YAML syntax error"
    fi
else
    print_test_result "GitHub Actions workflow syntax" "FAIL" "Workflow file missing"
fi

# Test 6: Check configuration files
echo -e "\n${YELLOW}📝 Testing Configuration Files...${NC}"

check_config() {
    local config_file="$1"
    local description="$2"
    
    if [ -f "$PROJECT_ROOT/$config_file" ]; then
        if python3 -c "import yaml; yaml.safe_load(open('$config_file'))" 2>/dev/null; then
            print_test_result "$description" "PASS"
        else
            print_test_result "$description" "FAIL" "Invalid YAML syntax"
        fi
    else
        print_test_result "$description" "FAIL" "Configuration file missing"
    fi
}

check_config "config/production.yaml" "Production configuration syntax"
check_config "monitoring/prometheus-production.yml" "Prometheus configuration syntax"

# Test 7: Test Docker build (if Docker is available)
echo -e "\n${YELLOW}🏗️ Testing Docker Build...${NC}"

if command -v docker >/dev/null 2>&1; then
    if docker build -f Dockerfile.production-v3 -t bis-validation:test --target=production . >/dev/null 2>&1; then
        print_test_result "Production Docker image builds" "PASS"
        # Cleanup test image
        docker rmi bis-validation:test >/dev/null 2>&1 || true
    else
        print_test_result "Production Docker image builds" "FAIL" "Docker build failed"
    fi
else
    print_test_result "Production Docker image builds" "SKIP" "Docker not available"
fi

# Test 8: Validate monitoring configurations
echo -e "\n${YELLOW}📊 Testing Monitoring Configuration...${NC}"

check_monitoring_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$PROJECT_ROOT/$file" ]; then
        print_test_result "$description" "PASS"
    else
        print_test_result "$description" "FAIL" "Missing monitoring file: $file"
    fi
}

check_monitoring_file "monitoring/prometheus-production.yml" "Prometheus configuration exists"
check_monitoring_file "monitoring/alert-rules-production.yml" "Alert rules configuration exists"

# Test 9: Check security configurations
echo -e "\n${YELLOW}🔒 Testing Security Configuration...${NC}"

# Check Dockerfile security practices
if grep -q "USER.*[0-9]" "$PROJECT_ROOT/Dockerfile.production-v3" 2>/dev/null; then
    print_test_result "Dockerfile uses non-root user" "PASS"
else
    print_test_result "Dockerfile uses non-root user" "FAIL" "No non-root user configuration found"
fi

# Check for health checks
if grep -q "HEALTHCHECK" "$PROJECT_ROOT/Dockerfile.production-v3" 2>/dev/null; then
    print_test_result "Dockerfile includes health checks" "PASS"
else
    print_test_result "Dockerfile includes health checks" "FAIL" "No health check configuration found"
fi

# Test 10: Validate backup script
echo -e "\n${YELLOW}💾 Testing Backup Configuration...${NC}"

if ./scripts/backup.sh --help >/dev/null 2>&1; then
    print_test_result "Backup script help function" "PASS"
else
    print_test_result "Backup script help function" "FAIL" "Backup script help failed"
fi

# Summary
echo -e "\n${BLUE}📊 Validation Summary${NC}"
echo "===================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}All validation tests passed!${NC}"
    echo -e "${GREEN}✅ Phase 3 Production Infrastructure is ready for deployment!${NC}"
    exit 0
else
    echo -e "\n⚠️  ${YELLOW}Some validation tests failed.${NC}"
    echo -e "${YELLOW}Please review the failed tests before proceeding with deployment.${NC}"
    exit 1
fi
