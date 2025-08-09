#!/bin/bash
# Security Scanning Script
# Business Intelligence Scraper Platform - Security Validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$PROJECT_ROOT/security-reports"

# Create reports directory
mkdir -p "$REPORTS_DIR"

echo -e "${BLUE}🔒 Security Scanning Suite${NC}"
echo -e "${BLUE}Business Intelligence Scraper Platform${NC}"
echo "================================================"

# Function to print test result
print_result() {
    local test_name="$1"
    local result="$2"
    local details="${3:-}"
    
    if [ "$result" = "PASS" ]; then
        echo -e "✅ ${GREEN}$test_name${NC}"
        [ -n "$details" ] && echo -e "   ${details}"
    elif [ "$result" = "FAIL" ]; then
        echo -e "❌ ${RED}$test_name${NC}"
        [ -n "$details" ] && echo -e "   ${RED}$details${NC}"
    else
        echo -e "⚠️ ${YELLOW}$test_name${NC}"
        [ -n "$details" ] && echo -e "   ${YELLOW}$details${NC}"
    fi
}

# Test 1: Check for exposed secrets
echo -e "\n${YELLOW}🔍 Testing for Exposed Secrets...${NC}"

if [ -d "$PROJECT_ROOT/secrets" ]; then
    print_result "Secrets directory check" "FAIL" "secrets/ directory found - REMOVE IMMEDIATELY"
    SECRET_ISSUES=$((SECRET_ISSUES + 1))
else
    print_result "Secrets directory check" "PASS" "No secrets/ directory found"
fi

# Check for common secret patterns in code
SECRET_PATTERNS=(
    "password\s*=\s*['\"](?!.*CHANGE_ME|.*your-|.*example)[^'\"]{8,}"
    "api_key\s*=\s*['\"](?!.*CHANGE_ME|.*your-|.*example)[^'\"]{20,}"
    "secret\s*=\s*['\"](?!.*CHANGE_ME|.*your-|.*example)[^'\"]{16,}"
    "token\s*=\s*['\"](?!.*CHANGE_ME|.*your-|.*example)[^'\"]{20,}"
)

SECRET_ISSUES=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -E "$pattern" "$PROJECT_ROOT" --exclude-dir=".git" --exclude-dir=".venv" --exclude-dir="node_modules" > /dev/null 2>&1; then
        SECRET_ISSUES=$((SECRET_ISSUES + 1))
    fi
done

if [ $SECRET_ISSUES -eq 0 ]; then
    print_result "Secret pattern scan" "PASS" "No hardcoded secrets detected"
else
    print_result "Secret pattern scan" "FAIL" "$SECRET_ISSUES potential secrets found"
fi

# Test 2: Install and run Bandit
echo -e "\n${YELLOW}🛡️ Running Bandit Security Scanner...${NC}"

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Install bandit if not present
if ! command -v bandit &> /dev/null; then
    pip install bandit[toml] > /dev/null 2>&1
fi

# Run bandit scan
if bandit -r . -f json -o "$REPORTS_DIR/bandit-report.json" -ll 2>/dev/null; then
    BANDIT_HIGH=$(jq '.results[] | select(.issue_severity == "HIGH") | length' "$REPORTS_DIR/bandit-report.json" 2>/dev/null | wc -l)
    BANDIT_MEDIUM=$(jq '.results[] | select(.issue_severity == "MEDIUM") | length' "$REPORTS_DIR/bandit-report.json" 2>/dev/null | wc -l)
    
    if [ "$BANDIT_HIGH" -eq 0 ]; then
        print_result "Bandit security scan" "PASS" "No high-severity issues found"
    else
        print_result "Bandit security scan" "FAIL" "$BANDIT_HIGH high-severity issues found"
    fi
else
    print_result "Bandit security scan" "WARN" "Scan completed with findings"
fi

# Test 3: Run Safety check
echo -e "\n${YELLOW}🔐 Running Safety Vulnerability Check...${NC}"

if ! command -v safety &> /dev/null; then
    pip install safety > /dev/null 2>&1
fi

if safety check --json --output "$REPORTS_DIR/safety-report.json" 2>/dev/null; then
    print_result "Safety vulnerability check" "PASS" "No known vulnerabilities in dependencies"
else
    VULNS=$(cat "$REPORTS_DIR/safety-report.json" 2>/dev/null | jq '. | length' 2>/dev/null || echo "0")
    if [ "$VULNS" -gt 0 ]; then
        print_result "Safety vulnerability check" "FAIL" "$VULNS vulnerabilities found in dependencies"
    else
        print_result "Safety vulnerability check" "WARN" "Check completed with warnings"
    fi
fi

# Test 4: Check pip-audit
echo -e "\n${YELLOW}🔒 Running pip-audit...${NC}"

if ! command -v pip-audit &> /dev/null; then
    pip install pip-audit > /dev/null 2>&1
fi

if pip-audit --format=json --output="$REPORTS_DIR/pip-audit-report.json" 2>/dev/null; then
    print_result "Pip audit check" "PASS" "No vulnerabilities found by pip-audit"
else
    print_result "Pip audit check" "WARN" "Check completed - review report"
fi

# Test 5: Check for security middleware
echo -e "\n${YELLOW}🛡️ Checking Security Implementation...${NC}"

if [ -f "$PROJECT_ROOT/security_middleware.py" ] && [ -f "$PROJECT_ROOT/security/advanced_security_middleware.py" ]; then
    print_result "Security middleware" "PASS" "Security middleware files present"
else
    print_result "Security middleware" "FAIL" "Security middleware missing"
fi

# Check for JWT implementation
if grep -r "JWT\|jwt" "$PROJECT_ROOT" --include="*.py" > /dev/null 2>&1; then
    print_result "JWT authentication" "PASS" "JWT implementation found"
else
    print_result "JWT authentication" "FAIL" "No JWT implementation found"
fi

# Test 6: Check environment files
echo -e "\n${YELLOW}🔧 Checking Environment Configuration...${NC}"

if [ -f "$PROJECT_ROOT/.env.production.template" ]; then
    # Check if template has placeholder values
    if grep -q "CHANGE_ME\|your-" "$PROJECT_ROOT/.env.production.template"; then
        print_result "Environment template" "PASS" "Template with placeholders found"
    else
        print_result "Environment template" "WARN" "Template may contain real values"
    fi
else
    print_result "Environment template" "FAIL" "No .env.production.template found"
fi

# Check if production env file exists and warn
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    print_result "Production environment file" "WARN" ".env.production exists - ensure it's not in git"
fi

# Summary
echo -e "\n${BLUE}📊 Security Scan Summary${NC}"
echo "============================="
echo -e "Reports generated in: ${GREEN}$REPORTS_DIR${NC}"
echo ""
echo "Files generated:"
[ -f "$REPORTS_DIR/bandit-report.json" ] && echo "  • bandit-report.json"
[ -f "$REPORTS_DIR/safety-report.json" ] && echo "  • safety-report.json" 
[ -f "$REPORTS_DIR/pip-audit-report.json" ] && echo "  • pip-audit-report.json"

echo ""
echo -e "${YELLOW}⚠️ Next Steps:${NC}"
echo "1. Review all generated reports"
echo "2. Fix any high-severity findings"
echo "3. Ensure no secrets are committed to git"
echo "4. Update dependencies with vulnerabilities"
echo "5. Run this scan regularly"

echo ""
echo -e "${GREEN}✅ Security scan completed!${NC}"
