#!/bin/bash

# Business Intelligence Scraper - One-Command Setup Script
# Usage: ./setup.sh [--dev] [--quick]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.11"
DEV_MODE=false
QUICK_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--dev] [--quick]"
            echo "  --dev    Install development dependencies"
            echo "  --quick  Skip optional components"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

check_python_version() {
    if check_command python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python $PYTHON_VERSION found, but $PYTHON_MIN_VERSION+ required"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

install_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Created virtual environment"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    if [ "$DEV_MODE" = true ]; then
        pip install pytest pytest-asyncio pytest-mock black ruff mypy pre-commit
        print_success "Development dependencies installed"
    fi
    
    print_success "Python dependencies installed"
}

setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_warning ".env file already exists, skipping"
    fi
}

setup_ai_system() {
    print_step "Setting up AI system..."
    
    # Check if user wants AI features
    echo -n "Enable AI features? (entity extraction, sentiment analysis, etc.) [Y/n]: "
    read enable_ai
    if [[ $enable_ai =~ ^[Nn]$ ]]; then
        echo "AI features disabled"
        return
    fi
    
    echo "Setting up AI configuration..."
    
    # Create AI cache directory
    mkdir -p data/ai_cache
    mkdir -p data/ai_cache/transformers
    mkdir -p data/ai_cache/sentence_transformers
    
    # Activate virtual environment for AI setup
    source .venv/bin/activate
    
    # Setup AI configuration
    if command -v python &> /dev/null; then
        python bis.py ai setup
    else
        echo "Python not found in virtual environment. AI setup will be available after installation."
    fi
    
    print_success "AI system configured"
    echo "  💡 Run 'python bis.py ai status' to check AI capabilities"
    echo "  📦 Run 'python bis.py ai requirements' to generate AI dependencies"
}

check_docker() {
    if check_command docker && check_command docker-compose; then
        print_success "Docker and Docker Compose found"
        return 0
    else
        print_warning "Docker or Docker Compose not found"
        print_warning "You can still run the application locally, but Docker is recommended"
        return 1
    fi
}

setup_frontend() {
    if [ "$QUICK_MODE" = true ]; then
        print_warning "Skipping frontend setup (quick mode)"
        return 0
    fi
    
    print_step "Setting up frontend..."
    
    if check_command npm; then
        cd business_intel_scraper/frontend
        npm install
        cd ../../
        print_success "Frontend dependencies installed"
    else
        print_warning "npm not found, skipping frontend setup"
        print_warning "Install Node.js to use the web dashboard"
    fi
}

setup_database() {
    print_step "Setting up database..."
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Run database initialization
    python -c "
from business_intel_scraper.backend.db.utils import init_db
try:
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database setup failed: {e}')
    exit(1)
"
    
    print_success "Database initialized"
}

create_demo_script() {
    print_step "Creating demo script..."
    
    cat > demo.sh << 'EOF'
#!/bin/bash

# Business Intelligence Scraper Demo
echo "🚀 Starting Business Intelligence Scraper Demo..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Start services in background
echo "📡 Starting Redis..."
if ! docker ps | grep -q redis; then
    docker run -d -p 6379:6379 --name redis-demo redis:7 || {
        echo "❌ Failed to start Redis. Make sure Docker is running."
        exit 1
    }
fi

echo "🔧 Starting API server..."
cd business_intel_scraper
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "⏳ Waiting for API to start..."
sleep 5

echo "🕷️  Running marketplace demo..."
cd ..
python demo_marketplace.py

echo "🌐 Starting frontend..."
cd business_intel_scraper/frontend
if [ -d "node_modules" ]; then
    npm run dev &
    FRONTEND_PID=$!
    echo "📱 Frontend starting at http://localhost:3000"
else
    echo "⚠️  Frontend dependencies not installed. Run: cd business_intel_scraper/frontend && npm install"
fi

echo "✅ Demo started successfully!"
echo "🌐 API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo "📱 Frontend: http://localhost:3000"
echo "🕷️  Marketplace: http://localhost:3000/marketplace"
echo "📈 Analytics: http://localhost:3000/analytics"
echo "⚡ Performance: http://localhost:8000/performance/status"
echo "📈 Health check: curl http://localhost:8000/"
echo ""
echo "Press Ctrl+C to stop the demo"

# Wait for interrupt
trap "echo '🛑 Stopping demo...'; kill $API_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; docker stop redis-demo 2>/dev/null; docker rm redis-demo 2>/dev/null; exit 0" INT
wait $API_PID
EOF

    chmod +x demo.sh
    print_success "Created demo script (./demo.sh)"
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run the demo: ${BLUE}./demo.sh${NC}"
    echo "3. Or start manually:"
    echo "   ${BLUE}source .venv/bin/activate${NC}"
    echo "   ${BLUE}cd business_intel_scraper${NC}"
    echo "   ${BLUE}uvicorn backend.api.main:app --reload${NC}"
    echo "4. Access the applications:"
    echo "   • API: ${BLUE}http://localhost:8000${NC}"
    echo "   • API Docs: ${BLUE}http://localhost:8000/docs${NC}"
    echo "   • Frontend: ${BLUE}http://localhost:3000${NC}"
    echo "   • Spider Marketplace: ${BLUE}http://localhost:3000/marketplace${NC}"
    echo "   • Analytics Dashboard: ${BLUE}http://localhost:3000/analytics${NC}"
    echo "   • Performance Monitor: ${BLUE}http://localhost:8000/performance/status${NC}"
    echo ""
    echo "5. AI Features:"
    echo "   • Status: ${BLUE}python bis.py ai status${NC}"
    echo "   • Configuration: ${BLUE}python bis.py ai setup${NC}"
    echo "   • Test AI: ${BLUE}python bis.py ai test-entities 'Apple Inc. is a technology company'${NC}"
    echo ""
    echo "6. Performance Optimization:"
    echo "   • Status: ${BLUE}curl http://localhost:8000/performance/status${NC}"
    echo "   • Metrics: ${BLUE}curl http://localhost:8000/performance/metrics${NC}"
    echo "   • Cache Stats: ${BLUE}curl http://localhost:8000/performance/cache/stats${NC}"
    echo "   • Recommendations: ${BLUE}curl http://localhost:8000/performance/recommendations${NC}"
    echo ""
    echo "📚 Documentation: ${BLUE}docs/tutorial.md${NC}"
    echo "🕷️  Marketplace demo: ${BLUE}python demo_marketplace.py${NC}"
    echo "🎯 Project templates: ${BLUE}./create-project.sh${NC}"
    echo "🤖 AI Integration: ${BLUE}docs/ai_integration.md${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🔧 Business Intelligence Scraper Setup${NC}"
    echo "============================================"
    
    # Check prerequisites
    print_step "Checking prerequisites..."
    
    if ! check_python_version; then
        print_error "Please install Python $PYTHON_MIN_VERSION or higher"
        exit 1
    fi
    
    check_docker
    
    # Run setup steps
    install_dependencies
    setup_environment
    setup_ai_system
    setup_frontend
    setup_database
    create_demo_script
    
    print_next_steps
}

# Run main function
main "$@"
