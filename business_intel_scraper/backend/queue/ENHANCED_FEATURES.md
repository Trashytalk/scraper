# Enhanced Distributed Crawler Documentation

## Overview

The Enhanced Distributed Crawler system provides enterprise-grade web crawling capabilities with advanced features for handling modern web applications, rate limiting, content management, and scalability.

## New Features

### 1. Configurable Rate Limiting with Jitter

**Purpose**: Prevent overwhelming target servers and avoid being blocked.

**Features**:
- Per-domain rate limiting
- Configurable requests per second
- Burst capacity for handling spikes
- Jitter to avoid thundering herd problems
- Global or per-domain throttling

**Configuration**:
```python
rate_limit_config = {
    'requests_per_second': 2.0,  # Max 2 requests per second per domain
    'burst_size': 10,            # Allow bursts up to 10 requests
    'jitter_factor': 0.2,        # Add 20% random jitter
    'per_domain': True           # Rate limit per domain
}
```

**Benefits**:
- Respectful crawling that doesn't overload servers
- Reduces chance of IP blocking
- Better success rates
- Configurable for different site requirements

### 2. DNS Caching

**Purpose**: Improve performance and reduce DNS lookup overhead.

**Features**:
- TTL-based DNS resolution caching
- Automatic cache expiration
- Reduced network latency
- Better performance for large crawls

**Configuration**:
```python
dns_cache_ttl = 600  # Cache DNS results for 10 minutes
```

**Benefits**:
- Faster URL processing
- Reduced DNS server load
- Better crawling performance
- Lower network overhead

### 3. Enhanced Metadata and Tagging

**Purpose**: Better tracking and categorization of crawled content.

**New Metadata Fields**:
- `last_crawled_at`: Timestamp of last crawl
- `link_depth`: Distance from original seed URL
- `requires_js`: Whether URL needs JavaScript rendering
- `is_dynamic`: Whether content changes frequently
- `content_size_estimate`: Expected content size
- `tags`: Array of descriptive tags

**Automatic Tags**:
- `last_crawled:2025-07-30T10:30:00Z`
- `link_depth:3`
- `domain:example.com`
- `discovered_from:https://parent-url.com`
- `link_type:form|link|image_link`

**Database Fields**:
```sql
last_crawled_at TIMESTAMP,
link_depth INTEGER,
requires_js BOOLEAN,
is_dynamic BOOLEAN,
content_size INTEGER,
etag VARCHAR(255),
last_modified TIMESTAMP
```

### 4. JavaScript Rendering with Headless Browser

**Purpose**: Handle modern single-page applications and JavaScript-heavy sites.

**Features**:
- Pyppeteer-based headless Chrome automation
- Smart detection of JS-required pages
- Configurable wait conditions
- Pool of browser instances for performance
- Extraction of dynamically generated content

**Configuration**:
```python
enable_js_rendering = True
browser_config = {
    'max_browsers': 3,      # Browser pool size
    'page_timeout': 45,     # Page load timeout
}
```

**Smart Detection**:
- URL pattern analysis (spa, react, angular, vue)
- Fragment identifiers (#app, #page)
- API endpoints
- Dynamic content indicators

**Wait Conditions**:
- Site-specific selectors (LinkedIn: `.core-rail`)
- Common patterns (`.results`, `.listings`)
- Custom wait conditions

### 5. Large Webpage Handling

**Purpose**: Efficiently handle large content while preventing memory issues.

**Features**:
- Configurable maximum content size
- Streaming content download
- Content size estimation
- Graceful handling of oversized content
- Memory-efficient processing

**Configuration**:
```python
max_content_size = 100 * 1024 * 1024  # 100MB limit
```

**Processing**:
- Check `Content-Length` header before download
- Stream content in chunks
- Stop download if size limit exceeded
- Log and track oversized content

### 6. Continual Updates and Dynamic Content

**Purpose**: Handle sites with frequently changing content.

**Features**:
- Conditional HTTP requests (If-Modified-Since, If-None-Match)
- ETag and Last-Modified tracking
- Dynamic recrawl intervals
- 304 Not Modified handling
- Content freshness detection

**Dynamic Interval Calculation**:
- Static content: 24 hours
- JavaScript-heavy: 12 hours  
- Dynamic content: 6 hours
- Configurable per content type

**Conditional Requests**:
```http
If-None-Match: "33a64df551425fcc55e4d42a148795d9f25f89d4"
If-Modified-Since: Wed, 21 Oct 2015 07:28:00 GMT
```

## Usage Examples

### Basic Enhanced Setup

```python
from business_intel_scraper.backend.queue import DistributedCrawlSystem, QueueBackend

# Enhanced configuration
rate_config = {
    'requests_per_second': 1.5,
    'jitter_factor': 0.1,
    'per_domain': True
}

system = DistributedCrawlSystem(
    queue_backend=QueueBackend.REDIS,
    rate_limit_config=rate_config,
    enable_js_rendering=True,
    max_content_size=50 * 1024 * 1024,  # 50MB
    dns_cache_ttl=300
)

await system.start()
```

### Adding URLs with Enhanced Metadata

```python
# Add JavaScript-heavy sites
await system.add_seed_urls(
    ["https://linkedin.com/company/", "https://crunchbase.com/"],
    job_id="js-business-sites",
    priority=8,
    requires_js=True,
    is_dynamic=True
)

# Add static business directories
await system.add_seed_urls(
    ["https://yellowpages.com", "https://yelp.com"],
    job_id="business-directories", 
    priority=6,
    requires_js=False,
    is_dynamic=False
)
```

### Monitoring Enhanced Metrics

```python
stats = await system.get_system_stats()

print(f"JS Rendered Pages: {stats['crawl_metrics']['js_rendered_pages']}")
print(f"Large Pages Skipped: {stats['crawl_metrics']['large_pages_skipped']}")
print(f"Conditional Requests: {stats['crawl_metrics']['conditional_requests']}")
print(f"Not Modified: {stats['crawl_metrics']['not_modified_responses']}")
```

## Performance Optimizations

### 1. Connection Pooling
- Persistent HTTP connections
- DNS caching
- Connection limits per host

### 2. Browser Pool Management
- Reuse browser instances
- Graceful browser lifecycle
- Memory management

### 3. Content Streaming
- Chunked download
- Size limit enforcement
- Memory-efficient processing

### 4. Smart Crawling
- Conditional requests
- Dynamic intervals
- Priority-based queuing

## Configuration Best Practices

### Rate Limiting
```python
# Conservative (respectful)
rate_config = {
    'requests_per_second': 0.5,
    'jitter_factor': 0.3
}

# Moderate (balanced)
rate_config = {
    'requests_per_second': 2.0,
    'jitter_factor': 0.1
}

# Aggressive (fast)
rate_config = {
    'requests_per_second': 5.0,
    'jitter_factor': 0.05
}
```

### Content Size Limits
```python
# Small sites
max_content_size = 10 * 1024 * 1024  # 10MB

# Medium sites
max_content_size = 50 * 1024 * 1024  # 50MB

# Large sites
max_content_size = 200 * 1024 * 1024  # 200MB
```

### JavaScript Rendering
```python
# Minimal (specific sites only)
enable_js_rendering = True
browser_config = {'max_browsers': 1}

# Balanced (moderate usage)
enable_js_rendering = True
browser_config = {'max_browsers': 3, 'page_timeout': 30}

# Heavy (JS-first approach)
enable_js_rendering = True
browser_config = {'max_browsers': 5, 'page_timeout': 60}
```

## Monitoring and Debugging

### Enhanced Metrics
- `js_rendered_pages`: Pages rendered with browser
- `large_pages_skipped`: Pages skipped due to size
- `conditional_requests`: Requests with If-Modified-Since/ETag
- `not_modified_responses`: 304 responses received
- `dns_cache_hits`: DNS cache utilization

### Logging
```python
import logging
logging.getLogger('distributed_crawler').setLevel(logging.DEBUG)
```

### Database Queries
```sql
-- Find JavaScript-heavy sites
SELECT url, requires_js, content_size FROM crawl_records WHERE requires_js = true;

-- Dynamic content analysis
SELECT domain, AVG(content_size), COUNT(*) 
FROM crawl_records 
WHERE is_dynamic = true 
GROUP BY domain;

-- Crawl frequency analysis
SELECT 
    CASE 
        WHEN recrawl_interval_hours <= 6 THEN 'Dynamic'
        WHEN recrawl_interval_hours <= 12 THEN 'JS-Heavy'
        ELSE 'Static'
    END as content_type,
    COUNT(*) as url_count
FROM crawl_records 
GROUP BY content_type;
```

## Troubleshooting

### Common Issues

1. **Browser Launch Failures**
   - Install Chrome/Chromium
   - Check system dependencies
   - Verify puppeteer installation

2. **Rate Limiting Too Aggressive**
   - Increase `requests_per_second`
   - Reduce `jitter_factor`
   - Check per-domain settings

3. **Large Content Issues**
   - Adjust `max_content_size`
   - Monitor memory usage
   - Check content streaming

4. **DNS Resolution Slow**
   - Increase `dns_cache_ttl`
   - Check DNS server performance
   - Consider custom DNS servers

### Performance Tuning

1. **Browser Performance**
   - Limit concurrent browsers
   - Use faster selectors
   - Optimize wait conditions

2. **Network Performance**
   - Tune connection limits
   - Adjust timeouts
   - Optimize DNS caching

3. **Memory Management**
   - Monitor browser memory
   - Tune content limits
   - Regular garbage collection

## Future Enhancements

1. **Smart Rate Limiting**
   - Adaptive rate adjustment
   - Server response analysis
   - Automatic backoff

2. **Enhanced Browser Features**
   - Screenshot capture
   - PDF generation
   - Performance metrics

3. **Advanced Content Detection**
   - Machine learning classification
   - Content type prediction
   - Automatic optimization

4. **Distributed Browser Pool**
   - Remote browser instances
   - Load balancing
   - Failover support
