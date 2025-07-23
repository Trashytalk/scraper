#!/bin/bash

# Comprehensive Testing Script for Business Intelligence Scraper
# Tests backend integration, authentication, and frontend-backend connectivity

echo "🧪 Starting Comprehensive Testing Suite..."
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${BLUE}🔍 Test $TOTAL_TESTS: $test_name${NC}"
    echo "Command: $test_command"
    
    # Run the test command
    result=$(eval "$test_command" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ] && [[ $result =~ $expected_pattern ]]; then
        echo -e "${GREEN}✅ PASSED${NC}"
        echo "Result: $result"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "Expected pattern: $expected_pattern"
        echo "Actual result: $result"
        echo "Exit code: $exit_code"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Health Check Tests
echo -e "\n${YELLOW}🏥 BACKEND HEALTH TESTS${NC}"
echo "========================"

run_test "Backend Health Check" \
    "curl -s http://localhost:8000/api/health" \
    "healthy"

run_test "Backend API Documentation" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/docs" \
    "200"

# Authentication Tests
echo -e "\n${YELLOW}🔐 AUTHENTICATION TESTS${NC}"
echo "========================="

# Test login with correct credentials
AUTH_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

run_test "Admin Login" \
    "curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\": \"admin\", \"password\": \"admin123\"}'" \
    "access_token"

run_test "Invalid Login" \
    "curl -s -X POST http://localhost:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\": \"invalid\", \"password\": \"wrong\"}'" \
    "Invalid username or password"

if [ -n "$AUTH_TOKEN" ]; then
    run_test "Authenticated User Info" \
        "curl -s -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/auth/me" \
        "admin"
else
    echo -e "${RED}❌ Could not obtain auth token for subsequent tests${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# API Endpoint Tests
echo -e "\n${YELLOW}📊 API ENDPOINT TESTS${NC}"
echo "======================"

if [ -n "$AUTH_TOKEN" ]; then
    run_test "Get Jobs List" \
        "curl -s -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/jobs" \
        "\\[.*\\]"

    run_test "Get Dashboard Analytics" \
        "curl -s -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/analytics/dashboard" \
        "jobs"

    run_test "Get Analytics Metrics" \
        "curl -s -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/analytics/metrics" \
        "job_completion_trend"

    # Test job creation
    JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/jobs \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Job", "type": "web_scraping", "config": {"url": "https://example.com"}}')
    
    run_test "Create Job" \
        "echo '$JOB_RESPONSE'" \
        "Job created successfully"

    # Extract job ID for further tests
    JOB_ID=$(echo "$JOB_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    
    if [ -n "$JOB_ID" ]; then
        run_test "Get Specific Job" \
            "curl -s -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/jobs/$JOB_ID" \
            "Test Job"

        run_test "Start Job" \
            "curl -s -X POST -H 'Authorization: Bearer $AUTH_TOKEN' http://localhost:8000/api/jobs/$JOB_ID/start" \
            "Job started successfully"
    fi
else
    echo -e "${RED}❌ Skipping API tests - no auth token available${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 6))
    TOTAL_TESTS=$((TOTAL_TESTS + 6))
fi

# Frontend Connectivity Tests
echo -e "\n${YELLOW}🌐 FRONTEND CONNECTIVITY TESTS${NC}"
echo "==============================="

run_test "Frontend Server Running" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/" \
    "200"

# Database Tests
echo -e "\n${YELLOW}💾 DATABASE TESTS${NC}"
echo "=================="

run_test "Database File Exists" \
    "ls -la /home/homebrew/scraper/data/scraper.db" \
    "scraper.db"

# Check if tables exist
run_test "Database Tables Created" \
    "sqlite3 /home/homebrew/scraper/data/scraper.db '.tables'" \
    "users.*jobs.*analytics"

# Count records
USERS_COUNT=$(sqlite3 /home/homebrew/scraper/data/scraper.db "SELECT COUNT(*) FROM users;" 2>/dev/null)
run_test "Admin User Exists" \
    "echo '$USERS_COUNT'" \
    "[1-9]"

# WebSocket Test (basic connectivity)
echo -e "\n${YELLOW}🔌 WEBSOCKET TESTS${NC}"
echo "=================="

# Note: WebSocket testing with curl is limited, but we can check if the endpoint responds
run_test "WebSocket Endpoint Available" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ws" \
    "426|400|405"  # Expected status codes for WebSocket upgrade attempts via HTTP

# Performance Tests
echo -e "\n${YELLOW}⚡ PERFORMANCE TESTS${NC}"
echo "===================="

# Test response times
HEALTH_TIME=$(curl -s -o /dev/null -w '%{time_total}' http://localhost:8000/api/health)
run_test "Health Endpoint Response Time" \
    "echo '$HEALTH_TIME < 1.0' | bc -l" \
    "1"

# Security Tests
echo -e "\n${YELLOW}🛡️ SECURITY TESTS${NC}"
echo "=================="

run_test "Unauthorized Access Blocked" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/jobs" \
    "401"

run_test "CORS Headers Present" \
    "curl -s -I http://localhost:8000/api/health | grep -i 'access-control-allow-origin'" \
    "Access-Control-Allow-Origin"

# Final Results
echo -e "\n${YELLOW}📋 TEST SUMMARY${NC}"
echo "================"
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "✅ Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "❌ Failed: ${RED}$TESTS_FAILED${NC}"

PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
echo -e "📊 Pass Rate: $PASS_RATE%"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED! System is fully operational.${NC}"
    exit 0
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "\n${YELLOW}⚠️ Most tests passed, but some issues detected.${NC}"
    exit 1
else
    echo -e "\n${RED}💥 Multiple test failures detected. System needs attention.${NC}"
    exit 2
fi
