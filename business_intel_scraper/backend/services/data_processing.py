"""
Advanced Data Processing Pipeline
Provides comprehensive data processing, validation, and transformation capabilities
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import re
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from urllib.parse import urlparse, urljoin
import html2text
from bs4 import BeautifulSoup
import langdetect
from textstat import flesch_reading_ease, automated_readability_index

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from ..database.config import get_async_session
from ..db.centralized_data import CentralizedDataRecord, DataAnalytics, DataDeduplication
from ..utils.performance import cached, performance_tracked


logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """Data processing status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"


class ValidationLevel(Enum):
    """Data validation levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"


@dataclass
class ProcessingResult:
    """Data processing result container"""
    status: ProcessingStatus
    processed_data: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScrapingTask:
    """Scraping task configuration"""
    task_id: str
    url: str
    job_id: Optional[int] = None
    job_name: Optional[str] = None
    job_type: str = "web_scraping"
    priority: int = 5  # 1-10, 10 being highest
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 30
    validation_level: ValidationLevel = ValidationLevel.STANDARD
    custom_headers: Dict[str, str] = field(default_factory=dict)
    extraction_rules: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProcessingMetrics:
    """Processing pipeline metrics"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    skipped_tasks: int = 0
    avg_processing_time: float = 0.0
    throughput_per_minute: float = 0.0
    error_rate: float = 0.0
    queue_size: int = 0
    active_workers: int = 0
    peak_memory_usage_mb: float = 0.0


class ContentExtractor:
    """Advanced content extraction and processing"""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap lines
        
    def extract_content(self, html_content: str, url: str) -> Dict[str, Any]:
        """Extract structured content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            extracted = {}
            
            # Basic metadata extraction
            extracted['title'] = self._extract_title(soup)
            extracted['description'] = self._extract_description(soup)
            extracted['keywords'] = self._extract_keywords(soup)
            extracted['author'] = self._extract_author(soup)
            extracted['published_date'] = self._extract_published_date(soup)
            
            # Content extraction
            extracted['main_content'] = self._extract_main_content(soup)
            extracted['headings'] = self._extract_headings(soup)
            extracted['links'] = self._extract_links(soup, url)
            extracted['images'] = self._extract_images(soup, url)
            extracted['videos'] = self._extract_videos(soup, url)
            
            # Content analysis
            text_content = extracted['main_content']
            if text_content:
                extracted['word_count'] = len(text_content.split())
                extracted['reading_time_minutes'] = max(1, extracted['word_count'] // 200)
                extracted['language'] = self._detect_language(text_content)
                extracted['readability_score'] = self._calculate_readability(text_content)
                extracted['content_type'] = self._classify_content_type(text_content, soup)
            
            # Technical metadata
            extracted['page_size_bytes'] = len(html_content.encode('utf-8'))
            extracted['load_time_ms'] = 0  # To be set by caller
            
            return extracted
            
        except Exception as e:
            logger.error(f"Content extraction failed for {url}: {e}")
            return {}
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page title"""
        # Try Open Graph title first
        og_title = soup.find('meta', property='og:title')
        if og_title:
            return og_title.get('content', '').strip()
        
        # Try Twitter title
        twitter_title = soup.find('meta', name='twitter:title')
        if twitter_title:
            return twitter_title.get('content', '').strip()
        
        # Fall back to regular title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try h1 as last resort
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return None
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract page description"""
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        
        # Try meta description
        meta_desc = soup.find('meta', name='description')
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try Twitter description
        twitter_desc = soup.find('meta', name='twitter:description')
        if twitter_desc:
            return twitter_desc.get('content', '').strip()
        
        return None
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from meta tags"""
        keywords = []
        
        # Meta keywords
        meta_keywords = soup.find('meta', name='keywords')
        if meta_keywords:
            content = meta_keywords.get('content', '')
            keywords.extend([k.strip() for k in content.split(',') if k.strip()])
        
        # Extract from heading tags
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            text = heading.get_text().strip()
            if text and len(text) < 100:  # Reasonable heading length
                keywords.append(text)
        
        return list(set(keywords))[:20]  # Limit to 20 unique keywords
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information"""
        # Try various author meta tags
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            'meta[name="twitter:creator"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                else:
                    return element.get_text().strip()
        
        return None
    
    def _extract_published_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract published date"""
        # Try various date selectors
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'meta[name="pubdate"]',
            'time[datetime]',
            '.date',
            '.published'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = None
                if element.name == 'meta':
                    date_str = element.get('content')
                elif element.name == 'time':
                    date_str = element.get('datetime') or element.get_text()
                else:
                    date_str = element.get_text()
                
                if date_str:
                    return self._parse_date(date_str.strip())
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        try:
            # Common date formats
            formats = [
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%B %d, %Y',
                '%d %B %Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all formats fail, try dateutil parser
            try:
                from dateutil.parser import parse
                return parse(date_str)
            except:
                pass
                
        except Exception as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Try to find main content areas
        main_selectors = [
            'main',
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.article-content',
            '#content',
            '#main'
        ]
        
        for selector in main_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                text = self.html_converter.handle(str(main_element))
                if len(text.strip()) > 200:  # Reasonable content length
                    return text.strip()
        
        # Fall back to body content
        body = soup.find('body')
        if body:
            text = self.html_converter.handle(str(body))
            return text.strip()
        
        # Last resort: all text
        return soup.get_text().strip()
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract heading structure"""
        headings = []
        for i, heading in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            headings.append({
                'level': int(heading.name[1]),
                'text': heading.get_text().strip(),
                'order': i
            })
        return headings
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract and categorize links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if not href or href.startswith('#'):
                continue
            
            absolute_url = urljoin(base_url, href)
            link_info = {
                'url': absolute_url,
                'text': link.get_text().strip(),
                'title': link.get('title', ''),
                'is_external': urlparse(absolute_url).netloc != urlparse(base_url).netloc
            }
            links.append(link_info)
        
        return links[:100]  # Limit to 100 links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract image information"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if not src:
                continue
            
            absolute_url = urljoin(base_url, src)
            img_info = {
                'url': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', ''),
                'width': img.get('width'),
                'height': img.get('height')
            }
            images.append(img_info)
        
        return images[:50]  # Limit to 50 images
    
    def _extract_videos(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract video information"""
        videos = []
        
        # Look for video tags
        for video in soup.find_all('video'):
            src = video.get('src')
            if not src:
                source = video.find('source')
                if source:
                    src = source.get('src')
            
            if src:
                absolute_url = urljoin(base_url, src)
                videos.append({
                    'url': absolute_url,
                    'type': 'video',
                    'title': video.get('title', '')
                })
        
        # Look for embedded videos (YouTube, Vimeo, etc.)
        iframe_selectors = [
            'iframe[src*="youtube.com"]',
            'iframe[src*="youtu.be"]',
            'iframe[src*="vimeo.com"]',
            'iframe[src*="dailymotion.com"]'
        ]
        
        for selector in iframe_selectors:
            for iframe in soup.select(selector):
                src = iframe.get('src')
                if src:
                    videos.append({
                        'url': urljoin(base_url, src),
                        'type': 'embedded',
                        'title': iframe.get('title', '')
                    })
        
        return videos[:20]  # Limit to 20 videos
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect text language"""
        try:
            if len(text) < 50:  # Too short for reliable detection
                return None
            return langdetect.detect(text)
        except:
            return None
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score"""
        try:
            if len(text) < 100:
                return 0.0
            
            # Use Flesch Reading Ease score (0-100, higher is easier)
            score = flesch_reading_ease(text)
            return max(0.0, min(100.0, score))
        except:
            return 0.0
    
    def _classify_content_type(self, text: str, soup: BeautifulSoup) -> str:
        """Classify content type based on text and HTML structure"""
        # Look for news indicators
        news_indicators = ['published', 'reporter', 'breaking', 'update', 'news']
        if any(indicator in text.lower() for indicator in news_indicators):
            return 'news'
        
        # Look for e-commerce indicators
        ecommerce_indicators = ['price', 'buy', 'cart', 'shipping', 'product']
        if any(indicator in text.lower() for indicator in ecommerce_indicators):
            return 'ecommerce'
        
        # Look for blog indicators
        if soup.find_all(['article', '.blog', '.post']):
            return 'blog'
        
        # Look for social media indicators
        social_indicators = ['share', 'like', 'follow', 'comment', 'post']
        if sum(text.lower().count(indicator) for indicator in social_indicators) > 3:
            return 'social_media'
        
        # Look for academic/research indicators
        academic_indicators = ['abstract', 'methodology', 'conclusion', 'references', 'doi']
        if any(indicator in text.lower() for indicator in academic_indicators):
            return 'academic'
        
        return 'general'


class DataValidator:
    """Comprehensive data validation and quality assessment"""
    
    def __init__(self):
        self.url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def validate_data(self, data: Dict[str, Any], level: ValidationLevel = ValidationLevel.STANDARD) -> ProcessingResult:
        """Validate scraped data based on validation level"""
        result = ProcessingResult(status=ProcessingStatus.PROCESSING)
        
        try:
            if level == ValidationLevel.BASIC:
                self._basic_validation(data, result)
            elif level == ValidationLevel.STANDARD:
                self._standard_validation(data, result)
            elif level == ValidationLevel.COMPREHENSIVE:
                self._comprehensive_validation(data, result)
            elif level == ValidationLevel.STRICT:
                self._strict_validation(data, result)
            
            # Calculate overall quality score
            result.quality_score = self._calculate_quality_score(data, result)
            
            # Determine final status
            if result.validation_errors:
                result.status = ProcessingStatus.FAILED
            elif result.warnings:
                result.status = ProcessingStatus.COMPLETED
            else:
                result.status = ProcessingStatus.COMPLETED
            
        except Exception as e:
            result.status = ProcessingStatus.FAILED
            result.validation_errors.append(f"Validation error: {str(e)}")
            logger.error(f"Data validation failed: {e}")
        
        return result
    
    def _basic_validation(self, data: Dict[str, Any], result: ProcessingResult):
        """Basic validation checks"""
        # Check required fields
        if not data.get('source_url'):
            result.validation_errors.append("Missing source URL")
        elif not self._is_valid_url(data['source_url']):
            result.validation_errors.append("Invalid source URL format")
        
        # Check for some content
        if not any([data.get('raw_data'), data.get('title'), data.get('extracted_text')]):
            result.validation_errors.append("No content data found")
    
    def _standard_validation(self, data: Dict[str, Any], result: ProcessingResult):
        """Standard validation checks"""
        self._basic_validation(data, result)
        
        # URL validation
        url = data.get('source_url', '')
        if url and len(url) > 2048:
            result.warnings.append("URL exceeds recommended length")
        
        # Content validation
        title = data.get('title', '')
        if title and len(title) > 500:
            result.warnings.append("Title exceeds recommended length")
        
        extracted_text = data.get('extracted_text', '')
        if extracted_text:
            if len(extracted_text) < 50:
                result.warnings.append("Extracted text is very short")
            elif len(extracted_text) > 1000000:  # 1MB
                result.warnings.append("Extracted text is very large")
        
        # Data type validation
        data_type = data.get('data_type', '')
        valid_types = ['news', 'ecommerce', 'blog', 'social_media', 'academic', 'general']
        if data_type and data_type not in valid_types:
            result.warnings.append(f"Unknown data type: {data_type}")
        
        # Language validation
        language = data.get('language', '')
        if language and len(language) > 10:
            result.warnings.append("Language code seems invalid")
    
    def _comprehensive_validation(self, data: Dict[str, Any], result: ProcessingResult):
        """Comprehensive validation checks"""
        self._standard_validation(data, result)
        
        # Content quality checks
        extracted_text = data.get('extracted_text', '')
        if extracted_text:
            # Check for suspicious patterns
            if self._has_suspicious_patterns(extracted_text):
                result.warnings.append("Content contains suspicious patterns")
            
            # Check content diversity
            if self._is_repetitive_content(extracted_text):
                result.warnings.append("Content appears repetitive or low quality")
        
        # Metadata validation
        word_count = data.get('word_count', 0)
        if isinstance(word_count, int) and word_count < 0:
            result.validation_errors.append("Invalid word count")
        
        # Date validation
        scraped_at = data.get('scraped_at')
        if scraped_at and isinstance(scraped_at, datetime):
            if scraped_at > datetime.utcnow() + timedelta(minutes=5):
                result.validation_errors.append("Scraped date is in the future")
        
        # Quality score validation
        quality_score = data.get('data_quality_score', 0)
        if isinstance(quality_score, (int, float)) and not (0 <= quality_score <= 100):
            result.validation_errors.append("Quality score out of valid range")
    
    def _strict_validation(self, data: Dict[str, Any], result: ProcessingResult):
        """Strict validation checks"""
        self._comprehensive_validation(data, result)
        
        # Mandatory fields in strict mode
        required_fields = ['title', 'extracted_text', 'data_type', 'source_job_id']
        for field in required_fields:
            if not data.get(field):
                result.validation_errors.append(f"Required field missing: {field}")
        
        # Strict content requirements
        extracted_text = data.get('extracted_text', '')
        if extracted_text and len(extracted_text) < 100:
            result.validation_errors.append("Insufficient content for strict validation")
        
        # Strict quality requirements
        quality_score = data.get('data_quality_score', 0)
        if isinstance(quality_score, (int, float)) and quality_score < 50:
            result.validation_errors.append("Quality score below strict threshold")
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        return bool(self.url_pattern.match(url))
    
    def _has_suspicious_patterns(self, text: str) -> bool:
        """Check for suspicious content patterns"""
        # Check for excessive repetition
        words = text.lower().split()
        if len(words) > 50:
            word_counts = defaultdict(int)
            for word in words:
                word_counts[word] += 1
            
            # If any word appears more than 10% of the time, it's suspicious
            max_count = max(word_counts.values())
            if max_count > len(words) * 0.1:
                return True
        
        # Check for excessive special characters
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if len(text) > 0 and special_chars / len(text) > 0.3:
            return True
        
        return False
    
    def _is_repetitive_content(self, text: str) -> bool:
        """Check if content is repetitive"""
        if len(text) < 200:
            return False
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) < 3:
            return False
        
        # Check for duplicate sentences
        unique_sentences = set(s.strip().lower() for s in sentences if s.strip())
        if len(unique_sentences) < len(sentences) * 0.7:  # Less than 70% unique
            return True
        
        return False
    
    def _calculate_quality_score(self, data: Dict[str, Any], result: ProcessingResult) -> float:
        """Calculate data quality score"""
        score = 100.0
        
        # Deduct points for errors and warnings
        score -= len(result.validation_errors) * 20
        score -= len(result.warnings) * 5
        
        # Content quality factors
        extracted_text = data.get('extracted_text', '')
        if extracted_text:
            # Reward good content length
            text_length = len(extracted_text)
            if 200 <= text_length <= 10000:
                score += 10
            elif text_length < 100:
                score -= 20
        
        # Metadata completeness
        important_fields = ['title', 'data_type', 'language', 'word_count']
        filled_fields = sum(1 for field in important_fields if data.get(field))
        score += (filled_fields / len(important_fields)) * 20
        
        return max(0.0, min(100.0, score))


class ProcessingPipeline:
    """Main data processing pipeline coordinator"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=500)
        self.workers: List[asyncio.Task] = []
        self.metrics = ProcessingMetrics()
        self.content_extractor = ContentExtractor()
        self.data_validator = DataValidator()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        
    async def start(self):
        """Start the processing pipeline"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        # Start priority worker
        priority_worker = asyncio.create_task(self._priority_worker())
        self.workers.append(priority_worker)
        
        # Start metrics collector
        metrics_worker = asyncio.create_task(self._metrics_collector())
        self.workers.append(metrics_worker)
        
        logger.info(f"Processing pipeline started with {self.max_workers} workers")
    
    async def stop(self):
        """Stop the processing pipeline"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("Processing pipeline stopped")
    
    async def submit_task(self, task: ScrapingTask) -> str:
        """Submit a scraping task for processing"""
        try:
            if task.priority >= 8:  # High priority tasks
                await self.priority_queue.put((10 - task.priority, task))
            else:
                await self.task_queue.put(task)
            
            self.metrics.total_tasks += 1
            self.metrics.queue_size = self.task_queue.qsize() + self.priority_queue.qsize()
            
            logger.info(f"Task {task.task_id} submitted for processing")
            return task.task_id
            
        except asyncio.QueueFull:
            logger.error(f"Task queue full, rejecting task {task.task_id}")
            raise RuntimeError("Processing queue is full")
    
    async def _worker(self, worker_id: str):
        """Worker coroutine for processing tasks"""
        logger.info(f"Worker {worker_id} started")
        
        while self.is_running:
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=5.0
                )
                
                await self._process_task(task, worker_id)
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue  # No task available, continue loop
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def _priority_worker(self):
        """High-priority task worker"""
        logger.info("Priority worker started")
        
        while self.is_running:
            try:
                # Wait for priority task
                priority, task = await asyncio.wait_for(
                    self.priority_queue.get(),
                    timeout=5.0
                )
                
                await self._process_task(task, "priority-worker")
                self.priority_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Priority worker error: {e}")
        
        logger.info("Priority worker stopped")
    
    async def _process_task(self, task: ScrapingTask, worker_id: str):
        """Process a single scraping task"""
        start_time = time.perf_counter()
        
        try:
            logger.debug(f"Worker {worker_id} processing task {task.task_id}")
            
            # Scrape the URL
            scraped_data = await self._scrape_url(task)
            
            if not scraped_data:
                self.metrics.failed_tasks += 1
                return
            
            # Extract and process content
            extracted_content = await self._extract_content(scraped_data, task)
            
            # Validate data
            validation_result = self.data_validator.validate_data(
                extracted_content, task.validation_level
            )
            
            if validation_result.status == ProcessingStatus.FAILED:
                logger.warning(f"Task {task.task_id} validation failed: {validation_result.validation_errors}")
                self.metrics.failed_tasks += 1
                return
            
            # Store in database
            await self._store_data(extracted_content, task, validation_result)
            
            # Update metrics
            processing_time = (time.perf_counter() - start_time) * 1000
            self.metrics.completed_tasks += 1
            self._update_processing_metrics(processing_time)
            
            logger.info(f"Task {task.task_id} completed successfully in {processing_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} processing failed: {e}")
            self.metrics.failed_tasks += 1
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                await self.submit_task(task)
    
    async def _scrape_url(self, task: ScrapingTask) -> Optional[Dict[str, Any]]:
        """Scrape content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                **task.custom_headers
            }
            
            timeout = aiohttp.ClientTimeout(total=task.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(task.url, headers=headers) as response:
                    if response.status != 200:
                        logger.warning(f"HTTP {response.status} for {task.url}")
                        return None
                    
                    content = await response.text()
                    
                    return {
                        'url': str(response.url),
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'content': content,
                        'content_type': response.headers.get('content-type', ''),
                        'content_length': len(content)
                    }
                    
        except Exception as e:
            logger.error(f"Failed to scrape {task.url}: {e}")
            return None
    
    async def _extract_content(self, scraped_data: Dict[str, Any], task: ScrapingTask) -> Dict[str, Any]:
        """Extract structured content from scraped data"""
        # Run content extraction in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        extracted = await loop.run_in_executor(
            self.executor,
            self.content_extractor.extract_content,
            scraped_data['content'],
            scraped_data['url']
        )
        
        # Combine with scraped metadata
        result = {
            'source_url': scraped_data['url'],
            'source_job_id': task.job_id,
            'source_job_name': task.job_name,
            'source_job_type': task.job_type,
            'raw_data': {
                'http_status': scraped_data['status_code'],
                'headers': scraped_data['headers'],
                'content_type': scraped_data['content_type'],
                'content_length': scraped_data['content_length']
            },
            'scraped_at': datetime.utcnow(),
            **extracted
        }
        
        # Extract domain
        try:
            result['source_domain'] = urlparse(scraped_data['url']).netloc
        except:
            result['source_domain'] = 'unknown'
        
        # Set processed data
        result['processed_data'] = {
            'extraction_method': 'automated',
            'extraction_timestamp': datetime.utcnow().isoformat(),
            'processing_pipeline_version': '1.0.0'
        }
        
        return result
    
    async def _store_data(self, data: Dict[str, Any], task: ScrapingTask, validation_result: ProcessingResult):
        """Store processed data in database"""
        try:
            async with get_async_session() as session:
                # Create centralized data record
                record = CentralizedDataRecord()
                
                # Set basic fields
                for key, value in data.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
                
                # Set validation results
                record.data_quality_score = validation_result.quality_score
                record.validation_status = "valid" if validation_result.status == ProcessingStatus.COMPLETED else "invalid"
                record.validation_notes = json.dumps({
                    'errors': validation_result.validation_errors,
                    'warnings': validation_result.warnings
                })
                
                # Generate content hash for deduplication
                record.content_hash = record.generate_content_hash()
                
                # Calculate quality scores
                record.calculate_quality_scores()
                
                # Add to session and commit
                session.add(record)
                await session.commit()
                await session.refresh(record)
                
                logger.debug(f"Stored record {record.record_uuid} for task {task.task_id}")
                
        except Exception as e:
            logger.error(f"Failed to store data for task {task.task_id}: {e}")
            raise
    
    def _update_processing_metrics(self, processing_time: float):
        """Update processing performance metrics"""
        # Update average processing time
        total_completed = self.metrics.completed_tasks
        if total_completed == 1:
            self.metrics.avg_processing_time = processing_time
        else:
            self.metrics.avg_processing_time = (
                (self.metrics.avg_processing_time * (total_completed - 1) + processing_time) 
                / total_completed
            )
        
        # Update error rate
        total_processed = self.metrics.completed_tasks + self.metrics.failed_tasks
        if total_processed > 0:
            self.metrics.error_rate = (self.metrics.failed_tasks / total_processed) * 100
    
    async def _metrics_collector(self):
        """Collect and update pipeline metrics"""
        while self.is_running:
            try:
                # Update queue size
                self.metrics.queue_size = self.task_queue.qsize() + self.priority_queue.qsize()
                
                # Update active workers
                self.metrics.active_workers = len([w for w in self.workers if not w.done()])
                
                # Calculate throughput (tasks per minute)
                if self.metrics.completed_tasks > 0:
                    # This is a simplified calculation; in production you'd track over time
                    self.metrics.throughput_per_minute = self.metrics.completed_tasks
                
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(5)
    
    def get_metrics(self) -> ProcessingMetrics:
        """Get current pipeline metrics"""
        return self.metrics
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get detailed queue status"""
        return {
            'regular_queue_size': self.task_queue.qsize(),
            'priority_queue_size': self.priority_queue.qsize(),
            'total_queue_size': self.metrics.queue_size,
            'active_workers': self.metrics.active_workers,
            'max_workers': self.max_workers,
            'is_running': self.is_running
        }


# Global processing pipeline instance
processing_pipeline = ProcessingPipeline()


# Convenience functions for external use
async def submit_scraping_task(
    url: str,
    job_id: Optional[int] = None,
    job_name: Optional[str] = None,
    priority: int = 5,
    validation_level: ValidationLevel = ValidationLevel.STANDARD,
    **kwargs
) -> str:
    """Submit a scraping task to the processing pipeline"""
    task = ScrapingTask(
        task_id=str(uuid.uuid4()),
        url=url,
        job_id=job_id,
        job_name=job_name,
        priority=priority,
        validation_level=validation_level,
        **kwargs
    )
    
    return await processing_pipeline.submit_task(task)


async def get_processing_metrics() -> ProcessingMetrics:
    """Get current processing pipeline metrics"""
    return processing_pipeline.get_metrics()


async def start_processing_pipeline():
    """Start the processing pipeline"""
    await processing_pipeline.start()


async def stop_processing_pipeline():
    """Stop the processing pipeline"""
    await processing_pipeline.stop()
