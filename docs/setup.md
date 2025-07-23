# Business Intelligence Scraper - Setup Guide v1.0.0

This guide covers the complete setup for the Business Intelligence Scraper platform, including the new performance monitoring, security hardening, and Docker containerization features.

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.11+** (3.11 or 3.12 recommended)
- **Git** (for cloning the repository)
- **Node.js 18+** (for React frontend)
- **Docker & Docker Compose** (recommended for production)

### **Optional Components**
- **Redis** (for caching - included in Docker stack)
- **PostgreSQL** (for production database - included in Docker stack)
- **VS Code** (with recommended extensions for development)

### **System Requirements**
- **OS**: Linux, macOS, or Windows (WSL2 recommended for Windows)
- **RAM**: Minimum 8GB, recommended 16GB+ (for Docker stack)
- **Storage**: At least 5GB free space
- **Network**: Internet connection for package downloads

---

## 🚀 **Quick Start - Production Setup**

### **Option 1: Docker Deployment (Recommended)**

```bash
# Clone the repository
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Start the complete production stack
docker-compose up --build -d

# Verify services are running
docker-compose ps

# Access the platform
# Frontend: http://localhost:5173
# API: http://localhost:8000/docs
# Grafana: http://localhost:3000
```

### **Option 2: Development Setup**

```bash
# Clone the repository
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Backend setup
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd business_intel_scraper/frontend
npm install

# Start development servers
# Terminal 1 - Backend
python backend_server.py

# Terminal 2 - Frontend
npm run dev
```
---

## 🔧 **Configuration**

### **Environment Variables**

The platform uses environment variables for configuration. Create a `.env` file:

```bash
# Copy the example configuration
cp .env.example .env

# Edit configuration
nano .env
```

### **Key Configuration Options**

```bash
# Security Configuration
JWT_SECRET=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24
API_RATE_LIMIT_PER_MINUTE=60

# Database Configuration
DATABASE_PATH=data/scraper.db

# Performance Settings
PERFORMANCE_CACHE_TTL=3600
PERFORMANCE_MONITORING_ENABLED=true

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true

# Security Headers
ENABLE_SECURITY_HEADERS=true
HSTS_MAX_AGE=31536000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO
```

### **Generate Secure Keys**

```bash
# Generate JWT secret
python -c "import secrets; print('JWT_SECRET=' + secrets.token_hex(32))"

# Generate database encryption key
python -c "import secrets; print('DB_ENCRYPTION_KEY=' + secrets.token_hex(32))"
```

---

## 🎯 **Feature Configuration**

### **Performance Monitoring Setup**

The platform includes comprehensive performance monitoring:

```bash
# Check performance system status
curl http://localhost:8000/api/performance/metrics

# View cache statistics
curl http://localhost:8000/api/performance/cache/stats

# Apply optimization profile
curl -X POST http://localhost:8000/api/performance/optimize/balanced
```

### **Security Configuration**

Security features are enabled by default:

- **JWT Authentication**: Token-based authentication with configurable expiration
- **Rate Limiting**: 60 requests per minute per IP (configurable)
- **Input Validation**: Automatic input sanitization and validation
- **Security Headers**: HSTS, CSP, X-Frame-Options enabled
- **Password Hashing**: bcrypt with secure salt rounds

### **Docker Services Configuration**

The docker-compose stack includes:

```yaml
services:
  api:           # Main FastAPI application
  frontend:      # React development server
  redis:         # Caching and session storage
  postgres:      # Production database
  nginx:         # Reverse proxy
  prometheus:    # Metrics collection
  grafana:       # Monitoring dashboard
```
import asyncio
result = asyncio.run(check_database_health())
print('Database Status:', result)
"

```

### Step 6: Verify Core Installation

```bash
# Test core imports (essential components only)
python3 -c "
print('Testing core components...')
from business_intel_scraper.database.config import get_async_session, check_database_health
print('✅ Database connection ready')
from business_intel_scraper.backend.api.dependencies import require_token
print('✅ Authentication system loaded')
print('🎉 Essential components working!')
"

# Test database connectivity
python3 -c "
import asyncio
from business_intel_scraper.database.config import check_database_health

async def test():
    health = await check_database_health()
    print(f'Database Status: {health}')

asyncio.run(test())
"
```

**Note**: Some advanced API modules may show warnings during full import testing. This is normal and doesn't affect core functionality.

---

## 🖥️ Running the Application

### Option A: Local Development (Recommended for testing)

#### Start the API Server

```bash
# Start the FastAPI server
uvicorn business_intel_scraper.backend.api.main:app --reload --port 8000

# You should see output like:
# INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO: Started reloader process
```

#### Test the API

Open a new terminal and test the endpoints:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Open API documentation in browser
# Visit: http://localhost:8000/docs
```

#### Start the CLI Tool

```bash
# Test the command-line interface
python bis.py --help

# Example: Start a basic crawling job
python bis.py crawl --url https://example.com --depth 1
```

### Option B: Frontend Development (Optional)

If you want to work with the web interface:

```bash
# Install Node.js dependencies
cd business_intel_scraper/frontend
npm install

# Start the development server
npm run dev
# OR if using older npm versions:
npm start

# Frontend will be available at: http://localhost:3000
cd ../../  # Return to project root
```

### Option C: Docker Deployment (Production-like)

For a complete production-like setup:

```bash
# Start Redis (required for task queuing)
docker run -d -p 6379:6379 --name redis redis:7

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

---

## 🧪 Testing Your Installation

### Step 1: Basic Functionality Test

```bash
# Run the comprehensive test suite
python3 comprehensive_test_suite.py
```

### Step 2: Database Test

```bash
# Test database operations
python3 -c "
import asyncio
from business_intel_scraper.database.config import get_async_session
from sqlalchemy import text

async def test_db():
    async with get_async_session() as session:
        result = await session.execute(text('SELECT 1 as test'))
        print(f'✅ Database query successful: {result.scalar()}')

asyncio.run(test_db())
"
```

### Step 3: API Endpoint Test

```bash
# Test API endpoints (make sure server is running first)
curl -X GET http://localhost:8000/health
curl -X GET http://localhost:8000/docs
```

### Step 4: CLI Test

```bash
# Test command-line interface
python bis.py --version
python bis.py --help
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "ModuleNotFoundError" when importing

**Problem**: Python can't find the business_intel_scraper module

**Solution**:
```bash
# Make sure you're in the project root and virtual environment is activated
pwd  # Should show /path/to/scraper
source .venv/bin/activate  # If not already activated

# Install in development mode
pip install -e .
```

#### 2. Database connection errors

**Problem**: SQLite database issues

**Solution**:
```bash
# Check if data.db file exists and has correct permissions
ls -la data.db

# If file doesn't exist, reinitialize
rm -f data.db  # Remove if corrupted
python3 -c "
from business_intel_scraper.database.config import init_database
import asyncio
asyncio.run(init_database())
"
```

#### 3. Port already in use

**Problem**: Port 8000 is already occupied

**Solution**:
```bash
# Use a different port
uvicorn business_intel_scraper.backend.api.main:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

#### 4. Permission denied on .env file

**Problem**: Environment file permissions error

**Solution**:
```bash
# Fix file permissions
chmod 600 .env
ls -la .env  # Should show -rw-------
```

#### 5. Missing dependencies

**Problem**: ImportError for specific packages

**Solution**:
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt

# Or install specific missing package
pip install package_name
```

---

## 🚦 Validation Checklist

Before proceeding to use the platform, verify these items:

- [ ] ✅ Virtual environment activated
- [ ] ✅ All dependencies installed (`pip list` shows required packages)
- [ ] ✅ `.env` file configured with secure permissions (600)
- [ ] ✅ Database initialized and accessible
- [ ] ✅ API server starts without errors
- [ ] ✅ Health endpoint returns 200 OK
- [ ] ✅ CLI tool responds to `--help`
- [ ] ✅ Core imports work without errors
- [ ] ✅ Authentication system loaded
- [ ] ✅ No critical warnings in logs

---

## 🔐 Security Configuration

### Production Security Checklist

- [ ] **SECRET_KEY**: Use the provided secure key (64-character hex)
- [ ] **File Permissions**: `.env` file has 600 permissions
- [ ] **Environment Variables**: No sensitive data in version control
- [ ] **Database**: SQLite file has appropriate access controls
- [ ] **Network**: Configure firewall rules for production
- [ ] **HTTPS**: Use reverse proxy (nginx) with SSL in production

### Environment Security

```bash
# Verify secure configuration
ls -la .env  # Should show -rw-------
grep SECRET_KEY .env  # Should show the 64-character key
```

---

## 📚 Next Steps

After successful installation:

1. **Read the Documentation**:
   - [API Usage Guide](api_usage.md)
   - [Architecture Overview](architecture.md)
   - [Developer Guide](developer_guide.md)

2. **Start Development**:
   - Explore the API at http://localhost:8000/docs
   - Try basic scraping with CLI: `python bis.py crawl --help`
   - Test the database interface

3. **Production Deployment**:
   - [Deployment Guide](deployment.md)
   - Configure monitoring and logging
   - Set up backup procedures

---

## 🆘 Getting Help

If you encounter issues not covered in this guide:

1. **Check the logs**: Look for error messages in terminal output
2. **Review documentation**: Check other files in the `docs/` directory
3. **Validate environment**: Run the test suite again
4. **Check dependencies**: Ensure all requirements are met

**Remember**: This platform is production-ready with all critical issues resolved. Most setup problems are related to environment configuration or missing dependencies.

---

## 📊 Platform Overview

Once setup is complete, you'll have access to:

- **REST API**: FastAPI server with comprehensive endpoints
- **GraphQL API**: Advanced querying capabilities
- **CLI Tool**: Command-line interface for batch operations
- **Database**: SQLite with full async/sync support
- **Security**: JWT authentication and rate limiting
- **Frontend**: React-based web interface (optional)
- **Task Queue**: Celery for background job processing
- **Monitoring**: Health checks and performance metrics

**Your Business Intelligence Scraper platform is now ready for real-world use!** 🎉
