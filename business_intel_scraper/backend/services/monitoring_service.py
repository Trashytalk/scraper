"""
Advanced Monitoring and Observability Service
Provides comprehensive system monitoring, alerting, and performance tracking
"""

import asyncio
import psutil
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from collections import defaultdict, deque
import statistics

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_

from ..db.centralized_data import SystemMetrics, AlertRecord, PerformanceBaseline
from ..dependencies import get_db
from .notification_handlers import notification_manager, send_alert_notifications


logger = logging.getLogger(__name__)


@dataclass
class MetricThreshold:
    """Threshold configuration for metrics"""
    warning_value: float
    critical_value: float
    comparison: str = "greater"  # greater, less, equal
    window_minutes: int = 5      # Evaluation window


@dataclass
class AlertConfiguration:
    """Alert configuration for monitoring"""
    metric_name: str
    thresholds: MetricThreshold
    enabled: bool = True
    notification_channels: List[str] = None
    suppression_minutes: int = 60  # Suppress duplicate alerts


class MonitoringService:
    """
    Comprehensive monitoring and observability service
    Handles metrics collection, alerting, baseline management, and performance tracking
    """

    def __init__(self):
        self.metrics_buffer = deque(maxlen=1000)  # Buffer for real-time metrics
        self.alert_configurations = self._load_default_alert_configs()
        self.baseline_cache = {}  # Cache for performance baselines
        self.notification_handlers = {}  # Pluggable notification system
        self.anomaly_detectors = {}  # ML-based anomaly detection
        
        # Performance tracking
        self.request_metrics = deque(maxlen=10000)  # Track API requests
        self.job_metrics = deque(maxlen=1000)       # Track job performance
        
        # Real-time monitoring state
        self.monitoring_active = False
        self.collection_interval = 30  # seconds
        
    def _load_default_alert_configs(self) -> Dict[str, AlertConfiguration]:
        """Load default alert configurations"""
        return {
            "cpu_usage": AlertConfiguration(
                metric_name="cpu_percent",
                thresholds=MetricThreshold(warning_value=75.0, critical_value=90.0),
                notification_channels=["email", "slack"]
            ),
            "memory_usage": AlertConfiguration(
                metric_name="memory_percent", 
                thresholds=MetricThreshold(warning_value=80.0, critical_value=95.0),
                notification_channels=["email", "slack"]
            ),
            "disk_usage": AlertConfiguration(
                metric_name="disk_usage_percent",
                thresholds=MetricThreshold(warning_value=85.0, critical_value=95.0),
                notification_channels=["email"]
            ),
            "response_time": AlertConfiguration(
                metric_name="avg_response_time_ms",
                thresholds=MetricThreshold(warning_value=1000.0, critical_value=3000.0),
                notification_channels=["slack"]
            ),
            "error_rate": AlertConfiguration(
                metric_name="error_rate_percent",
                thresholds=MetricThreshold(warning_value=5.0, critical_value=15.0),
                notification_channels=["email", "slack"]
            ),
            "failed_jobs": AlertConfiguration(
                metric_name="failed_jobs_last_hour",
                thresholds=MetricThreshold(warning_value=5.0, critical_value=15.0),
                notification_channels=["email", "slack"]
            )
        }

    async def start_monitoring(self):
        """Start continuous monitoring service"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        logger.info("Starting continuous monitoring service")
        
        # Start monitoring tasks
        await asyncio.gather(
            self._metrics_collection_loop(),
            self._alert_evaluation_loop(),
            self._baseline_update_loop(),
            self._anomaly_detection_loop(),
            return_exceptions=True
        )

    async def stop_monitoring(self):
        """Stop monitoring service"""
        self.monitoring_active = False
        logger.info("Stopping monitoring service")

    async def _metrics_collection_loop(self):
        """Continuous metrics collection"""
        while self.monitoring_active:
            try:
                await self.collect_system_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(10)  # Short delay on error

    async def _alert_evaluation_loop(self):
        """Continuous alert evaluation"""
        while self.monitoring_active:
            try:
                await self.evaluate_alerts()
                await asyncio.sleep(60)  # Check alerts every minute
            except Exception as e:
                logger.error(f"Error in alert evaluation: {e}")
                await asyncio.sleep(30)

    async def _baseline_update_loop(self):
        """Periodic baseline recalculation"""
        while self.monitoring_active:
            try:
                await self.update_performance_baselines()
                await asyncio.sleep(3600)  # Update baselines every hour
            except Exception as e:
                logger.error(f"Error updating baselines: {e}")
                await asyncio.sleep(600)

    async def _anomaly_detection_loop(self):
        """Continuous anomaly detection"""
        while self.monitoring_active:
            try:
                await self.detect_anomalies()
                await asyncio.sleep(300)  # Check for anomalies every 5 minutes
            except Exception as e:
                logger.error(f"Error in anomaly detection: {e}")
                await asyncio.sleep(120)

    async def collect_system_metrics(self, source: str = "monitoring_service") -> SystemMetrics:
        """
        Collect comprehensive system metrics
        """
        try:
            # System resource metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network_io = psutil.net_io_counters()
            disk_io = psutil.disk_io_counters()
            
            # Process-specific metrics
            process = psutil.Process()
            
            # Database connection info (if available)
            db_connections_active = 0
            db_connections_idle = 0
            try:
                # This would integrate with your database pool
                # db_pool = get_db_pool()
                # db_connections_active = db_pool.active_connections
                # db_connections_idle = db_pool.idle_connections
                pass
            except:
                pass
            
            # Calculate derived metrics
            requests_per_minute = self._calculate_requests_per_minute()
            avg_response_time, p95_response_time, p99_response_time = self._calculate_response_times()
            error_rate = self._calculate_error_rate()
            
            # Job metrics
            active_jobs, completed_jobs, failed_jobs = self._calculate_job_metrics()
            
            # Health assessment
            health_status = self._assess_system_health(cpu_percent, memory.percent, error_rate)
            
            # Create metrics record
            metrics = SystemMetrics(
                collected_at=datetime.utcnow(),
                collection_source=source,
                collection_context=f"interval_{self.collection_interval}s",
                
                # System resources
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=(disk.used / disk.total) * 100,
                disk_free_gb=disk.free / (1024 * 1024 * 1024),
                
                # Network and I/O
                network_connections_count=len(psutil.net_connections()),
                network_io_bytes_sent=network_io.bytes_sent if network_io else 0,
                network_io_bytes_recv=network_io.bytes_recv if network_io else 0,
                disk_io_read_bytes=disk_io.read_bytes if disk_io else 0,
                disk_io_write_bytes=disk_io.write_bytes if disk_io else 0,
                
                # Application metrics
                active_threads=process.num_threads(),
                open_file_descriptors=len(process.open_files()),
                database_connections_active=db_connections_active,
                database_connections_idle=db_connections_idle,
                cache_hit_rate=self._calculate_cache_hit_rate(),
                cache_memory_usage_mb=self._estimate_cache_memory(),
                
                # Performance metrics
                requests_per_minute=requests_per_minute,
                avg_response_time_ms=avg_response_time,
                p95_response_time_ms=p95_response_time,
                p99_response_time_ms=p99_response_time,
                error_rate_percent=error_rate,
                
                # Business metrics
                active_scraping_jobs=active_jobs,
                completed_jobs_last_hour=completed_jobs,
                failed_jobs_last_hour=failed_jobs,
                data_processing_rate_per_min=self._calculate_processing_rate(),
                
                # Health and alerts
                health_status=health_status,
                alert_count=await self._count_active_alerts(),
                anomaly_score=self._calculate_anomaly_score(),
                
                # Custom metrics
                custom_metrics={
                    "collection_timestamp": datetime.utcnow().isoformat(),
                    "monitoring_version": "2.0",
                    "deployment_environment": "production"  # This could be configurable
                }
            )
            
            # Store in buffer for real-time access
            self.metrics_buffer.append(metrics)
            
            # Persist to database
            await self._persist_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise

    async def _persist_metrics(self, metrics: SystemMetrics):
        """Persist metrics to database"""
        try:
            db = next(get_db())
            db.add(metrics)
            db.commit()
            db.refresh(metrics)
        except Exception as e:
            logger.error(f"Error persisting metrics: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()

    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute from recent metrics"""
        if not self.request_metrics:
            return 0.0
            
        # Count requests in the last minute
        cutoff = time.time() - 60
        recent_requests = [m for m in self.request_metrics if m.get('timestamp', 0) > cutoff]
        return len(recent_requests)

    def _calculate_response_times(self) -> tuple[float, float, float]:
        """Calculate response time percentiles"""
        if not self.request_metrics:
            return 0.0, 0.0, 0.0
            
        # Get response times from last 5 minutes
        cutoff = time.time() - 300
        recent_times = [
            m.get('response_time', 0) for m in self.request_metrics 
            if m.get('timestamp', 0) > cutoff and m.get('response_time', 0) > 0
        ]
        
        if not recent_times:
            return 0.0, 0.0, 0.0
            
        avg_time = statistics.mean(recent_times)
        p95_time = statistics.quantiles(recent_times, n=20)[18] if len(recent_times) > 20 else max(recent_times)
        p99_time = statistics.quantiles(recent_times, n=100)[98] if len(recent_times) > 100 else max(recent_times)
        
        return avg_time, p95_time, p99_time

    def _calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if not self.request_metrics:
            return 0.0
            
        # Count errors in the last 5 minutes
        cutoff = time.time() - 300
        recent_requests = [m for m in self.request_metrics if m.get('timestamp', 0) > cutoff]
        
        if not recent_requests:
            return 0.0
            
        error_count = len([m for m in recent_requests if m.get('status_code', 200) >= 400])
        return (error_count / len(recent_requests)) * 100

    def _calculate_job_metrics(self) -> tuple[int, int, int]:
        """Calculate job-related metrics"""
        if not self.job_metrics:
            return 0, 0, 0
            
        cutoff = time.time() - 3600  # Last hour
        recent_jobs = [j for j in self.job_metrics if j.get('timestamp', 0) > cutoff]
        
        active = len([j for j in recent_jobs if j.get('status') == 'running'])
        completed = len([j for j in recent_jobs if j.get('status') == 'completed'])
        failed = len([j for j in recent_jobs if j.get('status') == 'failed'])
        
        return active, completed, failed

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (placeholder implementation)"""
        # This would integrate with your caching system
        return 85.0  # Mock value

    def _estimate_cache_memory(self) -> float:
        """Estimate cache memory usage (placeholder implementation)"""
        # This would integrate with your caching system
        return 128.0  # Mock value in MB

    def _calculate_processing_rate(self) -> float:
        """Calculate data processing rate per minute"""
        # This would integrate with your data processing pipeline
        return 45.0  # Mock value

    def _assess_system_health(self, cpu: float, memory: float, error_rate: float) -> str:
        """Assess overall system health"""
        if cpu > 90 or memory > 95 or error_rate > 15:
            return "critical"
        elif cpu > 75 or memory > 80 or error_rate > 5:
            return "warning"
        else:
            return "healthy"

    async def _count_active_alerts(self) -> int:
        """Count currently active alerts"""
        try:
            db = next(get_db())
            count = db.query(func.count(AlertRecord.id)).filter(
                AlertRecord.status == "active"
            ).scalar() or 0
            return count
        except Exception as e:
            logger.error(f"Error counting active alerts: {e}")
            return 0
        finally:
            if db:
                db.close()

    def _calculate_anomaly_score(self) -> float:
        """Calculate anomaly score (placeholder for ML integration)"""
        # This would integrate with ML-based anomaly detection
        return 0.15  # Mock value (0.0 = normal, 1.0 = highly anomalous)

    async def evaluate_alerts(self):
        """Evaluate metrics against alert thresholds"""
        if not self.metrics_buffer:
            return
            
        latest_metrics = self.metrics_buffer[-1]
        
        for alert_name, config in self.alert_configurations.items():
            if not config.enabled:
                continue
                
            metric_value = getattr(latest_metrics, config.metric_name, 0)
            threshold = config.thresholds
            
            # Check if threshold is breached
            should_alert = False
            severity = "low"
            
            if threshold.comparison == "greater":
                if metric_value >= threshold.critical_value:
                    should_alert = True
                    severity = "critical"
                elif metric_value >= threshold.warning_value:
                    should_alert = True
                    severity = "medium"
            
            if should_alert:
                await self._create_alert(
                    alert_type="performance",
                    severity=severity,
                    category=alert_name,
                    title=f"{alert_name.replace('_', ' ').title()} Threshold Exceeded",
                    message=f"{config.metric_name} value {metric_value:.2f} exceeds {severity} threshold {threshold.warning_value if severity == 'medium' else threshold.critical_value}",
                    source_component="monitoring_service",
                    source_metric_name=config.metric_name,
                    source_metric_value=metric_value,
                    threshold_value=threshold.warning_value if severity == "medium" else threshold.critical_value,
                    notification_channels=config.notification_channels
                )

    async def _create_alert(self, **alert_data):
        """Create a new alert record"""
        try:
            # Check for duplicate/suppressed alerts
            if await self._is_alert_suppressed(alert_data.get('category'), alert_data.get('severity')):
                return
                
            alert = AlertRecord(
                alert_type=alert_data.get('alert_type', 'system'),
                severity=alert_data.get('severity', 'medium'), 
                category=alert_data.get('category', 'unknown'),
                title=alert_data.get('title', 'Alert'),
                message=alert_data.get('message', ''),
                technical_details=alert_data.get('technical_details', {}),
                source_component=alert_data.get('source_component', 'unknown'),
                source_metric_name=alert_data.get('source_metric_name'),
                source_metric_value=alert_data.get('source_metric_value'),
                threshold_value=alert_data.get('threshold_value'),
                triggered_at=datetime.utcnow(),
                status="active",
                notifications_sent=[],
                notification_channels=alert_data.get('notification_channels', []),
                correlation_key=f"{alert_data.get('category')}_{alert_data.get('severity')}",
                impact_level=alert_data.get('severity', 'medium'),
                affected_components=[alert_data.get('source_component', 'unknown')]
            )
            
            # Persist alert
            db = next(get_db())
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            logger.warning(f"Alert created: {alert.title} (Severity: {alert.severity})")
            
            # Send notifications
            await self._send_alert_notifications(alert)
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()

    async def _send_alert_notifications(self, alert: AlertRecord):
        """Send notifications for an alert"""
        try:
            # Determine notification channels
            channels = alert.notification_channels if alert.notification_channels else ["console"]
            
            # Add default channels for high severity alerts
            if alert.severity in ["critical", "high"]:
                if "email" not in channels:
                    channels.append("email")
                if "slack" not in channels:
                    channels.append("slack")
            
            # Send notifications
            results = await send_alert_notifications(
                alert, 
                channels=channels,
                custom_data={
                    "monitoring_service": "business_intel_scraper",
                    "alert_id": alert.alert_uuid,
                    "component": alert.source_component
                }
            )
            
            # Update alert with notification results
            db = next(get_db())
            try:
                sent_channels = [channel for channel, result in results.items() if result["success"]]
                alert.notifications_sent = sent_channels
                db.commit()
                
                logger.info(f"Notifications sent for alert {alert.alert_uuid}: {sent_channels}")
                
            except Exception as e:
                logger.error(f"Error updating alert notification status: {e}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error sending alert notifications: {e}")

    async def _is_alert_suppressed(self, category: str, severity: str) -> bool:
        """Check if alert should be suppressed due to recent similar alerts"""
        try:
            db = next(get_db())
            suppression_window = datetime.utcnow() - timedelta(minutes=60)
            
            existing_alert = db.query(AlertRecord).filter(
                and_(
                    AlertRecord.category == category,
                    AlertRecord.severity == severity,
                    AlertRecord.triggered_at >= suppression_window,
                    or_(AlertRecord.status == "active", AlertRecord.status == "acknowledged")
                )
            ).first()
            
            return existing_alert is not None
            
        except Exception as e:
            logger.error(f"Error checking alert suppression: {e}")
            return False
        finally:
            if db:
                db.close()

    async def update_performance_baselines(self):
        """Update performance baselines for anomaly detection"""
        logger.info("Updating performance baselines")
        
        # Key metrics to baseline
        metrics_to_baseline = [
            "cpu_percent", "memory_percent", "avg_response_time_ms", 
            "requests_per_minute", "error_rate_percent", "data_processing_rate_per_min"
        ]
        
        for metric_name in metrics_to_baseline:
            await self._calculate_metric_baseline(metric_name)

    async def _calculate_metric_baseline(self, metric_name: str):
        """Calculate baseline for a specific metric"""
        try:
            db = next(get_db())
            
            # Get last 7 days of data
            cutoff = datetime.utcnow() - timedelta(days=7)
            
            # Query metric values
            metric_attr = getattr(SystemMetrics, metric_name)
            values = db.query(metric_attr).filter(
                and_(
                    SystemMetrics.collected_at >= cutoff,
                    metric_attr.isnot(None),
                    metric_attr > 0
                )
            ).all()
            
            if len(values) < 100:  # Need sufficient data points
                logger.warning(f"Insufficient data for baseline calculation: {metric_name}")
                return
                
            # Extract numeric values
            numeric_values = [float(v[0]) for v in values if v[0] is not None]
            
            if not numeric_values:
                return
                
            # Calculate statistics
            mean_val = statistics.mean(numeric_values)
            median_val = statistics.median(numeric_values)
            std_dev = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
            min_val = min(numeric_values)
            max_val = max(numeric_values)
            
            # Calculate percentiles
            p95_val = statistics.quantiles(numeric_values, n=20)[18] if len(numeric_values) > 20 else max_val
            p99_val = statistics.quantiles(numeric_values, n=100)[98] if len(numeric_values) > 100 else max_val
            
            # Calculate thresholds
            warning_threshold = mean_val + (2 * std_dev)
            critical_threshold = mean_val + (3 * std_dev)
            
            # Create or update baseline
            existing_baseline = db.query(PerformanceBaseline).filter(
                and_(
                    PerformanceBaseline.metric_name == metric_name,
                    PerformanceBaseline.component == "system",
                    PerformanceBaseline.is_active == True
                )
            ).first()
            
            if existing_baseline:
                # Update existing baseline
                existing_baseline.baseline_mean = mean_val
                existing_baseline.baseline_median = median_val
                existing_baseline.baseline_std_dev = std_dev
                existing_baseline.baseline_min = min_val
                existing_baseline.baseline_max = max_val
                existing_baseline.baseline_p95 = p95_val
                existing_baseline.baseline_p99 = p99_val
                existing_baseline.warning_threshold = warning_threshold
                existing_baseline.critical_threshold = critical_threshold
                existing_baseline.sample_count = len(numeric_values)
                existing_baseline.confidence_score = min(1.0, len(numeric_values) / 1000)
                existing_baseline.variance_score = std_dev / mean_val if mean_val > 0 else 0
                existing_baseline.baseline_created_at = datetime.utcnow()
            else:
                # Create new baseline
                baseline = PerformanceBaseline(
                    metric_name=metric_name,
                    component="system",
                    environment="production",
                    baseline_period_start=cutoff,
                    baseline_period_end=datetime.utcnow(),
                    baseline_mean=mean_val,
                    baseline_median=median_val,
                    baseline_std_dev=std_dev,
                    baseline_min=min_val,
                    baseline_max=max_val,
                    baseline_p95=p95_val,
                    baseline_p99=p99_val,
                    warning_threshold=warning_threshold,
                    critical_threshold=critical_threshold,
                    sample_count=len(numeric_values),
                    confidence_score=min(1.0, len(numeric_values) / 1000),
                    variance_score=std_dev / mean_val if mean_val > 0 else 0,
                    is_active=True
                )
                db.add(baseline)
                
            db.commit()
            logger.info(f"Updated baseline for {metric_name}: mean={mean_val:.2f}, std_dev={std_dev:.2f}")
            
        except Exception as e:
            logger.error(f"Error calculating baseline for {metric_name}: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()

    async def detect_anomalies(self):
        """Detect anomalies using statistical baselines"""
        if not self.metrics_buffer:
            return
            
        latest_metrics = self.metrics_buffer[-1]
        
        # Check each metric against its baseline
        metrics_to_check = [
            "cpu_percent", "memory_percent", "avg_response_time_ms",
            "requests_per_minute", "error_rate_percent"
        ]
        
        for metric_name in metrics_to_check:
            await self._check_metric_anomaly(latest_metrics, metric_name)

    async def _check_metric_anomaly(self, metrics: SystemMetrics, metric_name: str):
        """Check if a metric value is anomalous"""
        try:
            # Get baseline for metric
            baseline = await self._get_metric_baseline(metric_name)
            if not baseline:
                return
                
            current_value = getattr(metrics, metric_name, 0)
            
            # Check for anomalies
            is_anomaly = False
            anomaly_type = "normal"
            
            if current_value > baseline.critical_threshold:
                is_anomaly = True
                anomaly_type = "critical_high"
            elif current_value > baseline.warning_threshold:
                is_anomaly = True
                anomaly_type = "warning_high"
            elif baseline.lower_bound and current_value < baseline.lower_bound:
                is_anomaly = True
                anomaly_type = "warning_low"
                
            if is_anomaly:
                await self._create_alert(
                    alert_type="anomaly",
                    severity="critical" if "critical" in anomaly_type else "medium",
                    category=f"anomaly_{metric_name}",
                    title=f"Anomaly Detected: {metric_name.replace('_', ' ').title()}",
                    message=f"Metric {metric_name} value {current_value:.2f} is anomalous (baseline: {baseline.baseline_mean:.2f} ± {baseline.baseline_std_dev:.2f})",
                    source_component="anomaly_detection",
                    source_metric_name=metric_name,
                    source_metric_value=current_value,
                    threshold_value=baseline.warning_threshold,
                    technical_details={
                        "baseline_mean": baseline.baseline_mean,
                        "baseline_std_dev": baseline.baseline_std_dev,
                        "anomaly_type": anomaly_type,
                        "confidence_score": baseline.confidence_score
                    }
                )
                
        except Exception as e:
            logger.error(f"Error checking anomaly for {metric_name}: {e}")

    async def _get_metric_baseline(self, metric_name: str) -> Optional[PerformanceBaseline]:
        """Get the current baseline for a metric"""
        try:
            db = next(get_db())
            baseline = db.query(PerformanceBaseline).filter(
                and_(
                    PerformanceBaseline.metric_name == metric_name,
                    PerformanceBaseline.component == "system",
                    PerformanceBaseline.is_active == True
                )
            ).first()
            return baseline
        except Exception as e:
            logger.error(f"Error retrieving baseline for {metric_name}: {e}")
            return None
        finally:
            if db:
                db.close()

    # Public API methods for external integration
    
    def record_request_metric(self, endpoint: str, response_time: float, status_code: int):
        """Record API request metrics"""
        self.request_metrics.append({
            'timestamp': time.time(),
            'endpoint': endpoint,
            'response_time': response_time * 1000,  # Convert to ms
            'status_code': status_code
        })

    def record_job_metric(self, job_id: str, status: str, duration: Optional[float] = None):
        """Record job execution metrics"""
        self.job_metrics.append({
            'timestamp': time.time(),
            'job_id': job_id,
            'status': status,
            'duration': duration
        })

    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive system health summary"""
        if not self.metrics_buffer:
            return {"status": "no_data", "message": "No metrics available"}
            
        latest = self.metrics_buffer[-1]
        
        # Count alerts by severity
        db = next(get_db())
        try:
            critical_alerts = db.query(func.count(AlertRecord.id)).filter(
                and_(AlertRecord.status == "active", AlertRecord.severity == "critical")
            ).scalar() or 0
            
            warning_alerts = db.query(func.count(AlertRecord.id)).filter(
                and_(AlertRecord.status == "active", AlertRecord.severity == "medium")
            ).scalar() or 0
            
        except Exception as e:
            logger.error(f"Error querying alerts: {e}")
            critical_alerts = warning_alerts = 0
        finally:
            db.close()
        
        return {
            "overall_status": latest.health_status,
            "timestamp": latest.collected_at.isoformat(),
            "system_resources": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_usage_percent": latest.disk_usage_percent
            },
            "performance": {
                "requests_per_minute": latest.requests_per_minute,
                "avg_response_time_ms": latest.avg_response_time_ms,
                "error_rate_percent": latest.error_rate_percent
            },
            "jobs": {
                "active": latest.active_scraping_jobs,
                "completed_last_hour": latest.completed_jobs_last_hour,
                "failed_last_hour": latest.failed_jobs_last_hour
            },
            "alerts": {
                "critical": critical_alerts,
                "warning": warning_alerts,
                "total_active": latest.alert_count
            },
            "anomaly_score": latest.anomaly_score
        }

    async def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        try:
            db = next(get_db())
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            metrics = db.query(SystemMetrics).filter(
                SystemMetrics.collected_at >= cutoff
            ).order_by(SystemMetrics.collected_at.desc()).limit(1000).all()
            
            return [
                {
                    "timestamp": m.collected_at.isoformat(),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "disk_usage_percent": m.disk_usage_percent,
                    "requests_per_minute": m.requests_per_minute,
                    "avg_response_time_ms": m.avg_response_time_ms,
                    "error_rate_percent": m.error_rate_percent,
                    "health_status": m.health_status
                }
                for m in metrics
            ]
            
        except Exception as e:
            logger.error(f"Error retrieving metrics history: {e}")
            return []
        finally:
            if db:
                db.close()

    def register_notification_handler(self, channel: str, handler: Callable):
        """Register a notification handler for a channel"""
        self.notification_handlers[channel] = handler
        logger.info(f"Registered notification handler for channel: {channel}")


# Global monitoring service instance
monitoring_service = MonitoringService()
