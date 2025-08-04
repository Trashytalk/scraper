# 🚀 Quick Start Guide - Business Intelligence Scraper

**Get your Business Intelligence Platform running in 2-3 minutes with our automated setup script!**

## 🎯 **One-Command Setup (Recommended)**

**Step 1: Clone and Navigate**

```bash

git clone https://github.com/Trashytalk/scraper.git
cd scraper

```

**Step 2: Make Script Executable (First Time Only)**

```bash

chmod +x quick_start.sh

```

**Step 3: Start Everything**

```bash

./quick_start.sh

```

### ✨ **What the Quick Start Script Does Automatically**

The `quick_start.sh` script provides a comprehensive automated setup:

- ✅ **System Requirements Check**: Verifies Python 3.8+, pip, and essential dependencies
- ✅ **Environment Setup**: Creates isolated Python virtual environment
- ✅ **Dependency Installation**: Installs all required packages (2-3 minutes)
- ✅ **Database Initialization**: Sets up SQLite database with proper schemas
- ✅ **Redis Server Management**: Starts Redis for caching and session management
- ✅ **Web Server Launch**: Starts FastAPI backend server on port 8000
- ✅ **Health Verification**: Checks all services are running correctly
- ✅ **Access Information**: Provides URLs and login credentials

### 🎉 **Expected Output**

When you run `./quick_start.sh`, you'll see:

```bash

🚀 Business Intelligence Scraper - Quick Start
==============================================

✅ Checking system requirements...
✅ Setting up Python virtual environment...
✅ Installing dependencies (this may take 2-3 minutes)...
✅ Initializing database...
✅ Starting Redis server...
✅ Starting web server...

🎉 Setup Complete!

📊 Dashboard: http://localhost:8000
📖 API Docs: http://localhost:8000/docs
📈 Admin Panel: http://localhost:8000/admin

🔐 Default Login Credentials:
   Username: admin
   Password: admin123

Press Ctrl+C to stop all services

```

## 🔧 **Advanced Quick Start Options**

The quick start script supports multiple modes for different use cases:

### **Development Mode**

```bash

./quick_start.sh --dev

```
- Enables hot reload for code changes
- Provides detailed debugging output
- Uses development configuration

### **Production Mode**

```bash

./quick_start.sh --production

```
- Optimized for production deployment
- Enhanced security settings
- Performance optimizations enabled

### **Clean Installation**

```bash

./quick_start.sh --clean

```
- Removes existing virtual environment
- Fresh installation of all dependencies
- Useful for troubleshooting

### **System Status Check**

```bash

./quick_start.sh --status

```
- Checks if services are running
- Shows port usage and process information
- Validates system health

### **Stop Services**

```bash

./quick_start.sh --stop

```
- Gracefully stops all running services
- Cleans up background processes
- Preserves data and configuration

### **Help and Options**

```bash

./quick_start.sh --help

```
- Shows all available options
- Provides usage examples
- Displays troubleshooting tips

## ⚡ One-Command Setup

```bash

# Clone and setup everything automatically

git clone https://github.com/Trashytalk/scraper.git
cd scraper
./setup.sh

```

## 🎯 5-Minute Demo

```bash

# Run the interactive demo

./demo.sh

```

This will:

- ✅ Start Redis automatically
- ✅ Launch the API server
- ✅ Run an example scraping job
- ✅ Show you where to access the results

## 🌐 Access Points

Once running, you can access:

- **🔗 API Health Check**: <http://localhost:8000/>
- **📚 Interactive API Docs**: <http://localhost:8000/docs>
- **📊 GraphQL Playground**: <http://localhost:8000/graphql>
- **📈 Metrics**: <http://localhost:8000/metrics>

## 📱 Quick API Examples

### Start a Scraping Job

```bash

curl -X POST http://localhost:8000/scrape

# Returns: {"task_id": "abc123..."}

```

### Check Job Status

```bash

curl http://localhost:8000/tasks/abc123

# Returns: {"status": "completed", "result": {...}}

```

### View All Data

```bash

curl http://localhost:8000/data

# Returns: [{"title": "Example Company", "url": "..."}]

```

### Export as CSV

```bash

curl "http://localhost:8000/export?format=csv" > results.csv

```

## 🛠️ Development Setup

```bash

# Setup with development tools

./setup.sh --dev

# Activate environment

source .venv/bin/activate

# Start with auto-reload

cd business_intel_scraper
uvicorn backend.api.main:app --reload

```

## 🎛️ Frontend Dashboard

```bash

# Install frontend (optional)

cd business_intel_scraper/frontend
npm install
npm start

# Access dashboard at http://localhost:8000

```

## 🆘 Need Help?

- **📖 Full Documentation**: [docs/README.md](docs/README.md)
- **🏗️ Architecture**: [docs/architecture.md](docs/architecture.md)
- **⚙️ Configuration**: [docs/setup.md](docs/setup.md)
- **🔒 Security**: [docs/security.md](docs/security.md)

## 🎪 What's Included?

- ✅ **RESTful API** with FastAPI
- ✅ **GraphQL endpoint** for flexible queries
- ✅ **Real-time WebSocket** notifications
- ✅ **Celery task queue** for async processing
- ✅ **Multiple scraping engines** (Scrapy, Playwright)
- ✅ **OSINT integrations** (SpiderFoot, theHarvester, etc.)
- ✅ **Database models** with migrations
- ✅ **Authentication & authorization**
- ✅ **Rate limiting & security**
- ✅ **Prometheus metrics**
- ✅ **Docker containerization**

## 🧪 Run Tests

```bash

# Run comprehensive test coverage

python3 tests/run_full_coverage.py --parallel --coverage --save-reports

# Run specific test suites

python3 tests/run_full_coverage.py --suites root_modules gui_components

# Run legacy test commands

python -m pytest tests/ -v --cov=.

```

## 🔧 Troubleshooting

**Port 8000 already in use?**

```bash

# Find and kill the process

lsof -ti:8000 | xargs kill -9

```

**Redis connection failed?**

```bash

# Start Redis manually

docker run -d -p 6379:6379 --name redis redis:7

```

**Permission denied on setup.sh?**

```bash

chmod +x setup.sh

```


---


🎉 **You're ready to scrape!** Check out the [tutorials](docs/tutorial.md) for more advanced usage.
