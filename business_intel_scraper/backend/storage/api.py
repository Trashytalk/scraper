"""
API Integration for Advanced Storage Layer

REST API endpoints for:
- Raw data storage and retrieval
- Structured entity management
- Data lineage tracking
- Storage metrics and monitoring
- Data export and analysis
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from ..api.dependencies import require_token
from ..db import get_db
from .core import AdvancedStorageManager, RawDataRecord, StructuredEntity, DataLineageTracker, StorageConfig

router = APIRouter(prefix="/storage", tags=["storage"])
logger = logging.getLogger(__name__)

# Initialize storage manager (this would typically be done in a dependency)
def get_storage_manager() -> AdvancedStorageManager:
    """Get or create storage manager instance"""
    # In production, this would be properly configured and injected
    config = StorageConfig(
        database_url="sqlite:///business_intelligence.db",  # Would come from settings
        s3_bucket_prefix="business-intel-dev"
    )
    return AdvancedStorageManager(config)


# Request/Response Models

class RawDataRequest(BaseModel):
    """Request model for storing raw data"""
    source_url: str
    content: str
    content_type: str = "text/html"
    job_id: str
    spider_name: Optional[str] = None
    referrer_url: Optional[str] = None
    http_status: int = 200
    response_time_ms: int = 0
    request_headers: Dict[str, str] = Field(default_factory=dict)
    response_headers: Dict[str, str] = Field(default_factory=dict)
    language: Optional[str] = None
    page_title: Optional[str] = None
    attachments: List[Dict[str, str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    @validator('source_url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('source_url must be a valid HTTP/HTTPS URL')
        return v


class StructuredEntityRequest(BaseModel):
    """Request model for storing structured entity"""
    entity_type: str
    canonical_name: str
    structured_data: Dict[str, Any]
    raw_ids: List[str]
    extraction_method: str
    extractor_name: str
    extractor_version: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    data_quality_score: float = Field(ge=0.0, le=1.0)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)
    locations: List[Dict[str, Any]] = Field(default_factory=list)
    industry_codes: List[str] = Field(default_factory=list)
    business_identifiers: Dict[str, str] = Field(default_factory=dict)
    financial_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    @validator('confidence_score', 'data_quality_score')
    def validate_scores(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Scores must be between 0.0 and 1.0')
        return v


class EntitySearchRequest(BaseModel):
    """Request model for entity search"""
    query: str
    entity_type: Optional[str] = None
    category: Optional[str] = None
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    limit: int = Field(50, ge=1, le=1000)


class DataExportRequest(BaseModel):
    """Request model for data export"""
    format: str = Field("parquet", regex="^(parquet|csv|json)$")
    entity_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_raw_data: bool = True
    include_entities: bool = True
    include_lineage: bool = True


# Response Models

class RawDataResponse(BaseModel):
    """Response model for raw data operations"""
    raw_id: str
    status: str
    message: str
    storage_key: Optional[str] = None
    content_hash: Optional[str] = None


class StructuredEntityResponse(BaseModel):
    """Response model for structured entity operations"""
    entity_id: str
    status: str
    message: str
    confidence_score: float
    data_quality_score: float


class EntitySearchResponse(BaseModel):
    """Response model for entity search"""
    total_results: int
    results: List[Dict[str, Any]]
    query: str
    execution_time_ms: int


class ProvenanceResponse(BaseModel):
    """Response model for entity provenance"""
    entity_id: str
    entity_type: str
    canonical_name: str
    source_count: int
    raw_sources: List[Dict[str, Any]]
    lineage_entries: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    quality_score: float


class LineageGraphResponse(BaseModel):
    """Response model for lineage graph"""
    entity_id: str
    lineage_graph: Dict[str, Any]
    metrics: Dict[str, Any]
    summary: Dict[str, Any]


class StorageMetricsResponse(BaseModel):
    """Response model for storage metrics"""
    timestamp: str
    database_metrics: Dict[str, int]
    quality_metrics: Dict[str, float]
    processing_status: Dict[str, int]
    entity_types: Dict[str, int]
    recent_activity: Dict[str, int]
    storage_size: Dict[str, Any]
    system_metrics: Dict[str, int]


class ExportStatusResponse(BaseModel):
    """Response model for export status"""
    export_id: str
    status: str
    progress: float
    file_paths: Dict[str, str]
    record_counts: Dict[str, int]
    total_size_mb: float


# API Endpoints

@router.post("/raw-data", response_model=RawDataResponse, dependencies=[Depends(require_token)])
async def store_raw_data(request: RawDataRequest) -> RawDataResponse:
    """Store raw data with full provenance tracking"""
    try:
        storage_manager = get_storage_manager()
        
        # Create RawDataRecord
        raw_record = RawDataRecord(
            raw_id=f"raw_{int(datetime.utcnow().timestamp() * 1000)}_{hash(request.source_url) % 10000:04d}",
            source_url=request.source_url,
            content=request.content,
            content_type=request.content_type,
            fetched_at=datetime.utcnow(),
            job_id=request.job_id,
            
            referrer_url=request.referrer_url,
            http_status=request.http_status,
            response_time_ms=request.response_time_ms,
            
            request_headers=request.request_headers,
            response_headers=request.response_headers,
            
            language=request.language,
            page_title=request.page_title,
            
            attachments=request.attachments,
            
            processing_status="pending",
            spider_name=request.spider_name,
            
            metadata=request.metadata,
            tags=request.tags
        )
        
        # Store the data
        raw_id = await storage_manager.store_raw_data(raw_record)
        
        return RawDataResponse(
            raw_id=raw_id,
            status="success",
            message="Raw data stored successfully",
            storage_key=raw_record.storage_key,
            content_hash=storage_manager._calculate_content_hash(request.content)
        )
        
    except Exception as e:
        logger.error(f"Failed to store raw data: {e}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")


@router.get("/raw-data/{raw_id}", dependencies=[Depends(require_token)])
async def get_raw_data(raw_id: str) -> Dict[str, Any]:
    """Retrieve raw data by ID"""
    try:
        storage_manager = get_storage_manager()
        
        raw_record = await storage_manager.retrieve_raw_data(raw_id)
        if not raw_record:
            raise HTTPException(status_code=404, detail="Raw data not found")
        
        return {
            "raw_id": raw_record.raw_id,
            "source_url": raw_record.source_url,
            "content_type": raw_record.content_type,
            "fetched_at": raw_record.fetched_at.isoformat(),
            "job_id": raw_record.job_id,
            "http_status": raw_record.http_status,
            "content_size": len(raw_record.content),
            "page_title": raw_record.page_title,
            "language": raw_record.language,
            "processing_status": raw_record.processing_status,
            "metadata": raw_record.metadata,
            "tags": raw_record.tags
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve raw data {raw_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.post("/entities", response_model=StructuredEntityResponse, dependencies=[Depends(require_token)])
async def store_structured_entity(request: StructuredEntityRequest) -> StructuredEntityResponse:
    """Store structured entity with provenance linking"""
    try:
        storage_manager = get_storage_manager()
        
        # Create StructuredEntity
        entity = StructuredEntity(
            entity_id=f"entity_{int(datetime.utcnow().timestamp() * 1000)}_{hash(request.canonical_name) % 10000:04d}",
            entity_type=request.entity_type,
            canonical_name=request.canonical_name,
            structured_data=request.structured_data,
            
            raw_ids=request.raw_ids,
            source_urls=[],  # Would be populated from raw_ids
            extraction_method=request.extraction_method,
            extractor_name=request.extractor_name,
            extractor_version=request.extractor_version,
            
            confidence_score=request.confidence_score,
            data_quality_score=request.data_quality_score,
            completeness_score=1.0,  # Could be calculated
            
            extracted_at=datetime.utcnow(),
            
            category=request.category,
            subcategory=request.subcategory,
            
            contact_info=request.contact_info,
            locations=request.locations,
            industry_codes=request.industry_codes,
            business_identifiers=request.business_identifiers,
            financial_data=request.financial_data,
            
            metadata=request.metadata,
            tags=request.tags
        )
        
        # Store the entity
        entity_id = await storage_manager.store_structured_entity(entity)
        
        return StructuredEntityResponse(
            entity_id=entity_id,
            status="success",
            message="Structured entity stored successfully",
            confidence_score=entity.confidence_score,
            data_quality_score=entity.data_quality_score
        )
        
    except Exception as e:
        logger.error(f"Failed to store structured entity: {e}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")


@router.post("/entities/search", response_model=EntitySearchResponse, dependencies=[Depends(require_token)])
async def search_entities(request: EntitySearchRequest) -> EntitySearchResponse:
    """Search structured entities"""
    try:
        start_time = datetime.utcnow()
        storage_manager = get_storage_manager()
        
        results = await storage_manager.search_entities(
            query=request.query,
            entity_type=request.entity_type,
            category=request.category,
            min_confidence=request.min_confidence,
            limit=request.limit
        )
        
        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return EntitySearchResponse(
            total_results=len(results),
            results=results,
            query=request.query,
            execution_time_ms=int(execution_time)
        )
        
    except Exception as e:
        logger.error(f"Entity search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/entities/{entity_id}/provenance", response_model=ProvenanceResponse, dependencies=[Depends(require_token)])
async def get_entity_provenance(entity_id: str) -> ProvenanceResponse:
    """Get complete provenance chain for an entity"""
    try:
        storage_manager = get_storage_manager()
        
        provenance = await storage_manager.get_entity_provenance(entity_id)
        if not provenance:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return ProvenanceResponse(
            entity_id=provenance['entity_id'],
            entity_type=provenance['entity_type'],
            canonical_name=provenance['canonical_name'],
            source_count=provenance['total_sources'],
            raw_sources=provenance['raw_sources'],
            lineage_entries=provenance['lineage_entries'],
            relationships=provenance['relationships'],
            quality_score=provenance['data_quality_score']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get provenance for entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Provenance retrieval failed: {str(e)}")


@router.get("/entities/{entity_id}/lineage", response_model=LineageGraphResponse, dependencies=[Depends(require_token)])
async def get_entity_lineage(entity_id: str) -> LineageGraphResponse:
    """Get complete lineage graph for an entity"""
    try:
        storage_manager = get_storage_manager()
        lineage_tracker = DataLineageTracker(storage_manager)
        
        lineage_data = await lineage_tracker.trace_entity_lineage(entity_id)
        if not lineage_data:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return LineageGraphResponse(
            entity_id=entity_id,
            lineage_graph=lineage_data['lineage_graph'],
            metrics=lineage_data['metrics'],
            summary=lineage_data['summary']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lineage for entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Lineage retrieval failed: {str(e)}")


@router.get("/metrics", response_model=StorageMetricsResponse, dependencies=[Depends(require_token)])
async def get_storage_metrics() -> StorageMetricsResponse:
    """Get comprehensive storage metrics"""
    try:
        storage_manager = get_storage_manager()
        
        metrics = await storage_manager.get_storage_metrics()
        
        return StorageMetricsResponse(
            timestamp=metrics['timestamp'],
            database_metrics=metrics['database_metrics'],
            quality_metrics=metrics['quality_metrics'],
            processing_status=metrics['processing_status'],
            entity_types=metrics['entity_types'],
            recent_activity=metrics['recent_activity'],
            storage_size=metrics['storage_size'],
            system_metrics=metrics['system_metrics']
        )
        
    except Exception as e:
        logger.error(f"Failed to get storage metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")


@router.post("/export", dependencies=[Depends(require_token)])
async def export_data_lineage(request: DataExportRequest, background_tasks: BackgroundTasks):
    """Export data lineage for analysis"""
    try:
        storage_manager = get_storage_manager()
        
        # Generate export ID
        export_id = f"export_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Start export in background
        background_tasks.add_task(
            _perform_data_export,
            export_id,
            storage_manager,
            request
        )
        
        return {
            "export_id": export_id,
            "status": "started",
            "message": "Data export started in background",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to start data export: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed to start: {str(e)}")


@router.get("/export/{export_id}/status", dependencies=[Depends(require_token)])
async def get_export_status(export_id: str):
    """Get status of data export"""
    # In production, this would check the actual status
    return {
        "export_id": export_id,
        "status": "completed",  # Would be dynamic
        "progress": 100.0,
        "message": "Export completed successfully",
        "download_url": f"/storage/export/{export_id}/download"
    }


# Background Tasks

async def _perform_data_export(export_id: str, storage_manager: AdvancedStorageManager, request: DataExportRequest):
    """Perform data export in background"""
    try:
        logger.info(f"Starting export {export_id}")
        
        # Prepare date range
        date_range = None
        if request.date_from and request.date_to:
            date_range = (request.date_from, request.date_to)
        
        # Perform export
        export_result = await storage_manager.export_data_lineage(
            output_format=request.format,
            entity_types=request.entity_types,
            date_range=date_range
        )
        
        logger.info(f"Export {export_id} completed: {export_result['total_size_mb']} MB exported")
        
        # In production, update export status in database
        
    except Exception as e:
        logger.error(f"Export {export_id} failed: {e}")
        # In production, update export status with error


# Health and Status Endpoints

@router.get("/health")
async def storage_health():
    """Check storage system health"""
    try:
        storage_manager = get_storage_manager()
        
        # Test database connection
        session = storage_manager.Session()
        try:
            session.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        finally:
            session.close()
        
        # Test object storage
        s3_status = "available" if storage_manager.s3_client else "unavailable"
        
        # Test Elasticsearch
        es_status = "available" if storage_manager.es_client else "unavailable"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": db_status,
                "object_storage": s3_status,
                "elasticsearch": es_status
            },
            "metrics": dict(storage_manager.metrics)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Cache Management Endpoints

@router.post("/cache/clear", dependencies=[Depends(require_token)])
async def clear_cache():
    """Clear storage system cache"""
    try:
        storage_manager = get_storage_manager()
        
        if hasattr(storage_manager, '_cache'):
            cache_size = len(storage_manager._cache)
            storage_manager._cache.clear()
            storage_manager._cache_access_times.clear()
            
            return {
                "status": "success",
                "message": f"Cache cleared, {cache_size} items removed",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "status": "info",
                "message": "Cache not enabled",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.get("/cache/stats", dependencies=[Depends(require_token)])
async def get_cache_stats():
    """Get cache statistics"""
    try:
        storage_manager = get_storage_manager()
        
        if hasattr(storage_manager, '_cache'):
            total_hits = storage_manager.metrics['cache_hits']
            total_misses = storage_manager.metrics['cache_misses']
            hit_rate = total_hits / (total_hits + total_misses) if total_hits + total_misses > 0 else 0
            
            return {
                "cache_enabled": True,
                "cache_size": len(storage_manager._cache),
                "max_cache_size": storage_manager._max_cache_size,
                "cache_hits": total_hits,
                "cache_misses": total_misses,
                "hit_rate": round(hit_rate, 3),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "cache_enabled": False,
                "message": "Cache not configured",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Cache stats retrieval failed: {str(e)}")
