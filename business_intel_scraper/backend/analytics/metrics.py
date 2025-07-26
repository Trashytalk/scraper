"""
Advanced metrics collection and monitoring system.
"""

import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, Optional, Any

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

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Advanced metrics collector with real-time capabilities."""

    def __init__(self):
        if PROMETHEUS_AVAILABLE:
            # Create dedicated registry to avoid conflicts
            self.registry = CollectorRegistry()

            # Prometheus metrics with unique names
            self.request_counter = Counter(
                "bi_analytics_requests_total",
                "Total HTTP requests",
                ["method", "endpoint", "status"],
                registry=self.registry,
            )

            self.request_duration = Histogram(
                "bi_analytics_request_duration_seconds",
                "Request duration in seconds",
                ["endpoint"],
                registry=self.registry,
            )

            self.active_jobs = Gauge(
                "bi_analytics_active_jobs",
                "Number of active scraping jobs",
                registry=self.registry,
            )

            self.data_quality_score = Gauge(
                "bi_analytics_data_quality_score",
                "Current data quality score",
                registry=self.registry,
            )

            self.system_memory = Gauge(
                "bi_analytics_system_memory_percent",
                "System memory usage percentage",
                registry=self.registry,
            )

            self.system_cpu = Gauge(
                "bi_analytics_system_cpu_percent",
                "System CPU usage percentage",
                registry=self.registry,
            )
        else:
            # Fallback when Prometheus not available
            self.registry = None
            self.request_counter = None
            self.request_duration = None
            self.active_jobs = None
            self.data_quality_score = None
            self.system_memory = None
            self.system_cpu = None

        # Internal metrics storage
        self.response_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.success_counts = defaultdict(int)
        self.job_statistics = defaultdict(dict)

        # Background collection control
        self._collection_task = None
        self._running = False

    def start_collection(self):
        """Start background metrics collection."""
        if not self._running:
            self._running = True
            try:
                loop = asyncio.get_event_loop()
                self._collection_task = loop.create_task(self._collect_system_metrics())
            except RuntimeError:
                # No event loop running
                logger.warning(
                    "No event loop available for background metrics collection"
                )

    def stop_collection(self):
        """Stop background metrics collection."""
        self._running = False
        if self._collection_task:
            self._collection_task.cancel()
            self._collection_task = None

    async def _collect_system_metrics(self):
        """Background task to collect system metrics."""
        while self._running:
            try:
                # Collect system resource metrics
                if psutil:
                    cpu_percent = psutil.cpu_percent()
                    memory_percent = psutil.virtual_memory().percent

                    if self.system_cpu:
                        self.system_cpu.set(cpu_percent)
                    if self.system_memory:
                        self.system_memory.set(memory_percent)

                    # Record to analytics engine if available
                    try:
                        await analytics_engine.record_metric(
                            "system.cpu_percent", cpu_percent
                        )
                        await analytics_engine.record_metric(
                            "system.memory_percent", memory_percent
                        )
                    except Exception:
                        pass  # Ignore analytics engine errors

                # Sleep for collection interval
                await asyncio.sleep(10)  # Collect every 10 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(10)

    async def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        # Update Prometheus metrics
        if self.request_counter:
            self.request_counter.labels(
                method=method, endpoint=endpoint, status=str(status_code)
            ).inc()

        if self.request_duration:
            self.request_duration.labels(endpoint=endpoint).observe(duration)

        # Update internal metrics
        self.response_times.append(duration)

        if 200 <= status_code < 400:
            self.success_counts[endpoint] += 1
        else:
            self.error_counts[endpoint] += 1

        # Record to analytics engine
        try:
            await analytics_engine.record_metric(
                f"request.{endpoint}.duration", duration
            )
            await analytics_engine.record_metric(f"request.{endpoint}.count", 1)
        except Exception:
            pass  # Ignore analytics engine errors

    async def record_job_metrics(
        self,
        job_type: str,
        job_id: str,
        status: str,
        duration: Optional[float] = None,
        items_processed: Optional[int] = None,
    ):
        """Record job execution metrics."""
        # Update job statistics
        if job_id not in self.job_statistics:
            self.job_statistics[job_id] = {
                "type": job_type,
                "start_time": datetime.now(),
                "status": "running",
                "items_processed": 0,
            }

        job_stats = self.job_statistics[job_id]
        job_stats["status"] = status

        if items_processed is not None:
            job_stats["items_processed"] = items_processed

        if duration is not None:
            job_stats["duration"] = duration

        # Count active jobs
        active_count = sum(
            1 for stats in self.job_statistics.values() if stats["status"] == "running"
        )

        if self.active_jobs:
            self.active_jobs.set(active_count)

        # Record to analytics engine
        try:
            await analytics_engine.record_metric(f"job.{job_type}.count", 1)
            if duration:
                await analytics_engine.record_metric(
                    f"job.{job_type}.duration", duration
                )
            if items_processed:
                await analytics_engine.record_metric(
                    f"job.{job_type}.items", items_processed
                )
        except Exception:
            pass  # Ignore analytics engine errors

    async def record_data_quality(self, source: str, score: float):
        """Record data quality metrics."""
        if self.data_quality_score:
            self.data_quality_score.set(score)

        # Record to analytics engine
        try:
            await analytics_engine.record_metric(f"quality.{source}.score", score)
        except Exception:
            pass  # Ignore analytics engine errors

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        summary = {
            "requests": {
                "total": sum(self.success_counts.values())
                + sum(self.error_counts.values()),
                "success": sum(self.success_counts.values()),
                "error": sum(self.error_counts.values()),
                "avg_response_time": (
                    sum(self.response_times) / len(self.response_times)
                    if self.response_times
                    else 0
                ),
            },
            "jobs": {
                "total": len(self.job_statistics),
                "active": sum(
                    1
                    for stats in self.job_statistics.values()
                    if stats["status"] == "running"
                ),
                "completed": sum(
                    1
                    for stats in self.job_statistics.values()
                    if stats["status"] == "completed"
                ),
                "failed": sum(
                    1
                    for stats in self.job_statistics.values()
                    if stats["status"] == "failed"
                ),
            },
            "system": {},
        }

        # Add system metrics if available
        if psutil:
            try:
                cpu = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage("/")

                summary["system"] = {
                    "cpu_percent": cpu,
                    "memory_percent": memory.percent,
                    "memory_available": memory.available,
                    "memory_total": memory.total,
                    "disk_percent": disk.percent,
                    "disk_free": disk.free,
                    "disk_total": disk.total,
                }
            except Exception as e:
                logger.error(f"Failed to collect system metrics: {e}")
                summary["system"] = {"error": str(e)}

        return summary

    def get_prometheus_metrics(self) -> Optional[str]:
        """Export Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE or not self.registry:
            return None

        try:
            from prometheus_client import generate_latest

            return generate_latest(self.registry).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return None

    def reset_metrics(self):
        """Reset all collected metrics."""
        self.response_times.clear()
        self.error_counts.clear()
        self.success_counts.clear()
        self.job_statistics.clear()

        logger.info("Metrics reset successfully")


# Global metrics collector instance
metrics_collector = MetricsCollector()
