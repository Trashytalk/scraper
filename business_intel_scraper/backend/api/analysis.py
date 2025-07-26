"""
Analysis API endpoints for entity resolution, relationship mapping, enrichment, and event detection
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, validator

from ..analysis import AnalysisOrchestrator
from ..analysis.orchestrator import AnalysisRequest
from .dependencies import get_current_user
from .schemas import BaseResponse

logger = logging.getLogger(__name__)

# Create router
analysis_router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

# Global analysis components (would be dependency injected in production)
analysis_orchestrator: Optional[AnalysisOrchestrator] = None


def get_analysis_orchestrator() -> AnalysisOrchestrator:
    """Get analysis orchestrator instance"""
    global analysis_orchestrator
    if analysis_orchestrator is None:
        config = {
            "entity_resolution": {
                "similarity_threshold": 0.7,
                "clustering_eps": 0.3,
                "min_samples": 2,
            },
            "relationship_mapping": {
                "confidence_threshold": 0.6,
                "max_relationships": 1000,
            },
            "enrichment": {"cache_ttl_hours": 24, "max_concurrent_requests": 10},
            "event_detection": {"deduplication_window_hours": 24},
        }
        analysis_orchestrator = AnalysisOrchestrator(config)
    return analysis_orchestrator


# Pydantic models for API
class EntityInput(BaseModel):
    """Input entity for analysis"""

    entity_id: str
    name: str
    entity_type: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalysisRequestModel(BaseModel):
    """Analysis request model"""

    entities: List[EntityInput]
    analysis_types: List[str] = Field(
        default=[
            "entity_resolution",
            "relationship_mapping",
            "enrichment",
            "event_detection",
        ],
        description="Types of analysis to perform",
    )
    enrichment_sources: List[str] = Field(
        default=["sanctions", "contracts", "financial"],
        description="Enrichment data sources to use",
    )
    relationship_types: List[str] = Field(
        default=["officer", "ownership", "address", "contact"],
        description="Relationship types to extract",
    )
    confidence_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Minimum confidence score for results"
    )
    include_low_confidence: bool = Field(
        default=False, description="Include low confidence results"
    )
    max_related_entities: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of related entities to return",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("analysis_types")
    def validate_analysis_types(cls, v):
        valid_types = {
            "entity_resolution",
            "relationship_mapping",
            "enrichment",
            "event_detection",
        }
        for analysis_type in v:
            if analysis_type not in valid_types:
                raise ValueError(f"Invalid analysis type: {analysis_type}")
        return v

    @validator("enrichment_sources")
    def validate_enrichment_sources(cls, v):
        valid_sources = {
            "sanctions",
            "contracts",
            "patents",
            "social",
            "financial",
            "news",
        }
        for source in v:
            if source not in valid_sources:
                raise ValueError(f"Invalid enrichment source: {source}")
        return v


class AnalysisResponse(BaseResponse):
    """Analysis response model"""

    request_id: str
    analysis_date: datetime
    summary: Dict[str, Any]
    entity_resolutions: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    enrichments: List[Dict[str, Any]] = Field(default_factory=list)
    events: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class EntityResolutionRequest(BaseModel):
    """Entity resolution specific request"""

    entities: List[EntityInput]
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    clustering_method: str = Field(
        default="dbscan", pattern="^(dbscan|hierarchical|kmeans)$"
    )
    include_similarity_matrix: bool = False


class RelationshipMappingRequest(BaseModel):
    """Relationship mapping specific request"""

    entities: List[EntityInput]
    relationship_types: List[str] = Field(default=["officer", "ownership", "address"])
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    include_network_graph: bool = False


class EnrichmentRequest(BaseModel):
    """Enrichment specific request"""

    entities: List[EntityInput]
    enrichment_sources: List[str] = Field(default=["sanctions", "contracts"])
    include_cached: bool = True
    max_cost: float = Field(default=10.0, ge=0.0)


class EventDetectionRequest(BaseModel):
    """Event detection specific request"""

    data_sources: List[Dict[str, Any]]
    entity_names: Optional[List[str]] = None
    severity_filter: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    time_range_hours: int = Field(default=24, ge=1, le=8760)  # 1 hour to 1 year


# API Endpoints


@analysis_router.post("/comprehensive", response_model=AnalysisResponse)
async def run_comprehensive_analysis(
    request: AnalysisRequestModel,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Run comprehensive analysis pipeline"""
    try:
        # Generate request ID
        request_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(request.entities))}"

        # Convert to internal format
        entities = [entity.dict() for entity in request.entities]

        analysis_request = AnalysisRequest(
            request_id=request_id,
            entities=entities,
            analysis_types=request.analysis_types,
            enrichment_sources=request.enrichment_sources,
            relationship_types=request.relationship_types,
            confidence_threshold=request.confidence_threshold,
            include_low_confidence=request.include_low_confidence,
            max_related_entities=request.max_related_entities,
            metadata=request.metadata,
        )

        # Run analysis
        result = await orchestrator.run_comprehensive_analysis(analysis_request)

        # Convert to response format
        return AnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            request_id=result.request_id,
            analysis_date=result.analysis_date,
            summary=result.summary,
            entity_resolutions=result.entity_resolutions,
            relationships=result.relationships,
            enrichments=result.enrichments,
            events=result.events,
            metrics=result.metrics,
            warnings=result.warnings,
            errors=result.errors,
        )

    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@analysis_router.post("/entity-resolution")
async def resolve_entities(
    request: EntityResolutionRequest,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Resolve entity duplicates using fuzzy matching"""
    try:
        entities = [entity.dict() for entity in request.entities]

        # Run entity resolution
        entity_clusters = await asyncio.to_thread(
            orchestrator.entity_resolver.resolve_entities, entities
        )

        response_data = {
            "clusters": entity_clusters,
            "total_entities": len(entities),
            "total_clusters": len(entity_clusters),
            "duplicate_ratio": (
                1.0 - (len(entity_clusters) / len(entities)) if entities else 0.0
            ),
        }

        if request.include_similarity_matrix:
            similarity_matrix = await asyncio.to_thread(
                orchestrator.entity_resolver.calculate_similarity_matrix, entities
            )
            response_data["similarity_matrix"] = similarity_matrix

        return JSONResponse(
            content={
                "success": True,
                "message": f"Entity resolution completed: {len(entity_clusters)} clusters found",
                "data": response_data,
            }
        )

    except Exception as e:
        logger.error(f"Entity resolution failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Entity resolution failed: {str(e)}"
        )


@analysis_router.post("/relationship-mapping")
async def map_relationships(
    request: RelationshipMappingRequest,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Extract and map entity relationships"""
    try:
        entities = [entity.dict() for entity in request.entities]

        # Extract relationships
        relationships = await asyncio.to_thread(
            orchestrator.relationship_mapper.extract_relationships,
            entities,
            request.relationship_types,
        )

        # Convert to serializable format
        relationship_data = []
        for rel in relationships:
            relationship_data.append(
                {
                    "source_entity": rel.source_entity,
                    "target_entity": rel.target_entity,
                    "relationship_type": rel.relationship_type,
                    "confidence_score": rel.confidence_score,
                    "metadata": rel.metadata,
                    "evidence": rel.evidence,
                }
            )

        response_data = {
            "relationships": relationship_data,
            "total_relationships": len(relationship_data),
            "relationship_types": list(
                set(rel["relationship_type"] for rel in relationship_data)
            ),
        }

        if request.include_network_graph and relationships:
            graph_metrics = await asyncio.to_thread(
                orchestrator.relationship_mapper.build_network_graph, relationships
            )
            response_data["network_metrics"] = graph_metrics

        return JSONResponse(
            content={
                "success": True,
                "message": f"Relationship mapping completed: {len(relationships)} relationships found",
                "data": response_data,
            }
        )

    except Exception as e:
        logger.error(f"Relationship mapping failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Relationship mapping failed: {str(e)}"
        )


@analysis_router.post("/enrichment")
async def enrich_entities(
    request: EnrichmentRequest,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Enrich entities with external data sources"""
    try:
        entities = [entity.dict() for entity in request.entities]

        # Run enrichment
        enrichments = await orchestrator.enrichment_engine.enrich_entities(
            entities, request.enrichment_sources
        )

        # Calculate total cost
        total_cost = sum(e.cost for e in enrichments)

        if total_cost > request.max_cost:
            raise HTTPException(
                status_code=400,
                detail=f"Enrichment cost ${total_cost:.2f} exceeds maximum ${request.max_cost:.2f}",
            )

        # Convert to serializable format
        enrichment_data = []
        for enrich in enrichments:
            enrichment_data.append(
                {
                    "entity_id": enrich.entity_id,
                    "source_name": enrich.source_name,
                    "enrichment_type": enrich.enrichment_type,
                    "data": enrich.data,
                    "confidence_score": enrich.confidence_score,
                    "metadata": enrich.metadata,
                    "cost": enrich.cost,
                    "created_at": enrich.created_at.isoformat(),
                }
            )

        return JSONResponse(
            content={
                "success": True,
                "message": f"Enrichment completed: {len(enrichments)} enrichments found",
                "data": {
                    "enrichments": enrichment_data,
                    "total_enrichments": len(enrichment_data),
                    "total_cost": total_cost,
                    "sources_used": list(
                        set(e["source_name"] for e in enrichment_data)
                    ),
                },
            }
        )

    except Exception as e:
        logger.error(f"Entity enrichment failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Entity enrichment failed: {str(e)}"
        )


@analysis_router.post("/event-detection")
async def detect_events(
    request: EventDetectionRequest,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Detect business events from data sources"""
    try:
        # Run event detection
        detected_events = await orchestrator.event_detector.detect_events(
            request.data_sources, request.entity_names
        )

        # Apply severity filter
        if request.severity_filter:
            detected_events = [
                e
                for e in detected_events
                if e.severity.value == request.severity_filter
            ]

        # Convert to serializable format
        event_data = []
        for event in detected_events:
            event_data.append(
                {
                    "event_id": event.event_id,
                    "entity_id": event.entity_id,
                    "event_type": event.event_type,
                    "category": event.category.value,
                    "severity": event.severity.value,
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.event_date.isoformat(),
                    "detection_date": event.detection_date.isoformat(),
                    "confidence_score": event.confidence_score,
                    "source": event.source,
                    "source_url": event.source_url,
                    "metadata": event.metadata,
                    "related_entities": event.related_entities,
                }
            )

        # Calculate severity distribution
        severity_counts = {}
        for event in event_data:
            severity = event["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return JSONResponse(
            content={
                "success": True,
                "message": f"Event detection completed: {len(event_data)} events detected",
                "data": {
                    "events": event_data,
                    "total_events": len(event_data),
                    "severity_distribution": severity_counts,
                    "high_priority_events": len(
                        [e for e in event_data if e["severity"] in ["high", "critical"]]
                    ),
                },
            }
        )

    except Exception as e:
        logger.error(f"Event detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Event detection failed: {str(e)}")


@analysis_router.get("/status/{request_id}")
async def get_analysis_status(
    request_id: str,
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Get analysis request status"""
    try:
        status = await orchestrator.get_analysis_status(request_id)

        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail="Analysis request not found")

        return JSONResponse(
            content={
                "success": True,
                "message": f"Analysis status: {status['status']}",
                "data": status,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis status: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis status: {str(e)}"
        )


@analysis_router.get("/export/{request_id}")
async def export_analysis_results(
    request_id: str,
    format: str = Query(default="json", pattern="^(json|summary)$"),
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Export analysis results"""
    try:
        exported_data = await orchestrator.export_analysis_results(request_id, format)

        if exported_data is None:
            raise HTTPException(status_code=404, detail="Analysis results not found")

        if format == "json":
            return JSONResponse(content=exported_data)
        elif format == "summary":
            return PlainTextResponse(content=exported_data, media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export analysis results: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to export results: {str(e)}"
        )


@analysis_router.get("/metrics")
async def get_analysis_metrics(
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Get analysis performance metrics"""
    try:
        orchestrator_metrics = orchestrator.get_orchestrator_metrics()
        entity_resolver_metrics = orchestrator.entity_resolver.get_resolution_metrics()
        enrichment_metrics = orchestrator.enrichment_engine.get_enrichment_metrics()
        event_detector_metrics = orchestrator.event_detector.get_detection_metrics()

        return JSONResponse(
            content={
                "success": True,
                "message": "Analysis metrics retrieved successfully",
                "data": {
                    "orchestrator": orchestrator_metrics,
                    "entity_resolver": entity_resolver_metrics,
                    "enrichment_engine": enrichment_metrics,
                    "event_detector": event_detector_metrics,
                },
            }
        )

    except Exception as e:
        logger.error(f"Failed to get analysis metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@analysis_router.delete("/cache")
async def clear_analysis_cache(
    current_user: Dict = Depends(get_current_user),
    orchestrator: AnalysisOrchestrator = Depends(get_analysis_orchestrator),
):
    """Clear analysis caches"""
    try:
        # Clear caches
        orchestrator.enrichment_engine.clear_cache()

        return JSONResponse(
            content={"success": True, "message": "Analysis caches cleared successfully"}
        )

    except Exception as e:
        logger.error(f"Failed to clear analysis cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


# Health check endpoint
@analysis_router.get("/health")
async def analysis_health_check():
    """Analysis service health check"""
    try:
        orchestrator = get_analysis_orchestrator()
        metrics = orchestrator.get_orchestrator_metrics()

        return JSONResponse(
            content={
                "success": True,
                "message": "Analysis service is healthy",
                "data": {
                    "service": "analysis",
                    "status": "healthy",
                    "total_requests": metrics.get("total_requests", 0),
                    "uptime_seconds": (
                        datetime.utcnow() - datetime.utcnow()
                    ).total_seconds(),
                },
            }
        )

    except Exception as e:
        logger.error(f"Analysis health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "message": f"Analysis service unhealthy: {str(e)}",
            },
        )
