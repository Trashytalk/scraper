# Automated Source Discovery System

The Automated Source Discovery System is a comprehensive solution for automatically finding, analyzing, and validating business intelligence sources. It implements intelligent discovery bots, confidence scoring, and seamless integration with the spider marketplace.

## 🎯 Overview

This system automatically discovers high-value business intelligence sources using multiple discovery strategies:

- **Domain Scanner Bot**: Crawls seed domains to find relevant sub-pages and linked resources
- **Search Engine Bot**: Uses Google Custom Search API to find business intelligence sources
- **Heuristic Analyzer Bot**: Analyzes page content to identify API endpoints, forms, and data structures

## ✅ Phase 1 Implementation Status

**COMPLETED - Core Automated Discovery**

- ✅ Multi-bot discovery system with specialized strategies
- ✅ Source registry with JSON persistence and deduplication
- ✅ Business intelligence specific confidence scoring algorithms
- ✅ Google Custom Search API integration framework
- ✅ Async orchestration and management layer
- ✅ Celery task integration for scheduled discovery
- ✅ CLI tools for discovery management
- ✅ Marketplace integration for automatic spider generation

## 🚀 Quick Start

### 1. Manual Discovery via CLI

```bash

# Run discovery on seed URLs

python -m business_intel_scraper.backend.cli.main discovery run \
    --urls https://www.usa.gov/business https://europa.eu/youreurope/business/

# List discovered sources

python -m business_intel_scraper.backend.cli.main discovery list \
    --min-confidence 0.7 --output-format table

# Validate candidate sources

python -m business_intel_scraper.backend.cli.main discovery validate --all

# Generate spiders from high-confidence sources

python -m business_intel_scraper.backend.cli.main discovery generate \
    --min-confidence 0.7 --template scrapy

```

### 2. Programmatic API

```python

import asyncio
from business_intel_scraper.backend.discovery import AutomatedDiscoveryManager

async def discover_sources():
    # Initialize discovery manager
    manager = AutomatedDiscoveryManager()

    # Run discovery on seed URLs
    seed_urls = [
        'https://www.usa.gov/business',
        'https://www.gov.uk/browse/business'
    ]

    sources = await manager.discover_sources(seed_urls)

    # Filter high-confidence sources
    high_confidence = [s for s in sources if s.confidence_score > 0.7]

    print(f"Found {len(high_confidence)} high-confidence sources")
    for source in high_confidence:
        print(f"  • {source.url} (confidence: {source.confidence_score:.2f})")

# Run discovery

asyncio.run(discover_sources())

```

### 3. Marketplace Integration

```python

from business_intel_scraper.backend.discovery import (
    AutomatedDiscoveryManager,
    MarketplaceIntegration
)

async def auto_generate_spiders():
    discovery_manager = AutomatedDiscoveryManager()
    marketplace = MarketplaceIntegration(discovery_manager)

    # Auto-generate spiders from validated sources
    generated_spiders = await marketplace.auto_generate_spiders(
        min_confidence=0.7,
        max_spiders=5
    )

    print(f"Generated {len(generated_spiders)} marketplace spiders")

```

## 🛠️ System Architecture

### Core Components

```
AutomatedDiscoveryManager
├── SourceDiscoveryBot (Base Class)
│   ├── DomainScannerBot     # Crawl domains for relevant pages
│   ├── SearchEngineBot     # Google Custom Search integration
│   └── HeuristicAnalyzerBot # Content analysis & API discovery
├── SourceRegistry          # Persistent storage & deduplication
└── MarketplaceIntegration  # Auto-generate spiders

```

### Discovery Bot Strategies

#### 1. Domain Scanner Bot

- Crawls seed domains to discover sub-pages
- Identifies high-value business intelligence sections
- Follows internal links intelligently
- Respects robots.txt and rate limits

#### 2. Search Engine Bot

- Uses Google Custom Search API
- Searches for business intelligence specific terms
- Filters results by domain authority and relevance
- Supports configurable search queries

#### 3. Heuristic Analyzer Bot

- Analyzes page content for business intelligence indicators
- Detects API endpoints and data feeds
- Identifies forms and interactive elements
- Scores pages based on BI relevance

### Confidence Scoring Algorithm

The system uses a sophisticated confidence scoring algorithm:

```python

def calculate_confidence_score(source):
    score = 0.0

    # Content quality indicators (40% weight)
    if has_structured_data(source): score += 0.2
    if has_business_keywords(source): score += 0.1
    if has_contact_info(source): score += 0.1

    # Technical indicators (30% weight)
    if has_api_endpoints(source): score += 0.15
    if is_mobile_friendly(source): score += 0.1
    if has_ssl(source): score += 0.05

    # Authority indicators (30% weight)
    if is_government_domain(source): score += 0.15
    if has_high_page_rank(source): score += 0.1
    if has_recent_updates(source): score += 0.05

    return min(score, 1.0)

```

## 📋 Scheduled Tasks

The system includes Celery tasks for automated operation:

### Task Schedule

- **Source Discovery**: Every 6 hours - Discover new sources from seed URLs
- **Source Validation**: Every 2 hours - Validate candidate sources
- **Spider Generation**: Daily - Generate marketplace spiders from validated sources
- **Spider Execution**: Every 12 hours - Run all configured spiders

### Task Configuration

```python

# In celery_config.py

beat_schedule = {
    'automated-source-discovery': {
        'task': 'business_intel_scraper.backend.workers.tasks.scheduled_source_discovery',
        'schedule': 6 * 60 * 60,  # Every 6 hours
    },
    'validate-discovered-sources': {
        'task': 'business_intel_scraper.backend.workers.tasks.validate_discovered_sources',
        'schedule': 2 * 60 * 60,  # Every 2 hours
    },
    'generate-marketplace-spiders': {
        'task': 'business_intel_scraper.backend.workers.tasks.generate_marketplace_spiders',
        'schedule': 24 * 60 * 60,  # Daily
    }
}

```

## 🔧 Configuration

### Discovery Bot Configuration

```python

config = {
    'bots': {
        'domain_scanner': {
            'max_depth': 3,           # Maximum crawl depth
            'max_pages': 50,          # Maximum pages per domain
            'respect_robots': True,   # Obey robots.txt
            'delay': 2               # Delay between requests
        },
        'search_engine': {
            'api_key': 'your_api_key',        # Google Custom Search API key
            'search_engine_id': 'your_cse_id', # Custom Search Engine ID
            'max_results': 20,               # Maximum results per query
            'queries': [                     # Custom search queries
                'business intelligence site:gov',
                'company directory site:gov',
                'business registration database'
            ]
        },
        'heuristic_analyzer': {
            'min_confidence': 0.3,    # Minimum confidence to save
            'analyze_apis': True,     # Detect API endpoints
            'analyze_forms': True,    # Analyze form structures
            'business_keywords': [    # BI-specific keywords
                'business', 'company', 'corporate',
                'directory', 'database', 'registry'
            ]
        }
    }
}

```

### Environment Variables

```bash

# Google Custom Search API (optional)

GOOGLE_CUSTOM_SEARCH_API_KEY=your_api_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id

# Discovery settings

DISCOVERY_DATA_DIR=/path/to/discovery/data
DISCOVERY_MAX_CONCURRENT_REQUESTS=10
DISCOVERY_DEFAULT_TIMEOUT=30

```

## 📊 Data Models

### DiscoveredSource

```python

@dataclass
class DiscoveredSource:
    url: str                    # Source URL
    domain: str                # Domain name
    title: Optional[str]       # Page title
    description: Optional[str] # Meta description
    source_type: str           # Type: government_data, business_directory, etc.
    confidence_score: float    # Confidence score (0.0-1.0)
    discovered_at: datetime    # Discovery timestamp
    discovered_by: str         # Discovery bot name
    status: str               # Status: candidate, validated, failed
    metadata: Dict[str, Any]  # Additional metadata

    # Computed properties
    @property
    def is_high_confidence(self) -> bool:
        return self.confidence_score > 0.7

    @property
    def is_government_source(self) -> bool:
        return 'gov' in self.domain or self.source_type == 'government_data'

```

## 🎛️ Management Commands

### Discovery Management

```bash

# Run manual discovery

python -m business_intel_scraper.backend.cli.main discovery run \
    --urls https://example.com \
    --config config.json \
    --output discovered_sources.json

# List and filter sources

python -m business_intel_scraper.backend.cli.main discovery list \
    --status validated \
    --min-confidence 0.8 \
    --output-format json

# Validate sources

python -m business_intel_scraper.backend.cli.main discovery validate \
    --urls https://example1.com https://example2.com

# Generate spiders

python -m business_intel_scraper.backend.cli.main discovery generate \
    --min-confidence 0.7 \
    --template scrapy \  # or 'playwright', 'requests'

```

### Celery Task Management

```bash

# Start Celery worker

celery -A business_intel_scraper.backend.workers.tasks worker --loglevel=info

# Start Celery beat scheduler

celery -A business_intel_scraper.backend.workers.tasks beat --loglevel=info

# Monitor tasks

celery -A business_intel_scraper.backend.workers.tasks flower

```

## 🔍 Example Discovery Output

```json

{
  "url": "https://www.usa.gov/business-directory",
  "domain": "usa.gov",
  "title": "Business Directory - USA.gov",
  "description": "Find business resources and directories",
  "source_type": "business_directory",
  "confidence_score": 0.85,
  "discovered_at": "2024-01-15T10:30:00Z",
  "discovered_by": "domain_scanner_bot",
  "status": "validated",
  "metadata": {
    "api_endpoints": [
      "/api/businesses/search",
      "/api/directories/list"
    ],
    "forms": [
      {"action": "/search", "method": "GET", "fields": ["query", "location"]}
    ],
    "business_indicators": {
      "has_contact_info": true,
      "has_business_listings": true,
      "has_search_functionality": true
    },
    "technical_indicators": {
      "ssl_enabled": true,
      "mobile_friendly": true,
      "load_time_ms": 1200
    }
  }
}

```

## 🔮 Future Phases

### Phase 2: DOM Change Detection (Planned)

- Monitor discovered sources for structural changes
- Automatically update spider extraction logic
- Alert system for broken spiders due to site changes
- Version control for spider templates

### Phase 3: Advanced Discovery Features (Planned)

- Federated source sharing between scraper instances
- Deep web discovery capabilities (tor integration)
- Machine learning enhanced source analysis
- Collaborative filtering for source recommendations

## 🤝 Contributing

The automated discovery system is designed to be extensible:

### Adding New Discovery Bots

```python

class CustomDiscoveryBot(SourceDiscoveryBot):
    """Custom discovery bot implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "custom_bot"

    async def discover(self, seed_urls: List[str]) -> List[DiscoveredSource]:
        """Implement custom discovery logic"""
        sources = []
        # Your discovery logic here
        return sources

    def calculate_confidence_score(self, url: str, content: str, metadata: Dict) -> float:
        """Implement custom confidence scoring"""
        # Your scoring logic here
        return 0.5

```

### Extending Source Types

Add new source types to the system:

```python

# In automated_discovery.py

SOURCE_TYPES = {
    'government_data': ['gov', 'government', 'official'],
    'business_directory': ['directory', 'listing', 'business'],
    'news_site': ['news', 'media', 'press'],
    'custom_type': ['custom', 'keywords']  # Add your type
}

```

## 📈 Performance Metrics

The system tracks key performance metrics:

- **Discovery Rate**: Sources discovered per hour
- **Confidence Distribution**: Distribution of confidence scores
- **Validation Success Rate**: Percentage of sources that validate
- **Spider Generation Rate**: Successful spiders generated
- **Coverage**: Unique domains and source types discovered

Monitor these metrics through the integrated dashboard or via API endpoints.

## 🛡️ Security & Compliance

- Respects robots.txt files
- Implements rate limiting to avoid overwhelming target sites
- Uses appropriate User-Agent headers
- Supports proxy rotation for large-scale discovery
- Validates SSL certificates and secure connections
- Logs all discovery activities for audit purposes


---


**Status**: Phase 1 Implementation Complete ✅
**Next**: Phase 2 DOM Change Detection
**Version**: 1.0.0
