# Enhanced Web Crawling Configuration Guide

## Overview

The Business Intelligence Scraper now includes advanced web crawling capabilities with comprehensive configuration options available through the GUI. This guide explains all the configuration options and their impact on crawling performance.

## Quick Start with Presets

### 🎯 Configuration Presets

Use these presets as starting points for different crawling scenarios:

#### 🐌 Conservative

- **Best for**: Production environments, respectful crawling
- **Rate**: 0.5 requests/second, 2 burst size
- **Features**: High jitter (20%), conditional requests enabled
- **Resource Usage**: Low (3 workers, 25MB content limit)
- **Use Cases**: News sites, corporate websites, compliance-sensitive crawling

#### ⚖️ Balanced

- **Best for**: General purpose crawling, development
- **Rate**: 1.0 requests/second, 5 burst size
- **Features**: Moderate jitter (10%), conditional requests enabled
- **Resource Usage**: Medium (10 workers, 50MB content limit)
- **Use Cases**: E-commerce sites, blogs, directory crawling

#### 🚀 Aggressive

- **Best for**: Large-scale data collection, time-sensitive projects
- **Rate**: 3.0 requests/second, 10 burst size
- **Features**: Low jitter (5%), fast recrawling intervals
- **Resource Usage**: High (20 workers, 100MB content limit)
- **Use Cases**: Public APIs, data aggregation, research projects

#### 🎭 SPA/JavaScript

- **Best for**: Single Page Applications, JavaScript-heavy sites
- **Rate**: 0.8 requests/second, 3 burst size
- **Features**: JavaScript rendering enabled, browser automation
- **Resource Usage**: Medium-High (5 workers + 3 browsers)
- **Use Cases**: React/Angular/Vue apps, social media, modern web apps

## Detailed Configuration Options

### 🚦 Rate Limiting & Performance

#### Requests Per Second (0.1 - 10.0)

- **Purpose**: Controls the maximum number of HTTP requests per second
- **Conservative**: 0.5 - 1.0 (respectful crawling)
- **Aggressive**: 2.0 - 5.0 (fast crawling)
- **Impact**: Higher values = faster crawling but more server load

#### Burst Size (1 - 20)

- **Purpose**: Number of requests that can be made immediately at startup
- **Conservative**: 2 - 3 (gentle startup)
- **Aggressive**: 10 - 15 (fast startup)
- **Impact**: Allows rapid initial crawling before rate limiting kicks in

#### Jitter Factor (0 - 50%)

- **Purpose**: Adds randomness to request timing to avoid detection
- **Conservative**: 15% - 30% (highly randomized)
- **Aggressive**: 5% - 10% (minimal randomization)
- **Impact**: Higher values = more human-like traffic patterns

#### Per-Domain Rate Limiting

- **Purpose**: Apply separate rate limits to each domain
- **Recommended**: Enabled (prevents overwhelming any single server)
- **Impact**: Better for multi-domain crawling, respectful behavior

### 🌐 JavaScript & Browser Rendering

#### Enable JavaScript Rendering

- **Purpose**: Use headless Chrome to execute JavaScript and render dynamic content
- **When to Enable**: SPAs, React/Angular/Vue apps, AJAX-heavy sites
- **Performance Impact**: High (requires browser instances)
- **Memory Usage**: ~100-200MB per browser instance

#### Max Browsers (1 - 10)

- **Purpose**: Number of concurrent headless browser instances
- **Conservative**: 2 - 3 (low resource usage)
- **Aggressive**: 5 - 8 (high parallelism)
- **Impact**: More browsers = faster JS rendering but higher memory usage

#### Page Timeout (10 - 120 seconds)

- **Purpose**: Maximum time to wait for page load and JavaScript execution
- **Fast Sites**: 15 - 30 seconds
- **Slow Sites**: 45 - 90 seconds
- **Impact**: Longer timeouts handle slow sites but increase crawl time

#### Wait Selector

- **Purpose**: CSS selector to wait for before considering page loaded
- **Examples**:
  - `.content-loaded` (wait for specific content)
  - `#main-container` (wait for main content area)
  - `[data-ready="true"]` (wait for data attribute)
- **Impact**: Ensures dynamic content is fully loaded before extraction

### 📄 Content Handling & Performance

#### Max Content Size (1 - 500 MB)

- **Purpose**: Maximum size of content to download per page
- **Conservative**: 10 - 25 MB (skip large files)
- **Aggressive**: 50 - 200 MB (handle large documents)
- **Impact**: Larger limits handle more content types but use more bandwidth

#### DNS Cache TTL (1 - 60 minutes)

- **Purpose**: How long to cache DNS resolution results
- **Conservative**: 10 - 30 minutes (fresh lookups)
- **Aggressive**: 5 - 15 minutes (faster lookups)
- **Impact**: Longer TTL = better performance but less fresh DNS data

#### Conditional HTTP Requests

- **Purpose**: Use If-Modified-Since and ETag headers to avoid re-downloading unchanged content
- **Recommendation**: Always enabled
- **Impact**: Significantly reduces bandwidth and improves performance

#### Content Compression

- **Purpose**: Request gzip/deflate compression from servers
- **Recommendation**: Always enabled
- **Impact**: Reduces bandwidth usage and download time

### 🔄 Queue & Retry Configuration

#### Queue Backend

- **Redis**: Best for production, distributed crawling
- **Kafka**: Best for high-throughput, stream processing
- **AWS SQS**: Best for cloud deployments, managed service
- **Memory**: Best for development and testing only

#### Max Retries (0 - 10)

- **Purpose**: Number of times to retry failed requests
- **Conservative**: 3 - 5 (handle temporary failures)
- **Aggressive**: 1 - 2 (fail fast)
- **Impact**: More retries = better success rate but slower failure handling

#### Concurrent Workers (1 - 50)

- **Purpose**: Number of parallel crawling processes
- **Conservative**: 3 - 10 (low resource usage)
- **Aggressive**: 15 - 30 (high parallelism)
- **Impact**: More workers = faster crawling but higher resource usage

### ⏰ Recrawl & Update Settings

#### Static Content Interval (1 - 168 hours)

- **Purpose**: How often to recrawl pages with static content
- **Conservative**: 48 - 168 hours (weekly updates)
- **Aggressive**: 12 - 24 hours (daily updates)
- **Use Cases**: News archives, company info pages, documentation

#### JavaScript Content Interval (1 - 72 hours)

- **Purpose**: How often to recrawl JavaScript-rendered pages
- **Conservative**: 24 - 48 hours (slower updates)
- **Aggressive**: 6 - 12 hours (frequent updates)
- **Use Cases**: SPAs, dashboards, dynamic applications

#### Dynamic Content Interval (1 - 48 hours)

- **Purpose**: How often to recrawl frequently changing content
- **Conservative**: 12 - 24 hours (moderate updates)
- **Aggressive**: 3 - 6 hours (frequent updates)
- **Use Cases**: Social media, news feeds, real-time data

#### Smart Recrawl

- **Purpose**: Automatically adjust recrawl intervals based on content change patterns
- **Recommendation**: Enabled for most use cases
- **Impact**: Optimizes crawling efficiency and reduces unnecessary requests

### 🏷️ Metadata & Tagging

#### Custom Tags

- **Purpose**: Add custom metadata tags to crawled content
- **Format**: Comma-separated key:value pairs
- **Examples**: `priority:high, category:news, source:external`
- **Use Cases**: Content classification, filtering, analytics

#### Auto-tag Options

- **Link Depth**: Automatically tag content with distance from seed URLs
- **Domain**: Automatically tag content with source domain
- **Timestamp**: Automatically tag content with crawl timestamps
- **Impact**: Enables better content organization and analysis

### 👁️ OCR & Content Processing

#### Enable OCR Processing

- **Purpose**: Extract text from images and PDF documents
- **Performance Impact**: High (requires image processing)
- **Use Cases**: Document archives, image-heavy sites, PDF content

#### OCR Engine Options

- **Tesseract**: Free, good quality, slower processing
- **AWS Textract**: Paid, high quality, fast processing
- **Google Vision**: Paid, excellent quality, cloud-based

#### OCR Languages

- **Purpose**: Specify languages for text recognition
- **Format**: Comma-separated language codes
- **Examples**: `eng,spa,fra,deu,chi_sim`
- **Impact**: Better recognition for specified languages

## Performance Guidelines

### Resource Usage Estimation

|   Configuration | CPU Usage | Memory Usage | Network Usage | Speed   |
|  ---------------|-----------|--------------|---------------|-------  |
|   Conservative  | Low       | 200-500 MB   | Low           | 30-60 pages/min   |
|   Balanced      | Medium    | 500-1 GB     | Medium        | 60-120 pages/min   |
|   Aggressive    | High      | 1-2 GB       | High          | 120-300 pages/min   |
|   JS Enabled    | Very High | 1-3 GB       | Medium        | 20-80 pages/min   |

### Best Practices

#### Production Deployments

1. Start with **Conservative** preset
2. Monitor server response times and error rates
3. Gradually increase rate limits if servers handle load well
4. Enable conditional requests and compression
5. Use Redis or SQS for queue backend
6. Set up monitoring and alerting

#### Development and Testing

1. Use **Balanced** preset or **Memory** queue backend
2. Lower concurrent workers to reduce resource usage
3. Use shorter recrawl intervals for testing
4. Enable debug logging and monitoring

#### Respectful Crawling

1. Always use per-domain rate limiting
2. Respect robots.txt (implement separately)
3. Use reasonable delays between requests
4. Monitor target server health
5. Implement proper error handling and backoff

#### JavaScript-Heavy Sites

1. Use **SPA/JavaScript** preset as starting point
2. Configure appropriate wait selectors
3. Increase page timeouts for slow-loading content
4. Monitor browser memory usage
5. Consider using specific user agents

## Troubleshooting

### Common Issues

#### High Memory Usage

- **Cause**: Too many concurrent workers or browsers
- **Solution**: Reduce max workers and browsers, increase content size limits

#### Slow Crawling Performance

- **Cause**: Conservative rate limiting or overloaded target servers
- **Solution**: Increase rate limits gradually, check server response times

#### Failed JavaScript Rendering

- **Cause**: Missing wait selectors or page timeouts too short
- **Solution**: Add appropriate wait selectors, increase timeouts

#### Content Not Updating

- **Cause**: Conditional requests preventing re-downloads
- **Solution**: Adjust recrawl intervals or disable conditional requests for specific sites

#### Queue Overload

- **Cause**: Rate of URL discovery exceeds processing capacity
- **Solution**: Increase workers, improve rate limiting, optimize parsing

### Monitoring and Optimization

#### Key Metrics to Monitor

- **Queue Sizes**: Frontier, parsing, retry, dead letter queues
- **Success Rates**: Percentage of successful requests vs failures
- **Response Times**: Average response time from target servers
- **Resource Usage**: CPU, memory, network bandwidth
- **Content Quality**: Percentage of pages with successful content extraction

#### Performance Optimization

1. **Profile Target Sites**: Test different configurations on small samples
2. **Monitor Queue Health**: Ensure queues don't grow unbounded
3. **Optimize Rate Limits**: Find the sweet spot between speed and server load
4. **Use Conditional Requests**: Dramatically reduces bandwidth for unchanged content
5. **Implement Circuit Breakers**: Automatically back off from overloaded servers

## Integration with Existing Systems

The enhanced crawling system integrates seamlessly with:

- **Storage Systems**: S3, PostgreSQL, Elasticsearch
- **Analytics**: Built-in analytics dashboard
- **Monitoring**: Performance metrics and health checks
- **APIs**: RESTful API for programmatic control
- **Scheduling**: Cron-based and event-driven crawling

For additional support and advanced configuration options, refer to the technical documentation or contact the development team.
