"""
Centralized Data Management for Business Intelligence Scraper

This module provides comprehensive data models for the Business Intelligence Scraper Platform,
implementing a centralized data architecture with advanced analytics, monitoring, and alerting
capabilities.

Key Components:
- CentralizedDataRecord: Core data storage with quality metrics and validation
- SystemMetrics: Performance monitoring and observability data
- AlertRecord: Comprehensive alerting and notification system
- DataAnalytics: Precomputed analytics for dashboard performance
- PerformanceBaseline: Anomaly detection and capacity planning

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

# Standard library imports
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union

# Third-party imports
from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, ForeignKey, Index, 
    Text, Boolean, Float, BigInteger, Numeric
)
from sqlalchemy.orm import relationship, DeclarativeBase, Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func


# Configuration and Constants
class DataConstants:
    """Central configuration for data management constants"""
    
    # Data Quality Thresholds
    MIN_QUALITY_SCORE = 0.7
    CRITICAL_QUALITY_THRESHOLD = 0.5
    EXCELLENT_QUALITY_THRESHOLD = 0.95
    
    # Performance Metrics
    DEFAULT_RESPONSE_TIME_THRESHOLD = 5.0  # seconds
    MAX_MEMORY_USAGE_MB = 1024
    CPU_USAGE_WARNING_THRESHOLD = 80.0  # percentage
    
    # Alert Severity Levels
    ALERT_LEVELS = {
        'LOW': 1,
        'MEDIUM': 2,
        'HIGH': 3,
        'CRITICAL': 4,
        'EMERGENCY': 5
    }
    
    # Data Retention Policies
    RETENTION_DAYS = {
        'raw_data': 90,
        'analytics': 365,
        'alerts': 30,
        'performance_metrics': 180
    }


class Base(DeclarativeBase):
    """Enhanced base class with common functionality"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model instance from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class CentralizedDataRecord(Base):
    """
    Enhanced central repository for all scraped data points.
    
    This model serves as the core data storage entity with comprehensive
    metadata, quality metrics, and analytics capabilities. It implements
    a standardized data structure for cross-job analytics and unified
    data access patterns.
    
    Key Features:
    - Source tracking and metadata
    - Data quality and validation metrics
    - Content analytics and engagement metrics
    - Comprehensive indexing for performance
    - Privacy and compliance features
    """

    __tablename__ = "centralized_data"

    # === PRIMARY IDENTIFIERS ===
    id = Column(Integer, primary_key=True, index=True)
    record_uuid = Column(
        String(36), 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True,
        doc="Unique identifier for external API access"
    )

    # === SOURCE TRACKING METADATA ===
    source_job_id = Column(Integer, index=True, doc="Reference to originating scraping job")
    source_job_name = Column(String(255), index=True, doc="Human-readable job identifier")
    source_job_type = Column(String(50), index=True, doc="Job type classification")
    source_url = Column(String(2048), index=True, doc="Original URL of scraped content")
    source_domain = Column(String(255), index=True, doc="Extracted domain for analytics")
    
    # === DATA CONTENT FIELDS ===
    raw_data = Column(JSON, doc="Original unprocessed scraped data")
    processed_data = Column(JSON, doc="Cleaned and structured data version")
    extracted_text = Column(Text, doc="Clean text for full-text search capabilities")
    title = Column(String(500), index=True, doc="Extracted title or headline")
    summary = Column(Text, doc="AI-generated or extracted summary")
    
    # === CLASSIFICATION AND METADATA ===
    data_type = Column(String(50), index=True, doc="Content type: news, ecommerce, social_media")
    content_category = Column(String(100), index=True, doc="Detailed content categorization")
    language = Column(String(10), index=True, doc="ISO language code")
    content_hash = Column(String(64), index=True, doc="SHA-256 hash for deduplication")
    
    # === TEMPORAL TRACKING ===
    scraped_at = Column(DateTime, index=True, doc="Original scraping timestamp")
    centralized_at = Column(DateTime, default=datetime.utcnow, index=True, doc="Storage timestamp")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last modification")
    content_published_at = Column(DateTime, index=True, doc="Original publication date")
    
    # === QUALITY AND VALIDATION METRICS ===
    data_quality_score = Column(Float, default=0.0, doc="Overall quality score (0.0-100.0)")
    completeness_score = Column(Float, default=0.0, doc="Data completeness percentage")
    reliability_score = Column(Float, default=0.0, doc="Source reliability assessment")
    validation_status = Column(String(20), default="pending", doc="Validation state")
    validation_notes = Column(Text, doc="Detailed validation information")
    
    # === CONTENT ANALYTICS ===
    word_count = Column(Integer, default=0, doc="Total word count")
    link_count = Column(Integer, default=0, doc="Number of hyperlinks")
    image_count = Column(Integer, default=0, doc="Number of images")
    video_count = Column(Integer, default=0, doc="Number of videos")
    file_size_bytes = Column(BigInteger, default=0, doc="Content size in bytes")
    
    # === ENGAGEMENT METRICS ===
    view_count = Column(BigInteger, default=0, doc="View/impression count")
    share_count = Column(Integer, default=0, doc="Social sharing count")
    like_count = Column(Integer, default=0, doc="Like/reaction count")
    comment_count = Column(Integer, default=0, doc="Comment count")
    
    # === PROCESSING AND STORAGE METADATA ===
    processing_duration_ms = Column(Integer, default=0, doc="Processing time in milliseconds")
    storage_location = Column(String(500), doc="External file storage path")
    is_archived = Column(Boolean, default=False, doc="Archive status")
    is_sensitive = Column(Boolean, default=False, doc="Contains sensitive data flag")
    
    # === PERFORMANCE OPTIMIZED INDEXING ===
    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_source_tracking", "source_job_id", "source_job_name"),
        Index("idx_content_classification", "data_type", "content_category"),
        Index("idx_temporal_analysis", "scraped_at", "centralized_at"),
        Index("idx_quality_metrics", "data_quality_score", "validation_status"),
        Index("idx_domain_analytics", "source_domain", "data_type"),
        Index("idx_language_content", "language", "content_category"),
        Index("idx_privacy_compliance", "validation_status", "is_sensitive"),
        Index("idx_content_discovery", "content_published_at", "data_type"),
        Index("idx_analytics_performance", "view_count", "share_count"),
        # Full-text search optimization
        Index("idx_content_search", "title", "extracted_text"),
    )
    
    # === COMPUTED PROPERTIES ===
    @property
    def overall_quality_score(self) -> float:
        """Computed overall quality score combining all quality metrics"""
        quality = getattr(self, 'data_quality_score', 0) or 0
        completeness = getattr(self, 'completeness_score', 0) or 0
        reliability = getattr(self, 'reliability_score', 0) or 0
        
        if not all([quality, completeness, reliability]):
            return 0.0
        return quality * 0.4 + completeness * 0.3 + reliability * 0.3
    
    @property
    def engagement_score(self) -> float:
        """Computed engagement score based on social metrics"""
        views = getattr(self, 'view_count', 0) or 0
        shares = getattr(self, 'share_count', 0) or 0
        likes = getattr(self, 'like_count', 0) or 0
        comments = getattr(self, 'comment_count', 0) or 0
        
        total_engagement = (
            views * 0.1 + shares * 2.0 + likes * 1.0 + comments * 3.0
        )
        return min(total_engagement, 100.0)
    
    @property
    def content_richness(self) -> float:
        """Computed content richness based on media elements"""
        word_count = getattr(self, 'word_count', 0) or 0
        image_count = getattr(self, 'image_count', 0) or 0
        video_count = getattr(self, 'video_count', 0) or 0
        
        richness_score = 0.0
        if word_count > 0:
            richness_score += min(word_count / 500.0, 1.0) * 40
        if image_count > 0:
            richness_score += min(image_count * 10, 30)
        if video_count > 0:
            richness_score += min(video_count * 20, 30)
        return min(richness_score, 100.0)
    
    @property
    def is_high_quality(self) -> bool:
        """Boolean indicator for high-quality content"""
        return (
            self.overall_quality_score >= DataConstants.EXCELLENT_QUALITY_THRESHOLD and
            getattr(self, 'validation_status', '') == "valid"
        )
    
    # === BUSINESS LOGIC METHODS ===
    
    def generate_content_hash(self) -> str:
        """Generate content hash for deduplication"""
        # Get actual values from the instance
        extracted_text = getattr(self, 'extracted_text', None)
        raw_data = getattr(self, 'raw_data', None)
        source_url = getattr(self, 'source_url', None)
        
        if extracted_text:
            content = extracted_text.strip().lower()
        elif raw_data:
            content = json.dumps(raw_data, sort_keys=True)
        else:
            content = str(source_url) if source_url else ""
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def calculate_quality_scores(self) -> None:
        """
        Calculate comprehensive quality metrics based on content analysis.
        
        This method evaluates multiple dimensions of data quality including
        completeness, content richness, metadata availability, and structural
        integrity to provide actionable quality metrics.
        """
        try:
            # Safely extract all attributes
            title = getattr(self, 'title', None)
            extracted_text = getattr(self, 'extracted_text', None) 
            source_url = getattr(self, 'source_url', None)
            data_type = getattr(self, 'data_type', None)
            content_category = getattr(self, 'content_category', None)
            language = getattr(self, 'language', None)
            scraped_at = getattr(self, 'scraped_at', None)
            word_count = getattr(self, 'word_count', 0) or 0
            content_published_at = getattr(self, 'content_published_at', None)
            raw_data = getattr(self, 'raw_data', None)
            
            # === COMPLETENESS SCORE CALCULATION ===
            essential_fields = [
                bool(title and title.strip()),
                bool(extracted_text and extracted_text.strip()),
                bool(source_url),
                bool(data_type),
                bool(content_category),
                bool(language),
                bool(scraped_at),
                bool(word_count > 0),
                bool(content_published_at),
                bool(raw_data)
            ]
            self.completeness_score = (sum(essential_fields) / len(essential_fields)) * 100.0
            
            # === DATA QUALITY SCORE CALCULATION ===
            quality_factors = []
            
            # Content Quality Assessment
            if extracted_text and extracted_text.strip():
                text_length = len(extracted_text.strip())
                if text_length >= 500:
                    quality_factors.append(90.0)  # Excellent content
                elif text_length >= 200:
                    quality_factors.append(75.0)  # Good content
                elif text_length >= 50:
                    quality_factors.append(55.0)  # Acceptable content
                else:
                    quality_factors.append(25.0)  # Poor content
            
            # URL Validity Assessment
            if source_url:
                if len(source_url) > 10 and '.' in source_url:
                    quality_factors.append(85.0)  # Valid URL structure
                else:
                    quality_factors.append(40.0)  # Questionable URL
            
            # Title Quality Assessment
            if title and title.strip():
                title_length = len(title.strip())
                if 10 <= title_length <= 200:
                    quality_factors.append(80.0)  # Optimal title length
                elif title_length > 5:
                    quality_factors.append(60.0)  # Acceptable title
                else:
                    quality_factors.append(30.0)  # Poor title
            
            # Metadata Completeness
            if data_type and content_category and language:
                quality_factors.append(75.0)  # Complete metadata
            elif data_type or content_category:
                quality_factors.append(50.0)  # Partial metadata
            
            # Calculate final quality score
            self.data_quality_score = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
            
            # === RELIABILITY SCORE CALCULATION ===
            # Base reliability on source characteristics and data consistency
            reliability_factors = []
            
            # Source URL reliability
            if source_url:
                domain = source_url.split('/')[2] if '//' in source_url else source_url
                if any(tld in domain for tld in ['.edu', '.gov', '.org']):
                    reliability_factors.append(95.0)  # High-trust domains
                elif any(tld in domain for tld in ['.com', '.net']):
                    reliability_factors.append(70.0)  # Standard domains
                else:
                    reliability_factors.append(50.0)  # Unknown domains
            
            # Content consistency
            if all([title, extracted_text, word_count > 0]):
                estimated_words = len(extracted_text.split()) if extracted_text else 0
                word_count_accuracy = 1.0 - abs(estimated_words - word_count) / max(estimated_words, 1)
                reliability_factors.append(word_count_accuracy * 80.0)
            
            # Timestamp consistency
            if scraped_at and content_published_at:
                if scraped_at >= content_published_at:
                    reliability_factors.append(90.0)  # Logical timestamp order
                else:
                    reliability_factors.append(30.0)  # Inconsistent timestamps
            
            self.reliability_score = sum(reliability_factors) / len(reliability_factors) if reliability_factors else 50.0
                
        except Exception as e:
            # Fallback to safe defaults on any calculation error
            self.data_quality_score = 0.0
            self.completeness_score = 0.0
            self.reliability_score = 0.0
    
    def update_content_hash(self) -> None:
        """Update the content hash for deduplication purposes"""
        self.content_hash = self.generate_content_hash()
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Comprehensive data validation with detailed results.
        
        Returns:
            Dict containing validation results and recommendations
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Required field validation
        if not getattr(self, 'source_url', None):
            validation_results['errors'].append("Missing source URL")
            validation_results['is_valid'] = False
        
        if not getattr(self, 'data_type', None):
            validation_results['warnings'].append("Data type not specified")
        
        # Content validation
        extracted_text = getattr(self, 'extracted_text', None)
        if not extracted_text or len(extracted_text.strip()) < 10:
            validation_results['warnings'].append("Very short or missing content")
        
        # Quality thresholds
        if self.overall_quality_score < DataConstants.MIN_QUALITY_SCORE:
            validation_results['recommendations'].append(
                f"Quality score ({self.overall_quality_score:.1f}) below threshold "
                f"({DataConstants.MIN_QUALITY_SCORE})"
            )
        
        # Update validation status
        if validation_results['errors']:
            self.validation_status = "invalid"
        elif validation_results['warnings']:
            self.validation_status = "flagged"
        else:
            self.validation_status = "valid"
        
        return validation_results


# === ADVANCED DATA MODELS ===


class DataAnalytics(Base):
    """
    Precomputed analytics and aggregated metrics for dashboard performance.
    
    This model stores pre-calculated statistics to avoid expensive real-time
    computations on large datasets. Analytics are updated periodically via
    background tasks to ensure dashboard responsiveness.
    
    Key Features:
    - Time-based aggregations (daily, weekly, monthly)
    - Content type breakdowns and trends
    - Quality metrics and performance indicators
    - Source diversity and reliability metrics
    """

    __tablename__ = "data_analytics"

    # === PRIMARY IDENTIFIERS ===
    id = Column(Integer, primary_key=True, index=True)
    analytics_uuid = Column(
        String(36), 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )

    # === TEMPORAL DIMENSIONS ===
    date = Column(DateTime, index=True, doc="Analysis date")
    period_type = Column(String(20), index=True, doc="Aggregation period: daily, weekly, monthly")
    period_start = Column(DateTime, index=True, doc="Period start timestamp")
    period_end = Column(DateTime, index=True, doc="Period end timestamp")

    # === VOLUME METRICS ===
    total_records = Column(BigInteger, default=0, doc="Total records processed")
    total_jobs = Column(Integer, default=0, doc="Total scraping jobs executed")
    unique_sources = Column(Integer, default=0, doc="Unique source domains")
    new_records = Column(BigInteger, default=0, doc="New records in period")
    updated_records = Column(BigInteger, default=0, doc="Updated records in period")

    # === QUALITY METRICS ===
    avg_quality_score = Column(Numeric(5, 2), default=0.0, doc="Average quality score")
    avg_completeness_score = Column(Numeric(5, 2), default=0.0, doc="Average completeness")
    avg_reliability_score = Column(Numeric(5, 2), default=0.0, doc="Average reliability")
    high_quality_records = Column(BigInteger, default=0, doc="High-quality record count")
    flagged_records = Column(BigInteger, default=0, doc="Flagged record count")

    # === CONTENT TYPE BREAKDOWN ===
    news_records = Column(BigInteger, default=0, doc="News content records")
    ecommerce_records = Column(BigInteger, default=0, doc="E-commerce records")
    social_media_records = Column(BigInteger, default=0, doc="Social media records")
    blog_records = Column(BigInteger, default=0, doc="Blog content records")
    forum_records = Column(BigInteger, default=0, doc="Forum discussion records")
    other_records = Column(BigInteger, default=0, doc="Other content types")

    # === PERFORMANCE METRICS ===
    avg_processing_time_ms = Column(Integer, default=0, doc="Average processing time")
    max_processing_time_ms = Column(Integer, default=0, doc="Maximum processing time")
    min_processing_time_ms = Column(Integer, default=0, doc="Minimum processing time")
    success_rate = Column(Numeric(5, 2), default=0.0, doc="Success rate percentage")
    error_rate = Column(Numeric(5, 2), default=0.0, doc="Error rate percentage")

    # === CONTENT ANALYTICS ===
    total_words = Column(BigInteger, default=0, doc="Total word count")
    total_images = Column(BigInteger, default=0, doc="Total image count")
    total_videos = Column(BigInteger, default=0, doc="Total video count")
    total_links = Column(BigInteger, default=0, doc="Total link count")
    avg_content_length = Column(Integer, default=0, doc="Average content length")

    # === ENGAGEMENT METRICS ===
    total_views = Column(BigInteger, default=0, doc="Total view count")
    total_shares = Column(BigInteger, default=0, doc="Total share count")
    total_likes = Column(BigInteger, default=0, doc="Total like count")
    total_comments = Column(BigInteger, default=0, doc="Total comment count")
    avg_engagement_score = Column(Numeric(5, 2), default=0.0, doc="Average engagement")

    # === TEMPORAL TRACKING ===
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # === INDEXING FOR PERFORMANCE ===
    __table_args__ = (
        Index("idx_period_analytics", "period_type", "date"),
        Index("idx_performance_metrics", "success_rate", "avg_processing_time_ms"),
        Index("idx_quality_analytics", "avg_quality_score", "high_quality_records"),
        Index("idx_temporal_lookup", "period_start", "period_end"),
    )

    # === COMPUTED PROPERTIES ===
    @property
    def total_content_items(self) -> int:
        """Total multimedia content items"""
        images = getattr(self, 'total_images', 0) or 0
        videos = getattr(self, 'total_videos', 0) or 0
        return images + videos
    
    @property
    def content_diversity_score(self) -> float:
        """Content type diversity score"""
        content_counts = [
            getattr(self, 'news_records', 0) or 0,
            getattr(self, 'ecommerce_records', 0) or 0,
            getattr(self, 'social_media_records', 0) or 0,
            getattr(self, 'blog_records', 0) or 0,
            getattr(self, 'forum_records', 0) or 0,
            getattr(self, 'other_records', 0) or 0
        ]
        non_zero_types = sum(1 for count in content_counts if count > 0)
        return (non_zero_types / 6.0) * 100.0  # Max 6 content types


class DataDeduplication(Base):
    """
    Advanced duplicate detection and content deduplication tracking.
    
    This model manages content deduplication across different sources and
    time periods, helping maintain data quality and storage efficiency.
    
    Key Features:
    - Content hash-based deduplication
    - Similarity scoring and clustering
    - Source attribution and conflict resolution
    - Deduplication performance metrics
    """

    __tablename__ = "data_deduplication"

    # === PRIMARY IDENTIFIERS ===
    id = Column(Integer, primary_key=True, index=True)
    dedup_uuid = Column(
        String(36), 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )

    # === CONTENT IDENTIFICATION ===
    content_hash = Column(String(64), index=True, doc="SHA-256 content hash")
    canonical_record_id = Column(
        Integer, 
        ForeignKey("centralized_data.id"), 
        doc="Primary record ID for duplicates"
    )
    duplicate_record_ids = Column(JSON, doc="List of duplicate record IDs")

    # === SIMILARITY METRICS ===
    similarity_score = Column(
        Numeric(5, 2), 
        default=0.0, 
        doc="Content similarity score (0.0-100.0)"
    )
    dedup_method = Column(
        String(50), 
        index=True, 
        doc="Deduplication method: hash, content_similarity, url_similarity"
    )
    confidence_level = Column(
        Numeric(5, 2), 
        default=0.0, 
        doc="Confidence in deduplication decision"
    )

    # === RESOLUTION METADATA ===
    resolution_strategy = Column(String(50), doc="How duplicates were resolved")
    manual_review_required = Column(Boolean, default=False, doc="Requires human review")
    reviewer_notes = Column(Text, doc="Manual review annotations")

    # === TEMPORAL TRACKING ===
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, doc="When deduplication was resolved")

    # === RELATIONSHIPS ===
    canonical_record = relationship("CentralizedDataRecord", backref="duplicates")

    # === INDEXING ===
    __table_args__ = (
        Index("idx_content_dedup", "content_hash", "similarity_score"),
        Index("idx_resolution_tracking", "dedup_method", "detected_at"),
    )


class SystemMetrics(Base):
    """
    Comprehensive system performance and observability metrics.
    
    This model tracks detailed system health, performance indicators,
    and application-specific metrics to enable proactive monitoring,
    alerting, and capacity planning.
    
    Key Features:
    - System resource monitoring (CPU, memory, disk, network)
    - Application performance metrics
    - Database and cache performance
    - Business logic metrics and KPIs
    """
    
    __tablename__ = "system_metrics"
    
    # === PRIMARY IDENTIFIERS ===
    id = Column(Integer, primary_key=True, index=True)
    metric_uuid = Column(
        String(36), 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    
    # === COLLECTION METADATA ===
    collected_at = Column(DateTime, default=datetime.utcnow, index=True)
    collection_source = Column(String(100), index=True, doc="Source: API, scraper, background_task")
    collection_context = Column(String(200), doc="Additional context")
    hostname = Column(String(255), index=True, doc="Server hostname")
    environment = Column(String(50), index=True, doc="Environment: production, staging, development")
    
    # === SYSTEM RESOURCE METRICS ===
    cpu_percent = Column(Numeric(5, 2), default=0.0, doc="CPU usage percentage")
    cpu_load_1min = Column(Numeric(8, 4), default=0.0, doc="1-minute load average")
    cpu_load_5min = Column(Numeric(8, 4), default=0.0, doc="5-minute load average")
    cpu_load_15min = Column(Numeric(8, 4), default=0.0, doc="15-minute load average")
    
    memory_percent = Column(Numeric(5, 2), default=0.0, doc="Memory usage percentage")
    memory_used_mb = Column(BigInteger, default=0, doc="Used memory in MB")
    memory_available_mb = Column(BigInteger, default=0, doc="Available memory in MB")
    memory_cached_mb = Column(BigInteger, default=0, doc="Cached memory in MB")
    memory_buffers_mb = Column(BigInteger, default=0, doc="Buffer memory in MB")
    
    disk_usage_percent = Column(Numeric(5, 2), default=0.0, doc="Disk usage percentage")
    disk_free_gb = Column(BigInteger, default=0, doc="Free disk space in GB")
    disk_total_gb = Column(BigInteger, default=0, doc="Total disk space in GB")
    
    # === NETWORK AND I/O METRICS ===
    network_connections_count = Column(Integer, default=0, doc="Active network connections")
    network_io_bytes_sent = Column(BigInteger, default=0, doc="Network bytes sent")
    network_io_bytes_recv = Column(BigInteger, default=0, doc="Network bytes received")
    disk_io_read_bytes = Column(BigInteger, default=0, doc="Disk bytes read")
    disk_io_write_bytes = Column(BigInteger, default=0, doc="Disk bytes written")
    disk_io_read_ops = Column(BigInteger, default=0, doc="Disk read operations")
    disk_io_write_ops = Column(BigInteger, default=0, doc="Disk write operations")
    
    # === APPLICATION PERFORMANCE METRICS ===
    active_threads = Column(Integer, default=0, doc="Active thread count")
    thread_pool_size = Column(Integer, default=0, doc="Thread pool size")
    open_file_descriptors = Column(Integer, default=0, doc="Open file descriptors")
    max_file_descriptors = Column(Integer, default=0, doc="Maximum file descriptors")
    
    # === DATABASE METRICS ===
    database_connections_active = Column(Integer, default=0, doc="Active DB connections")
    database_connections_idle = Column(Integer, default=0, doc="Idle DB connections")
    database_connections_total = Column(Integer, default=0, doc="Total DB connections")
    database_query_avg_time_ms = Column(Numeric(10, 3), default=0.0, doc="Average query time")
    database_slow_queries = Column(Integer, default=0, doc="Slow query count")
    
    # === CACHE PERFORMANCE METRICS ===
    cache_hit_rate = Column(Numeric(5, 2), default=0.0, doc="Cache hit rate percentage")
    cache_memory_usage_mb = Column(BigInteger, default=0, doc="Cache memory usage")
    cache_evictions = Column(BigInteger, default=0, doc="Cache evictions")
    cache_operations_per_sec = Column(Numeric(10, 2), default=0.0, doc="Cache ops/sec")
    
    # === REQUEST/RESPONSE METRICS ===
    requests_per_minute = Column(Numeric(10, 2), default=0.0, doc="Requests per minute")
    avg_response_time_ms = Column(Numeric(10, 3), default=0.0, doc="Average response time")
    p50_response_time_ms = Column(Numeric(10, 3), default=0.0, doc="50th percentile response time")
    p95_response_time_ms = Column(Numeric(10, 3), default=0.0, doc="95th percentile response time")
    p99_response_time_ms = Column(Numeric(10, 3), default=0.0, doc="99th percentile response time")
    error_rate_percent = Column(Numeric(5, 2), default=0.0, doc="Error rate percentage")
    timeout_count = Column(Integer, default=0, doc="Request timeout count")
    
    # === BUSINESS LOGIC METRICS ===
    active_scraping_jobs = Column(Integer, default=0, doc="Currently active jobs")
    completed_jobs_last_hour = Column(Integer, default=0, doc="Jobs completed in last hour")
    failed_jobs_last_hour = Column(Integer, default=0, doc="Jobs failed in last hour")
    queued_jobs = Column(Integer, default=0, doc="Jobs in queue")
    total_data_points = Column(BigInteger, default=0, doc="Total data points collected")
    data_processing_rate = Column(Numeric(10, 2), default=0.0, doc="Data points per minute")
    data_processing_rate_per_min = Column(Float, default=0.0)
    
    # Alert and health status
    health_status = Column(String(20), default="healthy")  # healthy, warning, critical
    alert_count = Column(Integer, default=0)
    anomaly_score = Column(Float, default=0.0)  # ML-based anomaly detection score
    
    # Extended metrics (JSON for flexibility)
    custom_metrics = Column(JSON, doc="Additional deployment-specific metrics")
    
    # === INDEXING FOR PERFORMANCE ===
    __table_args__ = (
        Index("idx_collection_time", "collected_at", "collection_source"),
        Index("idx_resource_monitoring", "cpu_percent", "memory_percent"),
        Index("idx_performance_tracking", "avg_response_time_ms", "error_rate_percent"),
        Index("idx_environment_metrics", "environment", "hostname"),
        Index("idx_business_metrics", "active_scraping_jobs", "completed_jobs_last_hour"),
    )
    
    # === COMPUTED PROPERTIES ===
    @property
    def system_health_score(self) -> float:
        """Overall system health score (0-100)"""
        cpu_score = max(0, 100 - (getattr(self, 'cpu_percent', 0) or 0))
        memory_score = max(0, 100 - (getattr(self, 'memory_percent', 0) or 0))
        error_score = max(0, 100 - ((getattr(self, 'error_rate_percent', 0) or 0) * 10))
        
        return (cpu_score + memory_score + error_score) / 3.0
    
    @property
    def resource_pressure_level(self) -> str:
        """Current resource pressure level"""
        cpu = getattr(self, 'cpu_percent', 0) or 0
        memory = getattr(self, 'memory_percent', 0) or 0
        
        if cpu > 90 or memory > 90:
            return "critical"
        elif cpu > 75 or memory > 75:
            return "high"
        elif cpu > 50 or memory > 50:
            return "medium"
        else:
            return "low"


class AlertRecord(Base):
    """
    Comprehensive alerting and notification system.
    
    This model manages the complete lifecycle of system alerts, from
    detection through resolution, including notification tracking,
    correlation, and impact assessment.
    
    Key Features:
    - Multi-severity alert classification
    - Complete alert lifecycle management
    - Notification channel tracking
    - Alert correlation and grouping
    - Impact assessment and SLA tracking
    """
    
    __tablename__ = "alert_records"
    
    # === PRIMARY IDENTIFIERS ===
    id = Column(Integer, primary_key=True, index=True)
    alert_uuid = Column(
        String(36), 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        index=True
    )
    
    # === ALERT CLASSIFICATION ===
    alert_type = Column(String(50), index=True, doc="Type: performance, security, data_quality, system")
    severity = Column(String(20), index=True, doc="Severity: low, medium, high, critical, emergency")
    category = Column(String(100), index=True, doc="Category: cpu_usage, memory_leak, failed_jobs")
    subcategory = Column(String(100), doc="Detailed subcategory")
    
    # === ALERT CONTENT ===
    title = Column(String(200), index=True, doc="Alert title/summary")
    message = Column(Text, doc="Detailed alert message")
    technical_details = Column(JSON, doc="Technical diagnostic information")
    recommended_actions = Column(JSON, doc="Suggested remediation steps")
    
    # === SOURCE INFORMATION ===
    source_component = Column(String(100), index=True, doc="Component: scraper, api, database")
    source_hostname = Column(String(255), doc="Source server hostname")
    source_environment = Column(String(50), doc="Environment: production, staging")
    source_metric_name = Column(String(100), doc="Triggering metric name")
    source_metric_value = Column(Numeric(15, 4), doc="Current metric value")
    threshold_value = Column(Numeric(15, 4), doc="Alert threshold value")
    
    # === ALERT LIFECYCLE ===
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True, doc="Alert creation time")
    first_detected_at = Column(DateTime, doc="First detection of condition")
    acknowledged_at = Column(DateTime, index=True, doc="Acknowledgment time")
    resolved_at = Column(DateTime, index=True, doc="Resolution time")
    auto_resolved_at = Column(DateTime, doc="Automatic resolution time")
    
    # === STATUS TRACKING ===
    status = Column(String(20), default="active", index=True, doc="Status: active, acknowledged, resolved, suppressed")
    acknowledged_by = Column(String(100), doc="User who acknowledged")
    resolved_by = Column(String(100), doc="User/system that resolved")
    resolution_method = Column(String(50), doc="Manual, automatic, or escalated")
    resolution_notes = Column(Text, doc="Resolution details and notes")
    
    # === NOTIFICATION TRACKING ===
    notifications_sent = Column(JSON, doc="Sent notification tracking")
    notification_channels = Column(JSON, doc="Channels: email, slack, webhook, sms")
    escalation_level = Column(Integer, default=0, doc="Current escalation level")
    escalation_history = Column(JSON, doc="Escalation timeline")
    
    # === ALERT CORRELATION ===
    parent_alert_id = Column(Integer, ForeignKey("alert_records.id"), doc="Parent alert for correlation")
    correlation_key = Column(String(100), index=True, doc="Key for grouping related alerts")
    occurrence_count = Column(Integer, default=1, doc="Duplicate occurrence count")
    related_alerts = Column(JSON, doc="Related alert IDs")
    
    # === IMPACT ASSESSMENT ===
    impact_level = Column(String(20), default="unknown", doc="Impact: low, medium, high, critical")
    affected_users = Column(Integer, default=0, doc="Number of affected users")
    affected_services = Column(JSON, doc="List of affected services")
    business_impact = Column(Text, doc="Business impact description")
    sla_breach = Column(Boolean, default=False, doc="SLA breach indicator")
    
    # === PERFORMANCE METRICS ===
    detection_latency_ms = Column(Integer, doc="Time from issue to detection")
    notification_latency_ms = Column(Integer, doc="Time from detection to notification")
    resolution_time_minutes = Column(Integer, doc="Total resolution time")
    mttr_minutes = Column(Integer, doc="Mean time to resolution")
    
    # === SUPPRESSION AND FILTERING ===
    is_suppressed = Column(Boolean, default=False, doc="Alert suppression status")
    suppression_reason = Column(String(200), doc="Reason for suppression")
    suppressed_until = Column(DateTime, doc="Suppression end time")
    is_false_positive = Column(Boolean, default=False, doc="False positive flag")
    
    # === RELATIONSHIPS ===
    parent_alert = relationship("AlertRecord", remote_side=[id], backref="child_alerts")
    
    # === INDEXING ===
    __table_args__ = (
        Index("idx_alert_status", "status", "severity", "triggered_at"),
        Index("idx_alert_source", "source_component", "source_environment"),
        Index("idx_alert_lifecycle", "triggered_at", "resolved_at"),
        Index("idx_alert_correlation", "correlation_key", "parent_alert_id"),
        Index("idx_alert_impact", "impact_level", "sla_breach"),
        Index("idx_alert_notifications", "escalation_level", "is_suppressed"),
    )
    
    # === COMPUTED PROPERTIES ===
    @property
    def is_active(self) -> bool:
        """Check if alert is currently active"""
        return getattr(self, 'status', '') in ['active', 'acknowledged']
    
    @property 
    def age_minutes(self) -> int:
        """Alert age in minutes"""
        triggered = getattr(self, 'triggered_at', None)
        if not triggered:
            return 0
        return int((datetime.utcnow() - triggered).total_seconds() / 60)
    
    @property
    def severity_score(self) -> int:
        """Numeric severity score for sorting"""
        severity_map = {
            'low': 1,
            'medium': 2, 
            'high': 3,
            'critical': 4,
            'emergency': 5
        }
        return severity_map.get(getattr(self, 'severity', ''), 0)



class DataRepository:
    """
    High-level data access and management interface.
    
    This class provides a clean API for interacting with all data models,
    implementing common operations, analytics queries, and business logic
    while maintaining separation of concerns.
    """
    
    def __init__(self, session: Session):
        """Initialize repository with database session"""
        self.session = session
    
    # === CENTRALIZED DATA OPERATIONS ===
    def create_data_record(self, data: Dict[str, Any]) -> CentralizedDataRecord:
        """Create a new centralized data record with validation"""
        record = CentralizedDataRecord(**data)
        record.update_content_hash()
        record.calculate_quality_scores()
        
        self.session.add(record)
        self.session.commit()
        return record
    
    def get_high_quality_records(self, limit: int = 100) -> List[CentralizedDataRecord]:
        """Retrieve high-quality records for dashboard display"""
        return (
            self.session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.data_quality_score >= DataConstants.EXCELLENT_QUALITY_THRESHOLD)
            .filter(CentralizedDataRecord.validation_status == "valid")
            .order_by(CentralizedDataRecord.centralized_at.desc())
            .limit(limit)
            .all()
        )
    
    def find_duplicates(self, content_hash: str) -> List[CentralizedDataRecord]:
        """Find potential duplicates by content hash"""
        return (
            self.session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.content_hash == content_hash)
            .all()
        )
    
    # === ANALYTICS OPERATIONS ===
    def get_latest_analytics(self, period_type: str = "daily") -> Optional[DataAnalytics]:
        """Get the most recent analytics for a period type"""
        return (
            self.session.query(DataAnalytics)
            .filter(DataAnalytics.period_type == period_type)
            .order_by(DataAnalytics.date.desc())
            .first()
        )
    
    def create_analytics_snapshot(self, period_type: str, date: datetime) -> DataAnalytics:
        """Create analytics snapshot for a specific period"""
        # This would contain the logic to calculate aggregated metrics
        # Implementation would compute values from CentralizedDataRecord
        analytics = DataAnalytics(
            period_type=period_type,
            date=date,
            period_start=date,
            period_end=date
        )
        # Add computation logic here
        self.session.add(analytics)
        self.session.commit()
        return analytics
    
    # === SYSTEM METRICS OPERATIONS ===
    def record_system_metrics(self, metrics: Dict[str, Any]) -> SystemMetrics:
        """Record current system performance metrics"""
        metric_record = SystemMetrics(**metrics)
        self.session.add(metric_record)
        self.session.commit()
        return metric_record
    
    def get_system_health_trend(self, hours: int = 24) -> List[SystemMetrics]:
        """Get system health metrics for trend analysis"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return (
            self.session.query(SystemMetrics)
            .filter(SystemMetrics.collected_at >= cutoff_time)
            .order_by(SystemMetrics.collected_at.asc())
            .all()
        )
    
    # === ALERT OPERATIONS ===
    def create_alert(self, alert_data: Dict[str, Any]) -> AlertRecord:
        """Create a new alert with correlation checking"""
        alert = AlertRecord(**alert_data)
        
        # Check for existing similar alerts for correlation
        correlation_key = alert_data.get('correlation_key')
        if correlation_key:
            existing_alert = (
                self.session.query(AlertRecord)
                .filter(AlertRecord.correlation_key == correlation_key)
                .filter(AlertRecord.status.in_(['active', 'acknowledged']))
                .first()
            )
            if existing_alert:
                existing_alert.occurrence_count += 1  # type: ignore[assignment]
                self.session.commit()
                return existing_alert
        
        self.session.add(alert)
        self.session.commit()
        return alert
    
    def get_active_alerts(self, severity_filter: Optional[str] = None) -> List[AlertRecord]:
        """Get currently active alerts with optional severity filtering"""
        query = (
            self.session.query(AlertRecord)
            .filter(AlertRecord.status.in_(['active', 'acknowledged']))
        )
        
        if severity_filter:
            query = query.filter(AlertRecord.severity == severity_filter)
        
        return (
            query
            .order_by(AlertRecord.severity.desc(), AlertRecord.triggered_at.desc())  # type: ignore
            .all()
        )
    
    def resolve_alert(self, alert_id: int, resolved_by: str, notes: Optional[str] = None) -> bool:
        """Resolve an alert and update its status"""
        alert = self.session.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
        if alert:
            alert.status = "resolved"  # type: ignore[assignment]
            alert.resolved_at = datetime.utcnow()  # type: ignore[assignment]
            alert.resolved_by = resolved_by  # type: ignore[assignment]
            alert.resolution_notes = notes  # type: ignore[assignment]
            self.session.commit()
            return True
        return False


# === UTILITY FUNCTIONS ===
def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)


def get_model_summary() -> Dict[str, Any]:
    """Get summary information about all data models"""
    return {
        "models": {
            "CentralizedDataRecord": {
                "description": "Core data storage with quality metrics",
                "key_features": ["Quality scoring", "Content analytics", "Deduplication"],
                "indexes": 10
            },
            "DataAnalytics": {
                "description": "Precomputed analytics for dashboards", 
                "key_features": ["Time-based aggregations", "Performance metrics", "Engagement tracking"],
                "indexes": 4
            },
            "SystemMetrics": {
                "description": "System performance and observability",
                "key_features": ["Resource monitoring", "Performance tracking", "Health scoring"],
                "indexes": 5
            },
            "AlertRecord": {
                "description": "Comprehensive alerting system",
                "key_features": ["Lifecycle management", "Correlation", "Impact assessment"],
                "indexes": 6
            },
            "DataDeduplication": {
                "description": "Duplicate detection and management",
                "key_features": ["Content hashing", "Similarity scoring", "Conflict resolution"],
                "indexes": 2
            }
        },
        "total_models": 5,
        "estimated_storage_per_million_records": "~2.5 GB",
        "recommended_maintenance": [
            "Archive old analytics data quarterly",
            "Clean up resolved alerts monthly", 
            "Rebuild indexes on high-traffic tables weekly",
            "Update performance baselines monthly"
        ]
    }
