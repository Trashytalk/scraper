# 🔧 Repository Architecture & Configuration Guide

## 📋 Overview

This document describes the enhanced architecture and configuration system implemented in the Business Intelligence Scraper repository. The system has been significantly improved with centralized configuration, structured logging, connection pooling, and robust error handling.


---


## 🏗️ Architecture Overview

### Core Systems

1. **Centralized Configuration** (`config/environment.py`)
2. **Structured Logging** (`config/logging_config.py`)
3. **Database Connection Management** (`config/database_manager.py`)
4. **Distributed Queue System** (`business_intel_scraper/backend/queue/distributed_crawler.py`)
5. **Performance Monitoring** (`backend_server.py`)


---


## ⚙️ Configuration Management

### Environment-Based Configuration

The system uses centralized environment-based configuration for easy deployment across different environments.

#### Configuration Files

- **`config/environment.py`** - Main configuration class
- **`config/.env.template`** - Template for environment variables

#### Usage

```python

from config.environment import get_config, get_test_credentials

config = get_config()
api_url = config.API_BASE_URL
credentials = get_test_credentials()

```

#### Environment Variables

```bash

# Core Settings

ENVIRONMENT=development  # or production
API_HOST=localhost
API_PORT=8000
FRONTEND_HOST=localhost
FRONTEND_PORT=5173

# Security (CRITICAL: Change in production)

DEFAULT_USERNAME=admin
DEFAULT_PASSWORD=admin123
JWT_SECRET=your-secret-key-change-in-production

# Database

DATABASE_URL=sqlite:///data.db

# Performance

MAX_PAGES_DEFAULT=50
MAX_DEPTH_DEFAULT=3
REQUEST_TIMEOUT=30

```

#### Production Deployment

1. Copy `config/.env.template` to `.env`
2. Update all security-related variables
3. Set `ENVIRONMENT=production`
4. Configure appropriate database URL


---


## 📝 Logging System

### Structured Logging

The system implements structured logging with consistent formatting across all modules.

#### Features

- **Color-coded console output** for development
- **File logging** for production persistence
- **Context-aware formatting** with metadata
- **Centralized configuration** for all modules

#### Usage

```python

from config.logging_config import get_logger, log_security_event

# Module-specific logger

logger = get_logger("my_module")
logger.info("Operation completed", user="admin", duration=1.2)

# Convenience functions

log_security_event("Login attempt", user="admin", success=True)

```

#### Log Format

```
11:19:53 | INFO | security | Login attempt | user=admin | success=True

```

#### File Logging

- Location: `logs/YYYY-MM-DD_scraper.log`
- Format: Includes timestamp, level, module, function, and message
- Rotation: Daily log files


---


## 💾 Database Management

### Connection Pooling

The system implements intelligent database connection pooling for optimal performance.

#### Features

- **Thread-safe connection pool** with configurable limits
- **Automatic connection lifecycle management**
- **Health monitoring** and statistics
- **Optimized SQLite settings** for performance

#### Usage

```python

from config.database_manager import (
    initialize_database_pool,
    execute_query,
    execute_update,
    get_database_stats
)

# Initialize pool (typically in application startup)

pool = initialize_database_pool("data.db", max_connections=10)

# Execute queries

results = execute_query("SELECT * FROM users WHERE active = ?", (1,))
affected = execute_update("UPDATE users SET last_login = ? WHERE id = ?", (time.time(), user_id))

# Monitor performance

stats = get_database_stats()

```

#### Pool Statistics

```json

{
  "total_connections": 5,
  "active_connections": 2,
  "available_connections": 3,
  "max_connections": 10,
  "total_queries": 1247,
  "avg_query_time_ms": 2.3,
  "pool_utilization": 20.0
}

```


---


## 🔄 Queue Management

### SQLite-Based Distributed Queuing

The system implements a robust distributed crawling queue using SQLite as the backend.

#### Features

- **Multiple specialized queues** (frontier, parse, retry, dead)
- **Thread-safe operations** with connection pooling
- **Automatic retry logic** with exponential backoff
- **Comprehensive monitoring** and statistics

#### Queue Types

1. **Frontier Queue** - URLs to be crawled
2. **Parse Queue** - Pages to be parsed
3. **Retry Queue** - Failed URLs for retry
4. **Dead Queue** - Permanently failed URLs

#### Usage

```python

from business_intel_scraper.backend.queue.distributed_crawler import SQLiteQueueManager

queue = SQLiteQueueManager()

# Add URL to frontier

await queue.put_frontier_url(crawl_url)

# Get next URL to crawl

next_url = await queue.get_frontier_url()

# Monitor queue status

stats = queue.get_queue_stats()

```


---


## ⚡ Performance Monitoring

### Enhanced Metrics Collection

The system includes comprehensive performance monitoring with fallback implementations.

#### Features

- **Request timing** and endpoint metrics
- **System resource monitoring** (CPU, memory, disk)
- **Smart caching** with TTL and LRU policies
- **Performance alerts** for resource thresholds

#### Metrics Available

```json

{
  "requests": {
    "total": 1523,
    "avg_duration_ms": 245.7,
    "success_rate": 98.2
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.6,
    "disk_usage_percent": 62.1
  },
  "cache": {
    "hit_rate": 89.3,
    "total_size": 256,
    "max_size": 1000
  }
}

```


---


## 🔧 Development Setup

### Quick Start

1. **Clone and Setup:**

```bash

git clone <repository>
cd scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```

2. **Configure Environment:**

```bash

cp config/.env.template .env

# Edit .env with your settings

```

3. **Initialize Services:**

```bash

python3 backend_server.py

```

### Development Commands

```bash

# Run tests

python3 tests/test_repository_fixes.py

# Check database health

python3 -c "from config.database_manager import database_health_check; print(database_health_check())"

# View logs

tail -f logs/$(date +%Y-%m-%d)_scraper.log

# Monitor performance

python3 -c "from config.database_manager import get_database_stats; print(get_database_stats())"

```


---


## 🚀 Production Deployment

### Deployment Checklist

#### Security Configuration

- [ ] Change `DEFAULT_PASSWORD` from default
- [ ] Set strong `JWT_SECRET` (32+ characters)
- [ ] Use HTTPS for API endpoints
- [ ] Configure proper database URL
- [ ] Set `ENVIRONMENT=production`

#### Performance Configuration

- [ ] Adjust `MAX_CONNECTIONS` for database pool
- [ ] Configure appropriate `CACHE_MAX_SIZE`
- [ ] Set resource monitoring thresholds
- [ ] Enable log rotation

#### Infrastructure

- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Configure log aggregation
- [ ] Set up monitoring alerts

### Docker Deployment

```bash

# Production deployment with Docker

docker-compose -f docker-compose.production.yml up -d

```

### Health Monitoring

```bash

# Health check endpoint

curl http://localhost:8000/health

# Database health

curl http://localhost:8000/api/system/database/health

# Performance metrics

curl http://localhost:8000/api/system/performance

```


---


## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash

# Check database connectivity

python3 -c "
from config.database_manager import database_health_check
print(database_health_check())
"

```

#### Configuration Issues

```bash

# Verify configuration

python3 -c "
from config.environment import get_config
config = get_config()
print(f'API URL: {config.API_BASE_URL}')
print(f'Environment: {config.is_production()}')
"

```

#### Queue Issues

```bash

# Check queue status

python3 -c "
from business_intel_scraper.backend.queue.distributed_crawler import SQLiteQueueManager
queue = SQLiteQueueManager()
print(queue.get_queue_stats())
"

```

### Log Analysis

```bash

# Recent errors

grep "ERROR" logs/$(date +%Y-%m-%d)_scraper.log | tail -10

# Security events

grep "security" logs/$(date +%Y-%m-%d)_scraper.log

# Performance metrics

grep "performance" logs/$(date +%Y-%m-%d)_scraper.log

```


---


## 📊 Monitoring & Metrics

### Key Performance Indicators

1. **System Health:**
   - Database connection pool utilization
   - API response times
   - Error rates

2. **Queue Performance:**
   - Queue lengths and processing rates
   - Retry queue accumulation
   - Dead queue items

3. **Resource Usage:**
   - CPU and memory utilization
   - Disk space usage
   - Cache hit rates

### Alerting Thresholds

- Database pool utilization > 80%
- API error rate > 5%
- Queue backup > 1000 items
- CPU usage > 85%
- Memory usage > 90%


---


## 🔄 Maintenance

### Regular Tasks

#### Daily

- Check log files for errors
- Monitor queue statistics
- Verify database health

#### Weekly

- Review performance metrics
- Check disk space usage
- Rotate log files if needed

#### Monthly

- Update dependencies
- Review security settings
- Performance optimization review

### Backup Procedures

```bash

# Database backup

cp data.db backup/data_$(date +%Y%m%d).db

# Configuration backup

tar -czf backup/config_$(date +%Y%m%d).tar.gz config/

# Log archive

tar -czf backup/logs_$(date +%Y%m%d).tar.gz logs/

```


---


## 📚 API Reference

### Configuration Endpoints

- `GET /api/config` - Current configuration
- `GET /api/config/health` - Configuration health check

### Database Endpoints

- `GET /api/system/database/health` - Database health
- `GET /api/system/database/stats` - Connection pool statistics

### Queue Endpoints

- `GET /api/queue/stats` - Queue statistics
- `POST /api/queue/reset` - Reset queues (admin only)

### Performance Endpoints

- `GET /api/system/performance` - Performance metrics
- `GET /api/system/health` - Overall system health


---


**Documentation Last Updated:** August 3, 2025
**Version:** 2.0.0 (Post-Polish)
**Compatibility:** Python 3.8+, SQLite 3.31+**
