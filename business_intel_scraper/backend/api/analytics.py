"""Analytics API Endpoints for Dashboard.

Provides comprehensive analytics endpoints for the dashboard including:
- Real-time metrics
- Performance analytics
- Data quality insights
- System monitoring
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends, WebSocket
from pydantic import BaseModel

from ..security import require_token
from ..analytics.dashboard import dashboard_analytics
from ..analytics.insights import insights_generator
from ..analytics.metrics import metrics_collector
from ..analytics.core import analytics_engine


router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsOverview(BaseModel):
    """Analytics overview response model."""
    
    timestamp: str
    status: str
    key_metrics: Dict[str, Any]
    system_health: Dict[str, Any]
    trends: Dict[str, Any]
    alerts_count: int


class PerformanceChartData(BaseModel):
    """Performance chart data response model."""
    
    timestamp: str
    value: float
    label: str


class AlertsResponse(BaseModel):
    """Alerts dashboard response model."""
    
    timestamp: str
    total_alerts: int
    alerts_by_severity: Dict[str, int]
    recent_alerts: List[Dict[str, Any]]
    alerts_by_category: Dict[str, int]


class JobAnalyticsResponse(BaseModel):
    """Job analytics response model."""
    
    timestamp: str
    summary: Dict[str, Any]
    status_distribution: Dict[str, int]
    recent_jobs: List[Dict[str, Any]]
    performance: Dict[str, Any]


class DataQualityResponse(BaseModel):
    """Data quality dashboard response model."""
    
    timestamp: str
    current_score: float
    metrics: Dict[str, Any]
    trend: str
    issues: List[str]


class InsightsResponse(BaseModel):
    """Analytics insights response model."""
    
    timestamp: str
    health_score: float
    summary: Dict[str, Any]
    insights: Dict[str, List[Dict[str, Any]]]
    recommendations: List[Dict[str, Any]]
    metrics_summary: Dict[str, Any]


@router.get("/overview", response_model=AnalyticsOverview, dependencies=[Depends(require_token)])
async def get_analytics_overview() -> AnalyticsOverview:
    """Get high-level analytics overview for dashboard."""
    try:
        overview = await dashboard_analytics.get_dashboard_overview()
        return AnalyticsOverview(**overview)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics overview: {str(e)}")


@router.get("/performance/charts", dependencies=[Depends(require_token)])
async def get_performance_charts(
    hours: int = Query(default=6, ge=1, le=168, description="Hours of historical data (1-168)")
) -> Dict[str, Any]:
    """Get performance chart data for specified time period."""
    try:
        charts = await dashboard_analytics.get_performance_charts(hours)
        return charts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance charts: {str(e)}")


@router.get("/alerts", response_model=AlertsResponse, dependencies=[Depends(require_token)])
async def get_alerts_dashboard() -> AlertsResponse:
    """Get alerts and notifications for dashboard."""
    try:
        alerts = await dashboard_analytics.get_alerts_dashboard()
        return AlertsResponse(**alerts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.get("/jobs", response_model=JobAnalyticsResponse, dependencies=[Depends(require_token)])
async def get_job_analytics() -> JobAnalyticsResponse:
    """Get job performance analytics."""
    try:
        jobs = await dashboard_analytics.get_job_analytics()
        return JobAnalyticsResponse(**jobs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job analytics: {str(e)}")


@router.get("/data-quality", response_model=DataQualityResponse, dependencies=[Depends(require_token)])
async def get_data_quality_dashboard() -> DataQualityResponse:
    """Get data quality metrics and trends."""
    try:
        quality = await dashboard_analytics.get_data_quality_dashboard()
        return DataQualityResponse(**quality)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data quality metrics: {str(e)}")


@router.get("/insights", response_model=InsightsResponse, dependencies=[Depends(require_token)])
async def get_analytics_insights() -> InsightsResponse:
    """Get comprehensive analytics insights and recommendations."""
    try:
        insights = await insights_generator.generate_comprehensive_report()
        return InsightsResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")


@router.get("/realtime", dependencies=[Depends(require_token)])
async def get_realtime_metrics() -> Dict[str, Any]:
    """Get real-time system metrics."""
    try:
        metrics = metrics_collector.get_realtime_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")


@router.get("/dashboard", dependencies=[Depends(require_token)])
async def get_complete_dashboard_data() -> Dict[str, Any]:
    """Get all dashboard data in a single request for efficiency."""
    try:
        dashboard_data = await dashboard_analytics.get_realtime_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.get("/historical/{metric_name}", dependencies=[Depends(require_token)])
async def get_historical_metric(
    metric_name: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours of historical data")
) -> Dict[str, Any]:
    """Get historical data for a specific metric."""
    try:
        historical_data = await analytics_engine.get_historical_data(metric_name, hours)
        return {
            "metric_name": metric_name,
            "hours": hours,
            "data": historical_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical data: {str(e)}")


@router.post("/record", dependencies=[Depends(require_token)])
async def record_custom_metric(
    name: str = Query(..., description="Metric name"),
    value: float = Query(..., description="Metric value"),
    tags: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Record a custom metric (for integrations and custom tracking)."""
    try:
        await analytics_engine.record_metric(name, value, tags, metadata)
        return {
            "status": "success",
            "message": f"Recorded metric: {name} = {value}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record metric: {str(e)}")


@router.get("/endpoints/stats", dependencies=[Depends(require_token)])
async def get_endpoint_statistics() -> Dict[str, Any]:
    """Get detailed statistics by API endpoint."""
    try:
        stats = metrics_collector.get_endpoint_stats()
        return {
            "timestamp": analytics_engine._start_time,
            "endpoints": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get endpoint stats: {str(e)}")


@router.delete("/data/cleanup", dependencies=[Depends(require_token)])
async def cleanup_analytics_data(
    days: int = Query(default=30, ge=1, le=365, description="Delete data older than this many days")
) -> Dict[str, str]:
    """Clean up old analytics data."""
    try:
        await analytics_engine.cleanup_old_data(days)
        return {
            "status": "success",
            "message": f"Cleaned up analytics data older than {days} days"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup data: {str(e)}")


@router.post("/flush", dependencies=[Depends(require_token)])
async def flush_metrics_buffer() -> Dict[str, str]:
    """Manually flush metrics buffer to persistent storage."""
    try:
        await analytics_engine.flush_metrics()
        return {
            "status": "success",
            "message": "Metrics buffer flushed to storage"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to flush metrics: {str(e)}")


@router.get("/health", dependencies=[Depends(require_token)])
async def get_analytics_health() -> Dict[str, Any]:
    """Get analytics system health status."""
    try:
        # Get basic health indicators
        realtime_metrics = metrics_collector.get_realtime_metrics()
        performance = analytics_engine.get_performance_metrics()
        
        # Calculate health score
        health_score = 100.0
        
        if performance.error_rate > 0.1:
            health_score -= 30
        if performance.avg_response_time > 5.0:
            health_score -= 20
        if realtime_metrics.get("system", {}).get("memory_percent", 0) > 90:
            health_score -= 25
        if realtime_metrics.get("system", {}).get("cpu_percent", 0) > 90:
            health_score -= 25
        
        status = "healthy"
        if health_score < 50:
            status = "critical"
        elif health_score < 70:
            status = "degraded"
        elif health_score < 85:
            status = "warning"
        
        return {
            "status": status,
            "health_score": max(0, health_score),
            "timestamp": analytics_engine._start_time,
            "metrics_buffer_size": len(analytics_engine.metrics_buffer),
            "database_connected": analytics_engine.db_engine is not None,
            "collection_active": metrics_collector._collection_task is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics health: {str(e)}")


# WebSocket endpoint for real-time analytics updates
@router.websocket("/ws")
async def analytics_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time analytics updates."""
    await websocket.accept()
    try:
        while True:
            # Send real-time metrics every 5 seconds
            metrics = metrics_collector.get_realtime_metrics()
            await websocket.send_json({
                "type": "metrics_update",
                "data": metrics
            })
            
            # Wait before next update
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
