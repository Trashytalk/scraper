# 🚀 Production Deployment Guide

# Business Intelligence Scraper v3.0 - Enterprise Production Deployment

## 📋 Overview

This guide covers the complete production deployment of the Business Intelligence Scraper using Docker containers, orchestrated with Docker Compose, and monitored with Prometheus/Grafana.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Application   │    │    Database     │
│     (Nginx)     │────│    (FastAPI)    │────│  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │      Cache      │    │   Monitoring    │
         └──────────────│     (Redis)     │    │ (Prometheus)    │
                        └─────────────────┘    └─────────────────┘

```

## 🔧 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 100GB+ SSD
- **Network**: Static IP with domain name

### Software Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- curl/wget
- jq (for JSON processing)

### Installation Commands

```bash

# Install Docker

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose

sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation

docker --version
docker-compose --version

```

## 📦 Deployment Steps

### 1. Clone Repository

```bash

git clone https://github.com/yourusername/business-intelligence-scraper.git
cd business-intelligence-scraper

```

### 2. Configure Environment

```bash

# Copy environment template

cp .env.production.template .env.production

# Edit production settings

nano .env.production

```

### 3. Set Production Secrets

```bash

# Generate secure passwords

openssl rand -base64 32  # For JWT_SECRET_KEY
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD

# Update .env.production with secure values

```

### 4. Deploy Application

```bash

# Make deployment script executable

chmod +x scripts/deploy.sh

# Deploy with backup

./scripts/deploy.sh deploy

# Or skip backup for initial deployment

./scripts/deploy.sh deploy --skip-backup

```

### 5. Verify Deployment

```bash

# Check deployment status

./scripts/deploy.sh status

# Run health checks

./scripts/deploy.sh health

# View logs

./scripts/deploy.sh logs

```

## ⚙️ Configuration Details

### Environment Variables (.env.production)

```bash

# Database

POSTGRES_USER=bisuser
POSTGRES_PASSWORD=your_secure_db_password
POSTGRES_DB=business_intelligence

# Redis

REDIS_PASSWORD=your_secure_redis_password

# Application Security

JWT_SECRET_KEY=your_jwt_secret_key
API_SECRET_KEY=your_api_secret_key

# Domain Configuration

ALLOWED_HOSTS=yourdomain.com,app.yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Monitoring

GRAFANA_PASSWORD=your_grafana_password

# Build Information

BUILD_DATE=2025-08-02T00:00:00Z
VERSION=3.0.0
VCS_REF=main

# Performance

LOG_LEVEL=INFO
WORKERS=4

```

### SSL/TLS Configuration

```bash

# Generate SSL certificates (Let's Encrypt recommended)

sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Update nginx configuration with SSL

# Edit docker/nginx-production.conf

```

## 🔒 Security Best Practices

### 1. Network Security

- Use firewall rules to restrict access
- Only expose necessary ports (80, 443)
- Use VPN for administrative access

### 2. Application Security

- Change all default passwords
- Use strong JWT secrets
- Enable rate limiting
- Regular security updates

### 3. Data Security

- Encrypt database connections
- Regular backups with encryption
- Access logging and monitoring

## 📊 Monitoring & Observability

### 1. Health Monitoring

- **Application Health**: http://yourdomain.com/api/health
- **Grafana Dashboard**: http://yourdomain.com:3000
- **Prometheus Metrics**: http://yourdomain.com:9090

### 2. Log Management

```bash

# View application logs

docker-compose -f docker-compose.production-v3.yml logs -f app

# View all service logs

docker-compose -f docker-compose.production-v3.yml logs -f

# Log rotation is automatically configured

```

### 3. Alerting

- Configure Slack/email notifications
- Set up custom alert rules
- Monitor key performance indicators

## 🔄 Maintenance Operations

### Backup Operations

```bash

# Manual backup

./scripts/deploy.sh backup

# Automated backups are configured via cron

# Add to crontab: 0 2 * * * /path/to/scripts/deploy.sh backup

```

### Scaling Operations

```bash

# Scale application horizontally

./scripts/deploy.sh scale 4

# Update resource limits in docker-compose.production-v3.yml

```

### Update Deployment

```bash

# Pull latest changes

git pull origin main

# Deploy with backup

./scripts/deploy.sh deploy

# Rollback if needed

./scripts/deploy.sh rollback backup_file.tar.gz

```

### Cleanup Operations

```bash

# Clean Docker resources

./scripts/deploy.sh cleanup

# Deep cleanup (removes unused volumes)

./scripts/deploy.sh cleanup --deep

```

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Not Starting

```bash

# Check container logs

docker-compose -f docker-compose.production-v3.yml logs app

# Check resource usage

docker stats

# Verify environment variables

docker-compose -f docker-compose.production-v3.yml config

```

#### 2. Database Connection Issues

```bash

# Test database connectivity

docker exec bis_postgres_prod pg_isready -U bisuser

# Check database logs

docker-compose -f docker-compose.production-v3.yml logs postgres

```

#### 3. Performance Issues

```bash

# Monitor resource usage

docker stats --no-stream

# Check application metrics

curl http://localhost:8000/api/health | jq

# Review Grafana dashboards

```

### Recovery Procedures

#### 1. Application Recovery

```bash

# Restart specific service

docker-compose -f docker-compose.production-v3.yml restart app

# Restart all services

docker-compose -f docker-compose.production-v3.yml restart

```

#### 2. Database Recovery

```bash

# Restore from backup

gunzip -c backup_file.sql.gz | docker exec -i bis_postgres_prod psql -U bisuser -d business_intelligence

```

#### 3. Complete System Recovery

```bash

# Stop all services

docker-compose -f docker-compose.production-v3.yml down

# Restore volumes from backup

# ... (restore commands)

# Restart services

./scripts/deploy.sh deploy

```

## 📈 Performance Optimization

### 1. Database Optimization

- Regular VACUUM and ANALYZE
- Index optimization
- Connection pooling tuning

### 2. Application Optimization

- Worker process tuning
- Memory management
- Cache optimization

### 3. Infrastructure Optimization

- SSD storage for databases
- CDN for static assets
- Load balancer optimization

## 🛡️ Disaster Recovery

### 1. Backup Strategy

- Daily automated database backups
- Weekly full system backups
- Offsite backup storage

### 2. Recovery Time Objectives

- **RTO**: 1 hour for critical services
- **RPO**: 24 hours for data loss
- **MTTR**: 30 minutes for common issues

### 3. Disaster Recovery Plan

1. Assess the situation
2. Activate backup systems
3. Restore from latest backup
4. Verify system functionality
5. Resume normal operations

## 📞 Support & Contact

For production support and escalation:
- **Primary Contact**: ops@yourdomain.com
- **Emergency**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.yourdomain.com
- **Status Page**: https://status.yourdomain.com


---


*Last Updated: August 2, 2025*
*Version: 3.0.0*
*Business Intelligence Scraper - Production Deployment Guide*
