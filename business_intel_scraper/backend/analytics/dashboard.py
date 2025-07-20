"""Dashboard Analytics Integration Module.

Provides specialized analytics for dashboard visualization including:
- Real-time dashboard metrics
- Chart data preparation
- Performance widgets
- Alert management for dashboard
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .core import analytics_engine
from .metrics import metrics_collector
from .insights import insights_generator

# Performance optimization imports
try:
    from ..performance import analytics_performance
    from ..performance.optimizer import PerformanceMonitor
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    analytics_performance = None  # type: ignore[misc,assignment]
    PerformanceMonitor = None  # type: ignore[misc,assignment]
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False


class DashboardAnalytics:
    """Analytics integration for dashboard visualization with performance optimization."""
    
    def __init__(self) -> None:
        self.cache_duration = 30  # Cache for 30 seconds
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        # Use performance optimization cache if available
        self.use_performance_cache = PERFORMANCE_OPTIMIZATION_AVAILABLE and analytics_performance
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if key not in self._cache_timestamps:
            return False
        
        return (datetime.now() - self._cache_timestamps[key]).total_seconds() < self.cache_duration
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if valid."""
        if self._is_cache_valid(key):
            return self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any) -> None:
        """Set cache value with timestamp."""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()
    
    async def _get_from_optimized_cache(self, key: str) -> Optional[Any]:
        """Get from performance-optimized cache."""
        if self.use_performance_cache and analytics_performance and hasattr(analytics_performance, 'optimizer'):
            return await analytics_performance.optimizer.cache.get(f"dashboard:{key}")
        return None
    
    async def _set_optimized_cache(self, key: str, value: Any, ttl: int = 30) -> None:
        """Set in performance-optimized cache."""
        if self.use_performance_cache and analytics_performance and hasattr(analytics_performance, 'optimizer'):
            await analytics_performance.optimizer.cache.set(f"dashboard:{key}", value, ttl)
    
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get high-level dashboard overview metrics with performance optimization."""
        cache_key = "overview"
        cached = self._get_cached(cache_key)
        if cached:
            return cached  # type: ignore[no-any-return]
        
        # Get real-time metrics - use summary instead of non-existent method
        metrics_summary = metrics_collector.get_metrics_summary()
        realtime_metrics = {
            "active_jobs": metrics_summary.get("jobs", {}).get("active", 0),
            "requests_total": metrics_summary.get("requests", {}).get("total", 0),
            "error_count": metrics_summary.get("requests", {}).get("error", 0)
        }
        
        # Get analytics summary
        analytics_summary = await analytics_engine.get_analytics_summary()
        
        # Get performance metrics
        performance = analytics_engine.get_performance_metrics()
        
        # Calculate derived metrics
        overview = {
            "timestamp": datetime.now().isoformat(),
            "status": self._determine_system_status(performance, analytics_summary),
            "key_metrics": {
                "requests_per_minute": performance.throughput * 60 if performance.throughput > 0 else 0,
                "avg_response_time": performance.avg_response_time,
                "success_rate": performance.success_rate,
                "error_rate": performance.error_rate,
                "active_jobs": realtime_metrics.get("active_jobs", 0),
                "data_quality_score": analytics_summary.get("data_quality", {}).get("quality_score", 0.0)
            },
            "system_health": {
                "cpu_percent": realtime_metrics.get("system", {}).get("cpu_percent", 0),
                "memory_percent": realtime_metrics.get("system", {}).get("memory_percent", 0),
                "disk_percent": realtime_metrics.get("system", {}).get("disk_percent", 0)
            },
            "trends": analytics_summary.get("trends", {}),
            "alerts_count": len(analytics_summary.get("alerts", []))
        }
        
        self._set_cache(cache_key, overview)
        return overview
    
    async def get_performance_charts(self, hours: int = 6) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance chart data for dashboard."""
        cache_key = f"performance_charts_{hours}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Get historical trends - use analytics engine instead
        try:
            response_times = await analytics_engine.get_historical_data("api.request", hours)
            cpu_data = await analytics_engine.get_historical_data("system.cpu_percent", hours) 
            memory_data = await analytics_engine.get_historical_data("system.memory_percent", hours)
            
            trends = {
                "api.request": response_times or [],
                "system.cpu_percent": cpu_data or [],
                "system.memory_percent": memory_data or []
            }
        except Exception as e:
            # Fallback to empty data if historical data unavailable
            trends = {
                "api.request": [],
                "system.cpu_percent": [],
                "system.memory_percent": []
            }
        
        # Prepare chart data
        charts = {
            "response_times": self._prepare_time_series(
                trends.get("api.request", []),
                "Response Time (seconds)"
            ),
            "system_cpu": self._prepare_time_series(
                trends.get("system.cpu_percent", []),
                "CPU Usage (%)"
            ),
            "system_memory": self._prepare_time_series(
                trends.get("system.memory_percent", []),
                "Memory Usage (%)"
            ),
            "data_quality": self._prepare_time_series(
                trends.get("data.quality_score", []),
                "Data Quality Score"
            )
        }
        
        self._set_cache(cache_key, charts)
        return charts
    
    def _prepare_time_series(self, data: List[Dict[str, Any]], 
                           label: str) -> List[Dict[str, Any]]:
        """Prepare time series data for charts."""
        if not data:
            return []
        
        # Group by time buckets (e.g., 5-minute intervals)
        buckets = defaultdict(list)
        
        for point in data:
            # Round timestamp to 5-minute bucket
            timestamp = datetime.fromisoformat(point["timestamp"].replace('Z', '+00:00'))
            bucket_time = timestamp.replace(
                minute=(timestamp.minute // 5) * 5,
                second=0,
                microsecond=0
            )
            buckets[bucket_time].append(point["value"])
        
        # Calculate averages for each bucket
        chart_data = []
        for bucket_time in sorted(buckets.keys()):
            values = buckets[bucket_time]
            avg_value = sum(values) / len(values)
            
            chart_data.append({
                "timestamp": bucket_time.isoformat(),
                "value": round(avg_value, 3),
                "label": label
            })
        
        return chart_data
    
    async def get_alerts_dashboard(self) -> Dict[str, Any]:
        """Get alerts and notifications for dashboard."""
        cache_key = "alerts_dashboard"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Get current analytics summary
        analytics_summary = await analytics_engine.get_analytics_summary()
        alerts = analytics_summary.get("alerts", [])
        
        # Get anomalies
        anomalies = await insights_generator.detect_anomalies(6)  # Last 6 hours
        
        # Combine and categorize alerts
        all_alerts = alerts + anomalies
        
        categorized_alerts = {
            "critical": [a for a in all_alerts if a.get("severity") == "high"],
            "warning": [a for a in all_alerts if a.get("severity") == "medium"],
            "info": [a for a in all_alerts if a.get("severity") == "low"],
        }
        
        # Add timestamps if missing
        for category in categorized_alerts.values():
            for alert in category:
                if "timestamp" not in alert:
                    alert["timestamp"] = datetime.now().isoformat()
        
        alert_dashboard = {
            "timestamp": datetime.now().isoformat(),
            "total_alerts": len(all_alerts),
            "alerts_by_severity": {
                "critical": len(categorized_alerts["critical"]),
                "warning": len(categorized_alerts["warning"]),
                "info": len(categorized_alerts["info"])
            },
            "recent_alerts": sorted(
                all_alerts,
                key=lambda x: x.get("timestamp", datetime.min.isoformat()),
                reverse=True
            )[:10],  # Last 10 alerts
            "alerts_by_category": self._categorize_alerts_by_type(all_alerts)
        }
        
        self._set_cache(cache_key, alert_dashboard)
        return alert_dashboard
    
    def _categorize_alerts_by_type(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize alerts by type for summary."""
        categories: Dict[str, int] = defaultdict(int)
        
        for alert in alerts:
            alert_type = alert.get("type", "unknown")
            categories[alert_type] += 1
        
        return dict(categories)
    
    async def get_job_analytics(self) -> Dict[str, Any]:
        """Get job performance analytics for dashboard."""
        cache_key = "job_analytics"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Get job statistics - use metrics summary since get_job_stats doesn't exist
        metrics_summary = metrics_collector.get_metrics_summary()
        job_stats = {
            "total": metrics_summary.get("jobs", {}).get("total", 0),
            "active": metrics_summary.get("jobs", {}).get("active", 0),
            "completed": metrics_summary.get("jobs", {}).get("completed", 0),
            "failed": metrics_summary.get("jobs", {}).get("failed", 0),
            "recent_jobs": [],  # No recent jobs data available
            "status_distribution": {
                "running": metrics_summary.get("jobs", {}).get("active", 0),
                "completed": metrics_summary.get("jobs", {}).get("completed", 0),
                "failed": metrics_summary.get("jobs", {}).get("failed", 0)
            }
        }
        
        # Calculate job performance metrics
        recent_jobs = job_stats.get("recent_jobs", [])
        
        # Analyze job durations and success rates
        job_analytics = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_jobs": job_stats.get("total", 0),
                "active_jobs": job_stats.get("active", 0),
                "completed_jobs": job_stats.get("completed", 0),
                "failed_jobs": job_stats.get("failed", 0),
                "success_rate": self._calculate_job_success_rate(job_stats)
            },
            "status_distribution": job_stats.get("status_distribution", {}),
            "recent_jobs": recent_jobs[:5],  # Last 5 jobs for dashboard
            "performance": self._analyze_job_performance(recent_jobs)
        }
        
        self._set_cache(cache_key, job_analytics)
        return job_analytics
    
    def _calculate_job_success_rate(self, job_stats: Dict[str, Any]) -> float:
        """Calculate overall job success rate."""
        completed = job_stats.get("completed", 0)
        failed = job_stats.get("failed", 0)
        total_finished = completed + failed
        
        if total_finished == 0:
            return 0.0
        
        return completed / total_finished
    
    def _analyze_job_performance(self, recent_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze job performance metrics."""
        if not recent_jobs:
            return {
                "avg_duration": 0,
                "success_rate": 0,
                "failure_rate": 0,
                "most_common_failure": None
            }
        
        # Analyze job durations (if available in metadata)
        durations = []
        successes = 0
        failures = 0
        failure_reasons: Dict[str, int] = defaultdict(int)
        
        for job in recent_jobs:
            status = job.get("status")
            metadata = job.get("metadata", {})
            
            if status == "completed":
                successes += 1
                if "duration" in metadata:
                    durations.append(metadata["duration"])
            elif status == "failed":
                failures += 1
                if "error" in metadata:
                    failure_reasons[metadata["error"]] += 1
        
        total_analyzed = successes + failures
        
        return {
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "success_rate": successes / total_analyzed if total_analyzed > 0 else 0,
            "failure_rate": failures / total_analyzed if total_analyzed > 0 else 0,
            "most_common_failure": max(failure_reasons.items(), key=lambda x: x[1])[0] if failure_reasons else None
        }
    
    async def get_data_quality_dashboard(self) -> Dict[str, Any]:
        """Get data quality metrics for dashboard."""
        cache_key = "data_quality_dashboard"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Get analytics summary
        analytics_summary = await analytics_engine.get_analytics_summary()
        quality_metrics = analytics_summary.get("data_quality", {})
        
        # Get historical quality trends
        quality_trends = await analytics_engine.get_historical_data("data.quality_score", 24)
        
        quality_dashboard = {
            "timestamp": datetime.now().isoformat(),
            "current_score": quality_metrics.get("quality_score", 0.0),
            "metrics": {
                "total_records": quality_metrics.get("total_records", 0),
                "valid_records": quality_metrics.get("valid_records", 0),
                "duplicate_records": quality_metrics.get("duplicate_records", 0),
                "incomplete_records": quality_metrics.get("incomplete_records", 0),
                "completeness_rate": quality_metrics.get("completeness_rate", 0.0),
                "accuracy_rate": quality_metrics.get("accuracy_rate", 0.0)
            },
            "trend": self._calculate_quality_trend(quality_trends),
            "issues": self._identify_quality_issues(quality_metrics)
        }
        
        self._set_cache(cache_key, quality_dashboard)
        return quality_dashboard
    
    def _calculate_quality_trend(self, quality_trends: List[Dict[str, Any]]) -> str:
        """Calculate quality trend direction."""
        if len(quality_trends) < 2:
            return "stable"
        
        recent_scores = [point["value"] for point in quality_trends[-5:]]
        earlier_scores = [point["value"] for point in quality_trends[-10:-5]] if len(quality_trends) >= 10 else []
        
        if not earlier_scores:
            return "stable"
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        if recent_avg > earlier_avg * 1.05:
            return "improving"
        elif recent_avg < earlier_avg * 0.95:
            return "declining"
        else:
            return "stable"
    
    def _identify_quality_issues(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Identify specific data quality issues."""
        issues = []
        
        completeness_rate = quality_metrics.get("completeness_rate", 1.0)
        accuracy_rate = quality_metrics.get("accuracy_rate", 1.0)
        duplicate_records = quality_metrics.get("duplicate_records", 0)
        total_records = quality_metrics.get("total_records", 0)
        
        if completeness_rate < 0.9:
            issues.append(f"Low completeness: {completeness_rate:.1%}")
        
        if accuracy_rate < 0.95:
            issues.append(f"Low accuracy: {accuracy_rate:.1%}")
        
        if total_records > 0 and duplicate_records / total_records > 0.1:
            issues.append(f"High duplicates: {duplicate_records} records")
        
        return issues
    
    def _determine_system_status(self, performance: Any, analytics_summary: Dict[str, Any]) -> str:
        """Determine overall system status."""
        alerts = analytics_summary.get("alerts", [])
        critical_alerts = [a for a in alerts if a.get("severity") == "high"]
        
        if critical_alerts:
            return "critical"
        elif performance.error_rate > 0.1:
            return "degraded"
        elif performance.error_rate > 0.05 or performance.avg_response_time > 3.0:
            return "warning"
        else:
            return "healthy"
    
    async def get_realtime_dashboard_data(self) -> Dict[str, Any]:
        """Get all real-time dashboard data in one call."""
        # Run all dashboard queries concurrently
        overview_task = self.get_dashboard_overview()
        alerts_task = self.get_alerts_dashboard()
        jobs_task = self.get_job_analytics()
        quality_task = self.get_data_quality_dashboard()
        
        overview, alerts, jobs, quality = await asyncio.gather(
            overview_task, alerts_task, jobs_task, quality_task
        )
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overview": overview,
            "alerts": alerts,
            "jobs": jobs,
            "data_quality": quality
        }


# Global dashboard analytics instance
dashboard_analytics = DashboardAnalytics()
