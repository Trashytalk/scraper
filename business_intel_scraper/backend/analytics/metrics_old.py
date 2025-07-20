"""Advanced Metrics Collection for Analytics Dashboard.

Provides specialized metrics collectors for different aspects of the system:
- API performance metrics
- Scraping operation metrics  
- Data quality metrics
- System resource metrics
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from .core import analytics_engine


class MetricsCollector:
    """Advanced metrics collector with real-time capabilities."""
    
    def __init__(self):
        if PROMETHEUS_AVAILABLE:
            # Create dedicated registry to avoid conflicts
            self.registry = CollectorRegistry()
            
            # Prometheus metrics with unique names
            self.request_counter = Counter(
                'bi_analytics_requests_total', 
                'Total HTTP requests',
                ['method', 'endpoint', 'status'],
                registry=self.registry
            )
            
            self.request_duration = Histogram(
                'bi_analytics_request_duration_seconds',
                'Request duration in seconds',
                ['endpoint'],
                registry=self.registry
            )
            
            self.active_jobs = Gauge(
                'bi_analytics_active_jobs',
                'Number of active scraping jobs',
                registry=self.registry
            )
            
            self.data_quality_score = Gauge(
                'bi_analytics_data_quality_score',
                'Current data quality score',
                registry=self.registry
            )
            
            self.system_memory = Gauge(
                'bi_analytics_system_memory_percent',
                'System memory usage percentage',
                registry=self.registry
            )
            
            self.system_cpu = Gauge(
                'bi_analytics_system_cpu_percent', 
                'System CPU usage percentage',
                registry=self.registry
            )
        else:
            # Fallback when Prometheus not available
            self.registry = None
            self.request_counter = None
            self.request_duration = None
            self.active_jobs = None
            self.data_quality_score = None
            self.system_memory = None
            self.system_cpu = None        # Internal metrics storage
        self.response_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
        self.job_statistics = defaultdict(dict)
        
        # Start background collection
        self._collection_task = None
        self.start_collection()
    
    def start_collection(self):
        """Start background metrics collection."""
        if self._collection_task is None:
            self._collection_task = asyncio.create_task(self._collect_system_metrics())
    
    def stop_collection(self):
        """Stop background metrics collection."""
        if self._collection_task:
            self._collection_task.cancel()
            self._collection_task = None
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics."""
        while True:
            try:
                # Collect system resource metrics
                if psutil:
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent
                    
                    self.system_cpu.set(cpu_percent)
                    self.system_memory.set(memory_percent)
                    
                    # Record to analytics engine
                    await analytics_engine.record_metric("system.cpu_percent", cpu_percent)
                    await analytics_engine.record_metric("system.memory_percent", memory_percent)
                else:
                    # Default values when psutil is not available
                    self.system_cpu.set(0)
                    self.system_memory.set(0)
                
                # Sleep for collection interval
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(10)
    
    async def record_request(self, method: str, endpoint: str, 
                           status_code: int, duration: float):
        """Record HTTP request metrics."""
        # Update Prometheus metrics
        self.request_counter.labels(
            method=method,
            endpoint=endpoint, 
            status=str(status_code)
        ).inc()
        
        self.request_duration.labels(endpoint=endpoint).observe(duration)
        
        # Update internal metrics
        self.response_times.append(duration)
        
        if 200 <= status_code < 400:
            self.success_counts[endpoint] += 1
            analytics_engine.record_success()
        else:
            self.error_counts[endpoint] += 1
            analytics_engine.record_error()
        
        analytics_engine.record_request_time(duration)
        
        # Record detailed metrics
        await analytics_engine.record_metric(
            "api.request",
            duration,
            tags={
                "method": method,
                "endpoint": endpoint,
                "status": str(status_code)
            }
        )
    
    async def record_scraping_job(self, job_id: str, status: str, 
                                metadata: Optional[Dict[str, Any]] = None):
        """Record scraping job metrics."""
        self.job_statistics[job_id].update({
            "status": status,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        })
        
        # Count active jobs
        active_count = sum(
            1 for job in self.job_statistics.values()
            if job.get("status") == "running"
        )
        self.active_jobs.set(active_count)
        
        # Record to analytics
        await analytics_engine.record_metric(
            "scraping.job_status",
            1,
            tags={"job_id": job_id, "status": status},
            metadata=metadata
        )
    
    async def record_data_quality(self, score: float, metadata: Optional[Dict[str, Any]] = None):
        """Record data quality metrics."""
        self.data_quality_score.set(score)
        
        await analytics_engine.record_metric(
            "data.quality_score",
            score,
            metadata=metadata or {}
        )
    
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics."""
        # Calculate response time statistics
        response_stats = {}
        if self.response_times:
            response_stats = {
                "avg": sum(self.response_times) / len(self.response_times),
                "min": min(self.response_times),
                "max": max(self.response_times),
                "count": len(self.response_times)
            }
        
        # Calculate error rates by endpoint
        error_rates = {}
        for endpoint in set(list(self.error_counts.keys()) + list(self.success_counts.keys())):
            total = self.error_counts[endpoint] + self.success_counts[endpoint]
            if total > 0:
                error_rates[endpoint] = self.error_counts[endpoint] / total
        
        # Get system metrics
        if psutil:
            try:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
            except Exception:
                cpu_percent = 0
                memory = type('obj', (object,), {'percent': 0, 'available': 0, 'total': 0})()
                disk = type('obj', (object,), {'percent': 0, 'free': 0, 'total': 0})()
        else:
            cpu_percent = 0
            memory = type('obj', (object,), {'percent': 0, 'available': 0, 'total': 0})()
            disk = type('obj', (object,), {'percent': 0, 'free': 0, 'total': 0})()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "response_times": response_stats,
            "error_rates": error_rates,
            "active_jobs": len([
                job for job in self.job_statistics.values()
                if job.get("status") == "running"
            ]),
            "total_jobs": len(self.job_statistics),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_percent": disk.percent,
                "disk_free": disk.free,
                "disk_total": disk.total,
            }
        }
    
    def get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed statistics by endpoint."""
        stats = {}
        
        for endpoint in set(list(self.error_counts.keys()) + list(self.success_counts.keys())):
            total_requests = self.error_counts[endpoint] + self.success_counts[endpoint]
            error_rate = self.error_counts[endpoint] / total_requests if total_requests > 0 else 0
            success_rate = self.success_counts[endpoint] / total_requests if total_requests > 0 else 0
            
            stats[endpoint] = {
                "total_requests": total_requests,
                "success_count": self.success_counts[endpoint],
                "error_count": self.error_counts[endpoint],
                "success_rate": success_rate,
                "error_rate": error_rate
            }
        
        return stats
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get detailed job statistics."""
        if not self.job_statistics:
            return {
                "total": 0,
                "active": 0,
                "completed": 0,
                "failed": 0,
                "recent_jobs": []
            }
        
        # Count jobs by status
        status_counts = defaultdict(int)
        recent_jobs = []
        
        for job_id, job_data in self.job_statistics.items():
            status = job_data.get("status", "unknown")
            status_counts[status] += 1
            
            recent_jobs.append({
                "job_id": job_id,
                "status": status,
                "timestamp": job_data.get("timestamp", datetime.now()).isoformat(),
                "metadata": job_data.get("metadata", {})
            })
        
        # Sort by timestamp, most recent first
        recent_jobs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "total": len(self.job_statistics),
            "active": status_counts.get("running", 0),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "pending": status_counts.get("pending", 0),
            "status_distribution": dict(status_counts),
            "recent_jobs": recent_jobs[:20]  # Last 20 jobs
        }
    
    async def get_historical_trends(self, hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical trend data."""
        trends = {}
        
        # Get historical data from analytics engine
        metrics_to_fetch = [
            "api.request",
            "data.quality_score", 
            "system.cpu_percent",
            "system.memory_percent",
            "scraping.job_status"
        ]
        
        for metric_name in metrics_to_fetch:
            historical_data = await analytics_engine.get_historical_data(metric_name, hours)
            trends[metric_name] = historical_data
        
        return trends
    
    def reset_metrics(self):
        """Reset all collected metrics (useful for testing)."""
        self.response_times.clear()
        self.error_counts.clear()
        self.success_counts.clear()
        self.job_statistics.clear()


# Global metrics collector instance
metrics_collector = MetricsCollector()
