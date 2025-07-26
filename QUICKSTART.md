# 🚀 Quick Start Guide

Get the Business Intelligence Scraper running in under 5 minutes!

## ⚡ **NEW: One-Command Setup**

```bash
# Clone and start instantly with our comprehensive quick start script
git clone https://github.com/Trashytalk/scraper.git
cd scraper
./quick_start.sh
```

**This single command will:**
- ✅ Check system requirements (Python 3.8+)
- ✅ Set up virtual environment automatically
- ✅ Install all dependencies
- ✅ Configure the application
- ✅ Initialize database
- ✅ Start Redis (via Docker if needed)
- ✅ Launch web server on port 8000
- ✅ Show access information and examples

**Additional Quick Start Options:**
```bash
./quick_start.sh --help       # Show all options
./quick_start.sh --dev        # Start in development mode
./quick_start.sh --status     # Check service status
./quick_start.sh --stop       # Stop all services
./quick_start.sh --clean      # Clean and reset
```

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
