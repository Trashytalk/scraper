"""
Advanced Crawling/Discovery Layer Implementation

This module implements the detailed best-practice pipeline for business intelligence
crawling with seed sources, recursive crawling, domain scoping, and metadata extraction.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, AsyncGenerator, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from urllib.robotparser import RobotFileParser
import json
import pickle
from pathlib import Path
import re
from collections import defaultdict, deque
import time

# Graceful imports for optional dependencies
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Mock objects for when SQLAlchemy is not available
    Base = object
    Column = String = Text = DateTime = Integer = Float = JSON = None
    create_engine = sessionmaker = Session = None

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    from sqlalchemy import create_engine, Column, String, DateTime, Integer, Float, Text, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = None

# Import our existing classifier
from ..discovery.classifier import AdaptiveLinkClassifier

logger = logging.getLogger(__name__)


@dataclass
class DiscoveredPage:
    """Container for discovered page metadata"""
    url: str
    parent_url: Optional[str] = None
    anchor_text: Optional[str] = None
    discovery_timestamp: datetime = field(default_factory=datetime.utcnow)
    page_hash: Optional[str] = None
    source_type: str = "unknown"
    depth: int = 0
    classification_score: float = 0.0
    classification_type: str = "unknown"
    crawl_status: str = "discovered"  # discovered, crawled, failed, skipped
    metadata: Dict = field(default_factory=dict)


@dataclass
class SeedSource:
    """Configuration for seed sources"""
    name: str
    urls: List[str]
    source_type: str  # 'business_registry', 'directory', 'industry_site', 'forum'
    priority: int = 5
    crawl_config: Dict = field(default_factory=dict)
    update_frequency: str = "daily"  # daily, weekly, monthly
    last_crawled: Optional[datetime] = None


class DiscoveredPageModel:
    """Database model for discovered pages - fallback implementation"""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


if SQLALCHEMY_AVAILABLE:
    class DiscoveredPageModel(Base):
        """Database model for discovered pages"""
        __tablename__ = 'discovered_pages'
        
        url = Column(String, primary_key=True)
        parent_url = Column(String)
        anchor_text = Column(Text)
        discovery_timestamp = Column(DateTime, index=True)
        page_hash = Column(String, index=True)
        source_type = Column(String, index=True)
        depth = Column(Integer, index=True)
        classification_score = Column(Float)
        classification_type = Column(String, index=True)
        crawl_status = Column(String, index=True)
        metadata = Column(Text)  # JSON string
else:
    # Mock model class when SQLAlchemy is not available
    class DiscoveredPageModel:
        """Mock model for when SQLAlchemy is not available"""
        pass


class AdvancedCrawlManager:
    """Comprehensive crawling/discovery system with intelligence and efficiency"""
    
    def __init__(self, 
                 db_url: str = None,
                 redis_url: str = "redis://localhost:6379/0",
                 max_concurrent: int = 50,
                 max_depth: int = 5):
        
        # Database setup
        if SQLALCHEMY_AVAILABLE and db_url:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            self.db_available = True
        else:
            self.engine = None
            self.Session = None
            self.db_available = False
            logger.warning("Database not available, using in-memory storage")
        
        # Redis for caching and deduplication
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Test connection
                self.redis_available = True
            except:
                self.redis_client = None
                self.redis_available = False
                logger.warning("Redis not available, using in-memory caching")
        else:
            self.redis_client = None
            self.redis_available = False
        
        # Configuration
        self.max_concurrent = max_concurrent
        self.max_depth = max_depth
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        
        # Components
        self.link_classifier = AdaptiveLinkClassifier()
        self.robots_cache = {}  # Cache robots.txt files
        self.domain_rules = self.load_domain_rules()
        self.seed_sources = self.load_seed_sources()
        
        # State tracking
        self.crawled_urls: Set[str] = set()
        self.url_queue = asyncio.PriorityQueue()
        self.discovery_graph = nx.DiGraph() if NETWORKX_AVAILABLE else None
        self.active_crawlers = 0
        self.in_memory_pages = {}  # Fallback storage
        
        # Metrics
        self.metrics = defaultdict(int)
        self.start_time = datetime.utcnow()
        
        logger.info(f"AdvancedCrawlManager initialized:")
        logger.info(f"  Database: {'Available' if self.db_available else 'Not Available'}")
        logger.info(f"  Redis: {'Available' if self.redis_available else 'Not Available'}")
        logger.info(f"  NetworkX: {'Available' if NETWORKX_AVAILABLE else 'Not Available'}")
        logger.info(f"  BeautifulSoup: {'Available' if BS4_AVAILABLE else 'Not Available'}")
        
    def load_seed_sources(self) -> Dict[str, SeedSource]:
        """Load predefined seed sources for business intelligence crawling"""
        seed_sources = {
            'business_registries': SeedSource(
                name="Business Registries",
                urls=[
                    "https://opencorpdata.com/",
                    "https://www.sec.gov/edgar/",
                    "https://www.dnb.com/business-directory.html"
                ],
                source_type='business_registry',
                priority=10,
                crawl_config={
                    'max_depth': 3,
                    'delay': 2.0,
                    'patterns': [r'/company/', r'/filing/', r'/business/']
                }
            ),
            'industry_directories': SeedSource(
                name="Industry Directories",
                urls=[
                    "https://www.yellowpages.com/",
                    "https://www.manta.com/",
                    "https://www.bizapedia.com/"
                ],
                source_type='directory',
                priority=8,
                crawl_config={
                    'max_depth': 4,
                    'delay': 1.5,
                    'patterns': [r'/directory/', r'/profile/', r'/listing/']
                }
            ),
            'financial_sites': SeedSource(
                name="Financial Information Sites",
                urls=[
                    "https://finance.yahoo.com/",
                    "https://www.bloomberg.com/",
                    "https://www.reuters.com/business/"
                ],
                source_type='financial',
                priority=9,
                crawl_config={
                    'max_depth': 2,
                    'delay': 3.0,
                    'patterns': [r'/quote/', r'/company/', r'/profile/']
                }
            ),
            'industry_forums': SeedSource(
                name="Industry Forums and Communities",
                urls=[
                    "https://www.reddit.com/r/business/",
                    "https://news.ycombinator.com/",
                    "https://www.linkedin.com/company/"
                ],
                source_type='forum',
                priority=6,
                crawl_config={
                    'max_depth': 2,
                    'delay': 2.5,
                    'patterns': [r'/company/', r'/discussion/', r'/post/']
                }
            )
        }
        return seed_sources
    
    def load_domain_rules(self) -> Dict[str, Dict]:
        """Load domain-specific crawling rules and restrictions"""
        return {
            'allowed_domains': [
                'sec.gov', 'opencorpdata.com', 'dnb.com', 'manta.com',
                'bizapedia.com', 'yellowpages.com', 'bloomberg.com',
                'yahoo.com', 'reuters.com', 'crunchbase.com'
            ],
            'blocked_domains': [
                'facebook.com', 'twitter.com', 'instagram.com',
                'youtube.com', 'tiktok.com', 'pinterest.com'
            ],
            'rate_limits': {
                'default': 1.0,
                'sec.gov': 5.0,
                'bloomberg.com': 3.0,
                'reuters.com': 2.5
            },
            'url_patterns': {
                'include': [
                    r'/company/', r'/business/', r'/profile/', r'/organization/',
                    r'/directory/', r'/listing/', r'/filing/', r'/quote/'
                ],
                'exclude': [
                    r'/login', r'/signup', r'/register', r'/cart', r'/checkout',
                    r'/privacy', r'/terms', r'/cookie', r'/help', r'/support'
                ]
            }
        }
    
    async def start_discovery_operation(self, operation_name: str = "default") -> AsyncGenerator[DiscoveredPage, None]:
        """Main entry point for discovery operation"""
        logger.info(f"Starting discovery operation: {operation_name}")
        
        # Initialize seeds
        await self.initialize_seeds()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Start concurrent crawling
        tasks = []
        
        while not self.url_queue.empty() or tasks or self.active_crawlers > 0:
            # Start new crawler tasks
            while len(tasks) < self.max_concurrent and not self.url_queue.empty():
                try:
                    priority, discovered_page = await asyncio.wait_for(self.url_queue.get(), timeout=1.0)
                    task = asyncio.create_task(
                        self.crawl_page_with_discovery(discovered_page, semaphore)
                    )
                    tasks.append(task)
                except asyncio.TimeoutError:
                    break
            
            if tasks:
                # Wait for at least one task to complete
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending)
                
                # Process completed crawls
                for task in done:
                    try:
                        result = await task
                        if result:
                            yield result
                            await self.process_discovery_result(result)
                    except Exception as e:
                        logger.error(f"Crawler task failed: {e}")
                        self.metrics['crawler_errors'] += 1
            else:
                # No active tasks, wait a bit before checking again
                await asyncio.sleep(1)
                
                # If no active crawlers and queue is empty, we're done
                if self.active_crawlers == 0 and self.url_queue.empty():
                    break
    
    async def initialize_seeds(self):
        """Initialize crawling with seed URLs from all sources"""
        for source_name, seed_source in self.seed_sources.items():
            for url in seed_source.urls:
                if await self.should_crawl_url(url):
                    discovered_page = DiscoveredPage(
                        url=url,
                        source_type=seed_source.source_type,
                        depth=0,
                        classification_score=1.0,  # Seeds get max score
                        classification_type='seed',
                        metadata={'seed_source': source_name}
                    )
                    
                    # Add to queue with high priority (low number = high priority)
                    priority = 10 - seed_source.priority
                    await self.url_queue.put((priority, discovered_page))
    
    async def crawl_page_with_discovery(self, page: DiscoveredPage, semaphore) -> Optional[DiscoveredPage]:
        """Crawl a single page and discover new links"""
        async with semaphore:
            self.active_crawlers += 1
            
            try:
                # Check if already crawled
                if await self.is_already_crawled(page.url):
                    return None
                
                # Check robots.txt
                if not await self.can_crawl_url(page.url):
                    page.crawl_status = "blocked_by_robots"
                    await self.save_discovered_page(page)
                    return page
                
                # Perform HTTP request
                async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
                    try:
                        # Apply rate limiting
                        await self.apply_rate_limit(page.url)
                        
                        async with session.get(page.url, headers=self.get_headers()) as response:
                            if response.status == 200:
                                content = await response.text()
                                
                                # Update page metadata
                                page.page_hash = self.calculate_content_hash(content)
                                page.crawl_status = "crawled"
                                page.metadata.update({
                                    'status_code': response.status,
                                    'content_type': response.headers.get('content-type', ''),
                                    'content_length': len(content),
                                    'response_time': response.headers.get('x-response-time', ''),
                                })
                                
                                # Extract and classify links
                                discovered_links = await self.extract_and_classify_links(
                                    content, page.url, page.depth
                                )
                                
                                # Add high-value links to crawl queue
                                for link_url, score, link_type in discovered_links:
                                    if score > 0.5 and page.depth < self.max_depth:
                                        new_page = DiscoveredPage(
                                            url=link_url,
                                            parent_url=page.url,
                                            anchor_text="",  # Will be populated by extract_and_classify_links
                                            depth=page.depth + 1,
                                            classification_score=score,
                                            classification_type=link_type,
                                            source_type=page.source_type
                                        )
                                        
                                        # Priority based on classification score
                                        priority = int((1.0 - score) * 100)
                                        await self.url_queue.put((priority, new_page))
                                
                                # Update metrics
                                self.metrics['pages_crawled'] += 1
                                self.metrics['links_discovered'] += len(discovered_links)
                                
                                # Save to database
                                await self.save_discovered_page(page)
                                
                                return page
                            
                            else:
                                page.crawl_status = f"error_{response.status}"
                                await self.save_discovered_page(page)
                                return page
                    
                    except asyncio.TimeoutError:
                        page.crawl_status = "timeout"
                        self.metrics['timeouts'] += 1
                    except Exception as e:
                        page.crawl_status = f"error: {str(e)}"
                        logger.error(f"Error crawling {page.url}: {e}")
                        self.metrics['crawl_errors'] += 1
                    
                    await self.save_discovered_page(page)
                    return page
            
            finally:
                self.active_crawlers -= 1
                # Mark URL as crawled to avoid duplicates
                await self.mark_as_crawled(page.url)
    
    async def extract_and_classify_links(self, content: str, base_url: str, current_depth: int) -> List[Tuple[str, float, str]]:
        """Extract links from page content and classify them using the AdaptiveLinkClassifier"""
        discovered_links = []
        
        if BS4_AVAILABLE:
            soup = BeautifulSoup(content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if not href:
                    continue
                
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Skip if not a valid HTTP/HTTPS URL
                if not absolute_url.startswith(('http://', 'https://')):
                    continue
                
                # Extract link context
                anchor_text = link.get_text(strip=True)
                
                # Get surrounding context (parent and sibling elements)
                context_elements = []
                if link.parent:
                    context_elements.append(link.parent.get_text(strip=True)[:200])
                for sibling in link.find_next_siblings(limit=2):
                    if sibling.name and hasattr(sibling, 'get_text'):
                        context_elements.append(sibling.get_text(strip=True)[:100])
                
                context = ' '.join(context_elements)
                
                # Apply domain and pattern filters
                if not await self.should_crawl_url(absolute_url):
                    continue
                
                # Classify using the AdaptiveLinkClassifier
                classified_link = self.link_classifier.classify_link(
                    url=absolute_url,
                    anchor_text=anchor_text,
                    parent_url=base_url,
                    context=context
                )
                
                discovered_links.append((
                    classified_link.url,
                    classified_link.confidence,
                    classified_link.category.value
                ))
        else:
            # Fallback: simple regex-based link extraction
            logger.warning("BeautifulSoup not available, using simple link extraction")
            link_pattern = r'href=["\']([^"\']+)["\']'
            for match in re.finditer(link_pattern, content):
                href = match.group(1)
                absolute_url = urljoin(base_url, href)
                
                if absolute_url.startswith(('http://', 'https://')) and await self.should_crawl_url(absolute_url):
                    # Simple classification based on URL patterns
                    score = 0.5
                    link_type = 'unknown'
                    
                    if any(pattern in absolute_url.lower() for pattern in ['/company/', '/business/', '/profile/']):
                        score = 0.8
                        link_type = 'business_profile'
                    
                    discovered_links.append((absolute_url, score, link_type))
        
        return discovered_links
    
    async def should_crawl_url(self, url: str) -> bool:
        """Comprehensive URL filtering based on domain rules and patterns"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check allowed domains
        if self.domain_rules['allowed_domains']:
            if not any(allowed_domain in domain for allowed_domain in self.domain_rules['allowed_domains']):
                return False
        
        # Check blocked domains
        if any(blocked_domain in domain for blocked_domain in self.domain_rules['blocked_domains']):
            return False
        
        # Check URL patterns
        url_lower = url.lower()
        
        # Check exclude patterns first
        if any(re.search(pattern, url_lower) for pattern in self.domain_rules['url_patterns']['exclude']):
            return False
        
        # Check include patterns
        if self.domain_rules['url_patterns']['include']:
            if not any(re.search(pattern, url_lower) for pattern in self.domain_rules['url_patterns']['include']):
                return False
        
        return True
    
    async def can_crawl_url(self, url: str) -> bool:
        """Check robots.txt permissions for the URL"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check cache first
        if domain in self.robots_cache:
            rp = self.robots_cache[domain]
        else:
            # Fetch and parse robots.txt
            rp = RobotFileParser()
            robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    async with session.get(robots_url) as response:
                        if response.status == 200:
                            robots_content = await response.text()
                            rp.set_url(robots_url)
                            rp.feed(robots_content)
                        else:
                            # If no robots.txt, assume crawling is allowed
                            return True
            except:
                # If can't fetch robots.txt, assume crawling is allowed
                return True
            
            self.robots_cache[domain] = rp
        
        # Check if crawling is allowed for our user agent
        return rp.can_fetch('*', url)
    
    async def apply_rate_limit(self, url: str):
        """Apply domain-specific rate limiting"""
        domain = urlparse(url).netloc
        delay = self.domain_rules['rate_limits'].get(domain, self.domain_rules['rate_limits']['default'])
        
        if self.redis_available:
            # Use Redis to implement distributed rate limiting
            last_request_key = f"last_request:{domain}"
            last_request = self.redis_client.get(last_request_key)
            
            if last_request:
                time_since_last = time.time() - float(last_request)
                if time_since_last < delay:
                    sleep_time = delay - time_since_last
                    await asyncio.sleep(sleep_time)
            
            # Record current request time
            self.redis_client.set(last_request_key, time.time(), ex=3600)
        else:
            # Simple in-memory rate limiting
            if not hasattr(self, 'last_requests'):
                self.last_requests = {}
            
            if domain in self.last_requests:
                time_since_last = time.time() - self.last_requests[domain]
                if time_since_last < delay:
                    await asyncio.sleep(delay - time_since_last)
            
            self.last_requests[domain] = time.time()
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash for duplicate detection"""
        # Normalize content by removing whitespace and lowercasing
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def is_already_crawled(self, url: str) -> bool:
        """Check if URL has already been crawled"""
        # Check in-memory set first (fastest)
        if url in self.crawled_urls:
            return True
        
        # Check Redis cache
        if self.redis_available:
            if self.redis_client.exists(f"crawled:{hashlib.md5(url.encode()).hexdigest()}"):
                self.crawled_urls.add(url)
                return True
        
        # Check database
        if self.db_available:
            session = self.Session()
            try:
                exists = session.query(DiscoveredPageModel).filter_by(url=url).first() is not None
                if exists:
                    self.crawled_urls.add(url)
                    return True
            finally:
                session.close()
        else:
            # Check in-memory storage
            if url in self.in_memory_pages:
                self.crawled_urls.add(url)
                return True
        
        return False
    
    async def mark_as_crawled(self, url: str):
        """Mark URL as crawled to prevent duplicates"""
        self.crawled_urls.add(url)
        
        if self.redis_available:
            url_hash = hashlib.md5(url.encode()).hexdigest()
            self.redis_client.set(f"crawled:{url_hash}", "1", ex=86400)  # 24 hour expiry
    
    async def save_discovered_page(self, page: DiscoveredPage):
        """Save discovered page to database or in-memory storage"""
        if self.db_available:
            session = self.Session()
            try:
                db_page = DiscoveredPageModel(
                    url=page.url,
                    parent_url=page.parent_url,
                    anchor_text=page.anchor_text,
                    discovery_timestamp=page.discovery_timestamp,
                    page_hash=page.page_hash,
                    source_type=page.source_type,
                    depth=page.depth,
                    classification_score=page.classification_score,
                    classification_type=page.classification_type,
                    crawl_status=page.crawl_status,
                    metadata=json.dumps(page.metadata)
                )
                session.merge(db_page)  # Use merge to handle duplicates
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"Failed to save page {page.url}: {e}")
            finally:
                session.close()
        else:
            # Save to in-memory storage
            self.in_memory_pages[page.url] = page
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            'User-Agent': 'BusinessIntelligence-Crawler/1.0 (+https://example.com/bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def get_discovery_metrics(self) -> Dict:
        """Get current discovery operation metrics"""
        runtime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            'runtime_seconds': runtime,
            'pages_crawled': self.metrics['pages_crawled'],
            'links_discovered': self.metrics['links_discovered'],
            'active_crawlers': self.active_crawlers,
            'queue_size': self.url_queue.qsize(),
            'crawl_rate_per_minute': (self.metrics['pages_crawled'] / runtime * 60) if runtime > 0 else 0,
            'high_value_pages': self.metrics.get('high_value_pages', 0),
            'medium_value_pages': self.metrics.get('medium_value_pages', 0),
            'low_value_pages': self.metrics.get('low_value_pages', 0),
            'errors': {
                'crawler_errors': self.metrics['crawler_errors'],
                'crawl_errors': self.metrics['crawl_errors'],
                'timeouts': self.metrics['timeouts']
            },
            'system_status': {
                'database_available': self.db_available,
                'redis_available': self.redis_available,
                'networkx_available': NETWORKX_AVAILABLE,
                'bs4_available': BS4_AVAILABLE
            }
        }
    
    async def process_discovery_result(self, page: DiscoveredPage):
        """Process discovery result and update internal state"""
        # Add to discovery graph for analysis
        if NETWORKX_AVAILABLE and self.discovery_graph:
            if page.parent_url:
                self.discovery_graph.add_edge(page.parent_url, page.url, 
                                            weight=page.classification_score,
                                            link_type=page.classification_type)
            else:
                self.discovery_graph.add_node(page.url, 
                                            source_type=page.source_type,
                                            classification_score=page.classification_score)
        
        # Update metrics based on page type and quality
        if page.classification_score > 0.8:
            self.metrics['high_value_pages'] += 1
        elif page.classification_score > 0.5:
            self.metrics['medium_value_pages'] += 1
        else:
            self.metrics['low_value_pages'] += 1
