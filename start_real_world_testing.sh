#!/bin/bash

# Real-World Testing Startup Script
# Enterprise Visual Analytics Platform

echo "🚀 Enterprise Visual Analytics Platform - Real-World Testing"
echo "=============================================================="

# Check if we're in the right directory
if [ ! -f "business_intel_scraper/backend/db/models.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 Pre-testing Setup..."

# 1. Ensure Python environment is configured
echo "🐍 Configuring Python environment..."
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "   ✅ Virtual environment activated"

# 2. Install required packages
echo "📦 Installing required packages..."
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt 2>/dev/null || echo "   Note: requirements-dev.txt not found, continuing..."
echo "   ✅ Packages installed"

# 3. Set up environment variables
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ✅ Created .env from template"
    else
        echo "   Creating basic .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./test_analytics.db
POSTGRES_URL=postgresql://localhost/analytics_db

# Redis Configuration  
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production

# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
EOF
        echo "   ✅ Created basic .env file"
    fi
fi

# 4. Create necessary directories
echo "📁 Creating test directories..."
mkdir -p data/real_world_testing
mkdir -p logs
mkdir -p monitoring
echo "   ✅ Test directories created"

# 5. Run infrastructure tests
echo ""
echo "🧪 Running Infrastructure Tests..."
echo "=================================="
python test_real_world_infrastructure.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🌍 Running Real-World Data Integration Tests..."
    echo "=============================================="
    python test_real_world_data_integration.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 SUCCESS: All real-world tests passed!"
        echo "📊 Your Enterprise Visual Analytics Platform is ready for production!"
        echo ""
        echo "🚀 Next Steps:"
        echo "   1. Deploy with Docker: docker-compose -f business_intel_scraper/docker-compose.yml up"
        echo "   2. Access API at: http://localhost:8000"
        echo "   3. Access Frontend at: http://localhost:3000"
        echo "   4. Check API docs at: http://localhost:8000/docs"
        echo ""
        echo "📚 For detailed deployment guide, see: README.md"
    else
        echo ""
        echo "⚠️  Data integration tests had issues. Check the output above."
    fi
else
    echo ""
    echo "⚠️  Infrastructure tests had issues. Check the output above."
fi

echo ""
echo "📖 For comprehensive testing guide, see: REAL_WORLD_TESTING_GUIDE.md"
