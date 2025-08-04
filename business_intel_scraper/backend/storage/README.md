# Storage/Indexing Layer

The Storage/Indexing Layer is a comprehensive data management system that provides advanced storage, indexing, and data lineage capabilities for the Business Intelligence Scraper.

## Architecture Overview

The Storage/Indexing Layer consists of three main components:

### 1. Raw Data Store

- **Backend**: S3/MinIO object storage with hierarchical key structure
- **Compression**: Configurable compression algorithms (gzip, bzip2, lz4)
- **Deduplication**: Content-based deduplication with similarity hashing
- **Metadata**: Rich metadata storage including HTTP headers, processing status, and quality scores

### 2. Structured Database

- **Backend**: PostgreSQL with comprehensive relational models
- **Models**: 7+ specialized tables for entities, relationships, and metrics
- **Indexing**: Optimized indexes for fast querying and analytics
- **Quality**: Built-in data quality scoring and validation

### 3. Search/Indexing Engine

- **Backend**: Elasticsearch for full-text search and analytics
- **Indexes**: Separate indexes for raw data, entities, and relationships
- **Real-time**: Real-time indexing with configurable refresh intervals

## Data Models

### Raw Data Model (`raw_data`)

Stores raw crawled content with comprehensive metadata:

- **Content**: Hash-based storage keys, compression, size tracking
- **Source**: URLs, domains, referrers, HTTP metadata
- **Processing**: Status tracking, extraction results, error handling
- **Quality**: Content quality scores, duplicate detection, validation

### Structured Entity Model (`structured_entities`)

Stores extracted business entities:

- **Identity**: Canonical names, display names, entity types
- **Classification**: Categories, confidence scores, importance ratings
- **Content**: Structured data, contact info, location data
- **Lifecycle**: Creation, updates, verification status

### Relationship Model (`entity_relationships`)

Captures relationships between entities:

- **Connection**: Source/target entities, relationship types
- **Strength**: Confidence scores, relationship strength
- **Evidence**: Supporting text, extraction sources
- **Temporal**: Start/end dates, verification status

### Mapping Model (`raw_to_structured_mapping`)

Links raw data to extracted entities:

- **Traceability**: Raw data ID to entity ID mapping
- **Extraction**: Method, confidence, field contributions
- **Quality**: Field-level quality scores, validation results

### Quality Metrics Model (`data_quality_metrics`)

Tracks data quality across the system:

- **Scope**: Entity-level, dataset-level, system-level metrics
- **Measurements**: Completeness, accuracy, consistency scores
- **Trends**: Historical tracking, trend analysis
- **Thresholds**: Configurable quality gates and alerting

### Lineage Model (`data_lineage`)

Provides complete data provenance:

- **Path**: Source to target transformation paths
- **Dependencies**: Direct and transitive dependencies
- **Transformations**: Processing steps, parameters, versions
- **Impact**: Downstream impact analysis

### Storage Metrics Model (`storage_metrics`)

System-wide storage performance metrics:

- **Usage**: Storage utilization, growth rates
- **Performance**: Query times, throughput metrics
- **Alerts**: Threshold-based alerting system

## Core Components

### AdvancedStorageManager

The central storage orchestrator:

```python

from business_intel_scraper.backend.storage import AdvancedStorageManager

storage = AdvancedStorageManager()

# Store raw data

raw_record = await storage.store_raw_data(
    content="<html>...</html>",
    source_url="https://example.com",
    job_id="job_123",
    metadata={"spider": "company_spider"}
)

# Store structured entity

entity = await storage.store_structured_entity(
    entity_type="company",
    canonical_name="Example Corp",
    structured_data={
        "name": "Example Corp",
        "industry": "Technology",
        "employees": 500
    },
    extractor_name="company_extractor",
    extractor_version="1.0.0"
)

# Create mapping

mapping = await storage.create_raw_to_structured_mapping(
    raw_id=raw_record.raw_id,
    entity_id=entity.entity_id,
    extraction_method="html_parsing",
    extraction_confidence=0.95
)

```

### DataLineageTracker

Comprehensive lineage tracking:

```python

from business_intel_scraper.backend.storage import DataLineageTracker

lineage = DataLineageTracker(storage)

# Track transformation

await lineage.track_transformation(
    source_type="raw_data",
    source_id=raw_record.raw_id,
    target_type="entity",
    target_id=entity.entity_id,
    transformation_type="extraction",
    transformation_name="company_extractor",
    transformation_params={"confidence_threshold": 0.8}
)

# Get upstream lineage

upstream = await lineage.get_upstream_lineage(
    target_type="entity",
    target_id=entity.entity_id
)

# Get downstream impact

impact = await lineage.get_downstream_impact(
    source_type="raw_data",
    source_id=raw_record.raw_id
)

```

## API Endpoints

The storage layer exposes a comprehensive REST API:

### Raw Data Operations

- `POST /api/v1/storage/raw-data` - Store raw data
- `GET /api/v1/storage/raw-data/{raw_id}` - Get raw data
- `PUT /api/v1/storage/raw-data/{raw_id}` - Update raw data
- `DELETE /api/v1/storage/raw-data/{raw_id}` - Delete raw data
- `POST /api/v1/storage/raw-data/search` - Search raw data

### Entity Operations

- `POST /api/v1/storage/entities` - Create entity
- `GET /api/v1/storage/entities/{entity_id}` - Get entity
- `PUT /api/v1/storage/entities/{entity_id}` - Update entity
- `DELETE /api/v1/storage/entities/{entity_id}` - Delete entity
- `POST /api/v1/storage/entities/search` - Search entities

### Relationship Operations

- `POST /api/v1/storage/relationships` - Create relationship
- `GET /api/v1/storage/relationships/{rel_id}` - Get relationship
- `GET /api/v1/storage/entities/{entity_id}/relationships` - Get entity relationships

### Data Quality & Lineage

- `GET /api/v1/storage/quality/metrics` - Get quality metrics
- `POST /api/v1/storage/quality/calculate` - Calculate quality scores
- `GET /api/v1/storage/lineage/{entity_id}` - Get data lineage
- `GET /api/v1/storage/provenance/{entity_id}` - Get data provenance

### Export Operations

- `GET /api/v1/storage/export/entities` - Export entities (CSV/JSON/Parquet)
- `GET /api/v1/storage/export/raw-data` - Export raw data
- `GET /api/v1/storage/metrics` - Get storage metrics

## Configuration

The storage layer is configured via environment variables or `storage_config.py`:

```python

# Raw Data Storage

STORAGE_RAW_BACKEND=s3
STORAGE_RAW_BUCKET=business-intel-raw-data
STORAGE_RAW_ACCESS_KEY=your_access_key
STORAGE_RAW_SECRET_KEY=your_secret_key

# Database

DATABASE_URL=postgresql://user:pass@localhost:5432/business_intel
STORAGE_DB_POOL_SIZE=10

# Elasticsearch

ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=password

# Features

STORAGE_ENABLE_CACHING=true
STORAGE_ENABLE_QUALITY_CHECKS=true
STORAGE_ENABLE_LINEAGE=true
STORAGE_ENABLE_COMPRESSION=true
STORAGE_ENABLE_DEDUPLICATION=true

# Performance

STORAGE_MAX_CONCURRENT_OPS=10
STORAGE_BATCH_SIZE=100
STORAGE_REQUEST_TIMEOUT=60

```

## CLI Commands

The storage layer includes comprehensive CLI commands:

### Initialize Storage

```bash

python -m business_intel_scraper.cli_enhanced storage init --create-indexes --create-buckets --test-connections

```

### Check Status

```bash

python -m business_intel_scraper.cli_enhanced storage status

```

### Cleanup Old Data

```bash

python -m business_intel_scraper.cli_enhanced storage cleanup --older-than-days 30

```

### Reindex Search Data

```bash

python -m business_intel_scraper.cli_enhanced storage reindex --entity-type company

```

### Show Data Lineage

```bash

python -m business_intel_scraper.cli_enhanced storage lineage entity_123 --max-depth 3 --direction both

```

### Generate Quality Report

```bash

python -m business_intel_scraper.cli_enhanced storage quality-report --entity-type company --format table

```

## Database Migration

To set up the storage layer database schema:

```bash

# Create migration

alembic revision --autogenerate -m "Add storage layer"

# Apply migration

alembic upgrade head

```

The storage layer includes a comprehensive migration file that creates all necessary tables with proper indexes and constraints.

## Performance Optimization

### Caching Strategy

- **Redis**: Configurable Redis-based caching
- **TTL**: Configurable cache expiration times
- **Invalidation**: Smart cache invalidation on updates

### Indexing Strategy

- **Database**: Composite indexes on frequently queried columns
- **Elasticsearch**: Full-text search with custom analyzers
- **Partitioning**: Time-based partitioning for large tables

### Connection Pooling

- **Database**: SQLAlchemy connection pooling
- **Storage**: Async client connection pooling
- **Elasticsearch**: Connection pooling with health checks

### Batch Operations

- **Bulk Inserts**: Optimized bulk insertion operations
- **Streaming**: Memory-efficient streaming for large datasets
- **Parallel**: Configurable parallel processing

## Monitoring & Alerting

### Metrics Collection

- **Storage Usage**: Disk usage, growth trends
- **Query Performance**: Response times, throughput
- **Quality Metrics**: Data quality scores, trend analysis
- **Error Rates**: Processing errors, system health

### Alerting

- **Thresholds**: Configurable quality and performance thresholds
- **Notifications**: Integration with notification systems
- **Health Checks**: Comprehensive system health monitoring

## Data Quality Framework

### Quality Dimensions

- **Completeness**: Missing field detection
- **Accuracy**: Data validation and verification
- **Consistency**: Cross-reference validation
- **Timeliness**: Data freshness tracking
- **Uniqueness**: Duplicate detection and deduplication

### Quality Rules

- **Field-level**: Individual field validation rules
- **Entity-level**: Cross-field validation rules
- **Dataset-level**: Statistical quality checks
- **System-level**: Overall system health metrics

### Quality Reporting

- **Dashboards**: Real-time quality dashboards
- **Reports**: Periodic quality reports
- **Alerts**: Quality threshold violations
- **Trends**: Historical quality trend analysis

## Integration Examples

### Pipeline Integration

```python

# In your scraping pipeline

from business_intel_scraper.backend.storage import AdvancedStorageManager

async def process_crawled_page(content, url, job_id):
    storage = AdvancedStorageManager()

    # Store raw data
    raw_record = await storage.store_raw_data(
        content=content,
        source_url=url,
        job_id=job_id,
        http_status=200,
        content_type="text/html"
    )

    # Extract entities
    entities = extract_entities(content)

    for entity_data in entities:
        # Store entity
        entity = await storage.store_structured_entity(
            entity_type="company",
            canonical_name=entity_data["name"],
            structured_data=entity_data,
            extractor_name="company_extractor"
        )

        # Create mapping
        await storage.create_raw_to_structured_mapping(
            raw_id=raw_record.raw_id,
            entity_id=entity.entity_id,
            extraction_method="html_parsing",
            extraction_confidence=entity_data["confidence"]
        )

```

### Analytics Integration

```python

# Export for analytics

entities_df = await storage.export_entities(
    format="dataframe",
    filters={"entity_type": "company", "is_active": True},
    include_relationships=True
)

# Quality analysis

quality_metrics = await storage.get_quality_metrics_summary(
    scope_type="entity_type",
    scope_id="company"
)

```

## Best Practices

### Data Modeling

- Use consistent entity identification schemes
- Implement proper data validation at ingestion
- Design for scalability with proper indexing
- Plan for data lifecycle management

### Performance

- Use batch operations for bulk data
- Implement proper caching strategies
- Monitor and optimize query performance
- Use appropriate data types and constraints

### Quality

- Implement quality checks at ingestion time
- Set up automated quality monitoring
- Use data lineage for impact analysis
- Regularly validate and clean data

### Security

- Implement proper access controls
- Use encryption for sensitive data
- Audit data access and modifications
- Follow data privacy regulations

## Troubleshooting

### Common Issues

**Connection Errors**
- Check database/storage/Elasticsearch connectivity
- Verify credentials and network access
- Check service health and logs

**Performance Issues**
- Monitor query execution plans
- Check index usage and optimization
- Review connection pool settings
- Analyze cache hit rates

**Data Quality Issues**
- Review quality metrics and reports
- Check extraction and validation rules
- Analyze data lineage for root causes
- Implement additional validation rules

**Storage Issues**
- Monitor disk usage and growth
- Check backup and retention policies
- Review compression and deduplication
- Analyze storage access patterns
