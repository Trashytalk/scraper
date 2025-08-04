# Backend Setup & Architecture Guide

This document provides comprehensive information about the backend setup, architecture, and key components of the Enterprise Visual Analytics Platform.

## 📋 Table of Contents

- [Quick Setup](#quick-setup)
- [Architecture Overview](#architecture-overview)
- [Core Components](#core-components)
- [API Endpoints](#api-endpoints)
- [Database Configuration](#database-configuration)
- [Security Implementation](#security-implementation)
- [Performance & Monitoring](#performance--monitoring)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)


---


## 🚀 Quick Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 13+ (or SQLite for development)
- Redis 6+ (for caching and task queue)
- Docker & Docker Compose (recommended)

### Environment Setup

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/Trashytalk/scraper.git
   cd scraper
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database Setup**
   ```bash
   # The system will automatically use SQLite if DATABASE_URL is set to sqlite:///data.db
   # Initialize the database (creates tables)
   python -c "from business_intel_scraper.database.config import init_database; import asyncio; asyncio.run(init_database())"

   # For PostgreSQL (if you prefer), first start PostgreSQL server:
   # sudo systemctl start postgresql  # or brew services start postgresql on macOS
   # createdb visual_analytics
   # Then update .env with: DATABASE_URL=postgresql://username:password@localhost:5432/visual_analytics
   ```

6. **Start Backend Services**
   ```bash
   # Development server
   uvicorn business_intel_scraper.backend.api.main:app --reload --host 0.0.0.0 --port 8000

   # Or with Docker
   docker-compose -f business_intel_scraper/docker-compose.yml up --build
   ```


---


## 🏗️ Architecture Overview

### System Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   React Frontend    │◄──►│   FastAPI Backend    │◄──►│   PostgreSQL DB     │
│   (Port 3000)       │    │   (Port 8000)        │    │   (Port 5432)       │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
          │                           │                           │
          │                  ┌────────▼────────┐                 │
          │                  │   Redis Cache    │                 │
          │                  │   (Port 6379)    │                 │
          │                  └─────────────────┘                 │
          │                                                      │
     ┌────▼──────────────────────────────────────────────────────▼────┐
     │              Monitoring & Logging Stack                        │
     │  Prometheus (Port 9090) + Grafana (Port 3001)                │
     └───────────────────────────────────────────────────────────────┘

```

### Backend Component Structure

```
business_intel_scraper/backend/
├── api/                     # FastAPI routes and endpoints
│   ├── main.py             # Main FastAPI application
│   ├── auth.py             # Authentication endpoints
│   ├── visualization.py    # Data visualization APIs
│   ├── analytics.py        # Analytics dashboard APIs
│   ├── documentation.py    # Enhanced API documentation
│   └── schemas.py          # Pydantic models
├── db/                     # Database layer
│   ├── models.py           # SQLAlchemy ORM models
│   ├── utils.py            # Database utilities
│   └── pipeline.py         # Data processing pipeline
├── utils/                  # Utility modules
│   ├── security.py         # Security & encryption
│   ├── performance.py      # Performance optimization
│   ├── compliance.py       # GDPR compliance
│   └── advanced_features.py # Advanced platform features
├── nlp/                    # Natural Language Processing
│   ├── pipeline.py         # NLP processing pipeline
│   └── cleaning.py         # Text cleaning utilities
├── geo/                    # Geographic processing
│   └── processing.py       # Location data processing
└── workers/                # Background task workers
    └── tasks.py            # Celery task definitions

```


---


## 🔧 Core Components

### 1. FastAPI Application (`api/main.py`)

**Main Features:**
- RESTful API with automatic OpenAPI/Swagger documentation
- WebSocket support for real-time updates
- Middleware for CORS, security, analytics, and metrics
- JWT-based authentication system
- Rate limiting and request validation

**Key Endpoints:**
- `/health` - Health check endpoint
- `/docs` - Interactive API documentation
- `/metrics` - Prometheus metrics endpoint
- `/auth/*` - Authentication endpoints
- `/api/v1/visualization/*` - Data visualization APIs
- `/api/v1/analytics/*` - Analytics dashboard APIs

### 2. Database Layer (`db/models.py`)

**Core Models:**

```python

# Primary entity model

class Entity(Base):
    __tablename__ = "entities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100))
    properties: Mapped[dict] = mapped_column(JSON)
    confidence: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# Relationship connections

class Connection(Base):
    __tablename__ = "connections"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    target_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    relationship_type: Mapped[str] = mapped_column(String(100))
    strength: Mapped[float] = mapped_column(default=0.0)
    properties: Mapped[dict] = mapped_column(JSON)

# Geographic data

class Location(Base):
    __tablename__ = "locations"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    address: Mapped[str] = mapped_column(Text)
    properties: Mapped[dict] = mapped_column(JSON)

# Timeline events

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey("entities.id"))
    event_type: Mapped[str] = mapped_column(String(100))
    timestamp: Mapped[datetime]
    properties: Mapped[dict] = mapped_column(JSON)

```

### 3. Security System (`utils/security.py`)

**Security Features:**
- **Encryption**: AES-256 encryption for sensitive data
- **Authentication**: JWT-based authentication with RSA key pairs
- **2FA Support**: TOTP-based two-factor authentication
- **Audit Logging**: Comprehensive security event logging
- **Rate Limiting**: IP-based request rate limiting
- **Input Validation**: SQL injection and XSS protection

**Usage Example:**

```python

from business_intel_scraper.backend.utils.security import EncryptionManager

# Initialize encryption

enc = EncryptionManager()

# Encrypt sensitive data

encrypted_data = enc.encrypt_text("sensitive information")
decrypted_data = enc.decrypt_text(encrypted_data)

# Security middleware automatically handles

# - Request validation

# - Rate limiting

# - Audit logging

# - Security headers

```

### 4. Performance Optimization (`utils/performance.py`)

**Performance Features:**
- **Redis Caching**: Multi-layer caching with TTL management
- **Query Optimization**: Database query performance optimization
- **Monitoring**: Real-time performance metrics collection
- **Memory Management**: Efficient memory usage tracking

**Cache Usage:**

```python

from business_intel_scraper.backend.utils.performance import CacheManager

cache = CacheManager()

# Cache data with TTL

await cache.set("key", "value", ttl=3600)
cached_value = await cache.get("key")

# Performance monitoring

from business_intel_scraper.backend.utils.performance import PerformanceMonitor

monitor = PerformanceMonitor()
await monitor.record_metric("response_time", 0.125)
metrics = await monitor.get_metrics()

```


---


## 📡 API Endpoints

### Authentication Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user info

### Data Visualization Endpoints

- `GET /api/v1/visualization/network-data` - Network graph data
- `GET /api/v1/visualization/timeline-data` - Timeline visualization data
- `GET /api/v1/visualization/geospatial-data` - Geographic data
- `POST /api/v1/visualization/filter` - Apply data filters

### Analytics Dashboard Endpoints

- `GET /api/v1/analytics/overview` - Dashboard overview
- `GET /api/v1/analytics/performance` - Performance metrics
- `GET /api/v1/analytics/insights` - Data insights
- `GET /api/v1/analytics/alerts` - System alerts

### Health & Monitoring Endpoints

- `GET /health` - Basic health check
- `GET /metrics` - Prometheus metrics
- `GET /api/version` - API version information
- `GET /api/capabilities` - Feature capabilities

### Real-time Endpoints

- `WebSocket /ws/updates` - Real-time data updates
- `GET /logs/stream` - Server-Sent Events log streaming


---


## 🗄️ Database Configuration

### Connection Setup (`database/config.py`)

```python

# Database configuration with connection pooling

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "visual_analytics"),
    "username": os.getenv("DB_USER", "va_user"),
    "password": os.getenv("DB_PASSWORD", "secure_password"),
}

# Async engine with optimized settings

async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Connection pool size
    max_overflow=30,       # Max overflow connections
    pool_timeout=30,       # Pool timeout seconds
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=DEBUG_MODE        # Log SQL queries in debug
)

```

### Database Session Management

```python

# Async session context manager

from business_intel_scraper.database.config import get_async_session

async def process_data():
    async with get_async_session() as session:
        # Database operations
        entity = Entity(name="Example", entity_type="test")
        session.add(entity)
        await session.commit()
        # Session automatically closed and committed

```

### Migration & Initialization

```python

# Initialize database tables

from business_intel_scraper.database.config import init_database
import asyncio

# Run initialization

asyncio.run(init_database())

```


---


## 🔒 Security Implementation

### Environment Variables

```bash

# JWT Configuration

JWT_SECRET_KEY=your-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Security

DB_PASSWORD=your-secure-database-password
ENCRYPTION_KEY=your-32-character-encryption-key

# API Security

API_RATE_LIMIT=100  # requests per minute
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

```

### Security Middleware Configuration

```python

# In main.py - Security middleware is automatically applied

from business_intel_scraper.backend.utils.security import SecurityMiddleware

# Provides

# - SQL injection protection

# - XSS prevention

# - CSRF protection

# - Rate limiting

# - IP blocking for suspicious activity

# - Comprehensive audit logging

```

### Authentication Usage

```python

# Protected endpoint example

from fastapi import Depends
from business_intel_scraper.backend.security import require_token

@app.get("/protected")
async def protected_endpoint(current_user = Depends(require_token)):
    return {"message": f"Hello {current_user.username}"}

```


---


## 📊 Performance & Monitoring

### Prometheus Metrics

The backend automatically exposes metrics at `/metrics`:

```

# Response time metrics

http_request_duration_seconds_bucket
http_requests_total

# Database metrics

database_connections_active
database_query_duration_seconds

# Custom business metrics

business_entities_total
business_connections_total
data_processing_duration_seconds

```

### Performance Monitoring

```python

# Built-in performance monitoring

from business_intel_scraper.backend.utils.performance import performance_tracked

@performance_tracked
async def complex_operation():
    # Operation automatically timed and recorded
    pass

# Cache performance monitoring

cache_hit_rate = await cache.get_hit_rate()
cache_memory_usage = await cache.get_memory_usage()

```

### Health Checks

```python

# Database health check

from business_intel_scraper.database.config import check_database_health

health_status = await check_database_health()

# Returns: {"status": "healthy", "connection_pool": "active", "response_time": "12ms"}

```


---


## 🔄 Development Workflow

### 1. Local Development Setup

```bash

# Setup development environment

cp .env.example .env.development
source .venv/bin/activate

# Install development dependencies

pip install -r requirements.txt

# Run with hot reload

uvicorn business_intel_scraper.backend.api.main:app --reload --port 8000

# Run background worker (separate terminal)

celery -A business_intel_scraper.backend.workers.tasks.celery_app worker --loglevel=info

```

### 2. Testing

```bash

# Run all tests

pytest business_intel_scraper/backend/tests/

# Run with coverage

pytest --cov=business_intel_scraper business_intel_scraper/backend/tests/

# Test specific component

pytest business_intel_scraper/backend/tests/test_auth_api.py

# Integration testing

python test_simplified_real_world.py
python test_production_business_data.py

```

### 3. Code Quality

```bash

# Format code

black business_intel_scraper/backend/
ruff format business_intel_scraper/backend/

# Lint code

ruff check business_intel_scraper/backend/
mypy business_intel_scraper/backend/

```

### 4. Database Migrations

```bash

# Generate migration

alembic revision --autogenerate -m "Add new feature"

# Apply migration

alembic upgrade head

# Rollback migration

alembic downgrade -1

```


---


## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Database Connection Issues

```bash

# Check database connectivity

python -c "
from business_intel_scraper.database.config import check_database_health
import asyncio
print(asyncio.run(check_database_health()))
"

# Common fixes

# - Verify DATABASE_URL in .env

# - Ensure PostgreSQL is running

# - Check firewall settings

# - Verify user permissions

```

#### 2. Redis Connection Issues

```bash

# Test Redis connectivity

python -c "
from business_intel_scraper.backend.utils.performance import CacheManager
import asyncio
cache = CacheManager()
print('Redis connected' if asyncio.run(cache.ping()) else 'Redis disconnected')
"

# Common fixes

# - Start Redis: redis-server

# - Check REDIS_URL in .env

# - Verify Redis port (default 6379)

```

#### 3. Import Errors

```bash

# Verify Python path

export PYTHONPATH="${PYTHONPATH}:/path/to/scraper"

# Or install in development mode

pip install -e .

```

#### 4. Performance Issues

```bash

# Monitor performance metrics

curl http://localhost:8000/metrics

# Check database query performance

python -c "
from business_intel_scraper.backend.utils.performance import PerformanceMonitor
import asyncio
monitor = PerformanceMonitor()
print(asyncio.run(monitor.get_metrics()))
"

```

#### 5. Security Issues

```bash

# Check security audit logs

python -c "
from business_intel_scraper.backend.utils.security import SecurityAuditLogger
import asyncio
audit = SecurityAuditLogger()
print(asyncio.run(audit.get_recent_events(limit=10)))
"

```

### Debug Mode

```bash

# Enable debug mode in .env

DEBUG=true
LOG_LEVEL=DEBUG

# This enables

# - SQL query logging

# - Detailed error traces

# - Performance timing logs

# - Security event details

```

### Logging Configuration

```python

# Custom logging setup

import logging
from business_intel_scraper.backend.utils.logging_config import setup_logging

# Setup comprehensive logging

logger = setup_logging()

# Log levels available

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system error")

```


---


## 📚 Additional Resources

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Development Tools

- **Database Admin**: http://localhost:8080 (if pgAdmin container is running)
- **Redis Admin**: http://localhost:8081 (if Redis Insight is running)
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

### Related Documentation

- [API Usage Guide](api_usage.md)
- [Security Guidelines](security.md)
- [Deployment Guide](deployment.md)
- [Architecture Overview](architecture.md)


---


## 🤝 Contributing

### Code Standards

- Follow PEP 8 Python style guidelines
- Use type hints for all function signatures
- Write docstrings for all public methods
- Maintain test coverage above 80%
- Use async/await for all I/O operations

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Ensure all tests pass locally
4. Update documentation as needed
5. Submit pull request with clear description

### Issue Reporting

- Use GitHub Issues for bug reports
- Include minimal reproduction steps
- Provide system information (OS, Python version)
- Include relevant log output


---


**📧 Support**: For additional help, please refer to the [main project documentation](../README.md) or create an issue in the GitHub repository.
