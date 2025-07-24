"""
Centralized Data Management for Business Intelligence Scraper
Handles aggregation, analytics, and centralized storage of all scraped data
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class CentralizedDataRecord(Base):
    """
    Central repository for all scraped data points
    Enables cross-job analytics and unified data access
    """
    __tablename__ = "centralized_data"
    
    id = Column(Integer, primary_key=True, index=True)
    record_uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    
    # Source tracking
    source_job_id = Column(Integer, index=True)
    source_job_name = Column(String(255), index=True)
    source_job_type = Column(String(50), index=True)
    source_url = Column(String(2048), index=True)
    
    # Data content
    raw_data = Column(JSON)  # Original scraped data
    processed_data = Column(JSON)  # Cleaned/processed version
    
    # Metadata
    data_type = Column(String(50), index=True)  # news, ecommerce, social_media, etc.
    content_hash = Column(String(64), index=True)  # For deduplication
    
    # Timestamps
    scraped_at = Column(DateTime, index=True)
    centralized_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quality metrics
    data_quality_score = Column(Integer, default=0)  # 0-100
    completeness_score = Column(Integer, default=0)  # 0-100
    validation_status = Column(String(20), default='pending')  # pending, valid, invalid
    
    # Analytics fields
    word_count = Column(Integer, default=0)
    link_count = Column(Integer, default=0)
    image_count = Column(Integer, default=0)
    
    # Create indexes for common queries
    __table_args__ = (
        Index('idx_source_job', 'source_job_id', 'source_job_type'),
        Index('idx_data_type_time', 'data_type', 'scraped_at'),
        Index('idx_quality_time', 'data_quality_score', 'centralized_at'),
        Index('idx_content_hash', 'content_hash'),
    )

class DataAnalytics(Base):
    """
    Precomputed analytics for faster dashboard queries
    """
    __tablename__ = "data_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    date = Column(DateTime, index=True)
    period_type = Column(String(20), index=True)  # daily, weekly, monthly
    
    # Aggregated metrics
    total_records = Column(Integer, default=0)
    total_jobs = Column(Integer, default=0)
    unique_sources = Column(Integer, default=0)
    avg_quality_score = Column(Integer, default=0)
    
    # Data type breakdown
    news_records = Column(Integer, default=0)
    ecommerce_records = Column(Integer, default=0)
    social_media_records = Column(Integer, default=0)
    other_records = Column(Integer, default=0)
    
    # Performance metrics
    avg_processing_time = Column(Integer, default=0)  # milliseconds
    success_rate = Column(Integer, default=0)  # percentage
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DataDeduplication(Base):
    """
    Track duplicate detection and management
    """
    __tablename__ = "data_deduplication"
    
    id = Column(Integer, primary_key=True, index=True)
    
    content_hash = Column(String(64), index=True)
    canonical_record_id = Column(Integer, ForeignKey('centralized_data.id'))
    duplicate_record_ids = Column(JSON)  # List of duplicate record IDs
    
    similarity_score = Column(Integer, default=0)  # 0-100
    dedup_method = Column(String(50))  # hash, content_similarity, url_similarity
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    canonical_record = relationship("CentralizedDataRecord", backref="duplicates")
