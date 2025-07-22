# Business Intelligence Scraper - Complete Setup Guide

This comprehensive guide will walk you through setting up the Business Intelligence Scraper platform step-by-step, from initial installation to production deployment.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### Required Software
- **Python 3.11+** (3.11 or 3.12 recommended)
- **Git** (for cloning the repository)
- **A text editor or IDE** (VS Code, PyCharm, etc.)

### Optional but Recommended
- **Node.js 18+** (for frontend development)
- **Docker & Docker Compose** (for containerized deployment)
- **Redis** (for task queuing - can be run via Docker)

### System Requirements
- **OS**: Linux, macOS, or Windows (WSL2 recommended for Windows)
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: At least 2GB free space
- **Network**: Internet connection for package downloads

---

## 🚀 Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Verify you're in the correct directory
ls -la
# You should see: business_intel_scraper/, docs/, requirements.txt, etc.
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Verify activation (you should see (.venv) in your prompt)
which python
# Should show: /path/to/scraper/.venv/bin/python
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep sqlalchemy
# You should see the installed packages
```

### Step 4: Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred editor
nano .env
# OR
code .env
```

### Generate a new secret key

'''bash
# Generate a new, unique secret key
python -c "import secrets; print(secrets.token_hex(32))"
'''

**Configure the following critical variables in `.env`:**

```bash
# Database Configuration (SQLite is pre-configured and ready to use)
DATABASE_URL=sqlite:///data.db

# Security (IMPORTANT: This is already set with a secure key)
SECRET_KEY=671e782ab9d1b6fbd7dee1d0eb71225a457cf61e2f8b2a04c68190898720d703

# Redis for task queuing (optional for basic usage)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO

# Optional: External APIs (add your keys if needed)
# GOOGLE_API_KEY=your_google_api_key_here
# API_KEY=your_other_api_keys_here
```

### Step 5: Database Initialization

```bash
# Test database configuration
python3 -c "
from business_intel_scraper.database.config import check_database_health
import asyncio
result = asyncio.run(check_database_health())
print('Database Status:', result)
"

# Initialize database tables
python3 -c "
from business_intel_scraper.database.config import init_database
import asyncio
asyncio.run(init_database())
print('✅ Database initialized successfully!')
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
