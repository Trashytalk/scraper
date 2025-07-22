#!/bin/bash

# Business Intelligence Scraper - Quick Start Script
# This script automates the basic setup process

set -e  # Exit on any error

echo "🚀 Business Intelligence Scraper - Quick Start"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "\n${BLUE}📋 Step $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "business_intel_scraper" ]; then
    print_error "Please run this script from the scraper project root directory"
    exit 1
fi

print_step "1" "Checking Prerequisites"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_success "Python 3 found: $PYTHON_VERSION"
    
    # Check if version is 3.11+
    if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
        print_success "Python version is 3.11+ ✓"
    else
        print_warning "Python 3.11+ recommended, you have $PYTHON_VERSION"
    fi
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check if pip is available
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    print_success "pip found ✓"
else
    print_error "pip not found. Please install pip"
    exit 1
fi

print_step "2" "Creating Virtual Environment"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

print_step "3" "Installing Dependencies"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt --quiet
print_success "All dependencies installed"

print_step "4" "Setting Up Environment Configuration"

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_success "Environment file already exists"
fi

# Set secure permissions on .env
chmod 600 .env
print_success "Environment file permissions secured (600)"

print_step "5" "Initializing Database"

# Initialize database
echo "Setting up database..."
python3 -c "
import asyncio
import sys
try:
    from business_intel_scraper.database.config import init_database
    asyncio.run(init_database())
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization failed: {e}')
    sys.exit(1)
" && print_success "Database initialized" || (print_error "Database initialization failed" && exit 1)

print_step "6" "Validating Installation"

# Run validation script
echo "Running setup validation..."
if python3 validate_setup.py > /dev/null 2>&1; then
    print_success "All validation checks passed!"
else
    print_warning "Some validation checks failed. Run 'python3 validate_setup.py' for details."
fi

print_step "7" "Quick Functionality Test"

# Test core imports
python3 -c "
try:
    from business_intel_scraper.backend.api.main import app
    from business_intel_scraper.database.config import get_async_session
    print('✅ Core components loaded successfully')
except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
" || (print_error "Core component test failed" && exit 1)

print_success "Setup completed successfully!"

echo ""
echo "🎉 Business Intelligence Scraper is ready to use!"
echo ""
echo "📋 Quick Start Commands:"
echo "  # Activate virtual environment (if not already active):"
echo "  source .venv/bin/activate"
echo ""
echo "  # Start the API server:"
echo "  uvicorn business_intel_scraper.backend.api.main:app --reload --port 8000"
echo ""
echo "  # Test the CLI tool:"
echo "  python bis.py --help"
echo ""
echo "  # View API documentation:"
echo "  # Visit http://localhost:8000/docs (after starting the server)"
echo ""
echo "  # Run full validation:"
echo "  python validate_setup.py"
echo ""
echo "📚 Next Steps:"
echo "  1. Read the documentation: docs/setup.md"
echo "  2. Start the API server and visit http://localhost:8000/docs"
echo "  3. Explore the CLI: python bis.py crawl --help"
echo "  4. Begin your scraping projects!"
echo ""
echo "🔧 Need help? Check docs/setup.md for detailed troubleshooting guide."
echo ""
