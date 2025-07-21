"""
Advanced Storage & Indexing Layer for Business Intelligence Pipeline

This package provides comprehensive storage infrastructure including:
- Raw data lake storage with full provenance tracking
- Structured entity storage with normalized data
- Complete data lineage mapping and traceability
- Multi-backend support (PostgreSQL, Elasticsearch, S3/MinIO)
- Advanced indexing and search capabilities
"""

from .core import (
    AdvancedStorageManager,
    RawDataRecord,
    StructuredEntity,
    DataLineageTracker
)
from .models import (
    RawDataModel,
    StructuredEntityModel,
    RawToStructuredMappingModel,
    EntityRelationshipModel,
    DataQualityMetricsModel
)

__all__ = [
    'AdvancedStorageManager',
    'RawDataRecord', 
    'StructuredEntity',
    'DataLineageTracker',
    'RawDataModel',
    'StructuredEntityModel', 
    'RawToStructuredMappingModel',
    'EntityRelationshipModel',
    'DataQualityMetricsModel'
]
