# Quick Start Guide - Business Intelligence Scraper
================================================

## 🚀 **One-Command Setup & Launch**

The `quick_start.sh` script provides a complete automated setup and launch solution for the Business Intelligence Scraper Platform.

### **⚡ Instant Setup**

```bash
# Clone and start in one command
git clone https://github.com/Trashytalk/scraper.git
cd scraper
./quick_start.sh
```

That's it! The script will:
- ✅ Check system requirements
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Configure the application
- ✅ Initialize the database
- ✅ Start Redis (if available)
- ✅ Launch the web server
- ✅ Show access information

## 📋 **What the Quick Start Does**

### **System Setup**
- **Python Environment**: Creates and activates virtual environment
- **Dependencies**: Installs all required Python packages
- **Configuration**: Sets up `.env` file with sensible defaults
- **Directories**: Creates necessary data, logs, cache directories
- **Database**: Initializes SQLite database automatically

### **Service Management**
- **Redis**: Attempts to start Redis via Docker if not available
- **Web Server**: Launches FastAPI backend server
- **Health Checks**: Validates all services are running
- **Port Management**: Automatically handles port conflicts

### **Validation**
- **Module Testing**: Validates core modules can be imported
- **Configuration**: Checks configuration files
- **Service Health**: Tests API endpoints
- **Ready State**: Confirms everything is operational

## 🎯 **Command Options**

### **Basic Usage**
```bash
./quick_start.sh              # Full setup and start
./quick_start.sh --help       # Show help information
```

### **Service Management**
```bash
./quick_start.sh --stop       # Stop all services
./quick_start.sh --status     # Check service status
./quick_start.sh --clean      # Clean and reset environment
```

### **Development Options**
```bash
./quick_start.sh --dev        # Start in development mode
./quick_start.sh --no-redis   # Skip Redis setup
```

## 🌐 **Access Points (After Launch)**

Once the quick start completes, you'll have access to:

### **Main API Endpoints**
- **🔗 Main API**: `http://localhost:8000/`
- **📚 API Documentation**: `http://localhost:8000/docs`
- **🔍 Health Check**: `http://localhost:8000/health`
- **📊 Metrics**: `http://localhost:8000/metrics`

### **Quick API Tests**
```bash
# Test health endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Test scraping endpoint (if available)
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## 🛠️ **Requirements & Dependencies**

### **System Requirements**
- **Python**: 3.8+ (automatically checked)
- **OS**: Linux, macOS, Windows (WSL)
- **Memory**: 512MB+ available RAM
- **Disk**: 1GB+ available space

### **Optional Components**
- **Docker**: For Redis container (auto-started if available)
- **curl**: For health checks and API testing
- **Redis**: External Redis server (optional)

### **Automatic Dependencies**
The script automatically installs:
- FastAPI and Uvicorn (web server)
- SQLAlchemy (database ORM)
- Redis client (caching)
- Testing framework (pytest)
- All project-specific requirements

## 🔧 **Configuration**

### **Environment Variables**
The script creates a `.env` file with:

```bash
# Database
DATABASE_URL=sqlite:///./data.db

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=quick-start-secret-key-change-in-production
JWT_SECRET_KEY=quick-start-jwt-secret-change-in-production

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Performance
CACHE_BACKEND=memory
PERFORMANCE_MONITORING=true
```

### **Custom Configuration**
To customize settings:

1. **Stop the server**: `./quick_start.sh --stop`
2. **Edit .env file**: Modify configuration values
3. **Restart**: `./quick_start.sh`

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# The script automatically handles this, but manually:
lsof -ti:8000 | xargs kill -9
./quick_start.sh
```

#### **Python Version Issues**
```bash
# Check Python version
python3 --version

# If < 3.8, install newer Python
# Ubuntu/Debian: sudo apt install python3.9
# macOS: brew install python@3.9
```

#### **Permission Errors**
```bash
# Make script executable
chmod +x quick_start.sh

# Fix directory permissions
chmod 755 data logs cache
```

#### **Redis Not Available**
```bash
# Install Redis via Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or skip Redis
./quick_start.sh --no-redis
```

### **Debugging**

#### **Check Logs**
```bash
# View quick start log
cat quick_start.log

# View server logs
tail -f logs/backend.log

# View all logs
find logs/ -name "*.log" -exec tail -f {} +
```

#### **Service Status**
```bash
# Check all services
./quick_start.sh --status

# Test API manually
curl -v http://localhost:8000/health
```

#### **Clean Restart**
```bash
# Complete clean restart
./quick_start.sh --clean
./quick_start.sh
```

## 🔄 **Development Workflow**

### **Development Mode**
```bash
# Start in development mode
./quick_start.sh --dev

# This enables:
# - Hot reloading
# - Debug logging
# - Development middleware
```

### **Testing Integration**
```bash
# Run comprehensive tests
python3 tests/run_full_coverage.py --coverage

# Run quick tests
pytest tests/ -v

# Run specific test category
python3 tests/run_full_coverage.py --suites root_modules
```

### **Frontend Development**
```bash
# Start frontend (if available)
cd business_intel_scraper/frontend
npm install
npm run dev

# Access frontend at http://localhost:5173
```

## 📊 **Next Steps**

### **Explore the Platform**
1. **API Documentation**: Visit `http://localhost:8000/docs`
2. **Test Endpoints**: Use the interactive API documentation
3. **Run Tests**: Execute `python3 tests/run_full_coverage.py --coverage`
4. **Check Monitoring**: View `http://localhost:8000/metrics`

### **Start Scraping**
```bash
# Submit a scraping job
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "scraper_type": "general",
    "options": {"extract_text": true}
  }'
```

### **View Data**
```bash
# Get scraped data
curl http://localhost:8000/api/data

# Export data
curl "http://localhost:8000/api/export?format=csv" > results.csv
```

## 🔒 **Security Notes**

### **Production Deployment**
⚠️ **Important**: The quick start uses development settings. For production:

1. **Change Secret Keys**: Update all secrets in `.env`
2. **Use PostgreSQL**: Replace SQLite with PostgreSQL
3. **Configure SSL**: Set up HTTPS certificates
4. **Enable Authentication**: Configure JWT authentication
5. **Firewall Rules**: Secure network access

### **Development Security**
- Default secrets are for development only
- Server binds to all interfaces (0.0.0.0)
- Debug mode is enabled
- No authentication required

## 🎉 **Success!**

If you see this message, your Business Intelligence Scraper is running:

```
🚀 Business Intelligence Scraper - Quick Start Complete!
===============================================

✅ Server Status:
   Backend Server: RUNNING on port 8000

🌐 Access Points:
   🔗 Main API:        http://localhost:8000/
   📚 API Docs:       http://localhost:8000/docs
   🔍 Health Check:   http://localhost:8000/health
   📊 Metrics:        http://localhost:8000/metrics

✨ Your Business Intelligence Scraper is ready!
```

**You're all set!** 🎯

---

## 📞 **Support**

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: Check logs in `quick_start.log` and `logs/`
- **Help**: Run `./quick_start.sh --help`
- **Clean Reset**: Run `./quick_start.sh --clean`
