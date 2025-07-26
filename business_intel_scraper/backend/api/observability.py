"""
Comprehensive Observability API
Provides endpoints for monitoring, alerting, metrics, and system health
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ..dependencies import get_db, require_token
from ..services.monitoring_service import monitoring_service
from ..db.centralized_data import SystemMetrics, AlertRecord, PerformanceBaseline
from sqlalchemy import func, desc, and_, or_

router = APIRouter(prefix="/observability", tags=["observability"])


# Pydantic models for request/response
class MetricsQuery(BaseModel):
    hours: int = Field(default=24, ge=1, le=168, description="Hours of data to retrieve")
    metric_names: Optional[List[str]] = Field(default=None, description="Specific metrics to retrieve")
    aggregation: str = Field(default="raw", regex="^(raw|hourly|daily)$")


class AlertQuery(BaseModel):
    severity: Optional[str] = Field(default=None, regex="^(low|medium|high|critical)$")
    status: Optional[str] = Field(default=None, regex="^(active|acknowledged|resolved)$")
    hours: int = Field(default=24, ge=1, le=720)
    limit: int = Field(default=100, ge=1, le=1000)


class AlertAcknowledgeRequest(BaseModel):
    alert_ids: List[str] = Field(description="List of alert UUIDs to acknowledge")
    acknowledged_by: str = Field(description="User acknowledging the alerts")
    notes: Optional[str] = Field(default=None, description="Acknowledgment notes")


class ThresholdUpdateRequest(BaseModel):
    metric_name: str = Field(description="Name of the metric")
    warning_threshold: float = Field(description="Warning threshold value")
    critical_threshold: float = Field(description="Critical threshold value")
    enabled: bool = Field(default=True, description="Whether alerting is enabled")


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    checks: Dict[str, Any]
    summary: Dict[str, Any]


@router.get("/health", response_model=HealthCheckResponse)
async def get_system_health():
    """
    Comprehensive system health check
    Returns overall system status and detailed health information
    """
    try:
        health_summary = await monitoring_service.get_system_health_summary()
        
        # Perform additional health checks
        health_checks = {
            "monitoring_service": await _check_monitoring_service(),
            "database": await _check_database_health(),
            "metrics_collection": await _check_metrics_collection(),
            "alerting_system": await _check_alerting_system(),
            "performance_baselines": await _check_baseline_health()
        }
        
        # Determine overall status
        overall_status = "healthy"
        if any(check.get("status") == "critical" for check in health_checks.values()):
            overall_status = "critical"
        elif any(check.get("status") == "degraded" for check in health_checks.values()):
            overall_status = "degraded"
        elif any(check.get("status") == "warning" for check in health_checks.values()):
            overall_status = "warning"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            checks=health_checks,
            summary=health_summary
        )
        
    except Exception as e:
        return HealthCheckResponse(
            status="critical",
            timestamp=datetime.utcnow().isoformat(),
            checks={"error": {"status": "critical", "message": str(e)}},
            summary={"error": str(e)}
        )


@router.get("/metrics/current")
async def get_current_metrics():
    """
    Get current real-time system metrics
    """
    try:
        current_metrics = await monitoring_service.collect_system_metrics(source="api_request")
        
        return {
            "timestamp": current_metrics.collected_at.isoformat(),
            "system_resources": {
                "cpu_percent": current_metrics.cpu_percent,
                "memory_percent": current_metrics.memory_percent,
                "memory_used_mb": current_metrics.memory_used_mb,
                "memory_available_mb": current_metrics.memory_available_mb,
                "disk_usage_percent": current_metrics.disk_usage_percent,
                "disk_free_gb": current_metrics.disk_free_gb
            },
            "network_io": {
                "connections_count": current_metrics.network_connections_count,
                "bytes_sent": current_metrics.network_io_bytes_sent,
                "bytes_recv": current_metrics.network_io_bytes_recv
            },
            "application": {
                "active_threads": current_metrics.active_threads,
                "open_file_descriptors": current_metrics.open_file_descriptors,
                "database_connections_active": current_metrics.database_connections_active,
                "database_connections_idle": current_metrics.database_connections_idle,
                "cache_hit_rate": current_metrics.cache_hit_rate,
                "cache_memory_usage_mb": current_metrics.cache_memory_usage_mb
            },
            "performance": {
                "requests_per_minute": current_metrics.requests_per_minute,
                "avg_response_time_ms": current_metrics.avg_response_time_ms,
                "p95_response_time_ms": current_metrics.p95_response_time_ms,
                "p99_response_time_ms": current_metrics.p99_response_time_ms,
                "error_rate_percent": current_metrics.error_rate_percent
            },
            "business_metrics": {
                "active_scraping_jobs": current_metrics.active_scraping_jobs,
                "completed_jobs_last_hour": current_metrics.completed_jobs_last_hour,
                "failed_jobs_last_hour": current_metrics.failed_jobs_last_hour,
                "data_processing_rate_per_min": current_metrics.data_processing_rate_per_min
            },
            "health": {
                "health_status": current_metrics.health_status,
                "alert_count": current_metrics.alert_count,
                "anomaly_score": current_metrics.anomaly_score
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving current metrics: {str(e)}")


@router.post("/metrics/query")
async def query_metrics(query: MetricsQuery, db: Session = Depends(get_db)):
    """
    Query historical metrics with flexible filtering and aggregation
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=query.hours)
        
        # Base query
        metrics_query = db.query(SystemMetrics).filter(
            SystemMetrics.collected_at >= cutoff
        )
        
        # Apply aggregation
        if query.aggregation == "raw":
            metrics = metrics_query.order_by(desc(SystemMetrics.collected_at)).limit(1000).all()
            
            result_data = []
            for metric in metrics:
                data_point = {
                    "timestamp": metric.collected_at.isoformat(),
                    "collection_source": metric.collection_source
                }
                
                # Include requested metrics or all if none specified
                if query.metric_names:
                    for metric_name in query.metric_names:
                        if hasattr(metric, metric_name):
                            data_point[metric_name] = getattr(metric, metric_name)
                else:
                    # Include all key metrics
                    data_point.update({
                        "cpu_percent": metric.cpu_percent,
                        "memory_percent": metric.memory_percent,
                        "disk_usage_percent": metric.disk_usage_percent,
                        "requests_per_minute": metric.requests_per_minute,
                        "avg_response_time_ms": metric.avg_response_time_ms,
                        "error_rate_percent": metric.error_rate_percent,
                        "health_status": metric.health_status
                    })
                
                result_data.append(data_point)
                
        elif query.aggregation == "hourly":
            # Hourly aggregation
            result_data = await _aggregate_metrics_hourly(db, cutoff, query.metric_names)
            
        elif query.aggregation == "daily":
            # Daily aggregation  
            result_data = await _aggregate_metrics_daily(db, cutoff, query.metric_names)
        
        return {
            "query": query.dict(),
            "data_points": len(result_data),
            "time_range": {
                "start": cutoff.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "data": result_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying metrics: {str(e)}")


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None, regex="^(low|medium|high|critical)$"),
    status: Optional[str] = Query(None, regex="^(active|acknowledged|resolved)$"),
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve alerts with filtering options
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query with filters
        alerts_query = db.query(AlertRecord).filter(
            AlertRecord.triggered_at >= cutoff
        )
        
        if severity:
            alerts_query = alerts_query.filter(AlertRecord.severity == severity)
            
        if status:
            alerts_query = alerts_query.filter(AlertRecord.status == status)
        
        alerts = alerts_query.order_by(desc(AlertRecord.triggered_at)).limit(limit).all()
        
        # Format alerts for response
        formatted_alerts = []
        for alert in alerts:
            formatted_alert = {
                "alert_uuid": alert.alert_uuid,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "category": alert.category,
                "title": alert.title,
                "message": alert.message,
                "source_component": alert.source_component,
                "source_metric_name": alert.source_metric_name,
                "source_metric_value": alert.source_metric_value,
                "threshold_value": alert.threshold_value,
                "triggered_at": alert.triggered_at.isoformat(),
                "status": alert.status,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "acknowledged_by": alert.acknowledged_by,
                "resolved_by": alert.resolved_by,
                "occurrence_count": alert.occurrence_count,
                "impact_level": alert.impact_level,
                "affected_components": alert.affected_components,
                "technical_details": alert.technical_details
            }
            formatted_alerts.append(formatted_alert)
        
        # Get alert summary statistics
        summary = await _get_alert_summary(db, cutoff)
        
        return {
            "alerts": formatted_alerts,
            "total_count": len(formatted_alerts),
            "summary": summary,
            "filters": {
                "severity": severity,
                "status": status,
                "hours": hours,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")


@router.post("/alerts/acknowledge")
async def acknowledge_alerts(
    request: AlertAcknowledgeRequest,
    db: Session = Depends(get_db)
):
    """
    Acknowledge one or more alerts
    """
    try:
        acknowledged_count = 0
        errors = []
        
        for alert_uuid in request.alert_ids:
            try:
                alert = db.query(AlertRecord).filter(
                    AlertRecord.alert_uuid == alert_uuid
                ).first()
                
                if not alert:
                    errors.append(f"Alert {alert_uuid} not found")
                    continue
                    
                if alert.status != "active":
                    errors.append(f"Alert {alert_uuid} is not in active status")
                    continue
                
                # Update alert
                alert.status = "acknowledged"
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = request.acknowledged_by
                if request.notes:
                    alert.resolution_notes = request.notes
                
                acknowledged_count += 1
                
            except Exception as e:
                errors.append(f"Error acknowledging alert {alert_uuid}: {str(e)}")
        
        if acknowledged_count > 0:
            db.commit()
        
        return {
            "acknowledged_count": acknowledged_count,
            "total_requested": len(request.alert_ids),
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error acknowledging alerts: {str(e)}")


@router.get("/baselines")
async def get_performance_baselines(
    metric_name: Optional[str] = Query(None, description="Specific metric to retrieve"),
    component: Optional[str] = Query(None, description="Component to filter by"),
    db: Session = Depends(get_db)
):
    """
    Retrieve performance baselines for anomaly detection
    """
    try:
        baselines_query = db.query(PerformanceBaseline).filter(
            PerformanceBaseline.is_active == True
        )
        
        if metric_name:
            baselines_query = baselines_query.filter(
                PerformanceBaseline.metric_name == metric_name
            )
            
        if component:
            baselines_query = baselines_query.filter(
                PerformanceBaseline.component == component
            )
        
        baselines = baselines_query.order_by(
            PerformanceBaseline.metric_name,
            desc(PerformanceBaseline.baseline_created_at)
        ).all()
        
        formatted_baselines = []
        for baseline in baselines:
            formatted_baseline = {
                "baseline_uuid": baseline.baseline_uuid,
                "metric_name": baseline.metric_name,
                "component": baseline.component,
                "environment": baseline.environment,
                "statistics": {
                    "mean": baseline.baseline_mean,
                    "median": baseline.baseline_median,
                    "std_dev": baseline.baseline_std_dev,
                    "min": baseline.baseline_min,
                    "max": baseline.baseline_max,
                    "p95": baseline.baseline_p95,
                    "p99": baseline.baseline_p99
                },
                "thresholds": {
                    "warning": baseline.warning_threshold,
                    "critical": baseline.critical_threshold,
                    "lower_bound": baseline.lower_bound
                },
                "quality_metrics": {
                    "sample_count": baseline.sample_count,
                    "confidence_score": baseline.confidence_score,
                    "variance_score": baseline.variance_score
                },
                "time_period": {
                    "start": baseline.baseline_period_start.isoformat() if baseline.baseline_period_start else None,
                    "end": baseline.baseline_period_end.isoformat() if baseline.baseline_period_end else None,
                    "created_at": baseline.baseline_created_at.isoformat()
                },
                "patterns": {
                    "hourly": baseline.hourly_patterns,
                    "daily": baseline.daily_patterns,
                    "seasonal": baseline.seasonal_factors
                },
                "status": {
                    "is_active": baseline.is_active,
                    "is_validated": baseline.is_validated,
                    "validation_notes": baseline.validation_notes
                }
            }
            formatted_baselines.append(formatted_baseline)
        
        return {
            "baselines": formatted_baselines,
            "total_count": len(formatted_baselines),
            "filters": {
                "metric_name": metric_name,
                "component": component
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving baselines: {str(e)}")


@router.post("/baselines/recalculate")
async def trigger_baseline_recalculation(
    background_tasks: BackgroundTasks,
    metric_names: Optional[List[str]] = Query(None, description="Specific metrics to recalculate")
):
    """
    Trigger recalculation of performance baselines
    """
    try:
        # Add background task to recalculate baselines
        background_tasks.add_task(
            _recalculate_baselines_task,
            metric_names
        )
        
        return {
            "message": "Baseline recalculation triggered",
            "metrics": metric_names or "all metrics",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering baseline recalculation: {str(e)}")


@router.put("/alert-thresholds")
async def update_alert_thresholds(request: ThresholdUpdateRequest):
    """
    Update alert thresholds for monitoring
    """
    try:
        # Update threshold in monitoring service
        if request.metric_name in monitoring_service.alert_configurations:
            config = monitoring_service.alert_configurations[request.metric_name]
            config.thresholds.warning_value = request.warning_threshold
            config.thresholds.critical_value = request.critical_threshold
            config.enabled = request.enabled
            
            return {
                "message": f"Alert thresholds updated for {request.metric_name}",
                "metric_name": request.metric_name,
                "warning_threshold": request.warning_threshold,
                "critical_threshold": request.critical_threshold,
                "enabled": request.enabled,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Alert configuration not found for metric: {request.metric_name}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating alert thresholds: {str(e)}")


@router.get("/dashboard/summary")
async def get_observability_dashboard():
    """
    Get comprehensive observability dashboard data
    """
    try:
        # Get current system health
        health_summary = await monitoring_service.get_system_health_summary()
        
        # Get recent metrics
        recent_metrics = await monitoring_service.get_metrics_history(hours=6)
        
        # Get active alerts summary
        db = next(get_db())
        try:
            alert_counts = {
                "critical": db.query(func.count(AlertRecord.id)).filter(
                    and_(AlertRecord.status == "active", AlertRecord.severity == "critical")
                ).scalar() or 0,
                "high": db.query(func.count(AlertRecord.id)).filter(
                    and_(AlertRecord.status == "active", AlertRecord.severity == "high")
                ).scalar() or 0,
                "medium": db.query(func.count(AlertRecord.id)).filter(
                    and_(AlertRecord.status == "active", AlertRecord.severity == "medium")
                ).scalar() or 0,
                "low": db.query(func.count(AlertRecord.id)).filter(
                    and_(AlertRecord.status == "active", AlertRecord.severity == "low")
                ).scalar() or 0
            }
            
            # Get recent alerts
            recent_alerts = db.query(AlertRecord).filter(
                AlertRecord.triggered_at >= datetime.utcnow() - timedelta(hours=24)
            ).order_by(desc(AlertRecord.triggered_at)).limit(10).all()
            
        finally:
            db.close()
        
        # Format recent alerts
        formatted_recent_alerts = [
            {
                "alert_uuid": alert.alert_uuid,
                "severity": alert.severity,
                "title": alert.title,
                "triggered_at": alert.triggered_at.isoformat(),
                "status": alert.status,
                "source_component": alert.source_component
            }
            for alert in recent_alerts
        ]
        
        # Calculate trends
        trends = _calculate_metric_trends(recent_metrics)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_health": health_summary,
            "metrics_trends": trends,
            "alerts": {
                "counts_by_severity": alert_counts,
                "total_active": sum(alert_counts.values()),
                "recent_alerts": formatted_recent_alerts
            },
            "monitoring_status": {
                "monitoring_active": monitoring_service.monitoring_active,
                "collection_interval": monitoring_service.collection_interval,
                "metrics_buffer_size": len(monitoring_service.metrics_buffer)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard summary: {str(e)}")


@router.post("/monitoring/start")
async def start_monitoring_service(background_tasks: BackgroundTasks):
    """
    Start the monitoring service
    """
    try:
        if monitoring_service.monitoring_active:
            return {
                "message": "Monitoring service is already active",
                "status": "already_running",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Start monitoring in background
        background_tasks.add_task(monitoring_service.start_monitoring)
        
        return {
            "message": "Monitoring service started",
            "status": "started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting monitoring service: {str(e)}")


@router.post("/monitoring/stop")
async def stop_monitoring_service():
    """
    Stop the monitoring service
    """
    try:
        await monitoring_service.stop_monitoring()
        
        return {
            "message": "Monitoring service stopped",
            "status": "stopped",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping monitoring service: {str(e)}")


# Helper functions

async def _check_monitoring_service() -> Dict[str, Any]:
    """Check monitoring service health"""
    try:
        is_active = monitoring_service.monitoring_active
        buffer_size = len(monitoring_service.metrics_buffer)
        
        status = "healthy" if is_active else "warning"
        
        return {
            "status": status,
            "active": is_active,
            "metrics_buffer_size": buffer_size,
            "last_collection": monitoring_service.metrics_buffer[-1].collected_at.isoformat() if buffer_size > 0 else None
        }
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }


async def _check_database_health() -> Dict[str, Any]:
    """Check database connectivity and health"""
    try:
        db = next(get_db())
        
        # Test query
        result = db.execute("SELECT 1").scalar()
        
        # Check recent metrics count
        metrics_count = db.query(func.count(SystemMetrics.id)).filter(
            SystemMetrics.collected_at >= datetime.utcnow() - timedelta(hours=1)
        ).scalar()
        
        db.close()
        
        status = "healthy" if result == 1 and metrics_count > 0 else "warning"
        
        return {
            "status": status,
            "connection": "ok",
            "recent_metrics_count": metrics_count
        }
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }


async def _check_metrics_collection() -> Dict[str, Any]:
    """Check metrics collection health"""
    try:
        if not monitoring_service.metrics_buffer:
            return {
                "status": "warning",
                "message": "No metrics in buffer"
            }
        
        latest_metric = monitoring_service.metrics_buffer[-1]
        time_since_last = (datetime.utcnow() - latest_metric.collected_at).total_seconds()
        
        status = "healthy" if time_since_last < 120 else "warning"  # Within 2 minutes
        
        return {
            "status": status,
            "last_collection_seconds_ago": time_since_last,
            "buffer_size": len(monitoring_service.metrics_buffer)
        }
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }


async def _check_alerting_system() -> Dict[str, Any]:
    """Check alerting system health"""
    try:
        config_count = len(monitoring_service.alert_configurations)
        enabled_count = len([c for c in monitoring_service.alert_configurations.values() if c.enabled])
        
        return {
            "status": "healthy" if enabled_count > 0 else "warning",
            "total_configurations": config_count,
            "enabled_configurations": enabled_count
        }
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }


async def _check_baseline_health() -> Dict[str, Any]:
    """Check performance baseline health"""
    try:
        db = next(get_db())
        
        baseline_count = db.query(func.count(PerformanceBaseline.id)).filter(
            PerformanceBaseline.is_active == True
        ).scalar()
        
        db.close()
        
        return {
            "status": "healthy" if baseline_count > 0 else "warning",
            "active_baselines": baseline_count
        }
    except Exception as e:
        return {
            "status": "critical",
            "error": str(e)
        }


async def _aggregate_metrics_hourly(db: Session, cutoff: datetime, metric_names: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Aggregate metrics by hour"""
    # This would implement hourly aggregation logic
    # For now, return simplified aggregation
    return []


async def _aggregate_metrics_daily(db: Session, cutoff: datetime, metric_names: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Aggregate metrics by day"""
    # This would implement daily aggregation logic
    # For now, return simplified aggregation
    return []


async def _get_alert_summary(db: Session, cutoff: datetime) -> Dict[str, Any]:
    """Get alert summary statistics"""
    try:
        total_alerts = db.query(func.count(AlertRecord.id)).filter(
            AlertRecord.triggered_at >= cutoff
        ).scalar() or 0
        
        active_alerts = db.query(func.count(AlertRecord.id)).filter(
            and_(
                AlertRecord.triggered_at >= cutoff,
                AlertRecord.status == "active"
            )
        ).scalar() or 0
        
        critical_alerts = db.query(func.count(AlertRecord.id)).filter(
            and_(
                AlertRecord.triggered_at >= cutoff,
                AlertRecord.severity == "critical"
            )
        ).scalar() or 0
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "critical_alerts": critical_alerts,
            "resolution_rate": ((total_alerts - active_alerts) / max(total_alerts, 1)) * 100
        }
    except Exception as e:
        return {"error": str(e)}


async def _recalculate_baselines_task(metric_names: Optional[List[str]]):
    """Background task to recalculate baselines"""
    try:
        if metric_names:
            for metric_name in metric_names:
                await monitoring_service._calculate_metric_baseline(metric_name)
        else:
            await monitoring_service.update_performance_baselines()
    except Exception as e:
        logger.error(f"Error in baseline recalculation task: {e}")


def _calculate_metric_trends(metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate trends from metrics history"""
    if len(metrics_history) < 2:
        return {}
    
    # Simple trend calculation
    recent = metrics_history[:len(metrics_history)//2]  # Recent half
    older = metrics_history[len(metrics_history)//2:]   # Older half
    
    trends = {}
    
    for metric_name in ["cpu_percent", "memory_percent", "avg_response_time_ms", "error_rate_percent"]:
        recent_values = [m.get(metric_name, 0) for m in recent if m.get(metric_name) is not None]
        older_values = [m.get(metric_name, 0) for m in older if m.get(metric_name) is not None]
        
        if recent_values and older_values:
            recent_avg = sum(recent_values) / len(recent_values)
            older_avg = sum(older_values) / len(older_values)
            
            if older_avg > 0:
                change_percent = ((recent_avg - older_avg) / older_avg) * 100
                trends[metric_name] = {
                    "change_percent": round(change_percent, 2),
                    "direction": "up" if change_percent > 0 else "down" if change_percent < 0 else "stable",
                    "recent_avg": round(recent_avg, 2),
                    "older_avg": round(older_avg, 2)
                }
    
    return trends
