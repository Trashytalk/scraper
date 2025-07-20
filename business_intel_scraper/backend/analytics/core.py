"""Core Analytics Engine for Business Intelligence Scraper.

Provides comprehensive analytics capabilities including performance monitoring,
data quality assessment, and business intelligence insights.
"""

from __future__ import annotations

import asyncio
import json
import logging
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    engine = None  # type: ignore[assignment]
    Session = None  # type: ignore[assignment]

# Performance optimization imports
try:
    from ..performance import analytics_performance
    from ..performance.optimizer import PerformanceMonitor
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False
    analytics_performance = None  # type: ignore[assignment]
    PerformanceMonitor = None  # type: ignore[assignment]

def get_config() -> Dict[str, str]:
    """Get configuration with defaults."""
    return {
        "DATABASE_URL": "sqlite:///./analytics.db"
    }

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Single metric measurement at a point in time."""
    
    timestamp: datetime
    name: str
    value: Union[int, float]
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """System performance metrics."""
    
    request_count: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    success_rate: float = 0.0
    peak_memory_usage: int = 0
    cpu_usage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_count": self.request_count,
            "avg_response_time": self.avg_response_time,
            "error_rate": self.error_rate,
            "throughput": self.throughput,
            "success_rate": self.success_rate,
            "peak_memory_usage": self.peak_memory_usage,
            "cpu_usage": self.cpu_usage,
        }


@dataclass
class DataQualityMetrics:
    """Data quality assessment metrics."""
    
    total_records: int = 0
    valid_records: int = 0
    duplicate_records: int = 0
    incomplete_records: int = 0
    quality_score: float = 0.0
    completeness_rate: float = 0.0
    accuracy_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "duplicate_records": self.duplicate_records,
            "incomplete_records": self.incomplete_records,
            "quality_score": self.quality_score,
            "completeness_rate": self.completeness_rate,
            "accuracy_rate": self.accuracy_rate,
        }


@dataclass
class ScrapingMetrics:
    """Spider and scraping specific metrics."""
    
    spiders_active: int = 0
    pages_scraped: int = 0
    items_extracted: int = 0
    robots_compliance: float = 0.0
    ban_rate: float = 0.0
    proxy_success_rate: float = 0.0
    avg_page_load_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "spiders_active": self.spiders_active,
            "pages_scraped": self.pages_scraped,
            "items_extracted": self.items_extracted,
            "robots_compliance": self.robots_compliance,
            "ban_rate": self.ban_rate,
            "proxy_success_rate": self.proxy_success_rate,
            "avg_page_load_time": self.avg_page_load_time,
        }


class AnalyticsEngine:
    """Main analytics engine for collecting and analyzing metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or get_config()
        self.metrics_buffer: List[MetricSnapshot] = []
        self.performance_history: List[PerformanceMetrics] = []
        self.quality_history: List[DataQualityMetrics] = []
        self.scraping_history: List[ScrapingMetrics] = []
        
        # Database connection for historical data
        self.db_engine: Optional[Any] = None
        self.Session: Optional[Any] = None
        self._init_database()
        
        # Real-time metrics tracking
        self._start_time = time.time()
        self._request_times: List[float] = []
        self._error_count = 0
        self._success_count = 0
        
    def _init_database(self) -> None:
        """Initialize database connection for analytics storage."""
        if not SQLALCHEMY_AVAILABLE or create_engine is None:
            logger.warning("SQLAlchemy not available, using in-memory storage only")
            return
            
        try:
            db_url = self.config.get("DATABASE_URL", "sqlite:///./analytics.db")
            self.db_engine = create_engine(db_url)
            if sessionmaker is not None:
                self.Session = sessionmaker(bind=self.db_engine)
            
            # Create analytics tables if they don't exist
            self._create_analytics_tables()
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics database: {e}")
            self.db_engine = None
    
    def _create_analytics_tables(self) -> None:
        """Create analytics tables in the database."""
        if not self.db_engine or not SQLALCHEMY_AVAILABLE or text is None:
            return
            
        try:
            with self.db_engine.connect() as conn:
                # Metrics table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS analytics_metrics (
                        id INTEGER PRIMARY KEY,
                        timestamp DATETIME,
                        name VARCHAR(100),
                        value REAL,
                        tags TEXT,
                        metadata TEXT
                    )
                """))
                
                # Performance snapshots table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS performance_snapshots (
                        id INTEGER PRIMARY KEY,
                        timestamp DATETIME,
                        metrics TEXT
                    )
                """))
                
                # Data quality snapshots table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS quality_snapshots (
                        id INTEGER PRIMARY KEY,
                        timestamp DATETIME,
                        metrics TEXT
                    )
                """))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to create analytics tables: {e}")
    
    async def record_metric(self, name: str, value: Union[int, float], 
                          tags: Optional[Dict[str, str]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record a single metric measurement with performance optimization."""
        # Use performance optimization if available
        if PERFORMANCE_OPTIMIZATION_AVAILABLE and PerformanceMonitor is not None:
            with PerformanceMonitor(f"record_metric_{name}"):
                return await self._record_metric_impl(name, value, tags, metadata)
        else:
            return await self._record_metric_impl(name, value, tags, metadata)
    
    async def _record_metric_impl(self, name: str, value: Union[int, float], 
                                tags: Optional[Dict[str, str]] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> None:
        """Internal metric recording implementation."""
        metric = MetricSnapshot(
            timestamp=datetime.now(),
            name=name,
            value=value,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        self.metrics_buffer.append(metric)
        
        # Flush buffer if it gets too large
        if len(self.metrics_buffer) > 1000:
            await self.flush_metrics()
    
    async def flush_metrics(self) -> None:
        """Flush buffered metrics to database."""
        if not self.metrics_buffer or not self.db_engine or not SQLALCHEMY_AVAILABLE or text is None:
            return
            
        try:
            with self.db_engine.connect() as conn:
                for metric in self.metrics_buffer:
                    conn.execute(text("""
                        INSERT INTO analytics_metrics 
                        (timestamp, name, value, tags, metadata)
                        VALUES (:timestamp, :name, :value, :tags, :metadata)
                    """), {
                        "timestamp": metric.timestamp,
                        "name": metric.name,
                        "value": metric.value,
                        "tags": json.dumps(metric.tags),
                        "metadata": json.dumps(metric.metadata)
                    })
                conn.commit()
                
            self.metrics_buffer.clear()
            logger.debug(f"Flushed {len(self.metrics_buffer)} metrics to database")
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
    
    def record_request_time(self, duration: float) -> None:
        """Record request processing time."""
        self._request_times.append(duration)
        
        # Keep only recent request times (last 1000)
        if len(self._request_times) > 1000:
            self._request_times = self._request_times[-1000:]
    
    def record_success(self) -> None:
        """Record successful request."""
        self._success_count += 1
    
    def record_error(self) -> None:
        """Record failed request."""
        self._error_count += 1
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics."""
        total_requests = self._success_count + self._error_count
        
        metrics = PerformanceMetrics()
        metrics.request_count = total_requests
        
        if self._request_times:
            metrics.avg_response_time = statistics.mean(self._request_times)
            
        if total_requests > 0:
            metrics.error_rate = self._error_count / total_requests
            metrics.success_rate = self._success_count / total_requests
            
            # Calculate throughput (requests per second)
            uptime = time.time() - self._start_time
            if uptime > 0:
                metrics.throughput = total_requests / uptime
        
        return metrics
    
    async def analyze_data_quality(self, data: List[Dict[str, Any]]) -> DataQualityMetrics:
        """Analyze data quality metrics."""
        if not data:
            return DataQualityMetrics()
            
        metrics = DataQualityMetrics()
        metrics.total_records = len(data)
        
        # Analyze completeness
        complete_records = 0
        valid_records = 0
        duplicate_check = set()
        duplicates = 0
        
        for item in data:
            # Check completeness (no empty/null values)
            if all(v is not None and str(v).strip() for v in item.values()):
                complete_records += 1
                
            # Check validity (basic validation)
            if self._is_valid_record(item):
                valid_records += 1
                
            # Check for duplicates
            item_key = str(sorted(item.items()))
            if item_key in duplicate_check:
                duplicates += 1
            else:
                duplicate_check.add(item_key)
        
        metrics.valid_records = valid_records
        metrics.duplicate_records = duplicates
        metrics.incomplete_records = metrics.total_records - complete_records
        
        # Calculate rates
        if metrics.total_records > 0:
            metrics.completeness_rate = complete_records / metrics.total_records
            metrics.accuracy_rate = valid_records / metrics.total_records
            
            # Overall quality score (weighted average)
            metrics.quality_score = (
                0.4 * metrics.completeness_rate +
                0.4 * metrics.accuracy_rate +
                0.2 * (1 - duplicates / metrics.total_records)
            )
        
        # Store in history
        self.quality_history.append(metrics)
        
        return metrics
    
    def _is_valid_record(self, record: Dict[str, Any]) -> bool:
        """Basic validation for record quality."""
        # Add custom validation logic here
        # For now, just check that it's not empty
        return bool(record and any(record.values()))
    
    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary with caching optimization."""
        # Use performance optimization for caching if available
        if PERFORMANCE_OPTIMIZATION_AVAILABLE and analytics_performance:
            cache_key = "analytics_summary"
            
            # Try to get from cache first
            cached_summary = await analytics_performance.optimizer.cache.get(cache_key)
            if cached_summary and isinstance(cached_summary, dict):
                return cached_summary  # type: ignore[no-any-return]
            
            # Generate summary with performance monitoring
            if PerformanceMonitor is not None:
                with PerformanceMonitor("analytics_summary_generation"):
                    summary = await self._generate_analytics_summary()
            else:
                summary = await self._generate_analytics_summary()
                
            # Cache for 30 seconds to balance freshness and performance
            await analytics_performance.optimizer.cache.set(cache_key, summary, ttl=30)
            
            return summary
        else:
            # Fallback without performance optimization
            return await self._generate_analytics_summary()
    
    async def _generate_analytics_summary(self) -> Dict[str, Any]:
        """Generate analytics summary implementation."""
        performance = self.get_performance_metrics()
        
        # Get recent data for quality analysis
        recent_quality = self.quality_history[-1] if self.quality_history else DataQualityMetrics()
        
        # Get recent scraping metrics
        recent_scraping = self.scraping_history[-1] if self.scraping_history else ScrapingMetrics()
        
        # Calculate trends
        performance_trend = self._calculate_performance_trend()
        quality_trend = self._calculate_quality_trend()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance": performance.to_dict(),
            "data_quality": recent_quality.to_dict(),
            "scraping": recent_scraping.to_dict(),
            "trends": {
                "performance": performance_trend,
                "quality": quality_trend,
            },
            "alerts": self._generate_alerts(performance, recent_quality),
        }
    
    def _calculate_performance_trend(self) -> str:
        """Calculate performance trend over time."""
        if len(self.performance_history) < 2:
            return "stable"
            
        recent = self.performance_history[-5:]  # Last 5 measurements
        earlier = self.performance_history[-10:-5] if len(self.performance_history) >= 10 else []
        
        if not earlier:
            return "stable"
            
        recent_avg = statistics.mean([m.avg_response_time for m in recent])
        earlier_avg = statistics.mean([m.avg_response_time for m in earlier])
        
        if recent_avg > earlier_avg * 1.1:
            return "degrading"
        elif recent_avg < earlier_avg * 0.9:
            return "improving"
        else:
            return "stable"
    
    def _calculate_quality_trend(self) -> str:
        """Calculate data quality trend over time."""
        if len(self.quality_history) < 2:
            return "stable"
            
        recent = self.quality_history[-5:]  # Last 5 measurements
        earlier = self.quality_history[-10:-5] if len(self.quality_history) >= 10 else []
        
        if not earlier:
            return "stable"
            
        recent_avg = statistics.mean([m.quality_score for m in recent])
        earlier_avg = statistics.mean([m.quality_score for m in earlier])
        
        if recent_avg > earlier_avg * 1.05:
            return "improving"
        elif recent_avg < earlier_avg * 0.95:
            return "degrading"
        else:
            return "stable"
    
    def _generate_alerts(self, performance: PerformanceMetrics, 
                        quality: DataQualityMetrics) -> List[Dict[str, Any]]:
        """Generate system alerts based on metrics."""
        alerts = []
        
        # Performance alerts
        if performance.error_rate > 0.1:  # 10% error rate
            alerts.append({
                "type": "error",
                "message": f"High error rate: {performance.error_rate:.1%}",
                "category": "performance"
            })
            
        if performance.avg_response_time > 5.0:  # 5 second response time
            alerts.append({
                "type": "warning",
                "message": f"Slow response time: {performance.avg_response_time:.2f}s",
                "category": "performance"
            })
        
        # Quality alerts
        if quality.quality_score < 0.7:  # 70% quality threshold
            alerts.append({
                "type": "warning",
                "message": f"Low data quality: {quality.quality_score:.1%}",
                "category": "data_quality"
            })
            
        if quality.duplicate_records > quality.total_records * 0.2:  # 20% duplicates
            alerts.append({
                "type": "info",
                "message": f"High duplicate rate: {quality.duplicate_records} records",
                "category": "data_quality"
            })
        
        return alerts
    
    async def get_historical_data(self, metric_name: str, 
                                hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric."""
        if not self.db_engine or text is None:
            return []
            
        try:
            with self.db_engine.connect() as conn:
                since = datetime.now() - timedelta(hours=hours)
                
                result = conn.execute(text("""
                    SELECT timestamp, value, tags, metadata
                    FROM analytics_metrics
                    WHERE name = :name AND timestamp >= :since
                    ORDER BY timestamp
                """), {"name": metric_name, "since": since})
                
                return [
                    {
                        "timestamp": row[0],
                        "value": row[1],
                        "tags": json.loads(row[2]) if row[2] else {},
                        "metadata": json.loads(row[3]) if row[3] else {}
                    }
                    for row in result.fetchall()
                ]
                
        except Exception as e:
            logger.error(f"Failed to get historical data: {e}")
            return []
    
    async def cleanup_old_data(self, days: int = 30) -> None:
        """Remove analytics data older than specified days."""
        if not self.db_engine or not SQLALCHEMY_AVAILABLE or text is None:
            return
            
        try:
            with self.db_engine.connect() as conn:
                cutoff = datetime.now() - timedelta(days=days)
                
                conn.execute(text("""
                    DELETE FROM analytics_metrics 
                    WHERE timestamp < :cutoff
                """), {"cutoff": cutoff})
                
                conn.execute(text("""
                    DELETE FROM performance_snapshots 
                    WHERE timestamp < :cutoff
                """), {"cutoff": cutoff})
                
                conn.execute(text("""
                    DELETE FROM quality_snapshots 
                    WHERE timestamp < :cutoff
                """), {"cutoff": cutoff})
                
                conn.commit()
                logger.info(f"Cleaned up analytics data older than {days} days")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Global analytics engine instance
analytics_engine = AnalyticsEngine()
