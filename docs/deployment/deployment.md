# Deployment Guide

## 🚀 Business Intelligence Scraper Platform Deployment

**Complete deployment guide for production, staging, and development environments**


---


## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Manual Deployment](#manual-deployment)
- [Database Setup](#database-setup)
- [Configuration](#configuration)
- [Monitoring Setup](#monitoring-setup)
- [Load Balancing](#load-balancing)
- [Security Hardening](#security-hardening)
- [Troubleshooting](#troubleshooting)


---


## ⚡ Quick Start

Get the platform running in under 5 minutes:

```bash

# Clone repository

git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Start with Docker Compose

docker-compose up -d

# Access the application

open http://localhost:3000

```

**Default Credentials:**
- Username: `admin@business-intel-scraper.com`
- Password: `admin123!` (Change immediately)


---


## 📋 Prerequisites

### System Requirements

#### Minimum Requirements

- **CPU**: 2 cores (x86_64)
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 1 Gbps connection

#### Recommended Requirements

- **CPU**: 4+ cores (x86_64)
- **RAM**: 8GB+
- **Storage**: 50GB+ NVMe SSD
- **Network**: 1 Gbps+ connection

#### Production Requirements

- **CPU**: 8+ cores (x86_64)
- **RAM**: 16GB+
- **Storage**: 100GB+ NVMe SSD
- **Network**: 10 Gbps connection
- **Backup**: Additional 200GB for backups

### Software Dependencies

#### Required Software

```bash

# Operating System

Ubuntu 20.04 LTS / 22.04 LTS (recommended)
CentOS 8+ / RHEL 8+
Debian 10+

# Container Runtime

Docker 20.10+
Docker Compose 2.0+

# Database

PostgreSQL 13+
Redis 6.0+

# Web Server (optional)

nginx 1.18+

```


---


## 🐳 Docker Deployment

### Complete Docker Compose Setup

A comprehensive Docker setup is available with production-ready configurations:

```bash

# Navigate to Docker configuration

cd business_intel_scraper/infra/docker

# Start complete stack

docker compose up --build -d

# View logs

docker compose logs -f

# Scale services

docker compose up -d --scale backend=3

# Stop services

docker compose down

```

### Production Docker Configuration

```yaml

# docker-compose.production.yml

version: '3.8'

services:
  frontend:
    image: business-intel-scraper/frontend:latest
    build:
      context: ./gui
      dockerfile: Dockerfile.production
    ports:
      - "3000:3000"

    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=https://api.yourdomain.com

    networks:
      - frontend-network

    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    image: business-intel-scraper/backend:latest
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"

    environment:
      - FLASK_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}

    depends_on:
      - database
      - redis

    networks:
      - backend-network
      - database-network

    restart: unless-stopped

  database:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=business_intel
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}

    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql

    networks:
      - database-network

    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

    networks:
      - backend-network

    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"

    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl

    depends_on:
      - frontend
      - backend

    networks:
      - frontend-network
      - backend-network

    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  frontend-network:
  backend-network:
  database-network:

```


---


## ☸️ Kubernetes Deployment

### Complete Kubernetes Setup

Deploy to Kubernetes with high availability and scalability:

#### 1. Apply Core Manifests

```bash

# Apply namespace and core resources

kubectl apply -f business_intel_scraper/infra/k8s/namespace.yaml
kubectl apply -f business_intel_scraper/infra/k8s/configmap.yaml
kubectl apply -f business_intel_scraper/infra/k8s/secrets.yaml

# Deploy data layer

kubectl apply -f business_intel_scraper/infra/k8s/redis-deployment.yaml
kubectl apply -f business_intel_scraper/infra/k8s/postgres-deployment.yaml

# Deploy application layer

kubectl apply -f business_intel_scraper/infra/k8s/api-deployment.yaml
kubectl apply -f business_intel_scraper/infra/k8s/worker-deployment.yaml
kubectl apply -f business_intel_scraper/infra/k8s/frontend-deployment.yaml

# Deploy services

kubectl apply -f business_intel_scraper/infra/k8s/api-service.yaml
kubectl apply -f business_intel_scraper/infra/k8s/frontend-service.yaml

# Deploy ingress

kubectl apply -f business_intel_scraper/infra/k8s/ingress.yaml

```

#### 2. Verify Deployment

```bash

# Check pod status

kubectl get pods -n business-intel-scraper

# Check services

kubectl get services -n business-intel-scraper

# View logs

kubectl logs -f deployment/api-deployment -n business-intel-scraper

# Check ingress

kubectl get ingress -n business-intel-scraper

```

### Enhanced Kubernetes Configuration

#### Production-Ready API Deployment

```yaml

# api-deployment-production.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  namespace: business-intel-scraper
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api

        image: business-intel-scraper/backend:latest
        ports:
        - containerPort: 8000

        env:
        - name: FLASK_ENV

          value: "production"
        - name: DATABASE_URL

          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL

          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

```

#### Horizontal Pod Autoscaler

```yaml

# hpa.yaml

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: business-intel-scraper
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource

    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource

    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80

```


---


## 🗄️ Database Setup

### PostgreSQL Configuration

#### Database Initialization

```sql

-- Connect as postgres user

sudo -u postgres psql

-- Create database and user

CREATE DATABASE business_intel;
CREATE USER scraper_user WITH PASSWORD 'secure_password';

-- Grant permissions

GRANT ALL PRIVILEGES ON DATABASE business_intel TO scraper_user;
ALTER USER scraper_user CREATEDB;

-- Enable required extensions

\c business_intel
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

```

#### Production PostgreSQL Configuration

```ini

# postgresql.conf

listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 512MB
effective_cache_size = 2GB
work_mem = 8MB
maintenance_work_mem = 128MB
wal_buffers = 32MB
checkpoint_completion_target = 0.9
max_wal_size = 2GB
min_wal_size = 160MB

```

### Redis Configuration

```conf

# redis.conf

bind 127.0.0.1 10.0.0.1
port 6379
requirepass your_redis_password
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

```


---


## ⚙️ Configuration

### Environment Variables

#### Production Configuration Template

```bash

# .env.production

NODE_ENV=production
FLASK_ENV=production
DEBUG=false

# Database

DATABASE_URL=postgresql://user:pass@localhost:5432/business_intel
DATABASE_POOL_SIZE=20

# Redis

REDIS_URL=redis://:password@localhost:6379/0

# Security

JWT_SECRET=your-256-bit-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1

# External Services

SMTP_SERVER=smtp.company.com
SMTP_PORT=587
SMTP_USERNAME=noreply@company.com
SMTP_PASSWORD=smtp-password

# Performance

WORKER_PROCESSES=4
MAX_CONNECTIONS=1000
API_RATE_LIMIT_PER_MINUTE=100

# Features

ENABLE_MFA=true
ENABLE_METRICS=true
ENABLE_API_DOCS=true

```


---


## 📊 Monitoring Setup

### Prometheus Configuration

```yaml

# prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'business-intel-backend'

    static_configs:
      - targets: ['backend:8000']

    metrics_path: /metrics

  - job_name: 'business-intel-frontend'

    static_configs:
      - targets: ['frontend:3000']

  - job_name: 'postgres'

    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'

    static_configs:
      - targets: ['redis-exporter:9121']

```

### Grafana Dashboards

Pre-configured dashboards are available for:
- Application performance metrics
- Database performance
- System resources
- User activity
- Security events


---


## ⚖️ Load Balancing

### nginx Configuration

```nginx

# nginx.conf

upstream backend_servers {
    least_conn;
    server backend-1:8000 max_fails=3 fail_timeout=30s;
    server backend-2:8000 max_fails=3 fail_timeout=30s;
    server backend-3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;

    # API proxy
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
    }
}

```


---


## 🔒 Security Hardening

### SSL/TLS Setup

```bash

# Install Certbot

sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate

sudo certbot --nginx -d yourdomain.com

# Auto-renewal

sudo crontab -e

# Add: 0 12 * * * /usr/bin/certbot renew --quiet

```

### Firewall Configuration

```bash

# UFW setup

sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

```


---


## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash

# Check PostgreSQL status

sudo systemctl status postgresql

# Test connection

psql -h localhost -U scraper_user -d business_intel -c "SELECT version();"

```

#### Redis Connection Issues

```bash

# Check Redis status

sudo systemctl status redis

# Test connection

redis-cli ping

```

#### Application Issues

```bash

# Check logs

docker-compose logs -f backend

# Health check

curl http://localhost:8000/health

```

### Performance Monitoring

```bash

# System resources

htop
iotop
nethogs

# Application metrics

curl http://localhost:8000/metrics

```


---


## 📞 Support

### Getting Help

- **Documentation**: Available at `/docs` endpoint
- **GitHub Issues**: [Report Issues](https://github.com/Trashytalk/scraper/issues)
- **Security Issues**: security@business-intel-scraper.com


---


**🚀 Your Business Intelligence Scraper Platform is ready for deployment!**
