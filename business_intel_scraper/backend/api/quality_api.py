"""
API Endpoints for Data Quality & Provenance Intelligence

FastAPI endpoints for accessing quality metrics, provenance data,
corrections, alerts, and dashboard functionality.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..api.dependencies import get_db_session, get_current_user
from .quality_engine import quality_engine
from .provenance_tracker import provenance_tracker
from .correction_system import correction_manager, CorrectionType
from .quality_dashboard import dashboard_api, DashboardTimeRange, MetricType
from .alert_system import alert_manager, AlertSeverity, AlertType

logger = logging.getLogger(__name__)

# Create router
quality_router = APIRouter(prefix="/api/v1/quality", tags=["Data Quality"])


# Pydantic models for request/response
class QualityAssessmentRequest(BaseModel):
    entity_ids: List[str] = Field(..., description="List of entity IDs to assess")
    force_refresh: bool = Field(
        False, description="Force new assessment even if recent one exists"
    )


class QualityAssessmentResponse(BaseModel):
    entity_id: str
    overall_score: float
    completeness_score: float
    consistency_score: float
    freshness_score: float
    confidence_score: float
    issues: List[str]
    assessed_at: datetime


class CorrectionSubmissionRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID to correct")
    field_name: str = Field(..., description="Field name to correct")
    current_value: Optional[Any] = Field(None, description="Current field value")
    suggested_value: Any = Field(..., description="Suggested new value")
    correction_type: CorrectionType = Field(..., description="Type of correction")
    reason: Optional[str] = Field(None, description="Reason for correction")
    evidence: Optional[str] = Field(None, description="Supporting evidence")
    auto_apply: bool = Field(False, description="Auto-apply if high confidence")


class CorrectionReviewRequest(BaseModel):
    decision: str = Field(..., description="Review decision: 'approve' or 'reject'")
    notes: Optional[str] = Field(None, description="Review notes")


class ProvenanceQueryRequest(BaseModel):
    entity_id: Optional[str] = Field(None, description="Entity ID to trace")
    field_name: Optional[str] = Field(None, description="Specific field to trace")
    source_url: Optional[str] = Field(None, description="Filter by source URL")
    include_lineage: bool = Field(True, description="Include lineage tree")


class AlertQueryRequest(BaseModel):
    severity: Optional[AlertSeverity] = Field(None, description="Filter by severity")
    alert_type: Optional[AlertType] = Field(None, description="Filter by alert type")
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    time_range: DashboardTimeRange = Field(
        DashboardTimeRange.LAST_DAY, description="Time range"
    )


# Quality Assessment Endpoints
@quality_router.post("/assess", response_model=List[QualityAssessmentResponse])
async def assess_quality(
    request: QualityAssessmentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Assess data quality for specified entities"""
    try:
        logger.info(
            f"Quality assessment requested for {len(request.entity_ids)} entities by {current_user}"
        )

        # If many entities, process in background
        if len(request.entity_ids) > 10:
            background_tasks.add_task(
                quality_engine.assess_batch_quality,
                request.entity_ids,
                db,
                request.force_refresh,
            )
            return {
                "message": "Quality assessment started in background",
                "entity_count": len(request.entity_ids),
            }

        # Process immediately for small batches
        results = []
        for entity_id in request.entity_ids:
            assessment = await quality_engine.assess_entity_quality(
                entity_id, db, request.force_refresh
            )
            if assessment:
                results.append(
                    QualityAssessmentResponse(
                        entity_id=entity_id,
                        overall_score=assessment.overall_score,
                        completeness_score=assessment.completeness_score,
                        consistency_score=assessment.consistency_score,
                        freshness_score=assessment.freshness_score,
                        confidence_score=assessment.confidence_score,
                        issues=(
                            assessment.issues.get("issues", [])
                            if assessment.issues
                            else []
                        ),
                        assessed_at=assessment.assessed_at,
                    )
                )

        return results

    except Exception as e:
        logger.error(f"Error in quality assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/entity/{entity_id}/quality")
async def get_entity_quality(
    entity_id: str, db: AsyncSession = Depends(get_db_session)
):
    """Get latest quality assessment for an entity"""
    try:
        assessment = await quality_engine.get_latest_assessment(entity_id, db)
        if not assessment:
            raise HTTPException(status_code=404, detail="Quality assessment not found")

        return QualityAssessmentResponse(
            entity_id=entity_id,
            overall_score=assessment.overall_score,
            completeness_score=assessment.completeness_score,
            consistency_score=assessment.consistency_score,
            freshness_score=assessment.freshness_score,
            confidence_score=assessment.confidence_score,
            issues=assessment.issues.get("issues", []) if assessment.issues else [],
            assessed_at=assessment.assessed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity quality: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Provenance Endpoints
@quality_router.post("/provenance/query")
async def query_provenance(
    request: ProvenanceQueryRequest, db: AsyncSession = Depends(get_db_session)
):
    """Query provenance information"""
    try:
        if request.entity_id:
            # Get provenance for specific entity
            if request.include_lineage:
                lineage = await provenance_tracker.get_entity_lineage(
                    request.entity_id, db
                )
                return {"entity_id": request.entity_id, "lineage": lineage}
            else:
                provenance = await provenance_tracker.get_entity_provenance(
                    request.entity_id, db
                )
                return {"entity_id": request.entity_id, "provenance": provenance}

        else:
            # General provenance query
            filters = {}
            if request.field_name:
                filters["field_name"] = request.field_name
            if request.source_url:
                filters["source_url"] = request.source_url

            # This would need implementation in provenance_tracker
            return {"message": "General provenance queries not yet implemented"}

    except Exception as e:
        logger.error(f"Error querying provenance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/entity/{entity_id}/lineage")
async def get_entity_lineage(
    entity_id: str, db: AsyncSession = Depends(get_db_session)
):
    """Get complete lineage tree for an entity"""
    try:
        lineage = await provenance_tracker.get_entity_lineage(entity_id, db)
        if not lineage:
            raise HTTPException(status_code=404, detail="Entity lineage not found")

        return lineage

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity lineage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/entity/{entity_id}/changes")
async def get_entity_changes(
    entity_id: str,
    limit: int = Query(50, description="Maximum number of changes to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get change history for an entity"""
    try:
        changes = await provenance_tracker.get_entity_change_history(
            entity_id, db, limit
        )
        return {"entity_id": entity_id, "changes": changes}

    except Exception as e:
        logger.error(f"Error getting entity changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Correction Endpoints
@quality_router.post("/corrections/submit")
async def submit_correction(
    request: CorrectionSubmissionRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Submit a data correction"""
    try:
        correction_data = {
            "entity_id": request.entity_id,
            "field_name": request.field_name,
            "current_value": request.current_value,
            "suggested_value": request.suggested_value,
            "correction_type": request.correction_type.value,
            "reason": request.reason,
            "evidence": request.evidence,
            "submitted_by": current_user,
            "auto_apply": request.auto_apply,
        }

        correction = await correction_manager.submit_correction(correction_data, db)

        return {
            "correction_id": correction.correction_id,
            "status": correction.status,
            "confidence": correction.confidence,
            "submitted_at": correction.submitted_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Error submitting correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.post("/corrections/{correction_id}/review")
async def review_correction(
    correction_id: str,
    request: CorrectionReviewRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Review and approve/reject a correction"""
    try:
        correction = await correction_manager.review_correction(
            correction_id, current_user, request.decision, request.notes, db
        )

        return {
            "correction_id": correction.correction_id,
            "status": correction.status,
            "reviewed_by": correction.reviewed_by,
            "reviewed_at": (
                correction.reviewed_at.isoformat() if correction.reviewed_at else None
            ),
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error reviewing correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/corrections/pending")
async def get_pending_corrections(
    limit: int = Query(50, description="Maximum number of corrections to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get pending corrections for review"""
    try:
        corrections = await correction_manager.get_pending_corrections(db, limit)
        return {"corrections": corrections}

    except Exception as e:
        logger.error(f"Error getting pending corrections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.post("/corrections/auto-generate")
async def generate_auto_corrections(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(100, description="Number of entities to process"),
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Generate automated correction suggestions"""
    try:
        background_tasks.add_task(
            correction_manager.generate_auto_corrections, db, batch_size
        )

        return {"message": "Auto-correction generation started in background"}

    except Exception as e:
        logger.error(f"Error starting auto-correction generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard Endpoints
@quality_router.get("/dashboard/{dashboard_type}")
async def get_dashboard_data(
    dashboard_type: str,
    time_range: DashboardTimeRange = Query(DashboardTimeRange.LAST_DAY),
    metric_type: MetricType = Query(MetricType.OVERALL),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(50, description="Maximum number of items to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get dashboard data"""
    try:
        kwargs = {"time_range": time_range, "limit": limit}

        if dashboard_type == "trends":
            kwargs["metric_type"] = metric_type

        if dashboard_type == "entities" and entity_type:
            kwargs["entity_type"] = entity_type

        data = await dashboard_api.get_dashboard_data(db, dashboard_type, **kwargs)
        return data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/dashboard/export/{report_type}")
async def export_quality_report(
    report_type: str,
    format: str = Query("json", description="Export format: json, csv"),
    db: AsyncSession = Depends(get_db_session),
):
    """Export comprehensive quality report"""
    try:
        report = await dashboard_api.export_quality_report(db, report_type, format)
        return report

    except Exception as e:
        logger.error(f"Error exporting quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alert Endpoints
@quality_router.post("/alerts/query")
async def query_alerts(
    request: AlertQueryRequest,
    limit: int = Query(100, description="Maximum number of alerts to return"),
    db: AsyncSession = Depends(get_db_session),
):
    """Query alerts with filters"""
    try:
        alerts = await alert_manager.get_active_alerts(
            db,
            severity_filter=request.severity,
            alert_type_filter=request.alert_type,
            limit=limit,
        )

        return {"alerts": alerts}

    except Exception as e:
        logger.error(f"Error querying alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_notes: str = Query(..., description="Resolution notes"),
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Resolve an alert"""
    try:
        alert = await alert_manager.resolve_alert(
            alert_id, current_user, resolution_notes, db
        )

        return {
            "alert_id": alert.alert_id,
            "resolved_by": alert.resolved_by,
            "resolved_at": alert.resolved_at.isoformat(),
            "resolution_notes": alert.resolution_notes,
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.post("/alerts/process-batch")
async def process_batch_alerts(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(100, description="Number of entities to process"),
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Process alerts for a batch of entities and sources"""
    try:
        background_tasks.add_task(alert_manager.process_batch_alerts, db, batch_size)

        return {"message": "Batch alert processing started in background"}

    except Exception as e:
        logger.error(f"Error starting batch alert processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Utility Endpoints
@quality_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }


@quality_router.get("/stats")
async def get_system_stats(db: AsyncSession = Depends(get_db_session)):
    """Get system statistics"""
    try:
        # Get basic stats from dashboard
        overview = await dashboard_api.get_dashboard_data(db, "overview")
        alerts = await dashboard_api.get_dashboard_data(db, "alerts")
        corrections = await dashboard_api.get_dashboard_data(db, "corrections")

        return {
            "overview": overview,
            "alerts_summary": {
                "total_alerts": alerts.get("total_alerts", 0),
                "active_alerts": alerts.get("active_alerts", 0),
            },
            "corrections_summary": {
                "total_corrections": corrections.get("total_corrections", 0),
                "pending_corrections": len(
                    await correction_manager.get_pending_corrections(db, 1000)
                ),
            },
        }

    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Integrity Endpoints
@quality_router.post("/integrity/verify")
async def verify_data_integrity(
    entity_ids: List[str] = Query(..., description="Entity IDs to verify"),
    db: AsyncSession = Depends(get_db_session),
):
    """Verify data integrity for specified entities"""
    try:
        results = []

        for entity_id in entity_ids:
            integrity_check = await provenance_tracker.verify_data_integrity(
                entity_id, db
            )
            results.append(
                {
                    "entity_id": entity_id,
                    "is_valid": integrity_check["is_valid"],
                    "hash_matches": integrity_check["hash_matches"],
                    "issues": integrity_check.get("issues", []),
                }
            )

        return {"verification_results": results}

    except Exception as e:
        logger.error(f"Error verifying data integrity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@quality_router.get("/audit/export")
async def export_audit_trail(
    entity_id: Optional[str] = Query(None, description="Entity ID to export"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    include_signatures: bool = Query(
        True, description="Include cryptographic signatures"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """Export audit trail"""
    try:
        filters = {}
        if entity_id:
            filters["entity_id"] = entity_id
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date

        audit_data = await provenance_tracker.export_audit_trail(
            filters, include_signatures, db
        )

        return audit_data

    except Exception as e:
        logger.error(f"Error exporting audit trail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration Endpoints
@quality_router.get("/config/rules")
async def get_quality_rules(db: AsyncSession = Depends(get_db_session)):
    """Get configured quality rules"""
    # This would return configured quality assessment rules
    return {
        "message": "Quality rules configuration endpoint",
        "default_thresholds": {
            "completeness_weight": 0.3,
            "consistency_weight": 0.25,
            "freshness_weight": 0.2,
            "confidence_weight": 0.25,
        },
    }


@quality_router.post("/config/rules")
async def update_quality_rules(
    rules_config: Dict[str, Any],
    db: AsyncSession = Depends(get_db_session),
    current_user: str = Depends(get_current_user),
):
    """Update quality assessment rules"""
    # This would update quality assessment configuration
    return {
        "message": "Quality rules updated",
        "updated_by": current_user,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
