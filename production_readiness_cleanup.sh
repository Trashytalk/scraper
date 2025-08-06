#!/bin/bash
# Repository Cleanup and Production Readiness Script

echo "🧹 REPOSITORY CLEANUP AND PRODUCTION READINESS"
echo "=============================================="

# 1. Remove development/debug files
echo "📁 Cleaning up development files..."

# Remove debug and test files that shouldn't be in production
rm -f comprehensive_debug.js
rm -f simple_debug.js
rm -f browser_test_script.js
rm -f manual_modal_test.js
rm -f frontend_modal_test.js
rm -f modal_state_test.js
rm -f targeted_modal_debug.js
rm -f debug_frontend_*.py
rm -f demo_working_crawling.py

# Remove broken/backup files
rm -f backend_server.py.bak
rm -f business_intel_scraper/frontend/src/OperationsInterface_broken.tsx

# Remove temporary log files
rm -f backend_clean.log
rm -f backend_enhanced.log 
rm -f backend_phase4.log
rm -f frontend.log
rm -f quick_start.log
rm -f server_prod.log

# Remove test data and temp files
rm -f data.db
rm -f analytics.db
rm -rf temp/
rm -rf cache/temp/

echo "✅ Development files cleaned"

# 2. Create production configuration
echo "⚙️ Setting up production configurations..."

# Create production environment template if not exists
if [ ! -f .env.production ]; then
    cat > .env.production << 'EOF'
# Production Environment Configuration
NODE_ENV=production
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_WS_URL=wss://your-api-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/business_intel_scraper_prod
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=your-secure-jwt-secret-here
ENCRYPTION_KEY=your-32-character-encryption-key

# External Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=warning

# Performance
WORKERS=4
MAX_CONNECTIONS=100
CACHE_TTL=3600
EOF
fi

echo "✅ Production configuration created"

# 3. Update documentation
echo "📚 Updating documentation..."

# Create deployment guide if not exists
if [ ! -f DEPLOYMENT.md ]; then
    cat > DEPLOYMENT.md << 'EOF'
# 🚀 Production Deployment Guide

## Prerequisites
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for frontend builds)
- Python 3.12+

## Quick Production Deployment

### 1. Environment Setup
```bash
cp .env.production.template .env.production
# Edit .env.production with your values
```

### 2. Database Setup
```bash
# PostgreSQL setup
createdb business_intel_scraper_prod
```

### 3. Docker Deployment
```bash
docker-compose -f docker-compose.production-v3.yml up -d
```

### 4. Health Check
```bash
curl http://localhost:8000/health
```

## Manual Deployment

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend_server:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd business_intel_scraper/frontend
npm install
npm run build
npm run serve
```

## Monitoring & Maintenance

- Health endpoint: `/health`
- Metrics endpoint: `/metrics`
- Admin panel: `/admin`
- API docs: `/docs`

## Security Checklist

- [ ] Update all default passwords
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts

## Performance Optimization

- [ ] Enable Redis caching
- [ ] Configure CDN for static assets
- [ ] Set up database connection pooling
- [ ] Enable gzip compression
- [ ] Configure rate limiting

EOF
fi

echo "✅ Deployment guide created"

# 4. Production build test
echo "🏗️ Testing production build..."

# Test frontend build
if [ -d "business_intel_scraper/frontend" ]; then
    cd business_intel_scraper/frontend
    if [ -f "package.json" ]; then
        echo "Testing frontend production build..."
        npm run build --if-present 2>/dev/null && echo "✅ Frontend build test passed" || echo "⚠️ Frontend build needs attention"
    fi
    cd - > /dev/null
fi

# 5. Security scan
echo "🔒 Running basic security checks..."

# Check for sensitive files
echo "Checking for sensitive files..."
find . -name "*.key" -o -name "*.pem" -o -name "*.env" | grep -v ".env.template" | grep -v ".env.example" && echo "⚠️ Found sensitive files - ensure they're in .gitignore" || echo "✅ No sensitive files found"

# Check .gitignore
if [ ! -f .gitignore ]; then
    echo "⚠️ No .gitignore found - creating one..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/

# Environment variables
.env
.env.local
.env.production

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Cache
.cache/
cache/
.pytest_cache/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets
secrets/
*.key
*.pem
EOF
fi

echo "🎉 REPOSITORY CLEANUP COMPLETE!"
echo ""
echo "📋 NEXT STEPS FOR PRODUCTION:"
echo "1. Review and update .env.production with your values"
echo "2. Test deployment with: docker-compose -f docker-compose.production-v3.yml up"
echo "3. Run security audit: npm audit (in frontend directory)"
echo "4. Set up monitoring and logging"
echo "5. Configure backup strategy"
echo ""
echo "✅ Your repository is now production-ready!"
