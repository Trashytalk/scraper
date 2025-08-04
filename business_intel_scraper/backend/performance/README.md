# Performance Optimization System

The Business Intelligence Scraper includes a comprehensive performance optimization system designed to enhance system performance, reduce resource usage, and provide detailed monitoring capabilities.

## Features

### 🚀 Core Components

- **Performance Cache**: Redis/local hybrid caching with compression and TTL management
- **Database Optimization**: Connection pooling, query caching, and batch processing
- **Task Processing**: Background task optimization with intelligent queuing
- **Memory Management**: Garbage collection optimization and object pooling
- **System Monitoring**: Real-time performance metrics and system resource tracking

### 📊 API Endpoints

The performance system provides REST API endpoints for monitoring and control:

- `GET /performance/status` - Overall system performance status
- `GET /performance/metrics` - Detailed performance metrics
- `GET /performance/cache/stats` - Cache performance statistics
- `POST /performance/optimize/{profile}` - Apply optimization profiles
- `POST /performance/cache/clear` - Clear performance cache
- `GET /performance/recommendations` - Get optimization recommendations

### 🖥️ CLI Commands

Use the performance CLI for command-line monitoring and control:

```bash

# Check system status

bi-performance status

# View detailed metrics

bi-performance metrics --json-output

# Apply optimization profile

bi-performance optimize balanced

# Clear cache

bi-performance clear-cache --pattern analytics

# Run performance benchmark

bi-performance benchmark --iterations 100

# Get recommendations

bi-performance recommendations

# Real-time monitoring

bi-performance monitor

```

### ⚙️ Optimization Profiles

Choose from three optimization profiles based on your needs:

#### Balanced (Default)

- Moderate caching with 1-hour TTL
- Standard connection pooling
- Balanced memory management
- General-purpose optimization

#### Memory Focused

- Aggressive garbage collection
- Reduced cache size
- Memory usage monitoring
- Lower memory footprint

#### Performance Focused

- Extended cache TTL (4 hours)
- Larger connection pools
- Background task optimization
- Maximum performance

## Installation

### Basic Installation

```bash

pip install -e .

```

### With Performance Dependencies

```bash

pip install -e .[performance]

```

This includes:
- `psutil` for system monitoring
- `memory-profiler` for memory analysis
- Enhanced Redis caching support

## Configuration

### Environment Variables

```bash

# Redis configuration (optional)

REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true

# Performance settings

PERFORMANCE_CACHE_TTL=3600
PERFORMANCE_CACHE_MAX_SIZE=10000
PERFORMANCE_MONITORING_ENABLED=true

# Database optimization

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30

```

### Configuration File

Create `config/performance.yaml`:

```yaml

performance:
  cache:
    enabled: true
    redis_url: "redis://localhost:6379/0"
    default_ttl: 3600
    max_size: 10000
    compression: true

  database:
    pool_size: 20
    max_overflow: 30
    pool_timeout: 30
    enable_query_cache: true

  monitoring:
    enabled: true
    metrics_interval: 60
    system_monitoring: true

```

## Usage Examples

### Python API

```python

from business_intel_scraper.backend.performance.optimizer import get_performance_optimizer

# Get optimizer instance

optimizer = get_performance_optimizer()

# Run performance analysis

analysis = await optimizer.run_performance_analysis()
print(f"Cache hit rate: {analysis['cache_performance']['hit_rate']:.1%}")

# Apply optimization

result = await optimizer.apply_optimizations('performance_focused')
print(f"Applied {result['profile_applied']} profile")

# Use performance cache

await optimizer.cache.set("key", "value", ttl=3600)
cached_value = await optimizer.cache.get("key")

```

### Analytics Integration

The performance system integrates with the analytics dashboard:

```python

from business_intel_scraper.backend.analytics.core import AnalyticsCore
from business_intel_scraper.backend.performance import AnalyticsPerformanceIntegration

# Analytics with performance optimization

analytics = AnalyticsCore()
perf_integration = AnalyticsPerformanceIntegration(analytics)

# Optimized dashboard data

dashboard_data = await perf_integration.get_optimized_dashboard_data()

```

### REST API Usage

```bash

# Get system status

curl http://localhost:8000/performance/status

# View metrics as JSON

curl http://localhost:8000/performance/metrics

# Apply optimization profile

curl -X POST http://localhost:8000/performance/optimize/balanced

# Clear specific cache pattern

curl -X POST "http://localhost:8000/performance/cache/clear?pattern=dashboard"

# Get recommendations

curl http://localhost:8000/performance/recommendations

```

## Monitoring

### Real-time Dashboard

Access the performance monitoring dashboard at:
- **API Status**: `http://localhost:8000/performance/status`
- **Metrics**: `http://localhost:8000/performance/metrics`
- **Cache Stats**: `http://localhost:8000/performance/cache/stats`

### CLI Monitoring

```bash

# Continuous monitoring

bi-performance monitor

# One-time status check

bi-performance status

# Detailed metrics

bi-performance metrics --json-output

```

### Log Integration

Performance events are logged to the standard application logs:

```python

import logging

# Enable performance logging

logging.getLogger('performance').setLevel(logging.INFO)

```

## Performance Testing

Run the included performance test suite:

```bash

python test_performance.py

```

This tests:
- Cache operations and hit rates
- Task processing performance
- Memory optimization
- System resource monitoring

## Troubleshooting

### Common Issues

**Cache not working**
- Ensure Redis is running: `redis-server`
- Check Redis connection: `redis-cli ping`
- Verify environment variables

**High memory usage**
- Apply memory-focused profile: `bi-performance optimize memory_focused`
- Clear cache: `bi-performance clear-cache`
- Monitor with: `bi-performance monitor`

**Poor performance**
- Check system resources: `bi-performance status`
- Get recommendations: `bi-performance recommendations`
- Apply performance profile: `bi-performance optimize performance_focused`

### Logs and Debugging

Enable debug logging:

```bash

export LOG_LEVEL=DEBUG

```

Check performance logs:

```bash

tail -f logs/performance.log

```

## Integration

### With Existing Analytics

The performance system integrates seamlessly with the analytics dashboard:

- Cached dashboard data for faster loading
- Optimized data processing
- Background metrics calculation
- Performance-aware data fetching

### With AI System

Performance optimization for AI operations:

- Model response caching
- Batch processing optimization
- Memory management for large datasets
- Async processing for AI tasks

### With Scraping System

Enhanced scraping performance:

- Request caching and deduplication
- Connection pooling optimization
- Memory-efficient data processing
- Background task scheduling

## Best Practices

1. **Start with Balanced Profile**: Use the default balanced profile for most workloads
2. **Monitor Regularly**: Check performance status periodically
3. **Use Redis**: Install Redis for optimal cache performance
4. **Profile-Specific Optimization**: Choose profiles based on your constraints
5. **Clear Cache Strategically**: Use pattern-based cache clearing
6. **Resource Monitoring**: Watch system resources during optimization

## Architecture

```
Performance System
├── PerformanceOptimizer (coordinator)
├── PerformanceCache (Redis/local hybrid)
├── DatabaseOptimizer (connection pooling)
├── TaskOptimizer (background processing)
├── MemoryOptimizer (GC management)
└── SystemMonitor (resource tracking)

```

The system is designed to:
- Work with or without optional dependencies
- Provide graceful fallbacks
- Scale with system load
- Integrate with existing components
- Minimize performance overhead

## Contributing

When contributing performance improvements:

1. Add tests to `test_performance.py`
2. Update benchmarks if needed
3. Document new optimization strategies
4. Ensure backward compatibility
5. Test with various system loads

For questions or issues, please see the main project documentation.
