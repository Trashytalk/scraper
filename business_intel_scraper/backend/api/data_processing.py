"""
Data Processing Pipeline API Endpoints
Provides REST API for data processing, quality management, and pipeline control
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..services.data_processing import (
    submit_scraping_task,
    get_processing_metrics,
    start_processing_pipeline,
    stop_processing_pipeline,
    processing_pipeline,
    ValidationLevel,
    ProcessingStatus
)
from ..services.data_quality import (
    assess_data_quality,
    run_quality_batch_assessment,
    cleanup_duplicate_records,
    get_quality_metrics,
    quality_manager
)
from ..dependencies import require_token


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data-processing", tags=["Data Processing"])


class ScrapingTaskRequest(BaseModel):
    """Request model for scraping task submission"""
    url: str = Field(..., description="URL to scrape")
    job_id: Optional[int] = Field(None, description="Associated job ID")
    job_name: Optional[str] = Field(None, description="Job name")
    job_type: str = Field("web_scraping", description="Type of scraping job")
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10)")
    validation_level: str = Field("standard", description="Validation level")
    timeout_seconds: int = Field(30, ge=5, le=300, description="Request timeout")
    custom_headers: Dict[str, str] = Field(default_factory=dict, description="Custom HTTP headers")
    extraction_rules: Dict[str, Any] = Field(default_factory=dict, description="Custom extraction rules")


class BatchScrapingRequest(BaseModel):
    """Request model for batch scraping submission"""
    urls: List[str] = Field(..., description="List of URLs to scrape")
    job_id: Optional[int] = Field(None, description="Associated job ID")
    job_name: Optional[str] = Field(None, description="Job name")
    priority: int = Field(5, ge=1, le=10, description="Default priority for all tasks")
    validation_level: str = Field("standard", description="Validation level")
    max_concurrent: int = Field(10, ge=1, le=50, description="Maximum concurrent tasks")


class QualityAssessmentRequest(BaseModel):
    """Request model for quality assessment"""
    record_uuid: Optional[str] = Field(None, description="Specific record to assess")
    batch_size: int = Field(100, ge=1, le=1000, description="Batch size for bulk assessment")
    validation_level: str = Field("standard", description="Validation level")


class PipelineControlRequest(BaseModel):
    """Request model for pipeline control"""
    action: str = Field(..., description="Action to perform (start/stop/restart)")
    max_workers: Optional[int] = Field(None, ge=1, le=50, description="Number of workers")


@router.post("/tasks/submit", dependencies=[Depends(require_token)])
async def submit_task(request: ScrapingTaskRequest) -> Dict[str, Any]:
    """Submit a single scraping task"""
    try:
        # Validate validation level
        try:
            validation_level = ValidationLevel(request.validation_level)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid validation level: {request.validation_level}"
            )
        
        # Submit task
        task_id = await submit_scraping_task(
            url=request.url,
            job_id=request.job_id,
            job_name=request.job_name,
            priority=request.priority,
            validation_level=validation_level,
            timeout_seconds=request.timeout_seconds,
            custom_headers=request.custom_headers,
            extraction_rules=request.extraction_rules
        )
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": "Task submitted successfully",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to submit scraping task: {e}")
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")


@router.post("/tasks/submit-batch", dependencies=[Depends(require_token)])
async def submit_batch_tasks(
    background_tasks: BackgroundTasks,
    request: BatchScrapingRequest
) -> Dict[str, Any]:
    """Submit multiple scraping tasks"""
    try:
        if len(request.urls) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 URLs per batch")
        
        # Validate validation level
        try:
            validation_level = ValidationLevel(request.validation_level)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid validation level: {request.validation_level}"
            )
        
        # Submit tasks in background to avoid timeout
        background_tasks.add_task(
            _submit_batch_tasks_background,
            request.urls,
            request.job_id,
            request.job_name,
            request.priority,
            validation_level,
            request.max_concurrent
        )
        
        return {
            "status": "success",
            "message": f"Batch submission started for {len(request.urls)} URLs",
            "estimated_completion": "Processing in background",
            "submitted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to submit batch tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Batch submission failed: {str(e)}")


@router.get("/pipeline/status", dependencies=[Depends(require_token)])
async def get_pipeline_status() -> Dict[str, Any]:
    """Get current pipeline status and metrics"""
    try:
        # Get processing metrics
        metrics = await get_processing_metrics()
        
        # Get queue status
        queue_status = await processing_pipeline.get_queue_status()
        
        # Calculate derived metrics
        total_processed = metrics.completed_tasks + metrics.failed_tasks
        success_rate = (metrics.completed_tasks / total_processed * 100) if total_processed > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "pipeline_running": queue_status["is_running"],
                "active_workers": queue_status["active_workers"],
                "max_workers": queue_status["max_workers"],
                "queue_size": {
                    "regular": queue_status["regular_queue_size"],
                    "priority": queue_status["priority_queue_size"],
                    "total": queue_status["total_queue_size"]
                },
                "processing_metrics": {
                    "total_tasks": metrics.total_tasks,
                    "completed_tasks": metrics.completed_tasks,
                    "failed_tasks": metrics.failed_tasks,
                    "success_rate": round(success_rate, 2),
                    "avg_processing_time_ms": round(metrics.avg_processing_time, 2),
                    "throughput_per_minute": round(metrics.throughput_per_minute, 2),
                    "error_rate": round(metrics.error_rate, 2)
                }
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")


@router.post("/pipeline/control", dependencies=[Depends(require_token)])
async def control_pipeline(request: PipelineControlRequest) -> Dict[str, Any]:
    """Control pipeline operations (start/stop/restart)"""
    try:
        if request.action == "start":
            if processing_pipeline.is_running:
                return {
                    "status": "info",
                    "message": "Pipeline is already running",
                    "action": "start"
                }
            
            await start_processing_pipeline()
            return {
                "status": "success",
                "message": "Pipeline started successfully",
                "action": "start"
            }
            
        elif request.action == "stop":
            if not processing_pipeline.is_running:
                return {
                    "status": "info",
                    "message": "Pipeline is already stopped",
                    "action": "stop"
                }
            
            await stop_processing_pipeline()
            return {
                "status": "success",
                "message": "Pipeline stopped successfully",
                "action": "stop"
            }
            
        elif request.action == "restart":
            await stop_processing_pipeline()
            await start_processing_pipeline()
            return {
                "status": "success",
                "message": "Pipeline restarted successfully",
                "action": "restart"
            }
            
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid action: {request.action}. Use 'start', 'stop', or 'restart'"
            )
            
    except Exception as e:
        logger.error(f"Pipeline control failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline control failed: {str(e)}")


@router.get("/quality/metrics", dependencies=[Depends(require_token)])
async def get_quality_metrics_endpoint(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze")
) -> Dict[str, Any]:
    """Get data quality metrics"""
    try:
        metrics = await get_quality_metrics(days)
        
        return {
            "status": "success",
            "data": {
                "total_records": metrics.total_records,
                "quality_distribution": {
                    "high_quality": metrics.high_quality_records,
                    "medium_quality": metrics.medium_quality_records,
                    "low_quality": metrics.low_quality_records
                },
                "averages": {
                    "quality_score": round(metrics.avg_quality_score, 2),
                    "completeness": round(metrics.avg_completeness, 2)
                },
                "duplicates": metrics.duplicate_count,
                "quality_trend": metrics.quality_trend,
                "common_issues": metrics.common_issues
            },
            "period_days": days,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Quality metrics retrieval failed: {str(e)}")


@router.post("/quality/assess", dependencies=[Depends(require_token)])
async def assess_quality(request: QualityAssessmentRequest) -> Dict[str, Any]:
    """Assess data quality for specific record or batch"""
    try:
        if request.record_uuid:
            # Assess specific record
            report = await assess_data_quality(request.record_uuid)
            
            return {
                "status": "success",
                "data": {
                    "record_id": report.record_id,
                    "overall_score": round(report.overall_score, 2),
                    "component_scores": {
                        "completeness": round(report.completeness_score, 2),
                        "accuracy": round(report.accuracy_score, 2),
                        "consistency": round(report.consistency_score, 2),
                        "timeliness": round(report.timeliness_score, 2)
                    },
                    "issues": [
                        {
                            "type": issue.issue_type.value,
                            "severity": issue.severity.value,
                            "description": issue.description,
                            "affected_field": issue.affected_field,
                            "suggested_fix": issue.suggested_fix
                        }
                        for issue in report.issues
                    ],
                    "recommendations": report.recommendations
                },
                "assessed_at": datetime.utcnow().isoformat()
            }
        else:
            # Batch assessment
            reports = await run_quality_batch_assessment(request.batch_size)
            
            # Aggregate results
            total_reports = len(reports)
            avg_score = sum(r.overall_score for r in reports) / total_reports if total_reports > 0 else 0
            
            issue_counts = {}
            for report in reports:
                for issue in report.issues:
                    issue_type = issue.issue_type.value
                    issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
            
            return {
                "status": "success",
                "data": {
                    "batch_size": total_reports,
                    "average_quality_score": round(avg_score, 2),
                    "issue_summary": issue_counts,
                    "detailed_reports": [
                        {
                            "record_id": r.record_id,
                            "overall_score": round(r.overall_score, 2),
                            "issue_count": len(r.issues)
                        }
                        for r in reports[:20]  # Limit detailed results
                    ]
                },
                "assessed_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quality assessment failed: {str(e)}")


@router.post("/quality/cleanup-duplicates", dependencies=[Depends(require_token)])
async def cleanup_duplicates(
    background_tasks: BackgroundTasks,
    batch_size: int = Query(50, ge=1, le=200, description="Number of duplicate groups to process")
) -> Dict[str, Any]:
    """Clean up duplicate records"""
    try:
        # Run cleanup in background for large batches
        if batch_size > 100:
            background_tasks.add_task(_cleanup_duplicates_background, batch_size)
            
            return {
                "status": "success",
                "message": f"Duplicate cleanup started for {batch_size} groups",
                "processing": "background",
                "started_at": datetime.utcnow().isoformat()
            }
        else:
            # Run immediately for small batches
            result = await cleanup_duplicate_records(batch_size)
            
            return {
                "status": "success",
                "data": {
                    "processed_groups": result["processed_groups"],
                    "duplicates_marked": result["duplicates_marked"],
                    "errors": result["errors"]
                },
                "completed_at": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Duplicate cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Duplicate cleanup failed: {str(e)}")


@router.get("/quality/dashboard", dependencies=[Depends(require_token)])
async def get_quality_dashboard() -> Dict[str, Any]:
    """Get comprehensive quality data for dashboard"""
    try:
        dashboard_data = await quality_manager.get_quality_dashboard_data()
        
        return {
            "status": "success",
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")


@router.get("/analytics/processing-trends", dependencies=[Depends(require_token)])
async def get_processing_trends(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze")
) -> Dict[str, Any]:
    """Get processing and quality trends over time"""
    try:
        from business_intel_scraper.database.config import get_async_session
        from business_intel_scraper.backend.db.centralized_data import CentralizedDataRecord
        from sqlalchemy import func, select
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with get_async_session() as session:
            # Get daily processing volumes
            daily_volumes = await session.execute(
                select(
                    func.date(CentralizedDataRecord.centralized_at).label('date'),
                    func.count(CentralizedDataRecord.id).label('count'),
                    func.avg(CentralizedDataRecord.data_quality_score).label('avg_quality'),
                    func.avg(CentralizedDataRecord.processing_duration_ms).label('avg_processing_time')
                )
                .where(CentralizedDataRecord.centralized_at >= cutoff_date)
                .group_by(func.date(CentralizedDataRecord.centralized_at))
                .order_by('date')
            )
            
            trends = []
            for row in daily_volumes:
                trends.append({
                    'date': row.date.isoformat(),
                    'volume': row.count,
                    'avg_quality': round(row.avg_quality or 0, 2),
                    'avg_processing_time_ms': round(row.avg_processing_time or 0, 2)
                })
            
            # Get data type distribution
            type_distribution = await session.execute(
                select(
                    CentralizedDataRecord.data_type,
                    func.count(CentralizedDataRecord.id).label('count')
                )
                .where(CentralizedDataRecord.centralized_at >= cutoff_date)
                .group_by(CentralizedDataRecord.data_type)
            )
            
            data_types = {row.data_type or 'unknown': row.count for row in type_distribution}
            
        return {
            "status": "success",
            "data": {
                "daily_trends": trends,
                "data_type_distribution": data_types,
                "period_days": days
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get processing trends: {e}")
        raise HTTPException(status_code=500, detail=f"Trends retrieval failed: {str(e)}")


# Background task functions
async def _submit_batch_tasks_background(
    urls: List[str],
    job_id: Optional[int],
    job_name: Optional[str],
    priority: int,
    validation_level: ValidationLevel,
    max_concurrent: int
):
    """Submit batch tasks in background with concurrency control"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def submit_single_task(url: str):
        async with semaphore:
            try:
                await submit_scraping_task(
                    url=url,
                    job_id=job_id,
                    job_name=job_name,
                    priority=priority,
                    validation_level=validation_level
                )
            except Exception as e:
                logger.error(f"Failed to submit task for {url}: {e}")
    
    # Submit all tasks concurrently
    tasks = [submit_single_task(url) for url in urls]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    logger.info(f"Completed batch submission of {len(urls)} tasks")


async def _cleanup_duplicates_background(batch_size: int):
    """Run duplicate cleanup in background"""
    try:
        result = await cleanup_duplicate_records(batch_size)
        logger.info(f"Background duplicate cleanup completed: {result}")
    except Exception as e:
        logger.error(f"Background duplicate cleanup failed: {e}")


# Helper function for testing
async def test_data_processing_api():
    """Test data processing API functionality"""
    try:
        # Test pipeline status
        metrics = await get_processing_metrics()
        print(f"Pipeline metrics: {metrics.total_tasks} total tasks")
        
        # Test quality metrics
        quality_metrics = await get_quality_metrics(30)
        print(f"Quality metrics: {quality_metrics.total_records} records analyzed")
        
        return True
        
    except Exception as e:
        logger.error(f"Data processing API test failed: {e}")
        return False