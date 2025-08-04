# Distributed Queue System

A comprehensive, enterprise-grade distributed crawling and queue management system for the Business Intelligence Scraper. This system provides fault-tolerant, scalable web crawling with multiple backend support and advanced features including OCR integration and sophisticated retry mechanisms.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash

# Navigate to the queue system directory

cd business_intel_scraper/backend/queue/

# Run the setup script (interactive mode)

./setup.sh

# Or with specific options

./setup.sh --backend redis --environment development --docker --start

```

### Option 2: Manual Setup

```bash

# Install dependencies

pip install -r requirements-consolidated.txt
pip install redis kafka-python boto3 rich click pyyaml

# Start Redis (or your chosen backend)

docker run -d -p 6379:6379 redis:7-alpine

# Initialize the system

python -m business_intel_scraper.backend.queue.cli system initialize --backend redis

```

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Queue Backends](#queue-backends)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Docker Deployment](#docker-deployment)
- [Monitoring](#monitoring)
- [OCR Integration](#ocr-integration)
- [Performance Tuning](#performance-tuning)
- [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

The distributed queue system consists of several key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Seed URLs     │    │  Frontier Queue │    │  Crawl Workers  │
│   Management    │───▶│   (Priority)    │───▶│  (Distributed)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Dead Letter    │    │  Parse Queue    │    │ Parse Workers   │
│     Queue       │◀───│   (Priority)    │◀───│ (Distributed)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Retry Queue    │    │   Storage       │    │  OCR Engine     │
│ (Exponential    │    │  (S3/MinIO)     │    │  Integration    │
│  Backoff)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘

```

### Core Components

1. **Distributed Crawl System**: Central coordinator managing workers and queues
2. **Queue Managers**: Abstract interface with multiple backend implementations
3. **Workers**: Specialized crawl and parse workers with fault tolerance
4. **OCR Integration**: Multi-engine support for image and PDF processing
5. **Database Layer**: PostgreSQL for crawl tracking and metadata
6. **Storage Layer**: S3/MinIO for content storage
7. **Monitoring**: Comprehensive metrics and health checks

## ✨ Features

### Queue Management

- **Multiple Backends**: Redis, Kafka, AWS SQS, and in-memory support
- **Priority Queues**: High-priority URL processing
- **Dead Letter Queues**: Failed URL collection and analysis
- **Retry Mechanisms**: Exponential backoff with configurable limits

### Fault Tolerance

- **Worker Recovery**: Automatic worker restart on failures
- **Circuit Breakers**: Prevent cascade failures
- **Health Checks**: Continuous system monitoring
- **Graceful Shutdown**: Clean process termination

### Scalability

- **Horizontal Scaling**: Add workers dynamically
- **Load Balancing**: Distribute work across workers
- **Resource Management**: Memory and CPU optimization
- **Batch Processing**: Efficient bulk operations

### OCR & Content Processing

- **Multi-Engine OCR**: Tesseract, AWS Textract, Google Vision
- **Image Processing**: PNG, JPEG, WebP support
- **PDF Processing**: Text and image extraction
- **Content Filtering**: Smart content type detection

### Monitoring & Analytics

- **Real-time Metrics**: Queue sizes, processing rates
- **Performance Tracking**: Response times, error rates
- **Worker Status**: Health and activity monitoring
- **System Statistics**: Comprehensive dashboards

## 🔧 Queue Backends

### Redis (Recommended for most use cases)

- **Use Case**: High-performance, small to medium scale
- **Pros**: Fast, reliable, easy to setup
- **Cons**: Single point of failure (without clustering)

```yaml

redis:
  url: redis://localhost:6379/0
  max_connections: 20
  socket_timeout: 30.0

```

### Kafka (High-throughput scenarios)

- **Use Case**: High-volume, stream processing
- **Pros**: Excellent throughput, durable, scalable
- **Cons**: Complex setup, higher resource usage

```yaml

kafka:
  bootstrap_servers: localhost:9092
  group_id: queue-workers
  topic_config:
    num_partitions: 12
    replication_factor: 3

```

### AWS SQS (Cloud-native)

- **Use Case**: AWS environments, managed service
- **Pros**: Fully managed, highly available, integrates with AWS
- **Cons**: Higher latency, costs, vendor lock-in

```yaml

sqs:
  region_name: us-west-2
  visibility_timeout: 300
  enable_fifo: true

```

### Memory (Development/Testing)

- **Use Case**: Development, testing, quick prototyping
- **Pros**: No external dependencies, instant setup
- **Cons**: Not persistent, not distributed

## 📦 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis/Kafka/SQS (depending on backend)
- Docker (optional, for containerized deployment)

### Install Python Dependencies

```bash

pip install -r requirements-consolidated.txt

# Backend-specific dependencies

pip install redis>=4.5.0          # For Redis backend
pip install kafka-python>=2.0.0   # For Kafka backend
pip install boto3>=1.26.0         # For SQS backend

# CLI and monitoring

pip install rich>=13.0.0 click>=8.0.0 pyyaml>=6.0

# OCR dependencies

pip install pytesseract>=0.3.10 Pillow>=9.0.0 pdf2image>=3.1.0

```

### System Dependencies

```bash

# Ubuntu/Debian

sudo apt-get update
sudo apt-get install postgresql-client redis-server tesseract-ocr

# macOS

brew install postgresql redis tesseract

# For PDF processing

sudo apt-get install poppler-utils  # Ubuntu/Debian
brew install poppler               # macOS

```

## ⚙️ Configuration

### Configuration File

Create a configuration file for your environment:

```yaml

# config.production.yaml

queue_backend: redis
environment: production
debug: false

crawl:
  num_crawl_workers: 10
  crawl_delay: 1.0
  timeout: 30.0
  max_retries: 3
  max_depth: 3

parse:
  num_parse_workers: 5
  enable_ocr: true
  ocr_engines: ["tesseract", "aws_textract"]

database:
  url: postgresql://user:pass@localhost:5432/business_intel
  pool_size: 10

storage:
  type: s3
  bucket: my-crawl-bucket
  region: us-west-2

monitoring:
  enable_metrics: true
  log_level: INFO

security:
  enable_auth: true
  rate_limit_enabled: true

```

### Environment Variables

```bash

# Core settings

export QUEUE_BACKEND=redis
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@localhost:5432/business_intel

# Redis settings

export REDIS_URL=redis://localhost:6379/0

# Kafka settings

export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# AWS SQS settings

export AWS_REGION=us-west-2
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Storage settings

export S3_BUCKET=my-crawl-bucket
export S3_ACCESS_KEY=your_s3_key
export S3_SECRET_KEY=your_s3_secret

```

## 🚀 Usage Examples

### Basic Usage

```python

from business_intel_scraper.backend.queue import DistributedCrawlSystem, QueueBackend

# Initialize the system

system = DistributedCrawlSystem(
    queue_backend=QueueBackend.REDIS,
    redis_url="redis://localhost:6379/0",
    num_crawl_workers=5,
    num_parse_workers=3
)

# Start the system

await system.start()

# Add seed URLs

await system.add_seed_urls([
    "https://example.com",
    "https://business-directory.com"
], job_id="my-crawl-job")

# Monitor progress

stats = await system.get_system_stats()
print(f"Frontier queue size: {stats['queue_stats']['frontier_queue_size']}")

# Stop the system

await system.stop()

```

### Advanced Configuration

```python

from business_intel_scraper.backend.queue.config import QueueSystemConfig, get_production_config

# Load production configuration

config = get_production_config()

# Customize for your needs

config.crawl.num_crawl_workers = 20
config.parse.enable_ocr = True
config.parse.ocr_engines = [OCREngine.TESSERACT, OCREngine.AWS_TEXTRACT]

# Initialize with custom config

system = DistributedCrawlSystem.from_config(config)

```

### Batch URL Processing

```python

# Add URLs with different priorities

await system.add_seed_urls([
    "https://high-priority.com",
    "https://medium-priority.com"
], job_id="batch-job", priority=[10, 5])

# Add URLs from file

with open("seed_urls.txt", "r") as f:
    urls = [line.strip() for line in f if line.strip()]
    await system.add_seed_urls(urls, job_id="file-job")

```

## 🖥️ CLI Reference

The queue system includes a comprehensive CLI for management:

### System Management

```bash

# Initialize the system

python -m business_intel_scraper.backend.queue.cli system initialize \
    --backend redis --crawl-workers 5 --parse-workers 3

# Check system health

python -m business_intel_scraper.backend.queue.cli system health

# Show system requirements

python -m business_intel_scraper.backend.queue.cli system requirements --backend kafka

```

### Monitoring

```bash

# Show queue statistics

python -m business_intel_scraper.backend.queue.cli monitor stats

# Watch real-time statistics

python -m business_intel_scraper.backend.queue.cli monitor stats --watch --interval 5

# Show queue details

python -m business_intel_scraper.backend.queue.cli monitor queues --queue frontier

```

### Worker Management

```bash

# List all workers

python -m business_intel_scraper.backend.queue.cli worker list

# Show worker details

python -m business_intel_scraper.backend.queue.cli worker status --worker-id crawl-worker-0

```

### Seed URL Management

```bash

# Add individual URLs

python -m business_intel_scraper.backend.queue.cli seed add \
    --job-id my-job --priority 5 \

    https://example.com https://test.com

# Import from file

python -m business_intel_scraper.backend.queue.cli seed import-file \
    --job-id bulk-job seed_urls.txt

# Import from CSV (column 0)

python -m business_intel_scraper.backend.queue.cli seed import-file \
    --job-id csv-job --column 0 urls.csv

```

## 🌐 API Reference

### REST API Endpoints

The queue system provides a comprehensive REST API:

```bash

# Start the API server

python -m business_intel_scraper.backend.queue.api

# API will be available at http://localhost:8000

```

#### System Endpoints

```http

GET /health                 # System health check
GET /stats                  # System statistics
POST /system/initialize     # Initialize system
POST /system/shutdown       # Shutdown system

```

#### Queue Management

```http

GET /queues                 # List all queues
GET /queues/{queue_name}    # Get queue details
DELETE /queues/{queue_name} # Clear queue

```

#### URL Management

```http

POST /urls/seed             # Add seed URLs
GET /urls/status/{url_id}   # Get URL status
DELETE /urls/{url_id}       # Remove URL from queue

```

#### Worker Management

```http

GET /workers                # List all workers
GET /workers/{worker_id}    # Get worker details
POST /workers/{worker_id}/stop    # Stop specific worker
POST /workers/{worker_id}/restart # Restart specific worker

```

### API Examples

```bash

# Add seed URLs via API

curl -X POST http://localhost:8000/urls/seed \
  -H "Content-Type: application/json" \
  -d '{

    "urls": ["https://example.com", "https://test.com"],
    "job_id": "api-job",
    "priority": 5
  }'

# Get system statistics

curl http://localhost:8000/stats

# Check system health

curl http://localhost:8000/health

```

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash

# Start Redis-based system

cd business_intel_scraper/backend/queue/
docker-compose -f docker-compose.queue.yml up -d redis-queue queue-api

# Start Kafka-based system

docker-compose -f docker-compose.queue.yml up -d zookeeper kafka queue-api

# Scale workers

docker-compose -f docker-compose.queue.yml up -d --scale crawl-worker=5 --scale parse-worker=3

```

### Production Deployment

```yaml

# docker-compose.production.yml

version: '3.8'

services:
  redis-cluster:
    image: redis:7-alpine
    deploy:
      replicas: 3
    configs:
      - redis.conf

  queue-api:
    image: business-intel/queue-system:latest
    deploy:
      replicas: 2
    environment:
      - QUEUE_BACKEND=redis
      - REDIS_URL=redis://redis-cluster:6379/0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/business_intel

  crawl-workers:
    image: business-intel/queue-system:latest
    deploy:
      replicas: 10
    command: python -m business_intel_scraper.backend.queue.worker --type crawl

  parse-workers:
    image: business-intel/queue-system:latest
    deploy:
      replicas: 5
    command: python -m business_intel_scraper.backend.queue.worker --type parse

```

### Kubernetes Deployment

```yaml

# k8s-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: queue-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: queue-api
  template:
    metadata:
      labels:
        app: queue-api
    spec:
      containers:
      - name: queue-api

        image: business-intel/queue-system:latest
        ports:
        - containerPort: 8000

        env:
        - name: QUEUE_BACKEND

          value: "redis"
        - name: REDIS_URL

          value: "redis://redis-service:6379/0"

```

## 📊 Monitoring

### Built-in Metrics

The system provides comprehensive metrics:

- **Queue Metrics**: Size, throughput, latency
- **Worker Metrics**: Active workers, tasks processed, error rates
- **System Metrics**: Memory usage, CPU utilization
- **Business Metrics**: URLs crawled, data extracted, success rates

### Prometheus Integration

```python

from prometheus_client import start_http_server, Counter, Gauge, Histogram

# Start metrics server

start_http_server(8080)

# Custom metrics

urls_processed = Counter('urls_processed_total', 'Total URLs processed')
queue_size = Gauge('queue_size', 'Current queue size', ['queue_name'])
response_time = Histogram('response_time_seconds', 'Response time in seconds')

```

### Grafana Dashboard

Example dashboard configuration:

```json

{
  "dashboard": {
    "title": "Queue System Dashboard",
    "panels": [
      {
        "title": "Queue Sizes",
        "type": "graph",
        "targets": [
          {
            "expr": "queue_size{queue_name=\"frontier\"}",
            "legendFormat": "Frontier Queue"
          }
        ]
      }
    ]
  }
}

```

## 🔍 OCR Integration

### Supported Engines

1. **Tesseract** (Default)
   - Free, open-source
   - Good for general text
   - Local processing

2. **AWS Textract**
   - Advanced table/form detection
   - Cloud-based
   - Higher accuracy

3. **Google Vision API**
   - Excellent accuracy
   - Cloud-based
   - Supports many languages

### Configuration

```yaml

parse:
  enable_ocr: true
  ocr_engines: ["tesseract", "aws_textract"]
  image_max_size: 5242880  # 5MB
  pdf_max_pages: 50

```

### Usage Examples

```python

from business_intel_scraper.backend.queue.ocr_integration import OCRProcessor

# Initialize OCR processor

processor = OCRProcessor(
    engines=[OCREngine.TESSERACT, OCREngine.AWS_TEXTRACT]
)

# Process image

text = await processor.extract_text_from_image("image.png")

# Process PDF

text = await processor.extract_text_from_pdf("document.pdf")

# Extract URLs from OCR text

urls = processor.extract_urls_from_text(text)

```

## ⚡ Performance Tuning

### Queue Backend Optimization

#### Redis

```yaml

redis:
  max_connections: 50
  socket_timeout: 60.0
  socket_keepalive: true
  socket_keepalive_options:
    TCP_KEEPIDLE: 1
    TCP_KEEPINTVL: 3
    TCP_KEEPCNT: 5

```

#### Kafka

```yaml

kafka:
  max_poll_records: 1000
  fetch_min_bytes: 1024
  fetch_max_wait: 500
  topic_config:
    num_partitions: 24
    batch_size: 16384
    linger_ms: 5

```

### Worker Optimization

```yaml

crawl:
  max_concurrent_requests: 20
  connection_pool_size: 100
  timeout: 30.0
  crawl_delay: 0.5

parse:
  batch_size: 50
  parallel_processing: true
  text_extraction_timeout: 60.0

```

### Database Optimization

```sql

-- Optimize PostgreSQL for queue workload

ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();

```

## 🐛 Troubleshooting

### Common Issues

#### High Memory Usage

```yaml

# Reduce batch sizes

parse:
  batch_size: 10
  max_content_size: 1048576  # 1MB

# Limit worker count

crawl:
  num_crawl_workers: 3

```

#### Queue Backup

```bash

# Check queue sizes

python -m business_intel_scraper.backend.queue.cli monitor stats

# Add more workers

docker-compose up -d --scale crawl-worker=10

# Clear dead letter queue

python -m business_intel_scraper.backend.queue.cli queues clear --queue dead

```

#### Connection Issues

```yaml

# Increase timeouts

redis:
  socket_timeout: 60.0
  socket_connect_timeout: 30.0
  retry_on_timeout: true

# Add connection retry

worker:
  restart_on_failure: true
  max_retries: 5

```

### Debugging

Enable debug logging:

```python

import logging
logging.basicConfig(level=logging.DEBUG)

# Or via configuration

monitoring:
  log_level: DEBUG
  enable_performance_monitoring: true

```

View worker logs:

```bash

# Docker logs

docker-compose logs -f crawl-worker

# System logs

journalctl -u queue-system -f

# Application logs

tail -f /var/log/queue-system/workers.log

```

### Performance Monitoring

```bash

# Check system resources

htop
iotop
nethogs

# Check database performance

SELECT * FROM pg_stat_activity WHERE state = 'active';

# Check Redis performance

redis-cli --latency
redis-cli info stats

```

## 📚 Additional Resources

### Documentation

- [API Documentation](./docs/api.md)
- [Configuration Reference](./docs/configuration.md)
- [Deployment Guide](./docs/deployment.md)
- [Troubleshooting Guide](./docs/troubleshooting.md)

### Examples

- [Basic Usage Examples](./examples/basic.py)
- [Advanced Configuration](./examples/advanced.py)
- [Custom Workers](./examples/custom_workers.py)
- [OCR Integration](./examples/ocr_examples.py)

### Community

- [GitHub Issues](https://github.com/your-org/business-intel-scraper/issues)
- [Discussions](https://github.com/your-org/business-intel-scraper/discussions)
- [Contributing Guide](./CONTRIBUTING.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../../../LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](../../../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📈 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a detailed history of changes.


---


**Happy Crawling! 🕷️**
