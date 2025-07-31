"""
Distributed Crawling and Queue Management System

This module implements a robust distributed crawling system with:
- Frontier Queue for seed URLs
- Parsing Queue for extracted content
- Fault tolerance with exponential backoff
- Dead URL queue for failed URLs
- OCR integration support
- Multiple queue backend support (Redis, Kafka, SQS)
"""

import asyncio
import hashlib
import json
import logging
import time
import random
import socket
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set, Optional, Any, Union, AsyncGenerator
from urllib.parse import urlparse, urljoin
import uuid
import aiohttp
import backoff
from pathlib import Path
import asyncio_throttle

# Queue backends
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import aiokafka
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    aiokafka = None

try:
    import boto3
    import aioboto3
    SQS_AVAILABLE = True
except ImportError:
    SQS_AVAILABLE = False
    boto3 = None

# OCR integration
try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None

# Headless browser support
try:
    from pyppeteer import launch
    PUPPETEER_AVAILABLE = True
except ImportError:
    PUPPETEER_AVAILABLE = False
    launch = None

# Database integration
try:
    from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
    Base = declarative_base()
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    Base = object

from ..storage.core import AdvancedStorageManager, RawDataRecord

logger = logging.getLogger(__name__)


class DNSCache:
    """DNS resolution cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, tuple] = {}  # hostname -> (ip, expiry_time)
        self.default_ttl = default_ttl
        self._lock = asyncio.Lock()
    
    async def resolve(self, hostname: str) -> Optional[str]:
        """Resolve hostname with caching"""
        async with self._lock:
            now = time.time()
            
            # Check cache
            if hostname in self.cache:
                ip, expiry = self.cache[hostname]
                if now < expiry:
                    return ip
                else:
                    # Expired, remove from cache
                    del self.cache[hostname]
            
            # Resolve and cache
            try:
                loop = asyncio.get_event_loop()
                ip = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
                if ip:
                    resolved_ip = ip[0][4][0]
                    self.cache[hostname] = (resolved_ip, now + self.default_ttl)
                    return resolved_ip
            except Exception as e:
                logger.warning(f"DNS resolution failed for {hostname}: {e}")
                return None
    
    def clear_expired(self):
        """Clear expired entries"""
        now = time.time()
        expired = [host for host, (_, expiry) in self.cache.items() if now >= expiry]
        for host in expired:
            del self.cache[host]


class RateLimiter:
    """Configurable rate limiter with jitter"""
    
    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: int = 5,
        jitter_factor: float = 0.1,
        per_domain: bool = True
    ):
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.jitter_factor = jitter_factor
        self.per_domain = per_domain
        
        if per_domain:
            self.throttlers: Dict[str, asyncio_throttle.Throttler] = {}
            self._throttler_lock = asyncio.Lock()
        else:
            self.global_throttler = asyncio_throttle.Throttler(
                rate_limit=requests_per_second,
                period=1.0
            )
    
    async def acquire(self, url: str = None):
        """Acquire rate limit permission"""
        if self.per_domain and url:
            domain = urlparse(url).netloc
            async with self._throttler_lock:
                if domain not in self.throttlers:
                    self.throttlers[domain] = asyncio_throttle.Throttler(
                        rate_limit=self.requests_per_second,
                        period=1.0
                    )
                throttler = self.throttlers[domain]
        else:
            throttler = self.global_throttler
        
        # Apply throttling
        async with throttler:
            # Add jitter
            if self.jitter_factor > 0:
                jitter_delay = random.uniform(0, self.jitter_factor)
                await asyncio.sleep(jitter_delay)


class HeadlessBrowser:
    """Headless browser manager for JavaScript-heavy sites"""
    
    def __init__(self, max_browsers: int = 3, page_timeout: int = 30):
        self.max_browsers = max_browsers
        self.page_timeout = page_timeout
        self.browsers = []
        self.browser_pool = asyncio.Queue()
        self._initialized = False
    
    async def initialize(self):
        """Initialize browser pool"""
        if not PUPPETEER_AVAILABLE:
            raise ImportError("Puppeteer not available")
        
        if self._initialized:
            return
        
        for i in range(self.max_browsers):
            browser = await launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            self.browsers.append(browser)
            await self.browser_pool.put(browser)
        
        self._initialized = True
        logger.info(f"Initialized {self.max_browsers} headless browsers")
    
    async def render_page(self, url: str, wait_for: str = None) -> Dict[str, Any]:
        """Render page with JavaScript execution"""
        if not self._initialized:
            await self.initialize()
        
        browser = await asyncio.wait_for(self.browser_pool.get(), timeout=10)
        
        try:
            page = await browser.newPage()
            await page.setUserAgent('BusinessIntelCrawler/1.0 (Headless)')
            await page.setViewport({'width': 1920, 'height': 1080})
            
            # Navigate to page
            response = await page.goto(url, waitUntil='networkidle0', timeout=self.page_timeout * 1000)
            
            # Wait for specific element if requested
            if wait_for:
                try:
                    await page.waitForSelector(wait_for, timeout=10000)
                except Exception:
                    logger.warning(f"Wait selector '{wait_for}' not found on {url}")
            
            # Get page content and metadata
            content = await page.content()
            title = await page.title()
            
            # Extract links (including dynamically generated ones)
            links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(link => ({
                    url: link.href,
                    text: link.textContent.trim(),
                    type: 'link'
                }));
            }''')
            
            # Extract forms
            forms = await page.evaluate('''() => {
                const forms = Array.from(document.querySelectorAll('form[action]'));
                return forms.map(form => ({
                    url: form.action,
                    text: '',
                    type: 'form'
                }));
            }''')
            
            await page.close()
            
            return {
                'content': content,
                'title': title,
                'links': links + forms,
                'status_code': response.status if response else 200,
                'final_url': page.url
            }
            
        except Exception as e:
            logger.error(f"Browser rendering failed for {url}: {e}")
            raise
        finally:
            await self.browser_pool.put(browser)
    
    async def close(self):
        """Close all browsers"""
        for browser in self.browsers:
            await browser.close()
        self.browsers.clear()
        self._initialized = False


class QueueBackend(Enum):
    """Supported queue backends"""
    REDIS = "redis"
    KAFKA = "kafka" 
    SQS = "sqs"
    MEMORY = "memory"


class URLStatus(Enum):
    """URL processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD = "dead"
    RETRY = "retry"


@dataclass
class CrawlURL:
    """URL record for crawling queue"""
    url: str
    source_url: Optional[str] = None
    depth: int = 0
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    scheduled_at: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    job_id: Optional[str] = None
    domain: Optional[str] = field(init=False)
    last_crawled_at: Optional[datetime] = None
    link_depth: int = 0  # Depth from the original seed URL
    requires_js: bool = False  # Whether this URL requires JavaScript rendering
    content_size_estimate: Optional[int] = None  # Estimated content size
    is_dynamic: bool = False  # Whether content changes frequently
    
    def __post_init__(self):
        self.domain = urlparse(self.url).netloc
        # Add metadata tags
        if 'tags' not in self.metadata:
            self.metadata['tags'] = []
        
        # Add last crawled tag if available
        if self.last_crawled_at:
            self.metadata['tags'].append(f"last_crawled:{self.last_crawled_at.isoformat()}")
        
        # Add link depth tag
        self.metadata['tags'].append(f"link_depth:{self.link_depth}")
        
        # Add domain tag
        self.metadata['tags'].append(f"domain:{self.domain}")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "source_url": self.source_url,
            "depth": self.depth,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat(),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
            "job_id": self.job_id,
            "domain": self.domain,
            "last_crawled_at": self.last_crawled_at.isoformat() if self.last_crawled_at else None,
            "link_depth": self.link_depth,
            "requires_js": self.requires_js,
            "content_size_estimate": self.content_size_estimate,
            "is_dynamic": self.is_dynamic
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CrawlURL':
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["scheduled_at"] = datetime.fromisoformat(data["scheduled_at"])
        if data.get("last_crawled_at"):
            data["last_crawled_at"] = datetime.fromisoformat(data["last_crawled_at"])
        return cls(**data)


@dataclass
class ParseTask:
    """Parsing task for extracted content"""
    task_id: str
    url: str
    raw_id: str
    storage_location: str
    content_type: str = "text/html"
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_ocr: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "url": self.url,
            "raw_id": self.raw_id,
            "storage_location": self.storage_location,
            "content_type": self.content_type,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "metadata": self.metadata,
            "requires_ocr": self.requires_ocr
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParseTask':
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


class CrawlRecord(Base):
    """Database model for crawl tracking"""
    __tablename__ = 'crawl_records'
    
    url = Column(String(2048), primary_key=True)
    url_hash = Column(String(64), index=True)
    domain = Column(String(255), index=True)
    first_crawled_at = Column(DateTime)
    last_crawled_at = Column(DateTime, index=True)
    crawl_count = Column(Integer, default=0)
    status = Column(String(50), index=True)
    last_status_code = Column(Integer)
    recrawl_interval_hours = Column(Integer, default=24)
    next_crawl_at = Column(DateTime, index=True)
    metadata = Column(JSON)
    content_size = Column(Integer)  # Size of last crawled content
    requires_js = Column(Boolean, default=False)  # Whether URL requires JavaScript
    is_dynamic = Column(Boolean, default=False)  # Whether content changes frequently
    link_depth = Column(Integer, default=0)  # Depth from seed URL
    last_modified = Column(DateTime)  # Last-Modified header from response
    etag = Column(String(255))  # ETag for conditional requests
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.url_hash:
            self.url_hash = hashlib.sha256(self.url.encode()).hexdigest()


class QueueManager:
    """Abstract base class for queue backends"""
    
    async def put_frontier_url(self, crawl_url: CrawlURL) -> bool:
        """Add URL to frontier queue"""
        raise NotImplementedError
    
    async def get_frontier_url(self) -> Optional[CrawlURL]:
        """Get next URL from frontier queue"""
        raise NotImplementedError
    
    async def put_parse_task(self, parse_task: ParseTask) -> bool:
        """Add task to parsing queue"""
        raise NotImplementedError
    
    async def get_parse_task(self) -> Optional[ParseTask]:
        """Get next parsing task"""
        raise NotImplementedError
    
    async def put_retry_url(self, crawl_url: CrawlURL, delay_seconds: int) -> bool:
        """Add URL to retry queue with delay"""
        raise NotImplementedError
    
    async def put_dead_url(self, crawl_url: CrawlURL, reason: str) -> bool:
        """Add URL to dead letter queue"""
        raise NotImplementedError
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        raise NotImplementedError


class RedisQueueManager(QueueManager):
    """Redis-based queue implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Queue names
        self.frontier_queue = "crawler:frontier"
        self.frontier_priority_queue = "crawler:frontier:priority"
        self.parse_queue = "crawler:parse"
        self.parse_priority_queue = "crawler:parse:priority"
        self.retry_queue = "crawler:retry"
        self.dead_queue = "crawler:dead"
        
        # Metrics
        self.metrics = {
            "urls_queued": 0,
            "urls_processed": 0,
            "parse_tasks_queued": 0,
            "parse_tasks_processed": 0,
            "urls_retried": 0,
            "urls_dead": 0
        }
    
    async def connect(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            raise ImportError("Redis not available")
        
        self.redis_client = redis.from_url(self.redis_url)
        await self.redis_client.ping()
        logger.info("Redis queue manager connected")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def put_frontier_url(self, crawl_url: CrawlURL) -> bool:
        """Add URL to frontier queue with priority support"""
        try:
            url_data = json.dumps(crawl_url.to_dict())
            
            if crawl_url.priority >= 8:  # High priority
                await self.redis_client.lpush(self.frontier_priority_queue, url_data)
            else:
                await self.redis_client.rpush(self.frontier_queue, url_data)
            
            self.metrics["urls_queued"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue URL {crawl_url.url}: {e}")
            return False
    
    async def get_frontier_url(self) -> Optional[CrawlURL]:
        """Get next URL from frontier queue (priority first)"""
        try:
            # Check priority queue first
            result = await self.redis_client.blpop(self.frontier_priority_queue, timeout=0.1)
            if not result:
                # Check regular queue
                result = await self.redis_client.blpop(self.frontier_queue, timeout=0.1)
            
            if result:
                _, url_data = result
                crawl_url = CrawlURL.from_dict(json.loads(url_data))
                self.metrics["urls_processed"] += 1
                return crawl_url
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get frontier URL: {e}")
            return None
    
    async def put_parse_task(self, parse_task: ParseTask) -> bool:
        """Add task to parsing queue with priority support"""
        try:
            task_data = json.dumps(parse_task.to_dict())
            
            if parse_task.priority >= 8:  # High priority
                await self.redis_client.lpush(self.parse_priority_queue, task_data)
            else:
                await self.redis_client.rpush(self.parse_queue, task_data)
            
            self.metrics["parse_tasks_queued"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue parse task {parse_task.task_id}: {e}")
            return False
    
    async def get_parse_task(self) -> Optional[ParseTask]:
        """Get next parsing task (priority first)"""
        try:
            # Check priority queue first
            result = await self.redis_client.blpop(self.parse_priority_queue, timeout=0.1)
            if not result:
                # Check regular queue
                result = await self.redis_client.blpop(self.parse_queue, timeout=0.1)
            
            if result:
                _, task_data = result
                parse_task = ParseTask.from_dict(json.loads(task_data))
                self.metrics["parse_tasks_processed"] += 1
                return parse_task
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get parse task: {e}")
            return None
    
    async def put_retry_url(self, crawl_url: CrawlURL, delay_seconds: int) -> bool:
        """Add URL to retry queue with delay"""
        try:
            # Schedule for future processing
            retry_time = time.time() + delay_seconds
            crawl_url.scheduled_at = datetime.fromtimestamp(retry_time)
            crawl_url.retry_count += 1
            
            url_data = json.dumps(crawl_url.to_dict())
            await self.redis_client.zadd(self.retry_queue, {url_data: retry_time})
            
            self.metrics["urls_retried"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue retry URL {crawl_url.url}: {e}")
            return False
    
    async def put_dead_url(self, crawl_url: CrawlURL, reason: str) -> bool:
        """Add URL to dead letter queue"""
        try:
            dead_record = {
                **crawl_url.to_dict(),
                "died_at": datetime.utcnow().isoformat(),
                "reason": reason
            }
            
            await self.redis_client.lpush(self.dead_queue, json.dumps(dead_record))
            self.metrics["urls_dead"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Failed to add dead URL {crawl_url.url}: {e}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics"""
        try:
            stats = {
                "frontier_queue_size": await self.redis_client.llen(self.frontier_queue),
                "frontier_priority_queue_size": await self.redis_client.llen(self.frontier_priority_queue),
                "parse_queue_size": await self.redis_client.llen(self.parse_queue),
                "parse_priority_queue_size": await self.redis_client.llen(self.parse_priority_queue),
                "retry_queue_size": await self.redis_client.zcard(self.retry_queue),
                "dead_queue_size": await self.redis_client.llen(self.dead_queue),
                **self.metrics
            }
            
            stats["total_frontier_size"] = stats["frontier_queue_size"] + stats["frontier_priority_queue_size"]
            stats["total_parse_size"] = stats["parse_queue_size"] + stats["parse_priority_queue_size"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return {}
    
    async def process_retry_queue(self) -> int:
        """Process retry queue for URLs ready to be retried"""
        try:
            current_time = time.time()
            
            # Get URLs ready for retry
            ready_urls = await self.redis_client.zrangebyscore(
                self.retry_queue, 0, current_time, withscores=True
            )
            
            processed = 0
            for url_data, score in ready_urls:
                try:
                    crawl_url = CrawlURL.from_dict(json.loads(url_data))
                    
                    # Move back to frontier queue
                    await self.put_frontier_url(crawl_url)
                    await self.redis_client.zrem(self.retry_queue, url_data)
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Failed to requeue retry URL: {e}")
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process retry queue: {e}")
            return 0


class MemoryQueueManager(QueueManager):
    """In-memory queue implementation for testing/development"""
    
    def __init__(self):
        self.frontier_queue = asyncio.Queue()
        self.frontier_priority_queue = asyncio.PriorityQueue()
        self.parse_queue = asyncio.Queue()
        self.parse_priority_queue = asyncio.PriorityQueue()
        self.retry_queue = []  # List of (retry_time, crawl_url)
        self.dead_queue = []
        
        self.metrics = {
            "urls_queued": 0,
            "urls_processed": 0,
            "parse_tasks_queued": 0,
            "parse_tasks_processed": 0,
            "urls_retried": 0,
            "urls_dead": 0
        }
    
    async def put_frontier_url(self, crawl_url: CrawlURL) -> bool:
        try:
            if crawl_url.priority >= 8:
                await self.frontier_priority_queue.put((10 - crawl_url.priority, crawl_url))
            else:
                await self.frontier_queue.put(crawl_url)
            
            self.metrics["urls_queued"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to queue URL {crawl_url.url}: {e}")
            return False
    
    async def get_frontier_url(self) -> Optional[CrawlURL]:
        try:
            # Check priority queue first
            try:
                _, crawl_url = self.frontier_priority_queue.get_nowait()
                self.metrics["urls_processed"] += 1
                return crawl_url
            except asyncio.QueueEmpty:
                pass
            
            # Check regular queue
            try:
                crawl_url = self.frontier_queue.get_nowait()
                self.metrics["urls_processed"] += 1
                return crawl_url
            except asyncio.QueueEmpty:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get frontier URL: {e}")
            return None
    
    async def put_parse_task(self, parse_task: ParseTask) -> bool:
        try:
            if parse_task.priority >= 8:
                await self.parse_priority_queue.put((10 - parse_task.priority, parse_task))
            else:
                await self.parse_queue.put(parse_task)
            
            self.metrics["parse_tasks_queued"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to queue parse task {parse_task.task_id}: {e}")
            return False
    
    async def get_parse_task(self) -> Optional[ParseTask]:
        try:
            # Check priority queue first
            try:
                _, parse_task = self.parse_priority_queue.get_nowait()
                self.metrics["parse_tasks_processed"] += 1
                return parse_task
            except asyncio.QueueEmpty:
                pass
            
            # Check regular queue
            try:
                parse_task = self.parse_queue.get_nowait()
                self.metrics["parse_tasks_processed"] += 1
                return parse_task
            except asyncio.QueueEmpty:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get parse task: {e}")
            return None
    
    async def put_retry_url(self, crawl_url: CrawlURL, delay_seconds: int) -> bool:
        try:
            retry_time = time.time() + delay_seconds
            crawl_url.scheduled_at = datetime.fromtimestamp(retry_time)
            crawl_url.retry_count += 1
            
            self.retry_queue.append((retry_time, crawl_url))
            self.retry_queue.sort(key=lambda x: x[0])  # Keep sorted by retry time
            
            self.metrics["urls_retried"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to queue retry URL {crawl_url.url}: {e}")
            return False
    
    async def put_dead_url(self, crawl_url: CrawlURL, reason: str) -> bool:
        try:
            dead_record = {
                **crawl_url.to_dict(),
                "died_at": datetime.utcnow().isoformat(),
                "reason": reason
            }
            self.dead_queue.append(dead_record)
            self.metrics["urls_dead"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to add dead URL {crawl_url.url}: {e}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        return {
            "frontier_queue_size": self.frontier_queue.qsize(),
            "frontier_priority_queue_size": self.frontier_priority_queue.qsize(),
            "parse_queue_size": self.parse_queue.qsize(),
            "parse_priority_queue_size": self.parse_priority_queue.qsize(),
            "retry_queue_size": len(self.retry_queue),
            "dead_queue_size": len(self.dead_queue),
            "total_frontier_size": self.frontier_queue.qsize() + self.frontier_priority_queue.qsize(),
            "total_parse_size": self.parse_queue.qsize() + self.parse_priority_queue.qsize(),
            **self.metrics
        }
    
    async def process_retry_queue(self) -> int:
        current_time = time.time()
        processed = 0
        
        # Process URLs ready for retry
        ready_indices = []
        for i, (retry_time, crawl_url) in enumerate(self.retry_queue):
            if retry_time <= current_time:
                ready_indices.append(i)
                await self.put_frontier_url(crawl_url)
                processed += 1
        
        # Remove processed URLs in reverse order to maintain indices
        for i in reversed(ready_indices):
            self.retry_queue.pop(i)
        
        return processed


class CrawlWorker:
    """Distributed crawl worker with enhanced capabilities"""
    
    def __init__(
        self,
        worker_id: str,
        queue_manager: QueueManager,
        storage_manager: AdvancedStorageManager,
        db_session_factory=None,
        max_concurrent: int = 10,
        rate_limit_config: Dict[str, Any] = None,
        enable_js_rendering: bool = False,
        dns_cache_ttl: int = 300,
        max_content_size: int = 50 * 1024 * 1024  # 50MB
    ):
        self.worker_id = worker_id
        self.queue_manager = queue_manager
        self.storage_manager = storage_manager
        self.db_session_factory = db_session_factory
        self.max_concurrent = max_concurrent
        self.enable_js_rendering = enable_js_rendering
        self.max_content_size = max_content_size
        
        # Rate limiting
        rate_config = rate_limit_config or {}
        self.rate_limiter = RateLimiter(
            requests_per_second=rate_config.get('requests_per_second', 1.0),
            burst_size=rate_config.get('burst_size', 5),
            jitter_factor=rate_config.get('jitter_factor', 0.1),
            per_domain=rate_config.get('per_domain', True)
        )
        
        # DNS caching
        self.dns_cache = DNSCache(default_ttl=dns_cache_ttl)
        
        # Headless browser
        self.headless_browser: Optional[HeadlessBrowser] = None
        if enable_js_rendering:
            self.headless_browser = HeadlessBrowser(
                max_browsers=rate_config.get('max_browsers', 2),
                page_timeout=rate_config.get('page_timeout', 30)
            )
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
        
        # State
        self.is_running = False
        self.active_tasks: Set[asyncio.Task] = set()
        
        # Metrics
        self.metrics = {
            "urls_crawled": 0,
            "urls_failed": 0,
            "bytes_downloaded": 0,
            "avg_response_time": 0.0,
            "js_rendered_pages": 0,
            "large_pages_skipped": 0,
            "conditional_requests": 0,
            "not_modified_responses": 0
        }
    
    async def start(self):
        """Start the crawl worker"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Initialize headless browser if enabled
        if self.headless_browser:
            try:
                await self.headless_browser.initialize()
                logger.info(f"Headless browser initialized for worker {self.worker_id}")
            except Exception as e:
                logger.warning(f"Failed to initialize headless browser: {e}")
                self.headless_browser = None
        
        # Create custom DNS resolver
        resolver = aiohttp.AsyncResolver()
        
        # Initialize HTTP session with DNS resolver
        connector = aiohttp.TCPConnector(
            limit=self.max_concurrent, 
            limit_per_host=5,
            resolver=resolver,
            use_dns_cache=True,
            ttl_dns_cache=300
        )
        timeout = aiohttp.ClientTimeout(total=60, connect=10, sock_read=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'BusinessIntelCrawler/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        )
        
        # Start main crawl loop
        self.crawl_task = asyncio.create_task(self._crawl_loop())
        
        logger.info(f"Crawl worker {self.worker_id} started")
    
    async def stop(self):
        """Stop the crawl worker"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel main task
        if hasattr(self, 'crawl_task'):
            self.crawl_task.cancel()
        
        # Cancel active tasks
        for task in self.active_tasks.copy():
            task.cancel()
        
        # Wait for tasks to finish
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        
        # Close headless browser
        if self.headless_browser:
            await self.headless_browser.close()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info(f"Crawl worker {self.worker_id} stopped")
    
    async def _crawl_loop(self):
        """Main crawl loop"""
        while self.is_running:
            try:
                # Get next URL from queue
                crawl_url = await self.queue_manager.get_frontier_url()
                
                if crawl_url:
                    # Check if we should crawl this URL
                    if await self._should_crawl_url(crawl_url):
                        # Create crawl task
                        task = asyncio.create_task(self._crawl_url(crawl_url))
                        self.active_tasks.add(task)
                        
                        # Clean up finished tasks
                        self.active_tasks = {t for t in self.active_tasks if not t.done()}
                    else:
                        logger.debug(f"Skipping URL {crawl_url.url} (shouldn't crawl)")
                else:
                    # No URLs available, wait a bit
                    await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in crawl loop: {e}")
                await asyncio.sleep(5)
    
    async def _should_crawl_url(self, crawl_url: CrawlURL) -> bool:
        """Check if URL should be crawled"""
        try:
            if not self.db_session_factory:
                return True  # No database, always crawl
            
            session = self.db_session_factory()
            try:
                url_hash = hashlib.sha256(crawl_url.url.encode()).hexdigest()
                
                # Check if URL exists in database
                record = session.query(CrawlRecord).filter_by(url_hash=url_hash).first()
                
                if not record:
                    return True  # New URL, should crawl
                
                # Check recrawl interval
                if record.next_crawl_at and datetime.utcnow() < record.next_crawl_at:
                    return False  # Too soon to recrawl
                
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Error checking crawl status for {crawl_url.url}: {e}")
            return True  # Default to crawling on error
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _crawl_url(self, crawl_url: CrawlURL):
        """Crawl a single URL with enhanced capabilities"""
        start_time = time.time()
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire(crawl_url.url)
            
            logger.info(f"Crawling URL: {crawl_url.url}")
            
            # Check if we should use conditional requests
            headers = {}
            last_record = await self._get_last_crawl_record(crawl_url)
            if last_record:
                if last_record.etag:
                    headers['If-None-Match'] = last_record.etag
                    self.metrics["conditional_requests"] += 1
                elif last_record.last_modified:
                    headers['If-Modified-Since'] = last_record.last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
                    self.metrics["conditional_requests"] += 1
            
            # Decide whether to use headless browser
            use_browser = (
                self.headless_browser and 
                (crawl_url.requires_js or self._likely_requires_js(crawl_url.url))
            )
            
            if use_browser:
                # Use headless browser for JavaScript-heavy sites
                result = await self._crawl_with_browser(crawl_url)
                content = result['content']
                response_headers = {}
                status_code = result['status_code']
                final_url = result['final_url']
                self.metrics["js_rendered_pages"] += 1
            else:
                # Use regular HTTP client
                async with self.session.get(crawl_url.url, headers=headers) as response:
                    # Check for 304 Not Modified
                    if response.status == 304:
                        logger.info(f"URL not modified: {crawl_url.url}")
                        self.metrics["not_modified_responses"] += 1
                        await self._update_crawl_record(crawl_url, 304, time.time() - start_time)
                        return
                    
                    # Check content size before downloading
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.max_content_size:
                        logger.warning(f"Skipping large content ({content_length} bytes): {crawl_url.url}")
                        self.metrics["large_pages_skipped"] += 1
                        return
                    
                    # Read content with size limit
                    content_chunks = []
                    bytes_read = 0
                    
                    async for chunk in response.content.iter_chunked(8192):
                        bytes_read += len(chunk)
                        if bytes_read > self.max_content_size:
                            logger.warning(f"Content too large ({bytes_read} bytes), truncating: {crawl_url.url}")
                            self.metrics["large_pages_skipped"] += 1
                            break
                        content_chunks.append(chunk)
                    
                    content = b''.join(content_chunks).decode('utf-8', errors='ignore')
                    response_headers = dict(response.headers)
                    status_code = response.status
                    final_url = str(response.url)
            
            response_time = time.time() - start_time
            
            # Update metrics
            self.metrics["urls_crawled"] += 1
            self.metrics["bytes_downloaded"] += len(content.encode())
            self.metrics["avg_response_time"] = (
                (self.metrics["avg_response_time"] * (self.metrics["urls_crawled"] - 1) + response_time) 
                / self.metrics["urls_crawled"]
            )
            
            # Determine content type and if it's dynamic
            content_type = response_headers.get('content-type', 'text/html')
            is_dynamic = self._is_dynamic_content(response_headers, content)
            
            # Create enhanced metadata
            enhanced_metadata = {
                **crawl_url.metadata,
                "response_status": status_code,
                "content_length": len(content),
                "response_time_ms": int(response_time * 1000),
                "final_url": final_url,
                "is_dynamic": is_dynamic,
                "crawled_with_js": use_browser,
                "worker_id": self.worker_id,
                "crawl_timestamp": datetime.utcnow().isoformat()
            }
            
            # Add last crawled tag
            if 'tags' not in enhanced_metadata:
                enhanced_metadata['tags'] = []
            enhanced_metadata['tags'].append(f"last_crawled:{datetime.utcnow().isoformat()}")
            
            # Store raw data
            raw_record = RawDataRecord(
                raw_id=str(uuid.uuid4()),
                source_url=crawl_url.url,
                content=content,
                content_type=content_type,
                fetched_at=datetime.utcnow(),
                job_id=crawl_url.job_id,
                referrer_url=crawl_url.source_url,
                http_status=status_code,
                response_time_ms=int(response_time * 1000),
                request_headers=headers,
                response_headers=response_headers,
                metadata=enhanced_metadata,
                storage_backend="s3",
                storage_bucket="crawl-data",
                storage_key=f"{crawl_url.domain}/{crawl_url.job_id}/{uuid.uuid4()}.html"
            )
            
            # Store in storage manager
            stored_id = await self.storage_manager.store_raw_data(raw_record)
            
            # Create parsing task
            parse_task = ParseTask(
                task_id=str(uuid.uuid4()),
                url=crawl_url.url,
                raw_id=stored_id,
                storage_location=raw_record.storage_key,
                content_type=content_type,
                priority=crawl_url.priority,
                metadata=enhanced_metadata,
                requires_ocr=self._requires_ocr(content_type)
            )
            
            # Queue for parsing
            await self.queue_manager.put_parse_task(parse_task)
            
            # Update database record with enhanced information
            await self._update_crawl_record(
                crawl_url, status_code, response_time, 
                content_size=len(content),
                response_headers=response_headers,
                is_dynamic=is_dynamic,
                requires_js=use_browser
            )
            
            logger.info(f"Successfully crawled and queued for parsing: {crawl_url.url}")
            
        except Exception as e:
            self.metrics["urls_failed"] += 1
            logger.error(f"Failed to crawl URL {crawl_url.url}: {e}")
            
            # Handle retry logic
            await self._handle_crawl_failure(crawl_url, str(e))
        
        finally:
            # Remove from active tasks
            self.active_tasks.discard(asyncio.current_task())
    
    async def _crawl_with_browser(self, crawl_url: CrawlURL) -> Dict[str, Any]:
        """Crawl URL using headless browser"""
        try:
            # Determine what to wait for based on URL patterns
            wait_for = self._get_wait_selector(crawl_url.url)
            
            result = await self.headless_browser.render_page(
                crawl_url.url, 
                wait_for=wait_for
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Browser crawling failed for {crawl_url.url}: {e}")
            raise
    
    def _likely_requires_js(self, url: str) -> bool:
        """Heuristics to determine if URL likely requires JavaScript"""
        js_indicators = [
            'spa', 'react', 'angular', 'vue', 'app', 'dashboard',
            'admin', 'portal', 'ajax', 'api', 'json'
        ]
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in js_indicators)
    
    def _get_wait_selector(self, url: str) -> Optional[str]:
        """Get CSS selector to wait for based on URL patterns"""
        # Common patterns for different site types
        if 'linkedin' in url:
            return '.core-rail'
        elif 'facebook' in url:
            return '[role="main"]'
        elif 'twitter' in url or 'x.com' in url:
            return '[data-testid="primaryColumn"]'
        elif any(term in url for term in ['directory', 'listing', 'search']):
            return '.results, .listings, .search-results'
        
        return None
    
    def _is_dynamic_content(self, headers: Dict[str, str], content: str) -> bool:
        """Determine if content is dynamic and changes frequently"""
        # Check headers for dynamic indicators
        cache_control = headers.get('cache-control', '').lower()
        if 'no-cache' in cache_control or 'max-age=0' in cache_control:
            return True
        
        # Check for dynamic content indicators in HTML
        dynamic_indicators = [
            'csrf', 'nonce', 'timestamp', 'session', 'real-time',
            'live', 'updated', 'current', 'now'
        ]
        
        content_lower = content.lower()
        dynamic_count = sum(1 for indicator in dynamic_indicators if indicator in content_lower)
        
        return dynamic_count >= 2
    
    async def _get_last_crawl_record(self, crawl_url: CrawlURL) -> Optional[Any]:
        """Get last crawl record for conditional requests"""
        if not self.db_session_factory:
            return None
        
        try:
            session = self.db_session_factory()
            try:
                url_hash = hashlib.sha256(crawl_url.url.encode()).hexdigest()
                record = session.query(CrawlRecord).filter_by(url_hash=url_hash).first()
                return record
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to get crawl record: {e}")
            return None
    
    def _requires_ocr(self, content_type: str) -> bool:
        """Check if content requires OCR processing"""
        ocr_content_types = {
            'image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp',
            'application/pdf'
        }
        return any(ct in content_type.lower() for ct in ocr_content_types)
    
    async def _handle_crawl_failure(self, crawl_url: CrawlURL, error: str):
        """Handle crawl failure with retry logic"""
        crawl_url.retry_count += 1
        
        if crawl_url.retry_count >= crawl_url.max_retries:
            # Move to dead queue
            await self.queue_manager.put_dead_url(crawl_url, f"Max retries exceeded: {error}")
            logger.warning(f"URL moved to dead queue after {crawl_url.retry_count} retries: {crawl_url.url}")
        else:
            # Calculate exponential backoff delay
            delay = min(300, 2 ** crawl_url.retry_count * 60)  # Max 5 minutes
            await self.queue_manager.put_retry_url(crawl_url, delay)
            logger.info(f"URL queued for retry in {delay}s: {crawl_url.url}")
    
    async def _update_crawl_record(
        self, 
        crawl_url: CrawlURL, 
        status_code: int, 
        response_time: float,
        content_size: Optional[int] = None,
        response_headers: Optional[Dict[str, str]] = None,
        is_dynamic: bool = False,
        requires_js: bool = False
    ):
        """Update crawl record in database with enhanced information"""
        if not self.db_session_factory:
            return
        
        try:
            session = self.db_session_factory()
            try:
                url_hash = hashlib.sha256(crawl_url.url.encode()).hexdigest()
                
                record = session.query(CrawlRecord).filter_by(url_hash=url_hash).first()
                
                if not record:
                    record = CrawlRecord(
                        url=crawl_url.url,
                        url_hash=url_hash,
                        domain=crawl_url.domain,
                        first_crawled_at=datetime.utcnow(),
                        crawl_count=0,
                        metadata={},
                        link_depth=crawl_url.link_depth
                    )
                    session.add(record)
                
                # Update record
                record.last_crawled_at = datetime.utcnow()
                record.crawl_count += 1
                record.status = URLStatus.COMPLETED.value
                record.last_status_code = status_code
                record.requires_js = requires_js
                record.is_dynamic = is_dynamic
                
                if content_size:
                    record.content_size = content_size
                
                # Extract caching headers
                if response_headers:
                    if 'etag' in response_headers:
                        record.etag = response_headers['etag']
                    if 'last-modified' in response_headers:
                        try:
                            from email.utils import parsedate_to_datetime
                            record.last_modified = parsedate_to_datetime(response_headers['last-modified'])
                        except Exception:
                            pass
                
                # Calculate next crawl time based on content type
                if is_dynamic:
                    # Dynamic content: crawl more frequently
                    record.recrawl_interval_hours = 6
                elif requires_js:
                    # JS-heavy sites: moderate frequency
                    record.recrawl_interval_hours = 12
                else:
                    # Static content: normal frequency
                    record.recrawl_interval_hours = 24
                
                record.next_crawl_at = datetime.utcnow() + timedelta(hours=record.recrawl_interval_hours)
                
                # Update metadata
                if not record.metadata:
                    record.metadata = {}
                record.metadata.update({
                    "last_response_time_ms": int(response_time * 1000),
                    "worker_id": self.worker_id,
                    "crawl_method": "browser" if requires_js else "http",
                    "tags": crawl_url.metadata.get('tags', [])
                })
                
                session.commit()
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to update crawl record for {crawl_url.url}: {e}")


class ParseWorker:
    """Distributed parsing worker with OCR support"""
    
    def __init__(
        self,
        worker_id: str,
        queue_manager: QueueManager,
        storage_manager: AdvancedStorageManager,
        max_concurrent: int = 5
    ):
        self.worker_id = worker_id
        self.queue_manager = queue_manager
        self.storage_manager = storage_manager
        self.max_concurrent = max_concurrent
        
        # State
        self.is_running = False
        self.active_tasks: Set[asyncio.Task] = set()
        
        # Metrics
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "urls_extracted": 0,
            "ocr_tasks_processed": 0
        }
    
    async def start(self):
        """Start the parse worker"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start main parsing loop
        self.parse_task = asyncio.create_task(self._parse_loop())
        
        logger.info(f"Parse worker {self.worker_id} started")
    
    async def stop(self):
        """Stop the parse worker"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel main task
        if hasattr(self, 'parse_task'):
            self.parse_task.cancel()
        
        # Cancel active tasks
        for task in self.active_tasks.copy():
            task.cancel()
        
        # Wait for tasks to finish
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        
        logger.info(f"Parse worker {self.worker_id} stopped")
    
    async def _parse_loop(self):
        """Main parsing loop"""
        while self.is_running:
            try:
                # Get next parsing task
                parse_task = await self.queue_manager.get_parse_task()
                
                if parse_task:
                    # Create parsing task
                    task = asyncio.create_task(self._process_parse_task(parse_task))
                    self.active_tasks.add(task)
                    
                    # Clean up finished tasks
                    self.active_tasks = {t for t in self.active_tasks if not t.done()}
                else:
                    # No tasks available, wait a bit
                    await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in parse loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_parse_task(self, parse_task: ParseTask):
        """Process a parsing task"""
        try:
            logger.info(f"Processing parse task: {parse_task.task_id}")
            
            # Retrieve raw data
            raw_record = await self.storage_manager.retrieve_raw_data(parse_task.raw_id)
            if not raw_record:
                raise ValueError(f"Raw data not found: {parse_task.raw_id}")
            
            # Extract content based on type
            if parse_task.requires_ocr:
                extracted_urls = await self._process_with_ocr(raw_record, parse_task)
            else:
                extracted_urls = await self._extract_urls_from_html(raw_record.content, parse_task.url)
            
            # Queue extracted URLs for crawling
            for url_info in extracted_urls:
                # Calculate link depth from original seed
                parent_depth = parse_task.metadata.get("link_depth", 0)
                new_link_depth = parent_depth + 1
                
                crawl_url = CrawlURL(
                    url=url_info["url"],
                    source_url=parse_task.url,
                    depth=parse_task.metadata.get("depth", 0) + 1,
                    priority=max(1, parse_task.priority - 1),  # Lower priority for discovered URLs
                    job_id=parse_task.metadata.get("job_id"),
                    link_depth=new_link_depth,
                    requires_js=self._url_requires_js(url_info["url"]),
                    metadata={
                        "discovered_from": parse_task.url,
                        "link_text": url_info.get("text", ""),
                        "link_type": url_info.get("type", "unknown"),
                        "discovered_at": datetime.utcnow().isoformat(),
                        "parent_link_depth": parent_depth,
                        "tags": [
                            f"discovered_from:{parse_task.url}",
                            f"link_depth:{new_link_depth}",
                            f"link_type:{url_info.get('type', 'unknown')}"
                        ]
                    }
                )
                
                await self.queue_manager.put_frontier_url(crawl_url)
            
            self.metrics["tasks_processed"] += 1
            self.metrics["urls_extracted"] += len(extracted_urls)
            
            logger.info(f"Processed parse task {parse_task.task_id}, extracted {len(extracted_urls)} URLs")
            
        except Exception as e:
            self.metrics["tasks_failed"] += 1
            logger.error(f"Failed to process parse task {parse_task.task_id}: {e}")
            
            # Handle retry logic for parsing
            await self._handle_parse_failure(parse_task, str(e))
        
        finally:
            # Remove from active tasks
            self.active_tasks.discard(asyncio.current_task())
    
    async def _extract_urls_from_html(self, content: str, base_url: str) -> List[Dict[str, str]]:
        """Extract URLs from HTML content"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            urls = []
            
            # Extract links
            for link in soup.find_all('a', href=True):
                url = urljoin(base_url, link['href'])
                urls.append({
                    "url": url,
                    "text": link.get_text(strip=True),
                    "type": "link"
                })
            
            # Extract forms
            for form in soup.find_all('form', action=True):
                url = urljoin(base_url, form['action'])
                urls.append({
                    "url": url,
                    "text": "",
                    "type": "form"
                })
            
            # Extract images with links
            for img in soup.find_all('img', src=True):
                parent_link = img.find_parent('a')
                if parent_link and parent_link.get('href'):
                    url = urljoin(base_url, parent_link['href'])
                    urls.append({
                        "url": url,
                        "text": img.get('alt', ''),
                        "type": "image_link"
                    })
            
            # Filter and deduplicate
            valid_urls = []
            seen_urls = set()
            
            for url_info in urls:
                url = url_info["url"]
                if url and url not in seen_urls and self._is_valid_url(url):
                    seen_urls.add(url)
                    valid_urls.append(url_info)
            
            return valid_urls
            
        except Exception as e:
            logger.error(f"Failed to extract URLs from HTML: {e}")
            return []
    
    async def _process_with_ocr(self, raw_record: RawDataRecord, parse_task: ParseTask) -> List[Dict[str, str]]:
        """Process content with OCR support"""
        if not OCR_AVAILABLE:
            logger.warning("OCR not available, skipping OCR processing")
            return []
        
        try:
            self.metrics["ocr_tasks_processed"] += 1
            
            # For images, extract text using OCR
            if 'image/' in raw_record.content_type:
                # Convert content to image
                image_bytes = raw_record.content.encode() if isinstance(raw_record.content, str) else raw_record.content
                image = Image.open(io.BytesIO(image_bytes))
                
                # Extract text using OCR
                ocr_text = pytesseract.image_to_string(image)
                
                # Look for URLs in OCR text
                import re
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                found_urls = re.findall(url_pattern, ocr_text)
                
                return [{"url": url, "text": "", "type": "ocr_extracted"} for url in found_urls]
            
            # For PDFs, would need different processing
            elif 'application/pdf' in raw_record.content_type:
                # Would implement PDF text extraction here
                logger.info("PDF OCR processing not yet implemented")
                return []
            
            return []
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return []
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid for crawling"""
        try:
            parsed = urlparse(url)
            
            # Must have scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Only HTTP/HTTPS
            if parsed.scheme not in ('http', 'https'):
                return False
            
            # Exclude common file types that aren't web pages
            excluded_extensions = {
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.zip', '.rar', '.tar', '.gz', '.exe', '.dmg',
                '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
                '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
                '.css', '.js', '.xml', '.rss'
            }
            
            path_lower = parsed.path.lower()
            if any(path_lower.endswith(ext) for ext in excluded_extensions):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _url_requires_js(self, url: str) -> bool:
        """Determine if a URL likely requires JavaScript rendering"""
        js_indicators = [
            'spa', 'react', 'angular', 'vue', 'app', 'dashboard',
            'admin', 'portal', 'ajax', 'api', 'json', 'search',
            'filter', 'sort', 'load-more', 'infinite-scroll'
        ]
        
        url_lower = url.lower()
        
        # Check URL path and query parameters
        if any(indicator in url_lower for indicator in js_indicators):
            return True
        
        # Check for single-page app patterns
        if '#' in url and any(term in url_lower for term in ['app', 'page', 'view']):
            return True
        
        # Check for API endpoints that serve JSON
        if url_lower.endswith('.json') or '/api/' in url_lower:
            return True
        
        return False
    
    async def _handle_parse_failure(self, parse_task: ParseTask, error: str):
        """Handle parsing failure with retry logic"""
        parse_task.retry_count += 1
        
        if parse_task.retry_count >= parse_task.max_retries:
            logger.warning(f"Parse task failed after {parse_task.retry_count} retries: {parse_task.task_id}")
            # Could implement a dead parsing task queue here
        else:
            # For now, just log the retry (could implement delayed retry queue)
            logger.info(f"Parse task will be retried: {parse_task.task_id}")


class DistributedCrawlSystem:
    """Main distributed crawl system coordinator with enhanced capabilities"""
    
    def __init__(
        self,
        queue_backend: QueueBackend = QueueBackend.REDIS,
        redis_url: str = "redis://localhost:6379/0",
        database_url: Optional[str] = None,
        storage_config: Optional[Dict] = None,
        num_crawl_workers: int = 5,
        num_parse_workers: int = 3,
        rate_limit_config: Optional[Dict[str, Any]] = None,
        enable_js_rendering: bool = False,
        max_content_size: int = 50 * 1024 * 1024,
        dns_cache_ttl: int = 300
    ):
        self.queue_backend = queue_backend
        self.num_crawl_workers = num_crawl_workers
        self.num_parse_workers = num_parse_workers
        self.rate_limit_config = rate_limit_config or {}
        self.enable_js_rendering = enable_js_rendering
        self.max_content_size = max_content_size
        self.dns_cache_ttl = dns_cache_ttl
        
        # Initialize queue manager
        if queue_backend == QueueBackend.REDIS:
            self.queue_manager = RedisQueueManager(redis_url)
        else:
            self.queue_manager = MemoryQueueManager()
        
        # Initialize storage manager
        if storage_config:
            from ..storage.core import StorageConfig
            config = StorageConfig(**storage_config)
            self.storage_manager = AdvancedStorageManager(config)
        else:
            # Default storage config
            from ..storage.core import StorageConfig
            config = StorageConfig(
                database_url=database_url or "sqlite:///crawl_data.db",
                enable_cache=True,
                local_storage_path="./crawl_storage"
            )
            self.storage_manager = AdvancedStorageManager(config)
        
        # Initialize database session factory
        if database_url and SQLALCHEMY_AVAILABLE:
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            engine = create_engine(database_url)
            if hasattr(Base, 'metadata'):
                Base.metadata.create_all(engine)
            self.db_session_factory = sessionmaker(bind=engine)
        else:
            self.db_session_factory = None
        
        # Workers
        self.crawl_workers: List[CrawlWorker] = []
        self.parse_workers: List[ParseWorker] = []
        
        # State
        self.is_running = False
        self.retry_processor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the distributed crawl system"""
        if self.is_running:
            return
        
        logger.info("Starting enhanced distributed crawl system...")
        
        # Connect to queue backend
        if hasattr(self.queue_manager, 'connect'):
            await self.queue_manager.connect()
        
        # Create and start crawl workers with enhanced capabilities
        for i in range(self.num_crawl_workers):
            worker = CrawlWorker(
                worker_id=f"crawl-worker-{i}",
                queue_manager=self.queue_manager,
                storage_manager=self.storage_manager,
                db_session_factory=self.db_session_factory,
                rate_limit_config=self.rate_limit_config,
                enable_js_rendering=self.enable_js_rendering,
                dns_cache_ttl=self.dns_cache_ttl,
                max_content_size=self.max_content_size
            )
            await worker.start()
            self.crawl_workers.append(worker)
        
        # Create and start parse workers
        for i in range(self.num_parse_workers):
            worker = ParseWorker(
                worker_id=f"parse-worker-{i}",
                queue_manager=self.queue_manager,
                storage_manager=self.storage_manager
            )
            await worker.start()
            self.parse_workers.append(worker)
        
        # Start retry queue processor
        self.retry_processor_task = asyncio.create_task(self._retry_processor())
        
        self.is_running = True
        logger.info(f"Enhanced crawl system started with {len(self.crawl_workers)} crawl workers and {len(self.parse_workers)} parse workers")
        if self.enable_js_rendering:
            logger.info("JavaScript rendering enabled")
    
    async def stop(self):
        """Stop the distributed crawl system"""
        if not self.is_running:
            return
        
        logger.info("Stopping enhanced distributed crawl system...")
        
        self.is_running = False
        
        # Stop retry processor
        if self.retry_processor_task:
            self.retry_processor_task.cancel()
        
        # Stop all workers
        stop_tasks = []
        for worker in self.crawl_workers + self.parse_workers:
            stop_tasks.append(worker.stop())
        
        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)
        
        # Disconnect from queue backend
        if hasattr(self.queue_manager, 'disconnect'):
            await self.queue_manager.disconnect()
        
        logger.info("Enhanced distributed crawl system stopped")
    
    async def add_seed_urls(
        self, 
        urls: List[str], 
        job_id: str, 
        priority: int = 5,
        requires_js: bool = False,
        is_dynamic: bool = False
    ) -> int:
        """Add seed URLs to the frontier queue with enhanced metadata"""
        added = 0
        
        for url in urls:
            crawl_url = CrawlURL(
                url=url,
                depth=0,
                priority=priority,
                job_id=job_id,
                link_depth=0,  # Seed URLs have link depth 0
                requires_js=requires_js,
                is_dynamic=is_dynamic,
                metadata={
                    "seed_url": True,
                    "added_at": datetime.utcnow().isoformat(),
                    "tags": [
                        "seed_url",
                        "link_depth:0",
                        f"job_id:{job_id}",
                        f"priority:{priority}"
                    ]
                }
            )
            
            if await self.queue_manager.put_frontier_url(crawl_url):
                added += 1
        
        logger.info(f"Added {added} enhanced seed URLs for job {job_id}")
        return added
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        queue_stats = await self.queue_manager.get_queue_stats()
        
        # Aggregate worker metrics
        crawl_metrics = {}
        for worker in self.crawl_workers:
            for key, value in worker.metrics.items():
                crawl_metrics[key] = crawl_metrics.get(key, 0) + value
        
        parse_metrics = {}
        for worker in self.parse_workers:
            for key, value in worker.metrics.items():
                parse_metrics[key] = parse_metrics.get(key, 0) + value
        
        return {
            "system_status": {
                "is_running": self.is_running,
                "crawl_workers": len(self.crawl_workers),
                "parse_workers": len(self.parse_workers),
                "queue_backend": self.queue_backend.value,
                "js_rendering_enabled": self.enable_js_rendering,
                "max_content_size_mb": self.max_content_size / (1024 * 1024),
                "dns_cache_ttl": self.dns_cache_ttl
            },
            "queue_stats": queue_stats,
            "crawl_metrics": crawl_metrics,
            "parse_metrics": parse_metrics,
            "rate_limiting": {
                "enabled": bool(self.rate_limit_config),
                "per_domain": self.rate_limit_config.get('per_domain', True),
                "requests_per_second": self.rate_limit_config.get('requests_per_second', 1.0)
            }
        }
    
    async def _retry_processor(self):
        """Process retry queue periodically"""
        while self.is_running:
            try:
                if hasattr(self.queue_manager, 'process_retry_queue'):
                    processed = await self.queue_manager.process_retry_queue()
                    if processed > 0:
                        logger.info(f"Requeued {processed} URLs from retry queue")
                
                # Process every 30 seconds
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry processor: {e}")
                await asyncio.sleep(60)


# Example usage and configuration
async def main():
    """Example usage of the enhanced distributed crawl system"""
    
    # Enhanced configuration
    rate_limit_config = {
        'requests_per_second': 2.0,  # 2 requests per second per domain
        'burst_size': 10,
        'jitter_factor': 0.2,  # 20% jitter
        'per_domain': True,
        'max_browsers': 3,  # For JavaScript rendering
        'page_timeout': 45
    }
    
    # Initialize enhanced system
    crawl_system = DistributedCrawlSystem(
        queue_backend=QueueBackend.REDIS,
        redis_url="redis://localhost:6379/0",
        database_url="postgresql://user:pass@localhost/crawldb",
        num_crawl_workers=8,
        num_parse_workers=4,
        rate_limit_config=rate_limit_config,
        enable_js_rendering=True,  # Enable JavaScript rendering
        max_content_size=100 * 1024 * 1024,  # 100MB max content
        dns_cache_ttl=600  # 10 minutes DNS cache
    )
    
    try:
        # Start the enhanced system
        await crawl_system.start()
        
        # Add seed URLs with enhanced metadata
        business_directories = [
            "https://www.yellowpages.com/search?search_terms=business&geo_location_terms=US",
            "https://www.yelp.com/biz/directory",
            "https://foursquare.com/explore"
        ]
        
        js_heavy_sites = [
            "https://www.linkedin.com/company/",
            "https://www.crunchbase.com/discover/organization.companies"
        ]
        
        # Add regular business directories
        await crawl_system.add_seed_urls(
            business_directories, 
            job_id="business-directory-crawl-001",
            priority=8,  # High priority
            requires_js=False,
            is_dynamic=False
        )
        
        # Add JavaScript-heavy sites
        await crawl_system.add_seed_urls(
            js_heavy_sites,
            job_id="js-business-sites-001", 
            priority=7,
            requires_js=True,  # Will use headless browser
            is_dynamic=True    # Dynamic content, crawl more frequently
        )
        
        # Let it run and monitor
        for i in range(30):  # Monitor for 30 iterations
            await asyncio.sleep(60)  # Wait 1 minute between checks
            
            # Get enhanced statistics
            stats = await crawl_system.get_system_stats()
            
            print(f"\n=== Enhanced Crawl System Stats (Iteration {i+1}) ===")
            print(f"System Status: {stats['system_status']}")
            print(f"Queue Stats: {stats['queue_stats']}")
            print(f"Crawl Metrics: {stats['crawl_metrics']}")
            print(f"Parse Metrics: {stats['parse_metrics']}")
            print(f"Rate Limiting: {stats['rate_limiting']}")
            
            # Show some interesting metrics
            crawl_metrics = stats['crawl_metrics']
            if crawl_metrics.get('urls_crawled', 0) > 0:
                success_rate = (crawl_metrics.get('urls_crawled', 0) / 
                              (crawl_metrics.get('urls_crawled', 0) + crawl_metrics.get('urls_failed', 0))) * 100
                print(f"Success Rate: {success_rate:.1f}%")
                print(f"JS Rendered Pages: {crawl_metrics.get('js_rendered_pages', 0)}")
                print(f"Large Pages Skipped: {crawl_metrics.get('large_pages_skipped', 0)}")
                print(f"Conditional Requests: {crawl_metrics.get('conditional_requests', 0)}")
                print(f"Not Modified Responses: {crawl_metrics.get('not_modified_responses', 0)}")
        
    finally:
        # Stop the system
        await crawl_system.stop()


if __name__ == "__main__":
    asyncio.run(main())
