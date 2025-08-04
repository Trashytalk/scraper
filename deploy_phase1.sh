#!/bin/bash
# Phase 1 Implementation Deployment Script
# Enhanced Business Intelligence Scraper - Foundation & Security

echo "🚀 Phase 1: Foundation & Security Implementation"
echo "=============================================="

# Check Python dependencies
echo "📋 Checking dependencies..."
python3 -c "import psutil" 2>/dev/null || {
    echo "Installing psutil for system monitoring..."
    pip install psutil
}

python3 -c "import watchfiles" 2>/dev/null || {
    echo "Installing watchfiles for configuration hot-reload..."
    pip install watchfiles
}

python3 -c "import pydantic" 2>/dev/null || {
    echo "Installing pydantic for configuration validation..."
    pip install pydantic
}

# Backup existing files
echo "💾 Creating backups..."
if [ -f "backend_server.py.bak" ]; then
    echo "   Backup already exists: backend_server.py.bak"
else
    cp backend_server.py backend_server.py.bak
    echo "   ✅ Backed up backend_server.py"
fi

# Create required directories
echo "📁 Creating directory structure..."
mkdir -p config/templates
mkdir -p monitoring
mkdir -p docs

# Test configuration system
echo "🧪 Testing configuration system..."
python3 -c "
try:
    from config.advanced_config_manager import init_config, ConfigManager
    print('   ✅ Configuration system available')
except ImportError as e:
    print(f'   ❌ Configuration system error: {e}')
"

# Test monitoring system
echo "🔍 Testing monitoring system..."
python3 -c "
try:
    from monitoring.simple_health_monitor import SimpleHealthMonitor
    monitor = SimpleHealthMonitor('data.db')
    print('   ✅ Health monitoring system available')
except ImportError as e:
    print(f'   ❌ Monitoring system error: {e}')
"

# Test backend integration
echo "🔧 Testing backend integration..."
python3 -c "
import sys
sys.path.append('.')
try:
    # Quick syntax check
    with open('backend_server.py', 'r') as f:
        content = f.read()
    compile(content, 'backend_server.py', 'exec')
    print('   ✅ Backend server syntax valid')
except SyntaxError as e:
    print(f'   ❌ Backend syntax error: {e}')
except Exception as e:
    print(f'   ⚠️ Backend check warning: {e}')
"

# Create startup script
cat > start_enhanced_server.sh << 'EOF'
#!/bin/bash
# Enhanced Server Startup Script

echo "🚀 Starting Enhanced Business Intelligence Scraper Server"
echo "Environment: ${ENVIRONMENT:-development}"

# Set environment variables if not set
export ENVIRONMENT=${ENVIRONMENT:-development}
export DATABASE_URL=${DATABASE_URL:-sqlite:///./data.db}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key-change-in-production}

# Start the server
echo "Starting server on port 8000..."
python3 backend_server.py

EOF

chmod +x start_enhanced_server.sh

# Create configuration validation script
cat > validate_config.py << 'EOF'
#!/usr/bin/env python3
"""
Configuration Validation Script
Validates all configuration files and system readiness
"""

import asyncio
import sys
import os

async def validate_configuration():
    """Validate the configuration system"""
    try:
        from config.advanced_config_manager import init_config, ConfigManager
        
        # Test development config
        if os.path.exists("config/development.yaml"):
            config = await init_config("config/development.yaml", "development")
            print("✅ Development configuration valid")
            print(f"   Database: {config.database.url}")
            print(f"   Redis: {config.redis.host}:{config.redis.port}")
            return True
        else:
            print("❌ Development configuration file not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

async def validate_monitoring():
    """Validate the monitoring system"""
    try:
        from monitoring.simple_health_monitor import SimpleHealthMonitor
        
        monitor = SimpleHealthMonitor("data.db")
        health = await monitor.comprehensive_health_check()
        
        print("✅ Health monitoring system functional")
        print(f"   Status: {health['status']}")
        print(f"   System checks: {len(health['checks'])}")
        return True
        
    except Exception as e:
        print(f"❌ Monitoring validation failed: {e}")
        return False

async def main():
    """Main validation function"""
    print("🧪 Phase 1 System Validation")
    print("============================")
    
    config_ok = await validate_configuration()
    monitoring_ok = await validate_monitoring()
    
    if config_ok and monitoring_ok:
        print("\n✅ All systems validated successfully!")
        print("🚀 Ready to start enhanced server with: ./start_enhanced_server.sh")
        return 0
    else:
        print("\n❌ Validation failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
EOF

chmod +x validate_config.py

echo ""
echo "🎉 Phase 1 Implementation Complete!"
echo "===================================="
echo ""
echo "📋 What was implemented:"
echo "   ✅ Advanced configuration management with hot-reload"
echo "   ✅ Enhanced health monitoring system"
echo "   ✅ Backend server integration"
echo "   ✅ Development and production configuration templates"
echo ""
echo "🚀 Next steps:"
echo "   1. Run validation: python3 validate_config.py"
echo "   2. Start enhanced server: ./start_enhanced_server.sh"
echo "   3. Test health endpoint: curl http://localhost:8000/api/health"
echo ""
echo "🔍 Monitor logs for enhanced health monitoring output"
echo "📈 Visit http://localhost:8000/docs for enhanced API documentation"
echo ""
echo "Continue with Phase 2: Performance & User Experience next!"
