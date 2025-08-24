# Docker Deployment Guide

## Business Intelligence Scraper - Production Deployment

This guide covers the complete Docker-based deployment of the Business Intelligence Scraper with performance monitoring, security, and production-ready features.

## 🏗️ Architecture Overview

The production deployment includes:

- **API Server**: FastAPI-based backend with security and performance monitoring
- **Redis**: Caching and session storage
- **PostgreSQL**: Production database (optional, defaults to SQLite)
- **Nginx**: Reverse proxy and load balancer
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Visualization and dashboards
- **Frontend**: React-based user interface

## 🚀 Quick Start

### Prerequisites

- Docker (>= 20.10)
- Docker Compose (>= 2.0)
- 4GB+ RAM available
- 10GB+ disk space

### 1. Clone and Setup

```bash

git clone <your-repo>
cd scraper

```

### 2. Configure Environment

The deployment script will automatically generate secure secrets, but you can customize:

```bash

# Edit environment variables if needed

cp .env.example .env

```

### 3. Deploy Production Stack

```bash

# Run the automated deployment

./deploy.sh

```

Or manually:

```bash

# Build and start all services

docker-compose -f docker-compose.prod.yml up -d

# Check service status

docker-compose -f docker-compose.prod.yml ps

```

## 🔧 Configuration Options

### Environment Variables

|      Variable | Description | Default      |
|     ----------|-------------|---------     |
|      `ENVIRONMENT` | Deployment environment | `production`      |
|      `DATABASE_PATH` | SQLite database path | `/app/data/scraper.db`      |
|      `REDIS_URL` | Redis connection URL | `redis://redis:6379/0`      |
|      `JWT_SECRET` | JWT signing secret | Auto-generated      |
|      `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000`      |

### Service Ports

|      Service | Port | Description      |
|     ---------|------|-------------     |
|      API Server | 8000 | Main application API      |
|      Frontend | 3000 | Web interface      |
|      Grafana | 3001 | Monitoring dashboard      |
|      Prometheus | 9090 | Metrics collection      |
|      Redis | 6379 | Cache and sessions      |
|      PostgreSQL | 5432 | Database      |
|      Nginx | 80/443 | Reverse proxy      |

## 📊 Monitoring & Performance

### Metrics Available

- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: Request rates, response times, error rates
- **Database Metrics**: Query performance, connection pooling
- **Cache Metrics**: Hit rates, memory usage
- **Security Metrics**: Authentication attempts, rate limiting

### Accessing Monitoring

1. **Grafana Dashboard**: http://localhost:3001
   - Username: `admin`
   - Password: See `secrets/grafana_password.txt`

2. **Prometheus Metrics**: http://localhost:9090

3. **API Performance**: http://localhost:8000/api/performance/summary

### Health Checks

All services include health checks:

```bash

# Check overall system health

curl http://localhost:8000/api/health

# Check individual service health

docker-compose -f docker-compose.prod.yml ps

```

## 🔒 Security Features

### Production Security

- **SSL/TLS**: Configure certificates in `docker/nginx/ssl/`
- **Rate Limiting**: API and authentication endpoints protected
- **Security Headers**: HSTS, CSP, XSS protection enabled
- **Input Validation**: All inputs sanitized and validated
- **Secrets Management**: Docker secrets for sensitive data
- **Non-root User**: Application runs as non-privileged user

### Authentication

- **JWT Tokens**: Secure token-based authentication
- **bcrypt Hashing**: Password security with salt
- **Role-based Access**: Admin and user roles

## 🔧 Development Mode

For development with hot reloading:

```bash

# Start development environment

docker-compose -f docker-compose.dev.yml up -d

# View logs

docker-compose -f docker-compose.dev.yml logs -f scraper-api

```

## 📝 Maintenance

### Backup Data

```bash

# Backup SQLite database

docker-compose -f docker-compose.prod.yml exec scraper-api cp /app/data/scraper.db /app/data/backup-$(date +%Y%m%d).db

# Backup PostgreSQL

docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U scraper scraper > backup-$(date +%Y%m%d).sql

```

### Update Application

```bash

# Pull latest changes

git pull

# Rebuild and restart

docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

```

### View Logs

```bash

# All services

docker-compose -f docker-compose.prod.yml logs

# Specific service

docker-compose -f docker-compose.prod.yml logs scraper-api

# Follow logs

docker-compose -f docker-compose.prod.yml logs -f scraper-api

```

### Scale Services

```bash

# Scale API servers

docker-compose -f docker-compose.prod.yml up -d --scale scraper-api=3

# Check scaled services

docker-compose -f docker-compose.prod.yml ps

```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   sudo chmod 700 secrets/
   sudo chmod 600 secrets/*.txt
   ```

2. **Services Not Starting**
   ```bash
   docker-compose -f docker-compose.prod.yml logs
   docker system prune -f
   ```

3. **Out of Memory**
   ```bash
   # Increase Docker memory limit or reduce services
   docker-compose -f docker-compose.prod.yml down nginx grafana prometheus
   ```

4. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose -f docker-compose.prod.yml logs postgres

   # Reset database
   docker-compose -f docker-compose.prod.yml down
   docker volume rm scraper_postgres_data
   ```

### Performance Tuning

1. **Redis Memory**
   - Adjust `maxmemory` in docker-compose.yml
   - Monitor with Redis CLI: `docker-compose exec redis redis-cli info memory`

2. **Database Performance**
   - Monitor query performance: http://localhost:8000/api/performance/summary
   - Check slow queries in PostgreSQL logs

3. **API Performance**
   - Monitor response times: http://localhost:8000/api/performance/metrics
   - Scale API servers if needed

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml

name: Deploy Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production

        run: |
          ./deploy.sh
          curl -f http://localhost:8000/api/health

```

### Health Check Endpoint

The API provides comprehensive health checks at `/api/health`:

```json

{
  "status": "healthy",
  "timestamp": "2025-07-23T20:00:00Z",
  "version": "1.0.0",
  "performance": {
    "requests_per_minute": 45.2,
    "avg_response_time": 0.123,
    "error_rate": 0.5
  },
  "system": {
    "cpu_percent": 15.3,
    "memory_percent": 45.8,
    "uptime_seconds": 86400
  }
}

```

## 📞 Support

For issues and questions:

1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Review monitoring dashboards: http://localhost:3001
3. Check API documentation: http://localhost:8000/docs
4. Monitor system performance: http://localhost:8000/api/performance/summary


---


**🎉 Production deployment complete!**

Your Business Intelligence Scraper is now running with enterprise-grade security, performance monitoring, and production-ready infrastructure.
