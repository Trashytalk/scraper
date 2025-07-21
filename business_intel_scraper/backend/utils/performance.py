"""
Performance Optimization Module for Visual Analytics Platform
Provides caching, query optimization, and performance monitoring
"""

import asyncio
import time
import json
import hashlib
from typing import Any, Dict, Optional, Union, List, Callable
from functools import wraps
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis.asyncio as redis
import psutil
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    operation: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    cache_hit: bool = False
    query_count: int = 0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class CacheManager:
    """Advanced caching with Redis backend and intelligent invalidation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        self.local_cache = {}  # Fallback local cache
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("✅ Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using local cache: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate consistent cache key from data"""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        hash_obj = hashlib.md5(sorted_data.encode())
        return f"{prefix}:{hash_obj.hexdigest()[:16]}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    self.cache_stats["hits"] += 1
                    return json.loads(value)
                else:
                    self.cache_stats["misses"] += 1
                    return None
            else:
                # Fallback to local cache
                if key in self.local_cache:
                    entry = self.local_cache[key]
                    if entry["expires"] > datetime.utcnow():
                        self.cache_stats["hits"] += 1
                        return entry["data"]
                    else:
                        del self.local_cache[key]
                
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            
            if self.redis_client:
                await self.redis_client.setex(key, ttl, serialized_value)
            else:
                # Fallback to local cache
                self.local_cache[key] = {
                    "data": value,
                    "expires": datetime.utcnow() + timedelta(seconds=ttl)
                }
                
                # Cleanup expired entries periodically
                if len(self.local_cache) > 1000:
                    await self._cleanup_local_cache()
            
            self.cache_stats["sets"] += 1
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(key)
            else:
                self.local_cache.pop(key, None)
            
            self.cache_stats["deletes"] += 1
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def delete_pattern(self, pattern: str):
        """Delete keys matching pattern"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    self.cache_stats["deletes"] += len(keys)
            else:
                # Local cache pattern deletion
                keys_to_delete = [k for k in self.local_cache.keys() if pattern.replace("*", "") in k]
                for key in keys_to_delete:
                    del self.local_cache[key]
                self.cache_stats["deletes"] += len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
    
    async def _cleanup_local_cache(self):
        """Cleanup expired local cache entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, entry in self.local_cache.items()
            if entry["expires"] <= now
        ]
        for key in expired_keys:
            del self.local_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            **self.cache_stats,
            "backend": "redis" if self.redis_client else "local",
            "local_cache_size": len(self.local_cache)
        }

class QueryOptimizer:
    """Database query optimization and analysis"""
    
    def __init__(self):
        self.query_stats = {}
        self.slow_query_threshold = 1000  # milliseconds
    
    @asynccontextmanager
    async def track_query(self, query_name: str):
        """Context manager to track query performance"""
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            yield
        finally:
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            duration_ms = (end_time - start_time) * 1000
            memory_delta = end_memory - start_memory
            
            # Update stats
            if query_name not in self.query_stats:
                self.query_stats[query_name] = {
                    "count": 0,
                    "total_duration_ms": 0,
                    "avg_duration_ms": 0,
                    "max_duration_ms": 0,
                    "slow_queries": 0
                }
            
            stats = self.query_stats[query_name]
            stats["count"] += 1
            stats["total_duration_ms"] += duration_ms
            stats["avg_duration_ms"] = stats["total_duration_ms"] / stats["count"]
            stats["max_duration_ms"] = max(stats["max_duration_ms"], duration_ms)
            
            if duration_ms > self.slow_query_threshold:
                stats["slow_queries"] += 1
                logger.warning(f"Slow query detected: {query_name} took {duration_ms:.2f}ms")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return {
            "queries": self.query_stats,
            "slow_query_threshold_ms": self.slow_query_threshold,
            "total_queries": sum(stats["count"] for stats in self.query_stats.values())
        }

class PerformanceMonitor:
    """System performance monitoring and alerting"""
    
    def __init__(self):
        self.metrics_history = []
        self.alerts_config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "response_time_threshold": 1000.0,
            "error_rate_threshold": 5.0
        }
        self.alert_callbacks = []
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric"""
        self.metrics_history.append(metric)
        
        # Keep only last 1000 metrics
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Check for alerts
        self._check_alerts(metric)
    
    def _check_alerts(self, metric: PerformanceMetrics):
        """Check if metric triggers any alerts"""
        alerts = []
        
        if metric.cpu_percent > self.alerts_config["cpu_threshold"]:
            alerts.append(f"High CPU usage: {metric.cpu_percent:.1f}%")
        
        if metric.memory_mb > self.alerts_config["memory_threshold"]:
            alerts.append(f"High memory usage: {metric.memory_mb:.1f}MB")
        
        if metric.duration_ms > self.alerts_config["response_time_threshold"]:
            alerts.append(f"Slow response time: {metric.duration_ms:.1f}ms")
        
        for alert in alerts:
            logger.warning(f"Performance Alert: {alert}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metric)
                except Exception as e:
                    logger.error(f"Alert callback error: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system performance statistics"""
        process = psutil.Process()
        
        # Recent metrics (last 100)
        recent_metrics = self.metrics_history[-100:] if self.metrics_history else []
        
        avg_response_time = sum(m.duration_ms for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        return {
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "network_connections": len(psutil.net_connections())
            },
            "process": {
                "cpu_percent": process.cpu_percent(),
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "open_files": len(process.open_files()),
                "num_threads": process.num_threads()
            },
            "application": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "total_requests": len(self.metrics_history),
                "metrics_history_size": len(self.metrics_history)
            }
        }

# Global instances
cache_manager = CacheManager()
query_optimizer = QueryOptimizer()
performance_monitor = PerformanceMonitor()

# Decorators for performance optimization
def cached(ttl: int = 3600, key_prefix: str = "default"):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_data = {"args": args, "kwargs": kwargs}
            cache_key = cache_manager._generate_cache_key(f"{key_prefix}:{func.__name__}", cache_data)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

def performance_tracked(operation_name: str = None):
    """Decorator to track function performance"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            start_cpu = psutil.Process().cpu_percent()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.perf_counter()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                end_cpu = psutil.Process().cpu_percent()
                
                duration_ms = (end_time - start_time) * 1000
                
                metric = PerformanceMetrics(
                    operation=op_name,
                    duration_ms=duration_ms,
                    memory_mb=end_memory,
                    cpu_percent=end_cpu
                )
                
                performance_monitor.record_metric(metric)
        
        return wrapper
    return decorator

# Optimization utilities
async def optimize_database_queries():
    """Analyze and suggest database query optimizations"""
    stats = query_optimizer.get_query_stats()
    
    recommendations = []
    
    for query_name, query_stats in stats["queries"].items():
        if query_stats["slow_queries"] > 0:
            slow_percentage = (query_stats["slow_queries"] / query_stats["count"]) * 100
            recommendations.append({
                "query": query_name,
                "issue": "slow_execution",
                "avg_duration_ms": query_stats["avg_duration_ms"],
                "slow_percentage": slow_percentage,
                "suggestion": "Consider adding database indexes or optimizing query structure"
            })
    
    return {
        "total_queries_analyzed": len(stats["queries"]),
        "recommendations": recommendations,
        "overall_stats": stats
    }

async def cache_warm_up():
    """Pre-populate cache with frequently accessed data"""
    logger.info("Starting cache warm-up...")
    
    try:
        # This would typically pre-load common queries
        warm_up_operations = [
            "network-data-default",
            "timeline-data-recent",
            "geospatial-data-summary"
        ]
        
        for operation in warm_up_operations:
            # Simulate cache population
            await cache_manager.set(f"warmup:{operation}", {"status": "ready"}, ttl=7200)
        
        logger.info(f"✅ Cache warm-up completed: {len(warm_up_operations)} operations")
        
    except Exception as e:
        logger.error(f"❌ Cache warm-up failed: {e}")

async def cleanup_expired_data():
    """Cleanup expired cache entries and old metrics"""
    try:
        # Cleanup local cache
        await cache_manager._cleanup_local_cache()
        
        # Cleanup old performance metrics
        if len(performance_monitor.metrics_history) > 10000:
            performance_monitor.metrics_history = performance_monitor.metrics_history[-5000:]
        
        logger.info("✅ Data cleanup completed")
        
    except Exception as e:
        logger.error(f"❌ Data cleanup failed: {e}")

# Performance optimization initialization
async def initialize_performance_optimization():
    """Initialize all performance optimization components"""
    try:
        await cache_manager.initialize()
        await cache_warm_up()
        logger.info("✅ Performance optimization initialized")
        
        # Schedule periodic cleanup
        asyncio.create_task(periodic_cleanup())
        
    except Exception as e:
        logger.error(f"❌ Performance optimization initialization failed: {e}")

async def periodic_cleanup():
    """Periodic maintenance tasks"""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            await cleanup_expired_data()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic cleanup error: {e}")

# Export for easy import
__all__ = [
    'CacheManager', 'QueryOptimizer', 'PerformanceMonitor',
    'cached', 'performance_tracked',
    'cache_manager', 'query_optimizer', 'performance_monitor',
    'initialize_performance_optimization'
]
