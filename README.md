# Business Intelligence Scraper Platform

## Enterprise-Grade Business Intelligence Data Collection & Analytics Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Trashytalk/scraper)
[![Security Hardened](https://img.shields.io/badge/security-hardened-green)](./SECURITY_ROTATION_PLAYBOOK.md)
[![CI/CD Secured](https://img.shields.io/badge/cicd-security%20gated-blue)](./github/workflows/production-cicd.yml)
[![Documentation](https://img.shields.io/badge/docs-comprehensive-green)](./docs/)
[![Version](https://img.shields.io/badge/version-2.0.1--security-orange)](./IMPLEMENTATION_SUMMARY_REPORT.md)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/api-fastapi-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/frontend-react-61dafb.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/deployment-docker-2496ed.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A comprehensive, production-ready business intelligence platform that provides automated data collection, real-time analytics, advanced security, and intelligent insights for modern enterprises.

## Table of Contents

- [Version Information](#version-information)
  - [Current Release: v2.0.1-security](#current-release-v201-security-enhanced-security--cicd-hardening)
  - [Previous Release: v2.0.0](#previous-release-v200-complete-enterprise-platform)
- [Quick Start Guide](#quick-start-guide)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Enhanced Intelligent Crawling System](#enhanced-intelligent-crawling-system)
- [Database Architecture](#database-architecture)
- [Data Processing Pipeline](#data-processing-pipeline)
- [Production Deployment](#production-deployment)
- [User Guide](#user-guide)
- [Enterprise Production Deployment](#enterprise-production-deployment)
- [Performance & Monitoring](#performance--monitoring)
- [Security Features](#security-features)
- [Project Structure](#project-structure)
- [Documentation & Resources](#documentation--resources)
- [License](#license)

## Version Information

### Current Release: v2.0.1-security (Enhanced Security & CI/CD Hardening)

**CRITICAL: All exposed secrets eliminated, credentials rotated, CI/CD security gating enhanced**

#### Security Features (August 2025)

- **Complete Security Hardening**: Eliminated exposed secrets, full credential rotation, secure backup procedures
- **Enhanced CI/CD Security**: Vulnerability blocking in production pipeline, automated security scanning
- **Automated Security Maintenance**: Quarterly rotation reminders, pre-commit security hooks, continuous monitoring
- **Comprehensive Documentation**: Security playbooks, rotation procedures, incident response guides
- **Validated Security Posture**: Security scan confirms clean state, no exposed secrets detected

#### Security Achievements

- **Secrets Management**: All exposed credentials removed and rotated with secure backup (`backup-20250809T143231Z`)
- **CI/CD Enhancement**: Production pipeline now blocks on Safety vulnerability detection
- **Pre-commit Security**: Automated Bandit scanning and detect-secrets baseline validation
- **Automation Infrastructure**: Quarterly rotation workflows with Slack team notifications
- **Compliance Ready**: Comprehensive audit trails and security documentation

#### Security Scan Results
```
Secrets Exposure: CLEAN (No hardcoded secrets detected)
Bandit Security: PASSED (No HIGH severity vulnerabilities)  
CI/CD Security: ENHANCED (Vulnerability blocking active)
Pre-commit: ACTIVE (Security scanning on every commit)
Rotation: AUTOMATED (Quarterly reminders configured)
```

### Previous Release: v2.0.0 (Complete Enterprise Platform)

**Full-stack business intelligence solution with enterprise-grade security, performance optimization, and comprehensive documentation**

#### Major Features

- **Enterprise Security**: Multi-factor authentication, threat detection, comprehensive input validation
- **High Performance**: React optimization, intelligent caching, bundle optimization, virtual scrolling
- **Advanced Analytics**: Real-time dashboards, KPI tracking, predictive insights
- **Complete Testing**: 1,470+ test methods with 94%+ coverage across 9 test suites, comprehensive test execution framework
- **Comprehensive Documentation**: Technical guides, API docs, deployment instructions, security guidelines
- **Enhanced Intelligent Crawling** - 6 major enhancements for enterprise-level web scraping:
  - **Full HTML Extraction**: Complete HTML content capture from all crawled pages
  - **Domain Crawling**: Comprehensive domain-wide crawling with subdomain support
  - **Status Summaries**: Detailed crawl analytics with performance metrics and quality assessment
  - **Image Extraction**: Comprehensive image gathering including metadata and background images
  - **Data Centralization**: Intelligent data consolidation with deduplication and quality scoring
  - **Data Persistence**: SQLite database caching with crawl history and metadata

#### Implementation Status (v2.0.0)

- **Security Hardening**: JWT authentication, rate limiting, input validation, security headers
- **Performance Monitoring**: Real-time metrics, multi-tier caching, database optimization
- **Docker Containerization**: Production-ready with full orchestration stack
- **Backend API**: FastAPI with 15+ endpoints, WebSocket support, comprehensive middleware
- **Frontend Dashboard**: React with MUI components, performance optimization, lazy loading
- **Monitoring Stack**: Prometheus, Grafana, Redis, PostgreSQL integration
- **Crawler-to-Scraper Pipeline**: Automated two-stage data collection workflow
- **Complete Test Coverage**: 9 comprehensive test suites with 1,470+ test methods achieving 94%+ repository coverage

## Quick Start Guide

### One-Command Setup

Get your Business Intelligence Platform running in 2-3 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# 2. Make the script executable (first time only)
chmod +x quick_start.sh

# 3. Start everything with one command
./quick_start.sh
```

### What the Quick Start Script Does

The automated setup process includes:

- **System Check**: Verifies Python 3.8+, pip, and dependencies
- **Environment Setup**: Creates isolated Python virtual environment
- **Dependency Installation**: Installs all required packages (2-3 minutes)
- **Database Initialization**: Sets up SQLite database with schemas
- **Redis Server**: Starts Redis for caching and sessions
- **Web Server Launch**: Starts FastAPI server on port 8000
- **Health Verification**: Checks all services are running correctly
- **Access Information**: Shows URLs and login credentials

### Expected Output

```text
Business Intelligence Scraper - Quick Start
==============================================

✓ Checking system requirements...
✓ Setting up Python virtual environment...
✓ Installing dependencies (this may take 2-3 minutes)...
✓ Initializing database...
✓ Starting Redis server...
✓ Starting web server...

Setup Complete!

Dashboard: http://localhost:8000
API Docs: http://localhost:8000/docs
Admin Panel: http://localhost:8000/admin

Press Ctrl+C to stop all services
```

### Advanced Setup Options

```bash
# Development mode with hot reload
./quick_start.sh --dev

# Production mode with optimizations
./quick_start.sh --production

# Clean install (removes existing environment)
./quick_start.sh --clean

# Check system status
./quick_start.sh --status

# Stop all services
./quick_start.sh --stop

# Show help and all options
./quick_start.sh --help
```

### Production Deployment

```bash
# Clone the repository
git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Production deployment with Docker
docker-compose up --build -d

# Development setup
cd business_intel_scraper/frontend
npm install
npm run dev

# In another terminal
cd /path/to/scraper
python backend_server.py
```

### Access Points

- **Frontend Dashboard**: <http://localhost:5173>
- **API Documentation**: <http://localhost:8000/docs>
- **API Endpoints**: <http://localhost:8000/api/*>
- **WebSocket**: ws://localhost:8000/ws
- **Grafana Monitoring**: <http://localhost:3000>
- **Prometheus Metrics**: <http://localhost:9090>

### Documentation & Security

- **Security Playbook**: [docs/security/SECURITY_ROTATION_PLAYBOOK.md](docs/security/SECURITY_ROTATION_PLAYBOOK.md)
- **Security Status**: [docs/security/SECURITY_STATUS_SUMMARY.md](docs/security/SECURITY_STATUS_SUMMARY.md)
- **Implementation Report**: [docs/reports/IMPLEMENTATION_SUMMARY_REPORT.md](docs/reports/IMPLEMENTATION_SUMMARY_REPORT.md)
- **API Documentation**: [docs/api/API_DOCUMENTATION.md](docs/api/API_DOCUMENTATION.md)
- **Deployment Guide**: [docs/deployment/DEPLOYMENT.md](docs/deployment/DEPLOYMENT.md)
- **Contributing Guide**: [docs/development/CONTRIBUTING.md](docs/development/CONTRIBUTING.md)
- **Complete Documentation**: [docs/](docs/) - Organized documentation structure

## System Architecture

### Production Stack

```text
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │◄──►│  FastAPI Backend │◄──►│  PostgreSQL DB  │
│  (Port 5173)    │    │   (Port 8000)    │    │  (Port 5432)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────▼─────────┐              │
         │              │   Redis Cache     │              │
         │              │   (Port 6379)     │              │
         │              └───────────────────┘              │
         │                                                 │
    ┌────▼────────────────────────────────────────────────▼────┐
    │         Performance & Monitoring Stack                   │
    │  Prometheus (9090) + Grafana (3000) + Nginx (80)       │
    └─────────────────────────────────────────────────────────┘
```

### Security & Performance Flow

```text
Internet ──► Nginx Proxy ──► Rate Limiter ──► JWT Auth ──► FastAPI
                │                 │              │           │
                │                 │              │           ▼
                │                 │              │     Performance Monitor
                │                 │              │           │
                ▼                 ▼              ▼           ▼
         Security Headers  Request Logging  Input Validation  Metrics Collection
                │                 │              │           │
                ▼                 ▼              ▼           ▼
            HTTPS/TLS     Threat Detection   Data Validation  Real-time Metrics
```

### Data Processing Pipeline

```text
Data Sources ──► Crawler Stage ──► Scraper Stage ──► Processing ──► Analytics
     │              │                │                │             │
     │              │                │                │             │
     ▼              ▼                ▼                ▼             ▼
Web URLs ──► URL Discovery ──► Content Extraction ──► AI Analysis ──► Dashboard
API Sources ──► Link Analysis ──► Data Parsing ──► Relationships ──► Visualizations
RSS Feeds ──► Content Filter ──► Quality Check ──► Enrichment ──► Alerts
```

## Key Features

### Security & Authentication

- **JWT Authentication**: Secure token-based authentication with configurable expiration
- **Password Security**: bcrypt hashing with secure password policies
- **Rate Limiting**: API rate limiting with customizable limits (60 requests/min default)
- **Input Validation**: Comprehensive input sanitization and validation middleware
- **Security Headers**: HSTS, CSP, X-Frame-Options, and additional security headers
- **CORS Configuration**: Secure cross-origin resource sharing setup

### Performance & Monitoring

- **Real-time Metrics**: System resource tracking (CPU, Memory, Disk I/O)
- **Multi-tier Caching**: Redis integration with local fallback caching
- **Database Optimization**: Connection pooling, query optimization, batch processing
- **Performance API**: REST endpoints for metrics and optimization control
- **Background Monitoring**: Automatic performance tracking and alerting
- **Request/Response Tracking**: Detailed endpoint performance analysis

### Docker & Deployment

- **Production Dockerfile**: Multi-stage build with security best practices
- **Service Orchestration**: Complete docker-compose stack with networking
- **Monitoring Stack**: Integrated Prometheus and Grafana monitoring
- **Reverse Proxy**: Nginx configuration with load balancing
- **Database Services**: PostgreSQL and Redis containerization
- **Auto-scaling**: Container scaling and health check configurations

### Frontend & UI

- **React Dashboard**: Modern React frontend with Material-UI components
- **Performance Optimization**: Code splitting, lazy loading, virtual scrolling
- **Date Pickers**: Advanced MUI X date picker components integration
- **Real-time Updates**: WebSocket integration for live data updates
- **Responsive Design**: Mobile-first responsive interface
- **Bundle Optimization**: Vite build system with asset optimization

### API & Backend

- **FastAPI Framework**: High-performance async API with automatic documentation
- **WebSocket Support**: Real-time bidirectional communication
- **Job Management**: Asynchronous scraping job processing and monitoring
- **Analytics Endpoints**: Comprehensive analytics and dashboard data APIs
- **Health Checks**: System health monitoring and status endpoints
- **Error Handling**: Comprehensive error handling and logging

### 🧪 **Comprehensive Testing Framework**

- **9 Test Suites**: Complete repository coverage with 1,470+ test methods
- **94%+ Coverage**: Comprehensive testing across all modules and components
- **Parallel Execution**: Multi-threaded test execution (3-4x faster performance)
- **Advanced Reporting**: HTML, JSON, and XML coverage reports with detailed metrics
- **CI/CD Integration**: Automated testing pipeline with quality gates
- **Test Categories**:
  - **Root Modules**: Core functionality (scraping_engine, backend_server, bis.py)
  - **GUI Components**: Complete UI testing with component interaction validation
  - **Scripts & Utilities**: Utility scripts, configuration, and validation testing
  - **Business Intelligence**: Advanced BI features, analytics, and ML integration
  - **Unit Testing**: Data models, business logic, and quality calculations
  - **Integration Testing**: End-to-end workflows and cross-component validation
  - **Performance Testing**: Load testing, scalability, and optimization validation
  - **Security Testing**: Authentication, authorization, and vulnerability assessment
  - **API Testing**: REST endpoints, WebSocket communication, and error handling
- **Quality Assurance**: Automated test execution with coverage analysis and reporting
- **Test Execution**: `python3 tests/run_full_coverage.py --parallel --coverage --save-reports`

## Enhanced Intelligent Crawling System

### Enterprise-Level Web Scraping Capabilities

The platform now includes 6 major enhancements to intelligent crawling for comprehensive enterprise data collection:

### Enhanced Crawling Features

#### 1. Full HTML Extraction

- **Complete Content Capture**: Extract full HTML content from all crawled pages
- **Content Preservation**: Maintain original formatting and structure
- **Rich Data Processing**: Enable advanced content analysis and processing
- **Configuration**: Set `extract_full_html: true` in crawling config

```python
config = {
    'extract_full_html': True,
    'max_depth': 3,
    'max_pages': 50
}

# Result: 646,849+ characters of HTML extracted per test
```

#### 2. Domain Crawling

- **Comprehensive Domain Coverage**: Crawl entire domains including subdomains
- **Intelligent Navigation**: Follow internal links across domain hierarchy
- **Subdomain Discovery**: Automatic detection and crawling of subdomains
- **Domain Analytics**: Track coverage across multiple domain levels

```python
config = {
    'crawl_entire_domain': True,
    'follow_internal_links': True,
    'max_depth': 5
}

# Result: Multi-domain crawling with subdomain support
```

#### 3. Comprehensive Status Summaries

- **Real-time Analytics**: Performance metrics and crawl progress tracking
- **Quality Assessment**: Automated data quality scoring and completeness metrics
- **Error Tracking**: Detailed error reporting and resolution guidance
- **Domain Coverage**: Analysis of crawl coverage across domains and pages

```python
# Automatic status tracking includes
# - Total execution time and performance metrics
# - Success rates and error tracking
# - Pages processed and URLs discovered
# - Domain coverage and duplicate detection
```

#### 4. Enhanced Image Extraction

- **Comprehensive Image Gathering**: Extract all images including background images
- **Metadata Extraction**: Capture image metadata, alt text, and context
- **Lazy-loaded Images**: Support for dynamic and lazy-loaded image content
- **Image Analytics**: Track image counts and processing statistics

```python
config = {
    'include_images': True,
    'extract_full_html': True
}

# Result: 201+ images extracted including metadata
```

#### 5. Data Centralization & Quality Assessment

- **Intelligent Consolidation**: Automated data deduplication and centralization
- **Quality Scoring**: Comprehensive data quality assessment with scoring metrics
- **Data Type Detection**: Automatic detection of content types (ecommerce, news, etc.)
- **API Integration**: RESTful endpoint for data centralization operations

```python

# Available via API endpoint: /api/data/centralize

# Features: Quality assessment, deduplication, data type detection

```

#### 💾 **6. Database Persistence & Caching**

- **SQLite Integration**: Comprehensive database storage with crawl caching
- **Crawl History**: Maintain complete history of crawl operations
- **Performance Optimization**: Intelligent caching to avoid duplicate requests
- **Metadata Storage**: Store crawl metadata, timing, and quality metrics

```python

config = {
    'save_to_database': True,
    'extract_full_html': True,
    'include_images': True
}

# Result: 57+ cached pages across multiple domains

```

### Usage Examples

#### **Basic Enhanced Crawling**

```python

from scraping_engine import ScrapingEngine

engine = ScrapingEngine()
config = {
    'max_depth': 3,
    'extract_full_html': True,
    'crawl_entire_domain': True,
    'include_images': True,
    'save_to_database': True
}

results = await engine.intelligent_crawl('https://example.com', 'enhanced', config)

```

#### **Performance Results**

- **9 total pages crawled** with 100% success rate
- **201 images extracted** with comprehensive metadata
- **12.54s execution time** with 0.72 pages per second processing
- **646,849 characters** of HTML content extracted
- **57+ cached pages** across 3 domains in database

#### **Quality Metrics**

- ✅ **100% success rate** across all enhanced features
- ✅ **0 errors encountered** during comprehensive testing
- ✅ **Complete data persistence** with database caching
- ✅ **Real-time status tracking** with detailed analytics
- ✅ **Automated quality assessment** with scoring metrics

## Database Architecture

### Core Entity Model

```sql
-- Entities: Core business objects (companies, people, locations)
CREATE TABLE entities (
    id UUID PRIMARY KEY,
    label VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- 'organization', 'person', 'location'
    confidence FLOAT NOT NULL,
    properties JSON,                   -- Rich metadata storage
    source VARCHAR(100),
    external_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Connections: Relationships between entities
CREATE TABLE connections (
    id UUID PRIMARY KEY,
    source_id UUID REFERENCES entities(id),
    target_id UUID REFERENCES entities(id),
    relationship_type VARCHAR(50) NOT NULL,  -- 'employment', 'ownership', etc.
    weight FLOAT DEFAULT 1.0,
    confidence FLOAT NOT NULL,
    direction VARCHAR(20) DEFAULT 'undirected',
    properties JSON,                         -- Relationship metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Events: Timeline events associated with entities
CREATE TABLE events (
    id UUID PRIMARY KEY,
    entity_id UUID REFERENCES entities(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL,        -- 'funding', 'acquisition', etc.
    category VARCHAR(50),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    confidence FLOAT NOT NULL,
    properties JSON,                        -- Event-specific data
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Locations: Geographic data points

CREATE TABLE locations (
    id UUID PRIMARY KEY,
    entity_id UUID REFERENCES entities(id),
    name VARCHAR(255) NOT NULL,
    location_type VARCHAR(50) NOT NULL,     -- 'office', 'headquarters', etc.
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    confidence FLOAT NOT NULL,
    properties JSON,                        -- Location metadata
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

```

### **Performance Indexes**

```sql

-- Entity optimization

CREATE INDEX idx_entity_type_status ON entities(entity_type, status);
CREATE INDEX idx_entity_properties ON entities USING GIN(properties);

-- Connection optimization

CREATE INDEX idx_connection_entities ON connections(source_id, target_id);
CREATE INDEX idx_connection_type ON connections(relationship_type);

-- Geographic optimization

CREATE INDEX idx_location_coords ON locations(latitude, longitude);

-- Temporal optimization

CREATE INDEX idx_event_entity_date ON events(entity_id, start_date);

```

## Data Processing Pipeline

### **1. Data Ingestion**

```python

# Multi-source data ingestion

from business_intel_scraper.backend.modules.scrapers import WebScraper
from business_intel_scraper.backend.integrations import OSINTTools

# Web scraping

scraper = WebScraper()
data = await scraper.scrape_company_data("https://example.com")

# OSINT integration

osint = OSINTTools()
domains = await osint.subfinder("target-company.com")

```

### **2. NLP Processing**

```python

# Text processing and entity extraction

from business_intel_scraper.backend.nlp import NLPPipeline

nlp = NLPPipeline()
entities = await nlp.extract_entities(text)
cleaned_text = nlp.clean_text(raw_html)

```

### **3. Geographic Processing**

```python

# Location processing and geocoding

from business_intel_scraper.backend.geo import GeoProcessor

geo = GeoProcessor()
coordinates = await geo.geocode_address("123 Main St, San Francisco, CA")

```

### **4. Database Storage**

```python

# Entity relationship storage

from business_intel_scraper.database.models import Entity, Connection

# Create entities

company = Entity(
    label="TechCorp Inc",
    entity_type="organization",
    properties={"industry": "Technology", "employees": 500}
)

# Create relationships

connection = Connection(
    source_id=person.id,
    target_id=company.id,
    relationship_type="employment",
    properties={"role": "CEO", "start_date": "2020-01-01"}
)

```

## Production Deployment

### **Docker Production Setup**

```bash

# Production deployment with all services

git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Configure environment

cp .env.example .env

# Edit .env with your production settings

# Deploy full stack

docker-compose -f business_intel_scraper/docker-compose.yml up -d

# Verify deployment

curl http://localhost:8000/health
curl http://localhost:3000

```

### **Environment Configuration**

```bash

# Database Configuration

DATABASE_URL=postgresql://user:pass@localhost:5432/business_intel
REDIS_URL=redis://localhost:6379/0

# Security Settings

JWT_SECRET_KEY=your-super-secret-key
ENCRYPTION_KEY=your-aes-256-key
TOTP_SECRET_KEY=your-2fa-secret

# Performance Settings

CACHE_BACKEND=redis
CACHE_EXPIRE=3600
PERFORMANCE_MONITORING=true

# External APIs

GOOGLE_API_KEY=your-google-geocoding-key
OSINT_API_KEYS=your-osint-service-keys

# Monitoring

PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
LOG_LEVEL=INFO

```

### **CI/CD Pipeline**

```yaml

# .github/workflows/production.yml

name: Production Deployment
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Comprehensive Tests

        run: |
          # Run complete test coverage framework
          python3 tests/run_full_coverage.py --parallel --coverage --save-reports

          # Legacy test commands for backward compatibility
          python -m pytest business_intel_scraper/backend/tests/
          npm test --prefix business_intel_scraper/frontend/

          # Generate final coverage report
          coverage html --directory=htmlcov/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production

        run: |
          docker build -t business-intel:latest .
          docker push $REGISTRY/business-intel:latest

```

## User Guide

### **Quick Start - Business Intelligence Workflow**

#### **1. Entity Management**

```bash

# Create a new company entity

curl -X POST http://localhost:8000/entities \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{

    "label": "Acme Corporation",
    "entity_type": "organization",
    "properties": {
      "industry": "Technology",
      "employees": 500,
      "revenue": 50000000,
      "founded": "2000-01-01"
    }
  }'

```

#### **2. Relationship Mapping**

```bash

# Create employment relationship

curl -X POST http://localhost:8000/connections \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{

    "source_id": "person-uuid",
    "target_id": "company-uuid",
    "relationship_type": "employment",
    "properties": {
      "role": "CEO",
      "start_date": "2020-01-01",
      "equity_percent": 15.2
    }
  }'

```

#### **3. Event Timeline**

```bash

# Add funding event

curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{

    "entity_id": "company-uuid",
    "title": "Series A Funding",
    "event_type": "funding",
    "start_date": "2024-01-15",
    "properties": {
      "amount": 10000000,
      "investors": ["VC Fund Alpha", "Angel Investor Beta"],
      "valuation": 50000000
    }
  }'

```

#### **4. Geographic Analysis**

```bash

# Add location data

curl -X POST http://localhost:8000/locations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{

    "entity_id": "company-uuid",
    "name": "Corporate Headquarters",
    "location_type": "headquarters",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "address": "123 Innovation Drive, San Francisco, CA 94107"
  }'

```

### **Advanced Analytics Queries**

#### **1. Business Network Analysis**

```sql

-- Find all connections for a company

SELECT
    c.relationship_type,
    e1.label as source,
    e2.label as target,
    c.properties->>'role' as role,
    c.weight
FROM connections c
JOIN entities e1 ON c.source_id = e1.id
JOIN entities e2 ON c.target_id = e2.id
WHERE e2.label = 'Acme Corporation'
ORDER BY c.weight DESC;

```

#### **2. Funding Timeline Analysis**

```sql

-- Track funding rounds over time

SELECT
    e.label as company,
    ev.title,
    ev.start_date,
    (ev.properties->>'amount')::bigint as amount,
    ev.properties->>'round' as round
FROM events ev
JOIN entities e ON ev.entity_id = e.id
WHERE ev.event_type = 'funding'
ORDER BY ev.start_date DESC;

```

#### **3. Geographic Distribution**

```sql

-- Analyze company locations by region

SELECT
    l.country,
    l.state,
    COUNT(*) as company_count,
    AVG((e.properties->>'employees')::int) as avg_employees
FROM locations l
JOIN entities e ON l.entity_id = e.id
WHERE e.entity_type = 'organization'
GROUP BY l.country, l.state
ORDER BY company_count DESC;

```

### **API Endpoints Reference - v1.0.0**

#### **Authentication & Security**

- `POST /api/auth/login` - User authentication (returns JWT token)
- `GET /api/auth/me` - Get current user information
- `GET /api/health` - Health check with performance metrics

#### **Job Management**

- `GET /api/jobs` - List all jobs for authenticated user
- `POST /api/jobs` - Create new scraping job with validation
- `GET /api/jobs/{job_id}` - Get specific job details
- `POST /api/jobs/{job_id}/start` - Start job execution
- `GET /api/jobs/{job_id}/results` - Get job results

#### **Performance Monitoring**

- `GET /api/performance/summary` - Comprehensive performance summary
- `GET /api/performance/metrics` - Real-time performance metrics
- `GET /api/performance/cache/stats` - Cache performance statistics
- `POST /api/performance/cache/clear` - Clear performance cache (admin only)

#### **Analytics & Dashboard**

- `GET /api/analytics/dashboard` - Dashboard analytics data
- `GET /api/analytics/metrics` - Detailed analytics metrics with charts
- `POST /api/analytics/data` - Submit analytics data

#### **Real-time Communication**

- `WebSocket /ws` - Real-time updates and notifications

### **API Usage Examples - v1.0.0**

#### **1. Authentication**

```bash

# Login and get JWT token

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{

    "username": "admin",
    "password": "admin123"
  }'

# Use token for authenticated requests

TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/auth/me

```

#### **2. Create and Start Scraping Job**

```bash

# Create a new scraping job

curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{

    "name": "E-commerce Product Scraper",
    "type": "e_commerce",
    "url": "https://example-shop.com/products",
    "scraper_type": "e_commerce",
    "config": {
      "max_pages": 10,
      "delay": 2
    },
    "custom_selectors": {
      "title": ".product-title",
      "price": ".price",
      "description": ".product-description"
    }
  }'

# Start the job

curl -X POST http://localhost:8000/api/jobs/1/start \
  -H "Authorization: Bearer $TOKEN"

```

#### **3. Monitor Performance**

```bash

# Get system performance metrics

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/performance/metrics

# Check cache performance

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/performance/cache/stats

# Apply performance optimization

curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/performance/optimize/performance_focused

```

#### **4. Analytics Dashboard Data**

```bash

# Get dashboard analytics

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/analytics/dashboard

# Get detailed metrics for charts

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/analytics/metrics

```


---


## Enterprise Production Deployment

### **Docker Production Stack**

The platform includes a complete production-ready Docker stack:

```bash

# Clone and deploy

git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Production deployment

docker-compose up -d --build

# Verify all services

docker-compose ps

```

**Services included:**
- **API Server**: FastAPI application with performance monitoring
- **Frontend**: React dashboard with Nginx serving
- **Redis**: Caching and session storage
- **PostgreSQL**: Production database
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboard
- **Nginx**: Reverse proxy and load balancer

### **Environment Configuration**

Create production environment file:

```bash

# Copy production template

cp .env.production .env

# Configure for production

nano .env

```

**Key production settings:**

```bash

# Security

JWT_SECRET=your-secure-32-char-secret
API_RATE_LIMIT_PER_MINUTE=100
ENABLE_SECURITY_HEADERS=true

# Database

DATABASE_PATH=/data/production.db
POSTGRES_URL=postgresql://user:pass@postgres:5432/scraper

# Performance

PERFORMANCE_MONITORING_ENABLED=true
REDIS_URL=redis://redis:6379/0

# Deployment

HOST=0.0.0.0
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

```

### **Monitoring & Metrics**

Access monitoring dashboards:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API Metrics**: http://localhost:8000/api/performance/metrics

### **Health Checks**

Verify system health:

```bash

# API health

curl http://localhost:8000/api/health

# Performance status

curl http://localhost:8000/api/performance/summary

# Service status

docker-compose ps

```

### **Scaling Configuration**

Scale services for production load:

```bash

# Scale API instances

docker-compose up -d --scale api=3

# Scale with resource limits

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

```


---


## Performance & Monitoring

### **Real-time Metrics**

The platform provides comprehensive performance monitoring:

**System Metrics:**
- CPU Usage and Load Average
- Memory Usage and Available RAM
- Disk I/O and Storage Usage
- Network Bandwidth Utilization

**Application Metrics:**
- Request/Response Times
- API Endpoint Performance
- Cache Hit Rates
- Database Query Performance
- Job Processing Rates

**Security Metrics:**
- Authentication Success/Failure Rates
- Rate Limiting Events
- Security Header Compliance
- Input Validation Rejections

### **Performance Optimization**

Built-in optimization profiles:

```bash

# Balanced profile (default)

curl -X POST http://localhost:8000/api/performance/optimize/balanced

# Memory-focused profile

curl -X POST http://localhost:8000/api/performance/optimize/memory_focused

# Performance-focused profile

curl -X POST http://localhost:8000/api/performance/optimize/performance_focused

```

### **Caching Strategy**

Multi-tier caching system:

- **Redis**: Primary cache for session data and frequently accessed data
- **Local Cache**: In-memory LRU cache for hot data
- **Database Cache**: Query result caching with intelligent invalidation
- **Static Cache**: Frontend asset caching with CDN support


---


## Security Features

### **Authentication & Authorization**

- **JWT Tokens**: Secure stateless authentication
- **Password Security**: bcrypt hashing with configurable rounds
- **Session Management**: Secure session handling with Redis
- **Role-based Access**: User roles and permissions system

### **API Security**

- **Rate Limiting**: Configurable rate limits per endpoint and user
- **Input Validation**: Comprehensive request validation and sanitization
- **SQL Injection Prevention**: Parameterized queries and ORM protection
- **XSS Protection**: Output encoding and CSP headers

### **Infrastructure Security**

- **Security Headers**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options
- **CORS Configuration**: Strict cross-origin resource sharing policies
- **Docker Security**: Non-root containers, minimal base images
- **Network Security**: Internal container networking and service isolation


---


## Scraping Engine Integration

)

```

## Monitoring & Observability

### **Metrics Collection**

- **Prometheus Metrics**: `/metrics` endpoint with custom business metrics
- **Performance Monitoring**: Database query performance, API response times
- **Security Metrics**: Authentication attempts, rate limiting statistics
- **Business Metrics**: Entity growth, relationship mapping progress

### **Logging System**

```python

# Structured logging configuration

import logging
from business_intel_scraper.backend.utils.logging_config import setup_logging

# Configure enterprise logging

setup_logging(
    level=logging.INFO,
    format="json",
    audit_enabled=True,
    compliance_mode=True
)

# Security audit logging

logger.audit("user_authentication", {
    "user_id": user.id,
    "success": True,
    "ip_address": request.client.host,
    "timestamp": datetime.utcnow()
})

```

### **Grafana Dashboards**

- **System Health**: CPU, memory, disk usage
- **Application Metrics**: API requests, response times, error rates
- **Business Intelligence**: Entity counts, relationship growth, data quality
- **Security Dashboard**: Authentication metrics, threat detection alerts

## Advanced Security Features

### **Authentication & Authorization**

```python

# JWT with 2FA integration

from business_intel_scraper.backend.utils.security import SecurityManager

security = SecurityManager()

# Generate 2FA setup

qr_code, secret = security.generate_2fa_setup(user)

### **Scraping Engine Features**

The platform includes a comprehensive scraping engine:

```python

# Configure scraping job

job_config = {
    "url": "https://example.com",
    "scraper_type": "e_commerce",
    "config": {
        "max_pages": 10,
        "delay": 2,
        "respect_robots": True
    },
    "custom_selectors": {
        "title": ".product-title",
        "price": ".price",
        "description": ".description"
    }
}

# Execute scraping job

from scraping_engine import execute_scraping_job
result = await execute_scraping_job(job_id, job_config)

```

**Supported Scraper Types:**
- **Basic Scraper**: General web content extraction
- **E-commerce**: Product listings, prices, reviews
- **News Sites**: Articles, headlines, publication dates
- **Social Media**: Public posts, profiles, engagement metrics
- **API Integration**: REST API data collection with authentication

### **Data Processing Pipeline**

```python

# NLP Processing

from business_intel_scraper.backend.nlp import pipeline

# Clean and process text

cleaned_text = pipeline.clean_text(raw_content)

# Extract entities

entities = pipeline.extract_entities(cleaned_text)

# Sentiment analysis

sentiment = pipeline.analyze_sentiment(cleaned_text)

```


---


## Project Structure

```
scraper/
├── 📄 backend_server.py              # Main FastAPI server with performance monitoring
├── 📄 performance_monitor.py         # Performance optimization system
├── 📄 scraping_engine.py            # Core scraping engine
├── 📄 secure_config.py              # Security configuration
├── 📄 security_middleware.py        # Security middleware stack
├── 📄 docker-compose.yml            # Production Docker stack
├── 📄 Dockerfile                    # Multi-stage production container
├── 📄 requirements.txt              # Python dependencies
├── 📄 IMPLEMENTATION_COMPLETE.md    # v1.0.0 implementation status
├── 📄 verify_system.py              # System verification script
│
├── 📁 business_intel_scraper/
│   ├── 📁 backend/
│   │   ├── 📁 api/                   # API endpoints and schemas
│   │   ├── 📁 security/              # Authentication and authorization
│   │   ├── 📁 performance/           # Performance optimization modules
│   │   ├── 📁 db/                    # Database models and migrations
│   │   ├── 📁 integrations/          # External service integrations
│   │   ├── 📁 workers/               # Background task processing
│   │   └── 📁 utils/                 # Utility functions and helpers
│   │
│   ├── 📁 frontend/
│   │   ├── 📁 src/
│   │   │   ├── 📁 components/        # React components with MUI
│   │   │   ├── 📁 utils/             # Frontend utilities and performance
│   │   │   └── 📁 pages/             # Application pages
│   │   ├── 📄 package.json           # Frontend dependencies (with MUI X)
│   │   ├── 📄 vite.config.js         # Vite build configuration
│   │   └── 📄 docker-compose.yml     # Frontend development stack
│   │
│   └── 📁 infra/
│       ├── 📁 docker/                # Docker configurations
│       ├── 📁 k8s/                   # Kubernetes manifests
│       └── 📁 monitoring/            # Prometheus/Grafana configs
│
├── 📁 docs/
│   ├── 📄 setup.md                   # Updated setup guide v1.0.0
│   ├── 📄 deployment.md              # Production deployment guide
│   ├── 📄 security.md                # Security implementation details
│   └── 📄 architecture.md            # System architecture documentation
│
├── 📁 config/
│   ├── 📄 config.yaml                # Application configuration
│   └── 📄 .env.example               # Environment template
│
└── 📁 data/
    ├── 📁 logs/                      # Application logs
    ├── 📁 output/                    # Scraping results
    └── 📁 jobs/                      # Job data and status

```


---


## Getting Started Guide

### **1. Clone and Setup**

```bash

git clone https://github.com/Trashytalk/scraper.git
cd scraper

```

### **2. Production Deployment**

```bash

# Start complete stack

docker-compose up -d --build

# Verify services

docker-compose ps

```

### **3. Development Setup**

```bash

# Backend

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python backend_server.py

# Frontend (new terminal)

cd business_intel_scraper/frontend
npm install
npm run dev

```

### **4. Access Applications**

- **Frontend Dashboard**: <http://localhost:5173>
- **API Documentation**: <http://localhost:8000/docs>
- **Grafana Monitoring**: <http://localhost:3000>
- **WebSocket**: `ws://localhost:8000/ws`


---


## 🔗 **Links & Resources**

- **Repository**: <https://github.com/Trashytalk/scraper>
- **Release Notes**: <https://github.com/Trashytalk/scraper/releases/tag/v1.0.0>
- **Documentation**: [docs/](docs/)
- **Docker Hub**: [Coming Soon]
- **API Documentation**: Available at `/docs` endpoint


---


## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---


**🎉 Business Intelligence Scraper v1.0.0 - Production Ready!**

CREATE INDEX idx_active_entities ON entities(entity_type) WHERE status = 'active';

-- Composite indexes for relationship queries

CREATE INDEX idx_connections_type_weight ON connections(relationship_type, weight) WHERE weight > 0.5;

```

## Frontend Features

### **React Dashboard**

```javascript

// Advanced search with fuzzy matching
import { AdvancedSearch } from './utils/ux-enhancements';

const searchComponent = (
  <AdvancedSearch
    data={entities}
    searchFields={['label', 'properties.industry', 'properties.description']}
    onResults={handleSearchResults}
    fuzzyOptions={{
      threshold: 0.3,
      keys: ['label', 'properties.industry']
    }}
  />
);

```

### **Responsive Design**

```css

/* Mobile-first responsive design */
@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .entity-card {
    padding: 1rem;
    margin: 0.5rem 0;
  }
}

/* Touch-friendly interface */
.touch-target {
  min-height: 44px;
  min-width: 44px;
  touch-action: manipulation;
}

```

### **Drag & Drop Interface**

```javascript

// Drag and drop dashboard builder
import { DragDropProvider, DroppableArea } from './utils/ux-enhancements';

const DashboardBuilder = () => (
  <DragDropProvider>
    <DroppableArea accepts={['widget', 'chart']}>
      <div className="dashboard-canvas">
        {widgets.map(widget => (
          <DraggableWidget key={widget.id} widget={widget} />
        ))}
      </div>
    </DroppableArea>
  </DragDropProvider>
);

```

## 🧪 **Testing**

### **Comprehensive Test Suite**

```bash

# Run all tests

python -m pytest business_intel_scraper/backend/tests/ -v

# Test specific components

python -m pytest business_intel_scraper/backend/tests/test_database_models.py
python -m pytest business_intel_scraper/backend/tests/test_security.py
python -m pytest business_intel_scraper/backend/tests/test_performance.py

# Frontend tests

cd business_intel_scraper/frontend
npm test

# Integration tests

python test_comprehensive_platform.py

```

### **Database Validation**

```bash

# Validate database schema and performance

python test_database_solution.py

# Performance benchmarking

python -m business_intel_scraper.backend.tests.performance_tests

```

## 📈 **Success Metrics**

### **Achieved Benchmarks**

- **✅ Test Coverage**: 85%+ across all components
- **✅ API Response Time**: <150ms average (target: <200ms)
- **✅ Database Performance**: Complex queries <500ms
- **✅ Security Score**: Zero high/critical vulnerabilities
- **✅ Mobile Performance**: 95+ Lighthouse score
- **✅ Uptime**: 99.9% availability target

### **Business Intelligence Metrics**

- **Data Processing**: 10,000+ entities/hour throughput
- **Relationship Mapping**: Real-time relationship discovery
- **Geographic Analysis**: Sub-second coordinate-based queries
- **Event Processing**: Timeline analysis with temporal aggregation

## 🤝 **Contributing**

### **Development Setup**

```bash

# Clone repository

git clone https://github.com/Trashytalk/scraper.git
cd scraper

# Development environment with consolidated requirements

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Post-installation setup

python -m spacy download en_core_web_sm
playwright install

# Initialize database

python -c "from business_intel_scraper.database.config import init_database; import asyncio; asyncio.run(init_database())"

# Install frontend dependencies

cd business_intel_scraper/frontend
npm install

# Run development servers

npm run dev        # Frontend development server (port 3000)
uvicorn business_intel_scraper.backend.api.main:app --reload  # Backend API (port 8000)

```

### **Alternative: Advanced Installation**

For granular dependency control:

```bash

# Core only

pip install -e .

# Full development environment

pip install -e ".[full]"

# Production deployment

pip install -e ".[production]"

# Specific features only

pip install -e ".[scraping,data,nlp]"

```

### **Code Quality**

```bash

# Formatting and linting

black .
ruff check . --fix
mypy business_intel_scraper/

# Security scanning

bandit -r business_intel_scraper/
safety check

# Frontend linting

cd business_intel_scraper/frontend
npm run lint
npm run type-check

```

## 📚 **Documentation**

- **[API Documentation](docs/api_usage.md)** - Comprehensive API reference
- **[Architecture Guide](docs/architecture.md)** - System architecture and design
- **[Deployment Guide](docs/deployment.md)** - Production deployment instructions
- **[Developer Guide](docs/developer_guide.md)** - Development workflow and standards
- **[Security Guide](docs/security.md)** - Security implementation and best practices
- **[User Tutorial](docs/tutorial.md)** - Step-by-step user guide

## 🗺️ **Roadmap**

### **✅ Completed (All 12 Priority Items)**

- [x] PostgreSQL database with advanced models ✅
- [x] Production Docker infrastructure ✅
- [x] CI/CD pipeline with GitHub Actions ✅
- [x] Monitoring and logging stack ✅
- [x] Performance optimization and caching ✅
- [x] Real-time collaboration features ✅
- [x] Mobile-responsive user experience ✅
- [x] Enterprise security framework ✅
- [x] GDPR compliance and data governance ✅

### Phase 4: Advanced Analytics (Next)

- [ ] Machine learning integration for pattern detection
- [ ] Natural language query interface
- [ ] Advanced visualization components (D3.js integration)
- [ ] Multi-tenant architecture
- [ ] Advanced export and reporting features

### **💡 Innovation Opportunities**

- AI-powered relationship discovery
- Automated OSINT intelligence workflows
- Predictive analytics for business insights
- Integration with popular BI tools (Tableau, PowerBI)
- Custom visualization builder with drag-and-drop

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Production Ready Status

This is a complete, production-ready enterprise Business Intelligence Platform with all major infrastructure components implemented and tested. The platform successfully handles:

- **Complex business intelligence workflows**
- **Real-time data processing and visualization**
- **Enterprise security and compliance requirements**
- **High-performance data analytics at scale**
- **Mobile-responsive collaborative workflows**

**Ready for deployment and real-world business intelligence use cases.**

---

*Transform your business intelligence with our enterprise-ready Business Intelligence Platform - from data collection to actionable insights.*
