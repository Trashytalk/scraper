"""
Data Quality & Provenance Models

SQLAlchemy models for tracking data quality, provenance, and lineage
throughout the business intelligence pipeline.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List
from uuid import uuid4

from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Float,
    Integer,
    Boolean,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .models import Base


class DataSourceType(str, Enum):
    """Types of data sources"""

    WEB_SCRAPING = "web_scraping"
    API = "api"
    DATABASE = "database"
    FILE_UPLOAD = "file_upload"
    MANUAL_ENTRY = "manual_entry"
    THIRD_PARTY = "third_party"


class QualityStatus(str, Enum):
    """Data quality assessment status"""

    EXCELLENT = "excellent"  # 90-100% quality score
    GOOD = "good"  # 75-89% quality score
    FAIR = "fair"  # 50-74% quality score
    POOR = "poor"  # 25-49% quality score
    CRITICAL = "critical"  # 0-24% quality score


class ConfidenceLevel(str, Enum):
    """Confidence levels for data"""

    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 75-89%
    MEDIUM = "medium"  # 50-74%
    LOW = "low"  # 25-49%
    VERY_LOW = "very_low"  # 0-24%


class ChangeType(str, Enum):
    """Types of data changes"""

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    MERGE = "merge"
    SPLIT = "split"
    CORRECTION = "correction"


class DataSource(Base):
    """Registry of all data sources with reliability metrics"""

    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[DataSourceType] = mapped_column(String(50), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Reliability metrics
    reliability_score: Mapped[float] = mapped_column(Float, default=0.5)
    last_successful_access: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Configuration
    update_frequency_hours: Mapped[int] = mapped_column(Integer, default=24)
    quality_checks: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    raw_records: Mapped[List["RawDataRecord"]] = relationship(back_populates="source")

    @hybrid_property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class RawDataRecord(Base):
    """Raw data records as extracted from sources"""

    __tablename__ = "raw_data_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("data_sources.id"), nullable=False
    )

    # Source details
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    extraction_job_id: Mapped[str] = mapped_column(String(100), nullable=True)
    extractor_version: Mapped[str] = mapped_column(String(50), nullable=True)

    # Content
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    content_type: Mapped[str] = mapped_column(String(100), nullable=True)

    # Timestamps
    extracted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source_timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=True
    )  # When source claims data was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    # Quality indicators
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_errors: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_errors: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Relationships
    source: Mapped["DataSource"] = relationship(back_populates="raw_records")
    provenance_records: Mapped[List["ProvenanceRecord"]] = relationship(
        back_populates="raw_record"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.raw_content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.raw_content.encode()).hexdigest()


class EntityRecord(Base):
    """Processed entity records with quality scores"""

    __tablename__ = "entity_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # company, person, address, etc.

    # Core data
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    data_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Quality metrics
    completeness_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    freshness_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    overall_quality_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1

    # Status
    quality_status: Mapped[QualityStatus] = mapped_column(
        String(20), default=QualityStatus.FAIR
    )
    confidence_level: Mapped[ConfidenceLevel] = mapped_column(
        String(20), default=ConfidenceLevel.MEDIUM
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Flags
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    has_issues: Mapped[bool] = mapped_column(Boolean, default=False)

    # Issue tracking
    quality_issues: Mapped[List[str]] = mapped_column(JSON, default=list)
    duplicate_of: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # entity_id of canonical record

    # Relationships
    provenance_records: Mapped[List["ProvenanceRecord"]] = relationship(
        back_populates="entity"
    )
    quality_assessments: Mapped[List["QualityAssessment"]] = relationship(
        back_populates="entity"
    )
    change_log: Mapped[List["DataChangeLog"]] = relationship(back_populates="entity")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.data and not self.data_hash:
            data_str = json.dumps(self.data, sort_keys=True)
            self.data_hash = hashlib.sha256(data_str.encode()).hexdigest()

    @hybrid_property
    def staleness_days(self) -> float:
        """Calculate staleness in days"""
        if not self.last_verified_at:
            return float("inf")
        delta = datetime.now(timezone.utc) - self.last_verified_at
        return delta.total_seconds() / 86400


class ProvenanceRecord(Base):
    """Field-level provenance tracking"""

    __tablename__ = "provenance_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    provenance_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Entity and field
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entity_records.id"), nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_value: Mapped[str] = mapped_column(Text, nullable=True)

    # Source tracking
    raw_record_id: Mapped[int] = mapped_column(
        ForeignKey("raw_data_records.id"), nullable=False
    )
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(100), nullable=True)

    # Processing details
    extracted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    processor_version: Mapped[str] = mapped_column(String(50), nullable=True)

    # Quality metrics
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    validation_status: Mapped[bool] = mapped_column(Boolean, default=True)
    transformation_applied: Mapped[str] = mapped_column(Text, nullable=True)

    # Cryptographic proof
    provenance_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[str] = mapped_column(
        String(512), nullable=True
    )  # For auditability

    # Relationships
    entity: Mapped["EntityRecord"] = relationship(back_populates="provenance_records")
    raw_record: Mapped["RawDataRecord"] = relationship(
        back_populates="provenance_records"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.provenance_id:
            self.provenance_id = str(uuid4())
        if not self.provenance_hash:
            self._generate_provenance_hash()

    def _generate_provenance_hash(self):
        """Generate cryptographic hash for auditability"""
        hash_data = f"{self.entity_id}:{self.field_name}:{self.field_value}:{self.source_url}:{self.extracted_at}"
        self.provenance_hash = hashlib.sha256(hash_data.encode()).hexdigest()


class QualityAssessment(Base):
    """Detailed quality assessments for entities"""

    __tablename__ = "quality_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entity_records.id"), nullable=False
    )

    # Assessment details
    assessment_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # completeness, consistency, etc.
    assessed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    assessor: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # system, user_id, etc.

    # Metrics
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-1
    max_possible_score: Mapped[float] = mapped_column(Float, default=1.0)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    # Details
    criteria: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    results: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    issues_found: Mapped[List[str]] = mapped_column(JSON, default=list)
    recommendations: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Relationships
    entity: Mapped["EntityRecord"] = relationship(back_populates="quality_assessments")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.assessment_id:
            self.assessment_id = str(uuid4())


class DataChangeLog(Base):
    """Comprehensive change logging for audit trails"""

    __tablename__ = "data_change_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    change_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entity_records.id"), nullable=False
    )

    # Change details
    change_type: Mapped[ChangeType] = mapped_column(String(20), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=True)
    old_value: Mapped[str] = mapped_column(Text, nullable=True)
    new_value: Mapped[str] = mapped_column(Text, nullable=True)

    # Context
    changed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    changed_by: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # user_id, system, etc.
    change_reason: Mapped[str] = mapped_column(Text, nullable=True)
    change_source: Mapped[str] = mapped_column(String(200), nullable=True)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str] = mapped_column(String(100), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Rollback support
    is_rollback: Mapped[bool] = mapped_column(Boolean, default=False)
    rollback_of: Mapped[str] = mapped_column(String(100), nullable=True)  # change_id

    # Metadata
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    entity: Mapped["EntityRecord"] = relationship(back_populates="change_log")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.change_id:
            self.change_id = str(uuid4())


class QualityRule(Base):
    """Configurable quality rules and thresholds"""

    __tablename__ = "quality_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Rule definition
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=True
    )  # Apply to specific entity types
    field_name: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # Apply to specific fields
    rule_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # completeness, format, range, etc.
    rule_config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Thresholds
    critical_threshold: Mapped[float] = mapped_column(Float, default=0.25)
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.75)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.rule_id:
            self.rule_id = str(uuid4())


class DataCorrection(Base):
    """User-submitted data corrections and feedback"""

    __tablename__ = "data_corrections"

    id: Mapped[int] = mapped_column(primary_key=True)
    correction_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entity_records.id"), nullable=False
    )

    # Correction details
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_value: Mapped[str] = mapped_column(Text, nullable=False)
    correction_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # fix, merge, split, flag

    # Submission details
    submitted_by: Mapped[str] = mapped_column(String(100), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    submission_source: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # gui, api, etc.

    # Justification
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    evidence: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, approved, rejected, applied
    reviewed_by: Mapped[str] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    review_notes: Mapped[str] = mapped_column(Text, nullable=True)

    # Implementation
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    change_log_id: Mapped[str] = mapped_column(String(100), nullable=True)

    # Relationships
    entity: Mapped["EntityRecord"] = relationship()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.correction_id:
            self.correction_id = str(uuid4())


class QualityAlert(Base):
    """Automated quality alerts and notifications"""

    __tablename__ = "quality_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    alert_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Alert details
    alert_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # quality_drop, staleness, anomaly
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # critical, warning, info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Context
    entity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("data_sources.id"), nullable=True)
    affected_count: Mapped[int] = mapped_column(Integer, default=0)

    # Metrics
    current_value: Mapped[float] = mapped_column(Float, nullable=True)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=True)
    historical_average: Mapped[float] = mapped_column(Float, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20), default="active"
    )  # active, acknowledged, resolved
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    acknowledged_by: Mapped[str] = mapped_column(String(100), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Actions taken
    actions_taken: Mapped[List[str]] = mapped_column(JSON, default=list)

    # Relationships
    source: Mapped["DataSource"] = relationship()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.alert_id:
            self.alert_id = str(uuid4())


# Indexes for performance
Index("idx_raw_data_source_url", RawDataRecord.source_url)
Index("idx_raw_data_extracted_at", RawDataRecord.extracted_at)
Index("idx_raw_data_hash", RawDataRecord.content_hash)

Index(
    "idx_entity_type_quality",
    EntityRecord.entity_type,
    EntityRecord.overall_quality_score,
)
Index("idx_entity_updated_at", EntityRecord.updated_at)
Index("idx_entity_quality_status", EntityRecord.quality_status)

Index(
    "idx_provenance_entity_field",
    ProvenanceRecord.entity_id,
    ProvenanceRecord.field_name,
)
Index("idx_provenance_source_url", ProvenanceRecord.source_url)
Index("idx_provenance_extracted_at", ProvenanceRecord.extracted_at)

Index(
    "idx_quality_assessment_entity",
    QualityAssessment.entity_id,
    QualityAssessment.assessment_type,
)
Index("idx_quality_assessment_assessed_at", QualityAssessment.assessed_at)

Index("idx_change_log_entity_time", DataChangeLog.entity_id, DataChangeLog.changed_at)
Index("idx_change_log_type", DataChangeLog.change_type)

Index("idx_correction_status", DataCorrection.status)
Index("idx_correction_submitted_at", DataCorrection.submitted_at)

Index("idx_alert_status_severity", QualityAlert.status, QualityAlert.severity)
Index("idx_alert_created_at", QualityAlert.created_at)
