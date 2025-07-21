"""
Analysis & Cross-Referencing Layer

This package provides advanced entity resolution, relationship mapping, and cross-referencing
capabilities for business intelligence applications.

Key Components:
- AdvancedEntityResolver: Fuzzy matching and entity deduplication
- EntityRelationshipMapper: Relationship extraction and graph construction
- DataEnrichmentEngine: External data source integration
- BusinessEventDetector: Event detection and monitoring
- AnalysisOrchestrator: Coordinated analysis pipeline
"""

from .entity_resolver import AdvancedEntityResolver
from .relationship_mapper import EntityRelationshipMapper
from .enrichment_engine import DataEnrichmentEngine
from .event_detector import BusinessEventDetector
from .orchestrator import AnalysisOrchestrator

__all__ = [
    'AdvancedEntityResolver',
    'EntityRelationshipMapper', 
    'DataEnrichmentEngine',
    'BusinessEventDetector',
    'AnalysisOrchestrator'
]

from .entity_resolver import AdvancedEntityResolver, EntityMatch, ResolvedEntity
from .relationship_mapper import EntityRelationshipMapper, EntityRelationship
from .enrichment_engine import DataEnrichmentEngine, EnrichmentResult
from .event_detector import BusinessEventDetector, DetectedEvent
from .orchestrator import AnalysisOrchestrator
from .link_classifier import AdaptiveLinkClassifier

__all__ = [
    'AdvancedEntityResolver',
    'EntityMatch', 
    'ResolvedEntity',
    'EntityRelationshipMapper',
    'EntityRelationship', 
    'DataEnrichmentEngine',
    'EnrichmentResult',
    'BusinessEventDetector',
    'DetectedEvent',
    'AnalysisOrchestrator',
    'AdaptiveLinkClassifier'
]
