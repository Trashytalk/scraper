# Spider Marketplace Guide

The Spider Marketplace is a community-driven platform that allows users to discover, install, share, and manage custom web scraping spiders. It provides a centralized repository for business intelligence scrapers with features like ratings, validation, and easy installation.

## 🎯 Overview

### What is the Spider Marketplace?

The Spider Marketplace transforms the Business Intelligence Scraper from a single-purpose tool into an extensible platform. Users can:

- **Discover** spiders created by the community
- **Install** spiders with one click
- **Share** their own spider implementations
- **Rate and review** spider effectiveness
- **Validate** spider security and quality
- **Manage** installed spiders through a web interface

### Key Features

#### 🔍 **Spider Discovery**

- Search by keywords, categories, and tags
- Featured and trending spiders
- Detailed spider information and documentation
- Community ratings and reviews

#### 📦 **One-Click Installation**

- Automatic dependency management
- Validation and security scanning
- Version management
- Local installation tracking

#### 🛡️ **Security & Quality**

- Automated security scanning
- Code validation
- Signature verification
- Sandboxed testing (planned)

#### 🌐 **Community Features**

- User ratings and reviews
- Spider marketplace statistics
- Author profiles and reputation
- Community moderation

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Virtual environment set up
- Node.js 16+ (for web interface)
- Business Intelligence Scraper installed

### Quick Start

1. **Access via Web Interface**:
   ```bash
   # Start the frontend (if not running)
   cd business_intel_scraper/frontend
   npm run dev

   # Visit http://localhost:3000/marketplace
   ```

2. **Access via API**:
   ```bash
   # Start the backend (if not running)
   cd business_intel_scraper
   uvicorn backend.api.main:app --reload

   # API available at http://localhost:8000/marketplace/*
   ```

3. **Access via CLI**:
   ```bash
   source .venv/bin/activate
   python -m business_intel_scraper.backend.marketplace.cli search
   ```

### Demo

Run the marketplace demo to see it in action:

```bash

python demo_marketplace.py

```

## 🎮 Usage Guide

### Web Interface

#### Browsing Spiders

1. **Navigate** to http://localhost:3000/marketplace
2. **Search** using the search bar or filter by category
3. **View Details** by clicking on any spider card
4. **Switch Views** between grid and list layouts

#### Installing Spiders

1. **Find** the spider you want to install
2. **Click** the "Install" button
3. **Wait** for installation to complete
4. **Check** the "Installed" tab to see your spiders

#### Managing Installed Spiders

1. **Go to** the "Installed" tab
2. **View** all your installed spiders
3. **Uninstall** spiders you no longer need
4. **Update** spiders when new versions are available

### API Usage

#### Search Spiders

```bash

curl "http://localhost:8000/marketplace/search?query=linkedin&category=business-intelligence&limit=10"

```

#### Get Spider Information

```bash

curl "http://localhost:8000/marketplace/spider/linkedin-company-scraper"

```

#### Install a Spider

```bash

curl -X POST "http://localhost:8000/marketplace/install" \
  -H "Content-Type: application/json" \
  -d '{"name": "linkedin-company-scraper", "version": "latest"}'

```

#### List Installed Spiders

```bash

curl "http://localhost:8000/marketplace/installed"

```

### CLI Usage

#### Search for Spiders

```bash

# Basic search

python -m business_intel_scraper.backend.marketplace.cli search

# Search with filters

python -m business_intel_scraper.backend.marketplace.cli search \
  --query "linkedin" \
  --category "business-intelligence" \
  --limit 5

```

#### Install a Spider

```bash

python -m business_intel_scraper.backend.marketplace.cli install linkedin-company-scraper

```

#### List Installed Spiders

```bash

python -m business_intel_scraper.backend.marketplace.cli list-installed

```

#### Get Spider Information

```bash

python -m business_intel_scraper.backend.marketplace.cli info linkedin-company-scraper

```

## 🛠️ Development Guide

### Creating a New Spider

#### 1. Create Spider Template

```bash

python -m business_intel_scraper.backend.marketplace.cli create-template my-spider ./my-spider

```

This creates:

```
my-spider/
├── spider.yaml          # Metadata
├── my_spider.py         # Main spider code
├── requirements.txt     # Dependencies
└── README.md           # Documentation

```

#### 2. Customize Your Spider

**Edit `spider.yaml`**:

```yaml

name: my-custom-spider
version: 1.0.0
author: Your Name
description: Description of what your spider does
category: business-intelligence
tags: [company-data, scraping]
requirements: [scrapy, requests]
entry_point: my_spider.MySpiderClass
license: MIT

```

**Edit `my_spider.py`**:

```python

import scrapy

class MySpiderClass(scrapy.Spider):
    name = "my-custom-spider"

    def start_requests(self):
        # Your scraping logic here
        pass

    def parse(self, response):
        # Your parsing logic here
        yield {"data": "extracted_data"}

```

#### 3. Test Your Spider

```bash

# Validate spider structure

python -m business_intel_scraper.backend.marketplace.cli validate ./my-spider

# Test locally

cd my-spider
scrapy crawl my-custom-spider

```

#### 4. Publish Your Spider

```bash

python -m business_intel_scraper.backend.marketplace.cli publish ./my-spider \
  --name "my-custom-spider" \
  --version "1.0.0" \
  --author "Your Name" \
  --description "My custom spider" \
  --category "business-intelligence"

```

### Spider Structure Requirements

#### Required Files

1. **`spider.yaml`** - Metadata file
2. **`requirements.txt`** - Python dependencies
3. **Main Python file** - Spider implementation
4. **`README.md`** - Documentation (recommended)

#### Metadata Schema

```yaml

# Required fields

name: string              # Unique spider name
version: string           # Semantic version (1.0.0)
author: string            # Author name
description: string       # What the spider does
category: string          # From allowed categories
entry_point: string       # module.ClassName

# Optional fields

tags: [string]            # Search tags
requirements: [string]    # Python packages
license: string           # License type
homepage: string          # Project homepage
repository: string        # Source code repo
documentation: string     # Docs URL

```

#### Spider Categories

Available categories:
- `business-intelligence`
- `news-scraping`
- `social-media`
- `e-commerce`
- `job-boards`
- `research`
- `monitoring`
- `osint`
- `competitive-analysis`
- `market-research`
- `financial-data`
- `real-estate`
- `healthcare`
- `legal`
- `education`

### Best Practices

#### Spider Development

1. **Follow Scrapy conventions**
2. **Handle errors gracefully**
3. **Respect rate limits**
4. **Use proper user agents**
5. **Document your code**
6. **Include tests**
7. **Follow ethical scraping practices**

#### Security Guidelines

1. **No eval() or exec() statements**
2. **No file system access outside project**
3. **No network access to internal services**
4. **Validate all inputs**
5. **Use safe parsing libraries**

#### Quality Standards

1. **Comprehensive error handling**
2. **Proper logging**
3. **Configurable settings**
4. **Clean, readable code**
5. **Documentation**
6. **Version control**

## 🔧 Configuration

### Marketplace Configuration

Edit `config/marketplace.yaml`:

```yaml

marketplace:
  registry_url: "https://api.spider-registry.com"
  local_registry: true
  auto_update: true

  validation:
    max_package_size: "10MB"
    scan_timeout: 30
    test_timeout: 60

  security:
    scan_for_malware: true
    check_signatures: true

```

### Environment Variables

```bash

# Optional marketplace configuration

MARKETPLACE_REGISTRY_URL=https://api.spider-registry.com
MARKETPLACE_LOCAL_REGISTRY=true
MARKETPLACE_AUTO_UPDATE=true

```

## 📊 Marketplace Statistics

The marketplace tracks various metrics:

- **Total spiders available**
- **Number of installed spiders**
- **Download counts**
- **Rating distributions**
- **Category popularity**
- **Author statistics**

Access stats via:
- Web interface: http://localhost:3000/marketplace
- API: `GET /marketplace/stats`
- CLI: `python -m business_intel_scraper.backend.marketplace.cli stats`

## 🔒 Security

### Validation Process

Every spider goes through validation:

1. **Structure check** - Required files present
2. **Syntax validation** - Python code compiles
3. **Security scan** - No dangerous patterns
4. **Dependency check** - Valid requirements
5. **Size limits** - Package not too large

### Security Features

- **Sandboxed execution** (planned)
- **Code signing** (planned)
- **Reputation system**
- **Community reporting**
- **Automated scanning**

### Safe Usage Tips

1. **Review spider code** before installation
2. **Check author reputation**
3. **Read community reviews**
4. **Start with verified spiders**
5. **Monitor spider behavior**

## 🤝 Community

### Contributing

1. **Create quality spiders**
2. **Write good documentation**
3. **Help others with reviews**
4. **Report security issues**
5. **Improve the platform**

### Support

- **Documentation**: This guide and API docs
- **Issues**: GitHub repository
- **Community**: Discord/Slack (planned)
- **Security**: security@yourorg.com

## 🚀 Roadmap

### Current Features (v1.0)

- ✅ Spider discovery and search
- ✅ One-click installation
- ✅ Web interface
- ✅ API endpoints
- ✅ CLI tools
- ✅ Basic validation
- ✅ Local registry

### Upcoming Features (v2.0)

- 🔄 Remote registry support
- 🔄 User authentication
- 🔄 Advanced security scanning
- 🔄 Automated testing
- 🔄 Spider versioning
- 🔄 Community features

### Future Plans (v3.0)

- 📋 Marketplace analytics
- 📋 AI-powered recommendations
- 📋 Collaboration tools
- 📋 Commercial spider support
- 📋 Cloud deployment
- 📋 Mobile app

## 📚 Examples

### Example Spider: LinkedIn Company Scraper

```python

"""
LinkedIn Company Scraper
Extracts company information from LinkedIn company pages
"""

import scrapy
from typing import Dict, Any, Generator

class LinkedinCompanySpider(scrapy.Spider):
    name = "linkedin-company-scraper"
    allowed_domains = ["linkedin.com"]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'BusinessIntelScraper/1.0 (+https://your-site.com)'
    }

    def start_requests(self):
        # Company URLs to scrape
        companies = getattr(self, 'companies', '').split(',')

        for company in companies:
            if company.strip():
                url = f"https://www.linkedin.com/company/{company.strip()}"
                yield scrapy.Request(url, self.parse)

    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        yield {
            'company_name': response.css('h1.text-heading-xlarge::text').get(),
            'industry': response.css('.company-industries::text').get(),
            'headquarters': response.css('.company-location::text').get(),
            'employee_count': response.css('.company-size::text').get(),
            'description': response.css('.company-description::text').get(),
            'website': response.css('.company-website::attr(href)').get(),
            'url': response.url,
            'scraped_at': response.meta.get('download_time')
        }

```

### Example Usage

```bash

# Install the spider

python -m business_intel_scraper.backend.marketplace.cli install linkedin-company-scraper

# Use the spider

scrapy crawl linkedin-company-scraper -a companies="apple,microsoft,google"

```

This comprehensive guide provides everything needed to understand, use, and contribute to the Spider Marketplace ecosystem.
