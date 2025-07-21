"""
Advanced Storage Models for Raw Data, Structured Entities, and Data Lineage

Comprehensive database models supporting:
- Raw data storage with full provenance
- Structured entity normalization  
- Data lineage and relationship mapping
- Data quality metrics and monitoring
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy import (
    Column, String, DateTime, Integer, Float, Text, Boolean, 
    JSON, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from ..db.models import Base


class RawDataModel(Base):
    """Database model for raw data records with full provenance"""
    __tablename__ = 'raw_data'
    
    # Primary identification
    raw_id = Column(String, primary_key=True)
    content_hash = Column(String(64), nullable=False, index=True)
    
    # Source information
    source_url = Column(String, nullable=False, index=True)
    referrer_url = Column(String)
    source_domain = Column(String, nullable=False, index=True)
    
    # Temporal information
    fetched_at = Column(DateTime, nullable=False, index=True, server_default=func.now())
    page_last_modified = Column(DateTime)
    
    # Job and processing context
    job_id = Column(String, nullable=False, index=True)
    spider_name = Column(String, index=True)
    crawl_depth = Column(Integer, default=0)
    
    # HTTP metadata
    http_status = Column(Integer, index=True)
    content_type = Column(String)
    content_encoding = Column(String)
    response_time_ms = Column(Integer)
    
    # Storage information
    storage_backend = Column(String, nullable=False, default='s3')
    storage_bucket = Column(String, nullable=False)
    storage_key = Column(String, nullable=False)
    content_size_bytes = Column(Integer)
    is_compressed = Column(Boolean, default=False)
    
    # Request/response details
    request_headers = Column(JSONB)
    response_headers = Column(JSONB)
    
    # Content metadata
    language = Column(String)
    charset = Column(String)
    page_title = Column(String)
    
    # Processing status
    processing_status = Column(String, default='pending', index=True)
    extraction_attempted = Column(Boolean, default=False)
    extraction_successful = Column(Boolean, default=False)
    extraction_error = Column(Text)
    
    # Quality metrics
    content_quality_score = Column(Float)
    is_duplicate = Column(Boolean, default=False, index=True)
    similarity_hash = Column(String)
    
    # Attachments and related resources
    attachments = Column(JSONB)  # URLs of images, PDFs, etc.
    linked_resources = Column(JSONB)  # CSS, JS, etc.
    
    # Custom metadata
    metadata = Column(JSONB)
    tags = Column(JSONB)
    
    # Audit trail
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    structured_mappings = relationship("RawToStructuredMappingModel", back_populates="raw_data")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_raw_data_job_status', 'job_id', 'http_status'),
        Index('idx_raw_data_content_hash', 'content_hash'),
        Index('idx_raw_data_domain_date', 'source_domain', 'fetched_at'),
        Index('idx_raw_data_processing', 'processing_status', 'extraction_attempted'),
        Index('idx_raw_data_quality', 'content_quality_score', 'is_duplicate'),
    )


class StructuredEntityModel(Base):
    """Database model for structured entities extracted from raw data"""
    __tablename__ = 'structured_entities'
    
    # Primary identification
    entity_id = Column(String, primary_key=True)
    entity_type = Column(String, nullable=False, index=True)
    
    # Core entity data
    canonical_name = Column(String, index=True)
    display_name = Column(String)
    description = Column(Text)
    
    # Classification and scoring
    category = Column(String, index=True)
    subcategory = Column(String, index=True)
    confidence_score = Column(Float, index=True)
    importance_score = Column(Float, index=True)
    
    # Temporal information
    extracted_at = Column(DateTime, nullable=False, index=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    first_seen_at = Column(DateTime)
    last_verified_at = Column(DateTime)
    
    # Processing metadata
    extractor_name = Column(String, nullable=False)
    extractor_version = Column(String, nullable=False)
    extraction_method = Column(String)  # ml, rule-based, hybrid
    
    # Entity data (structured)
    structured_data = Column(JSONB, nullable=False)
    
    # Contact and location information
    contact_info = Column(JSONB)
    locations = Column(JSONB)
    
    # Business-specific fields
    industry_codes = Column(JSONB)
    business_identifiers = Column(JSONB)  # Tax ID, DUNS, etc.
    financial_data = Column(JSONB)
    
    # Verification and validation
    verification_status = Column(String, default='unverified', index=True)
    verification_source = Column(String)
    data_quality_score = Column(Float, index=True)
    completeness_score = Column(Float)
    
    # Source attribution
    primary_source_url = Column(String)
    source_count = Column(Integer, default=1)
    
    # Custom metadata and tags
    metadata = Column(JSONB)
    tags = Column(JSONB)
    
    # Status tracking
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    needs_review = Column(Boolean, default=False, index=True)
    
    # Relationships
    raw_mappings = relationship("RawToStructuredMappingModel", back_populates="entity")
    relationships_as_source = relationship("EntityRelationshipModel", 
                                         foreign_keys="EntityRelationshipModel.source_entity_id",
                                         back_populates="source_entity")
    relationships_as_target = relationship("EntityRelationshipModel", 
                                         foreign_keys="EntityRelationshipModel.target_entity_id",
                                         back_populates="target_entity")
    quality_metrics = relationship("DataQualityMetricsModel", back_populates="entity")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_entity_type_name', 'entity_type', 'canonical_name'),
        Index('idx_entity_confidence', 'entity_type', 'confidence_score'),
        Index('idx_entity_category', 'category', 'subcategory'),
        Index('idx_entity_status', 'is_active', 'verification_status'),
        Index('idx_entity_quality', 'data_quality_score', 'completeness_score'),
        Index('idx_entity_temporal', 'first_seen_at', 'last_verified_at'),
    )


class RawToStructuredMappingModel(Base):
    """Mapping between raw data and structured entities with extraction details"""
    __tablename__ = 'raw_to_structured_mapping'
    
    # Primary key
    mapping_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    raw_id = Column(String, ForeignKey('raw_data.raw_id'), nullable=False, index=True)
    entity_id = Column(String, ForeignKey('structured_entities.entity_id'), nullable=False, index=True)
    
    # Extraction details
    extraction_method = Column(String, nullable=False)
    extraction_confidence = Column(Float, nullable=False)
    extracted_fields = Column(JSONB)
    extraction_context = Column(JSONB)  # Surrounding text, position, etc.
    
    # Quality and validation
    field_quality_scores = Column(JSONB)
    validation_results = Column(JSONB)
    extraction_errors = Column(JSONB)
    
    # Processing information
    extractor_name = Column(String, nullable=False)
    extractor_version = Column(String, nullable=False)
    processing_time_ms = Column(Integer)
    
    # Contribution metrics
    contribution_weight = Column(Float, default=1.0)  # How much this source contributed
    is_primary_source = Column(Boolean, default=False, index=True)
    field_contributions = Column(JSONB)  # Which fields came from this source
    
    # Temporal information
    extracted_at = Column(DateTime, nullable=False, server_default=func.now())
    last_validated = Column(DateTime)
    
    # Status and notes
    status = Column(String, default='active', index=True)
    extraction_notes = Column(Text)
    reviewer_notes = Column(Text)
    
    # Relationships
    raw_data = relationship("RawDataModel", back_populates="structured_mappings")
    entity = relationship("StructuredEntityModel", back_populates="raw_mappings")
    
    # Constraints
    __table_args__ = (
        Index('idx_mapping_raw_entity', 'raw_id', 'entity_id'),
        Index('idx_mapping_entity_confidence', 'entity_id', 'extraction_confidence'),
        Index('idx_mapping_method', 'extraction_method', 'extractor_name'),
        UniqueConstraint('raw_id', 'entity_id', 'extractor_name', 
                        name='uq_raw_entity_extractor'),
    )


class EntityRelationshipModel(Base):
    """Relationships between structured entities"""
    __tablename__ = 'entity_relationships'
    
    # Primary key
    relationship_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Entity references
    source_entity_id = Column(String, ForeignKey('structured_entities.entity_id'), 
                             nullable=False, index=True)
    target_entity_id = Column(String, ForeignKey('structured_entities.entity_id'), 
                             nullable=False, index=True)
    
    # Relationship details
    relationship_type = Column(String, nullable=False, index=True)
    relationship_subtype = Column(String, index=True)
    
    # Relationship strength and confidence
    strength = Column(Float, default=1.0, index=True)
    confidence = Column(Float, nullable=False, index=True)
    
    # Directionality and semantics
    is_directional = Column(Boolean, default=True)
    semantic_role = Column(String)  # subject, object, etc.
    
    # Evidence and sources
    evidence_sources = Column(JSONB)  # Raw data IDs that support this relationship
    extraction_method = Column(String, nullable=False)
    supporting_text = Column(JSONB)  # Text snippets that show the relationship
    
    # Temporal aspects
    relationship_start_date = Column(DateTime)
    relationship_end_date = Column(DateTime)
    extracted_at = Column(DateTime, nullable=False, server_default=func.now())
    last_verified = Column(DateTime)
    
    # Validation and quality
    verification_status = Column(String, default='unverified', index=True)
    quality_score = Column(Float, index=True)
    validation_notes = Column(Text)
    
    # Processing metadata
    extractor_name = Column(String, nullable=False)
    extractor_version = Column(String, nullable=False)
    
    # Custom attributes
    attributes = Column(JSONB)
    metadata = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    needs_review = Column(Boolean, default=False, index=True)
    
    # Relationships
    source_entity = relationship("StructuredEntityModel", 
                               foreign_keys=[source_entity_id],
                               back_populates="relationships_as_source")
    target_entity = relationship("StructuredEntityModel", 
                               foreign_keys=[target_entity_id], 
                               back_populates="relationships_as_target")
    
    # Constraints and indexes
    __table_args__ = (
        Index('idx_rel_source_target', 'source_entity_id', 'target_entity_id'),
        Index('idx_rel_type', 'relationship_type', 'relationship_subtype'),
        Index('idx_rel_strength', 'strength', 'confidence'),
        Index('idx_rel_temporal', 'relationship_start_date', 'relationship_end_date'),
        CheckConstraint('strength >= 0 AND strength <= 1', name='ck_strength_range'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='ck_confidence_range'),
    )


class DataQualityMetricsModel(Base):
    """Data quality metrics for entities and the overall system"""
    __tablename__ = 'data_quality_metrics'
    
    # Primary key
    metric_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Scope of metrics
    scope_type = Column(String, nullable=False, index=True)  # entity, domain, job, global
    scope_id = Column(String, index=True)  # ID of the scope (entity_id, domain, job_id, etc.)
    
    # Entity reference (if applicable)
    entity_id = Column(String, ForeignKey('structured_entities.entity_id'), index=True)
    
    # Metric details
    metric_type = Column(String, nullable=False, index=True)  # completeness, accuracy, consistency, etc.
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_threshold = Column(Float)
    
    # Scoring and evaluation
    score = Column(Float, index=True)  # Normalized score 0-1
    grade = Column(String, index=True)  # A, B, C, D, F
    passes_threshold = Column(Boolean, index=True)
    
    # Calculation details
    calculation_method = Column(String, nullable=False)
    sample_size = Column(Integer)
    calculation_params = Column(JSONB)
    
    # Temporal information
    measurement_date = Column(DateTime, nullable=False, server_default=func.now())
    measurement_period_start = Column(DateTime)
    measurement_period_end = Column(DateTime)
    
    # Trends and history
    previous_value = Column(Float)
    trend = Column(String, index=True)  # improving, declining, stable
    trend_confidence = Column(Float)
    
    # Issues and recommendations
    issues_identified = Column(JSONB)
    recommendations = Column(JSONB)
    
    # Processing metadata
    calculated_by = Column(String, nullable=False)
    calculation_version = Column(String, nullable=False)
    
    # Additional context
    metadata = Column(JSONB)
    tags = Column(JSONB)
    
    # Relationships
    entity = relationship("StructuredEntityModel", back_populates="quality_metrics")
    
    # Indexes
    __table_args__ = (
        Index('idx_quality_scope', 'scope_type', 'scope_id'),
        Index('idx_quality_metric', 'metric_type', 'metric_name'),
        Index('idx_quality_score', 'score', 'grade'),
        Index('idx_quality_temporal', 'measurement_date', 'scope_type'),
        Index('idx_quality_trend', 'trend', 'passes_threshold'),
    )


class DataLineageModel(Base):
    """Complete data lineage tracking from raw sources to final entities"""
    __tablename__ = 'data_lineage'
    
    # Primary key
    lineage_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Lineage path
    source_type = Column(String, nullable=False, index=True)  # raw_data, entity, external
    source_id = Column(String, nullable=False, index=True)
    target_type = Column(String, nullable=False, index=True)  # entity, relationship, aggregate
    target_id = Column(String, nullable=False, index=True)
    
    # Transformation details
    transformation_type = Column(String, nullable=False, index=True)  # extraction, enrichment, aggregation
    transformation_name = Column(String, nullable=False)
    transformation_version = Column(String, nullable=False)
    
    # Path and dependencies
    lineage_path = Column(JSONB)  # Complete path from ultimate source to target
    direct_dependencies = Column(JSONB)  # Immediate dependencies
    dependency_count = Column(Integer, index=True)
    path_length = Column(Integer, index=True)
    
    # Transformation metadata
    transformation_params = Column(JSONB)
    input_schema = Column(JSONB)
    output_schema = Column(JSONB)
    
    # Quality and validation
    transformation_confidence = Column(Float, index=True)
    data_quality_impact = Column(Float)
    validation_results = Column(JSONB)
    
    # Temporal tracking
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    transformation_timestamp = Column(DateTime, nullable=False)
    last_verified = Column(DateTime)
    
    # Processing information
    processing_job_id = Column(String, index=True)
    processing_duration_ms = Column(Integer)
    resource_usage = Column(JSONB)
    
    # Impact tracking
    downstream_entities = Column(JSONB)  # Entities affected by changes to this source
    impact_score = Column(Float, index=True)  # How many things depend on this
    
    # Status and maintenance
    is_active = Column(Boolean, default=True, index=True)
    needs_refresh = Column(Boolean, default=False, index=True)
    last_refresh_attempt = Column(DateTime)
    
    # Custom metadata
    metadata = Column(JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_lineage_source', 'source_type', 'source_id'),
        Index('idx_lineage_target', 'target_type', 'target_id'),
        Index('idx_lineage_transformation', 'transformation_type', 'transformation_name'),
        Index('idx_lineage_path', 'path_length', 'dependency_count'),
        Index('idx_lineage_quality', 'transformation_confidence', 'data_quality_impact'),
    )


class StorageMetricsModel(Base):
    """System-wide storage metrics and monitoring"""
    __tablename__ = 'storage_metrics'
    
    # Primary key  
    metric_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Metric identification
    metric_category = Column(String, nullable=False, index=True)  # storage, performance, quality
    metric_name = Column(String, nullable=False, index=True)
    metric_description = Column(Text)
    
    # Metric value
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String)
    
    # Context and scope
    scope = Column(String, index=True)  # system, bucket, entity_type, etc.
    scope_id = Column(String, index=True)
    
    # Temporal information
    measured_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    measurement_period = Column(String)  # hourly, daily, weekly, etc.
    
    # Aggregation details
    aggregation_method = Column(String)  # sum, avg, max, min, count
    sample_count = Column(Integer)
    
    # Trend analysis
    trend_direction = Column(String, index=True)  # up, down, stable
    change_rate = Column(Float)
    
    # Thresholds and alerts
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    alert_level = Column(String, index=True)  # normal, warning, critical
    
    # Additional data
    metadata = Column(JSONB)
    
    # Indexes
    __table_args__ = (
        Index('idx_storage_metrics_category', 'metric_category', 'metric_name'),
        Index('idx_storage_metrics_temporal', 'measured_at', 'measurement_period'),
        Index('idx_storage_metrics_scope', 'scope', 'scope_id'),
        Index('idx_storage_metrics_alerts', 'alert_level', 'measured_at'),
    )
