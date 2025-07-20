"""
Spider Marketplace System
Handles spider discovery, installation, validation, and community features
"""

import os
import json
import shutil
import tempfile
import hashlib
import zipfile
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from urllib.parse import urlparse
import requests
import yaml

from ..db.models import Base
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base


@dataclass
class SpiderInfo:
    """Spider metadata information"""
    name: str
    version: str
    author: str
    description: str
    category: str
    tags: List[str]
    requirements: List[str]
    entry_point: str
    license: str
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MarketplaceSpider(Base):
    """Database model for marketplace spiders"""
    __tablename__ = "marketplace_spiders"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, index=True)
    version = Column(String(50))
    author = Column(String(255))
    description = Column(Text)
    category = Column(String(100))
    tags = Column(Text)  # JSON array as string
    requirements = Column(Text)  # JSON array as string
    entry_point = Column(String(500))
    license = Column(String(100))
    homepage = Column(String(500))
    repository = Column(String(500))
    documentation = Column(String(500))
    downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    package_url = Column(String(500))
    package_hash = Column(String(128))


class SpiderMarketplace:
    """Main spider marketplace manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/marketplace.yaml"
        self.spiders_dir = Path("business_intel_scraper/modules/marketplace_spiders")
        self.cache_dir = Path("data/marketplace_cache")
        self.temp_dir = Path("data/temp")
        
        # Create directories
        self.spiders_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load marketplace configuration"""
        default_config = {
            "marketplace": {
                "registry_url": "https://api.spider-registry.com",
                "local_registry": True,
                "auto_update": True,
                "verify_signatures": True,
                "allowed_categories": [
                    "business-intelligence",
                    "news-scraping", 
                    "social-media",
                    "e-commerce",
                    "job-boards",
                    "research",
                    "monitoring",
                    "osint"
                ],
                "validation": {
                    "max_package_size": "10MB",
                    "scan_timeout": 30,
                    "test_timeout": 60
                }
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    # Merge with defaults
                    default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            
        return default_config

    def search_spiders(self, query: str = "", category: str = "", 
                      tags: Optional[List[str]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for spiders in the marketplace"""
        # For now, return local spiders and sample marketplace data
        local_spiders = self._get_local_spiders()
        sample_spiders = self._get_sample_marketplace_spiders()
        
        all_spiders = local_spiders + sample_spiders
        
        # Apply filters
        if query:
            all_spiders = [s for s in all_spiders 
                          if query.lower() in s['name'].lower() 
                          or query.lower() in s['description'].lower()]
        
        if category:
            all_spiders = [s for s in all_spiders 
                          if s['category'].lower() == category.lower()]
        
        if tags:
            all_spiders = [s for s in all_spiders 
                          if any(tag in s.get('tags', []) for tag in tags)]
        
        return all_spiders[:limit]

    def _get_local_spiders(self) -> List[Dict[str, Any]]:
        """Get locally installed spiders"""
        local_spiders = []
        
        for spider_dir in self.spiders_dir.iterdir():
            if spider_dir.is_dir() and (spider_dir / "spider.yaml").exists():
                try:
                    with open(spider_dir / "spider.yaml", 'r') as f:
                        spider_info = yaml.safe_load(f)
                        spider_info['installed'] = True
                        spider_info['local_path'] = str(spider_dir)
                        local_spiders.append(spider_info)
                except Exception as e:
                    print(f"Error loading spider {spider_dir.name}: {e}")
        
        return local_spiders

    def _get_sample_marketplace_spiders(self) -> List[Dict[str, Any]]:
        """Get sample marketplace spiders for demonstration"""
        return [
            {
                "name": "linkedin-company-scraper",
                "version": "1.2.0",
                "author": "DataHunters",
                "description": "Extract company information and employee data from LinkedIn profiles",
                "category": "business-intelligence",
                "tags": ["linkedin", "companies", "employees", "social"],
                "requirements": ["selenium", "beautifulsoup4"],
                "entry_point": "linkedin_scraper.CompanySpider",
                "license": "MIT",
                "downloads": 1250,
                "rating": 4.6,
                "rating_count": 89,
                "verified": True,
                "installed": False,
                "package_url": "https://github.com/datahunters/linkedin-scraper/archive/v1.2.0.zip"
            },
            {
                "name": "indeed-job-scraper",
                "version": "2.1.1", 
                "author": "JobScrapers",
                "description": "Comprehensive job posting scraper for Indeed with salary and company details",
                "category": "job-boards",
                "tags": ["jobs", "indeed", "careers", "salaries"],
                "requirements": ["scrapy", "pandas"],
                "entry_point": "indeed_scraper.JobSpider",
                "license": "Apache-2.0",
                "downloads": 2100,
                "rating": 4.8,
                "rating_count": 156,
                "verified": True,
                "installed": False,
                "package_url": "https://github.com/jobscrapers/indeed-scraper/archive/v2.1.1.zip"
            },
            {
                "name": "twitter-sentiment-monitor",
                "version": "1.5.3",
                "author": "SentimentLab",
                "description": "Monitor Twitter for brand mentions and sentiment analysis",
                "category": "social-media",
                "tags": ["twitter", "sentiment", "monitoring", "brand"],
                "requirements": ["tweepy", "textblob", "pandas"],
                "entry_point": "twitter_monitor.SentimentSpider",
                "license": "GPL-3.0",
                "downloads": 890,
                "rating": 4.3,
                "rating_count": 67,
                "verified": False,
                "installed": False,
                "package_url": "https://github.com/sentimentlab/twitter-monitor/archive/v1.5.3.zip"
            },
            {
                "name": "ecommerce-price-tracker",
                "version": "3.0.2",
                "author": "PriceWatch",
                "description": "Track product prices across major e-commerce platforms",
                "category": "e-commerce",
                "tags": ["prices", "ecommerce", "tracking", "amazon", "ebay"],
                "requirements": ["scrapy", "price-parser", "notifications"],
                "entry_point": "price_tracker.PriceSpider",
                "license": "MIT",
                "downloads": 3400,
                "rating": 4.9,
                "rating_count": 234,
                "verified": True,
                "installed": False,
                "package_url": "https://github.com/pricewatch/ecommerce-tracker/archive/v3.0.2.zip"
            },
            {
                "name": "news-aggregator-pro",
                "version": "1.8.0",
                "author": "NewsHarvest",
                "description": "Advanced news aggregation from 500+ sources with categorization",
                "category": "news-scraping",
                "tags": ["news", "aggregation", "categorization", "rss"],
                "requirements": ["feedparser", "newspaper3k", "nlp-utils"],
                "entry_point": "news_aggregator.NewsSpider",
                "license": "Commercial",
                "downloads": 567,
                "rating": 4.7,
                "rating_count": 45,
                "verified": True,
                "installed": False,
                "package_url": "https://marketplace.spider-registry.com/packages/news-aggregator-pro-1.8.0.zip"
            }
        ]

    def install_spider(self, spider_name: str, version: str = "latest") -> Dict[str, Any]:
        """Install a spider from the marketplace"""
        try:
            # Find spider in marketplace
            spiders = self.search_spiders(query=spider_name)
            spider_info = None
            
            for spider in spiders:
                if spider['name'] == spider_name:
                    if version == "latest" or spider['version'] == version:
                        spider_info = spider
                        break
            
            if not spider_info:
                return {"success": False, "error": f"Spider {spider_name} not found"}
            
            if spider_info.get('installed'):
                return {"success": False, "error": f"Spider {spider_name} already installed"}
            
            # Download and install
            result = self._download_and_install_spider(spider_info)
            
            if result["success"]:
                # Update download count (in real implementation)
                pass
                
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Installation failed: {str(e)}"}

    def _download_and_install_spider(self, spider_info: Dict[str, Any]) -> Dict[str, Any]:
        """Download and install a spider package"""
        spider_name = spider_info['name']
        package_url = spider_info.get('package_url')
        
        if not package_url:
            return {"success": False, "error": "No package URL provided"}
        
        try:
            # Create spider directory
            spider_dir = self.spiders_dir / spider_name
            if spider_dir.exists():
                shutil.rmtree(spider_dir)
            spider_dir.mkdir(parents=True)
            
            # For demonstration, create a sample spider structure
            self._create_sample_spider_structure(spider_dir, spider_info)
            
            return {
                "success": True,
                "message": f"Spider {spider_name} installed successfully",
                "path": str(spider_dir)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Download failed: {str(e)}"}

    def _create_sample_spider_structure(self, spider_dir: Path, spider_info: Dict[str, Any]) -> None:
        """Create a sample spider structure for demonstration"""
        spider_name = spider_info['name']
        
        # Create spider.yaml metadata
        with open(spider_dir / "spider.yaml", 'w') as f:
            yaml.dump(spider_info, f, default_flow_style=False)
        
        # Create main spider file
        spider_code = f'''"""
{spider_info['description']}

Author: {spider_info['author']}
Version: {spider_info['version']}
License: {spider_info['license']}
"""

import scrapy
from typing import Dict, Any, Generator


class {spider_name.replace('-', '_').title()}Spider(scrapy.Spider):
    """
    {spider_info['description']}
    """
    
    name = "{spider_name}"
    custom_settings = {{
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'BusinessIntelScraper/{spider_info["version"]} (+https://github.com/your-org/scraper)'
    }}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger.info(f"Initialized {{self.name}} spider v{spider_info['version']}")
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate initial requests"""
        # Implementation would depend on the specific spider
        urls = self.get_start_urls()
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={{'spider_info': {spider_info}}}
            )
    
    def get_start_urls(self) -> list:
        """Get starting URLs for scraping"""
        # This would be customized per spider
        return ["https://example.com"]
    
    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        """Parse the response and extract data"""
        self.logger.info(f"Parsing {{response.url}}")
        
        # Sample data extraction (would be spider-specific)
        yield {{
            'url': response.url,
            'title': response.css('title::text').get(),
            'scraped_at': response.meta.get('download_time'),
            'spider': self.name,
            'version': '{spider_info["version"]}'
        }}
'''
        
        with open(spider_dir / f"{spider_name.replace('-', '_')}.py", 'w') as f:
            f.write(spider_code)
        
        # Create requirements file
        with open(spider_dir / "requirements.txt", 'w') as f:
            for req in spider_info.get('requirements', []):
                f.write(f"{req}\\n")
        
        # Create README
        readme_content = f"""# {spider_info['name']}

{spider_info['description']}

## Information
- **Author**: {spider_info['author']}
- **Version**: {spider_info['version']}
- **License**: {spider_info['license']}
- **Category**: {spider_info['category']}

## Tags
{', '.join(spider_info.get('tags', []))}

## Installation
This spider was installed from the marketplace.

## Usage
```python
from business_intel_scraper.modules.marketplace_spiders.{spider_name.replace('-', '_')} import {spider_name.replace('-', '_').title()}Spider

spider = {spider_name.replace('-', '_').title()}Spider()
# Configure and run spider
```

## Requirements
{chr(10).join(f"- {req}" for req in spider_info.get('requirements', []))}
"""
        
        with open(spider_dir / "README.md", 'w') as f:
            f.write(readme_content)

    def uninstall_spider(self, spider_name: str) -> Dict[str, Any]:
        """Uninstall a spider"""
        try:
            spider_dir = self.spiders_dir / spider_name
            
            if not spider_dir.exists():
                return {"success": False, "error": f"Spider {spider_name} not installed"}
            
            shutil.rmtree(spider_dir)
            
            return {
                "success": True,
                "message": f"Spider {spider_name} uninstalled successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Uninstallation failed: {str(e)}"}

    def list_installed_spiders(self) -> List[Dict[str, Any]]:
        """List all installed spiders"""
        return self._get_local_spiders()

    def get_spider_info(self, spider_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a spider"""
        spiders = self.search_spiders(query=spider_name)
        
        for spider in spiders:
            if spider['name'] == spider_name:
                return spider
        
        return None

    def validate_spider(self, spider_path: str) -> Dict[str, Any]:
        """Validate a spider package"""
        try:
            # Basic validation checks
            checks = {
                "has_metadata": False,
                "has_spider_class": False,
                "requirements_valid": False,
                "syntax_valid": False,
                "security_scan": False
            }
            
            spider_dir = Path(spider_path)
            
            # Check for metadata file
            if (spider_dir / "spider.yaml").exists():
                checks["has_metadata"] = True
            
            # Check for Python files with spider classes
            for py_file in spider_dir.glob("*.py"):
                with open(py_file, 'r') as f:
                    content = f.read()
                    if "scrapy.Spider" in content and "class " in content:
                        checks["has_spider_class"] = True
                        
                        # Basic syntax check
                        try:
                            compile(content, py_file.name, 'exec')
                            checks["syntax_valid"] = True
                        except SyntaxError:
                            pass
            
            # Check requirements
            if (spider_dir / "requirements.txt").exists():
                checks["requirements_valid"] = True
            
            # Security scan (basic)
            checks["security_scan"] = self._basic_security_scan(spider_dir)
            
            passed = sum(checks.values())
            total = len(checks)
            
            return {
                "valid": passed == total,
                "score": passed / total,
                "checks": checks,
                "issues": [check for check, passed in checks.items() if not passed]
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }

    def _basic_security_scan(self, spider_dir: Path) -> bool:
        """Perform basic security scanning"""
        dangerous_patterns = [
            "eval(",
            "exec(",
            "subprocess.",
            "__import__",
            "open(",
            "file(",
            "os.system",
            "os.popen"
        ]
        
        for py_file in spider_dir.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            return False
            except Exception:
                return False
        
        return True

    def publish_spider(self, spider_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a spider to the marketplace (local registry)"""
        try:
            # Validate spider first
            validation = self.validate_spider(spider_path)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Spider validation failed",
                    "validation": validation
                }
            
            # Create package
            spider_name = metadata["name"]
            version = metadata["version"]
            
            # For demonstration, just copy to marketplace directory
            marketplace_dir = self.cache_dir / "published" / f"{spider_name}-{version}"
            marketplace_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy spider files
            spider_source = Path(spider_path)
            for item in spider_source.iterdir():
                if item.is_file():
                    shutil.copy2(item, marketplace_dir)
                elif item.is_dir():
                    shutil.copytree(item, marketplace_dir / item.name, dirs_exist_ok=True)
            
            # Save metadata
            with open(marketplace_dir / "spider.yaml", 'w') as f:
                yaml.dump(metadata, f, default_flow_style=False)
            
            return {
                "success": True,
                "message": f"Spider {spider_name} v{version} published successfully",
                "package_path": str(marketplace_dir)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Publishing failed: {str(e)}"}

    def get_categories(self) -> List[str]:
        """Get available spider categories"""
        categories = self.config["marketplace"]["allowed_categories"]
        return list(categories) if categories else []

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        local_spiders = self._get_local_spiders()
        sample_spiders = self._get_sample_marketplace_spiders()
        
        return {
            "total_spiders": len(sample_spiders),
            "installed_spiders": len(local_spiders),
            "categories": len(self.get_categories()),
            "verified_spiders": len([s for s in sample_spiders if s.get('verified')]),
            "total_downloads": sum(s.get('downloads', 0) for s in sample_spiders)
        }
