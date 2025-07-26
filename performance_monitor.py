#!/usr/bin/env python3
"""
Performance Monitoring and Optimization Module
Provides real-time performance metrics, caching, and optimization features
"""

import time
import psutil
import asyncio
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import threading
from functools import wraps

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from cachetools import TTLCache, LRUCache

# Optional Redis imports - gracefully handle import errors
try:
    import redis
    import aioredis

    REDIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Redis not available: {e}. Redis caching will be disabled.")
    redis = None
    aioredis = None
    REDIS_AVAILABLE = False


class PerformanceMetrics:
    """Collects and manages performance metrics"""

    def __init__(self):
        self.request_times = deque(maxlen=1000)  # Last 1000 requests
        self.endpoint_metrics = defaultdict(
            lambda: {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float("inf"),
                "max_time": 0.0,
                "errors": 0,
            }
        )
        self.system_metrics = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_usage": 0.0,
            "active_connections": 0,
            "total_requests": 0,
            "errors_per_minute": 0,
        }
        self.start_time = time.time()
        self._lock = threading.Lock()

    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record performance metrics for a request"""
        with self._lock:
            # Update request times
            self.request_times.append(
                {
                    "endpoint": endpoint,
                    "duration": duration,
                    "status_code": status_code,
                    "timestamp": time.time(),
                }
            )

            # Update endpoint metrics
            metrics = self.endpoint_metrics[endpoint]
            metrics["count"] += 1
            metrics["total_time"] += duration
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            metrics["min_time"] = min(metrics["min_time"], duration)
            metrics["max_time"] = max(metrics["max_time"], duration)

            if status_code >= 400:
                metrics["errors"] += 1

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Calculate errors per minute
            current_time = time.time()
            one_minute_ago = current_time - 60
            recent_errors = sum(
                1
                for req in self.request_times
                if req["timestamp"] > one_minute_ago and req["status_code"] >= 400
            )

            self.system_metrics.update(
                {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_usage": disk.percent,
                    "total_requests": len(self.request_times),
                    "errors_per_minute": recent_errors,
                    "uptime_seconds": int(current_time - self.start_time),
                }
            )

            return self.system_metrics.copy()
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return self.system_metrics.copy()

    def get_endpoint_metrics(self) -> Dict[str, Any]:
        """Get performance metrics by endpoint"""
        with self._lock:
            return dict(self.endpoint_metrics)

    def get_recent_performance(self, minutes: int = 5) -> Dict[str, Any]:
        """Get performance data for the last N minutes"""
        current_time = time.time()
        cutoff_time = current_time - (minutes * 60)

        recent_requests = [
            req for req in self.request_times if req["timestamp"] > cutoff_time
        ]

        if not recent_requests:
            return {
                "requests_per_minute": 0,
                "avg_response_time": 0,
                "error_rate": 0,
                "total_requests": 0,
            }

        total_requests = len(recent_requests)
        avg_response_time = (
            sum(req["duration"] for req in recent_requests) / total_requests
        )
        error_count = sum(1 for req in recent_requests if req["status_code"] >= 400)
        error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0

        return {
            "requests_per_minute": total_requests / minutes,
            "avg_response_time": round(avg_response_time, 3),
            "error_rate": round(error_rate, 2),
            "total_requests": total_requests,
        }


class CacheManager:
    """Advanced caching system with multiple cache types"""

    def __init__(self, redis_url: Optional[str] = None):
        # In-memory caches
        self.ttl_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL
        self.lru_cache = LRUCache(maxsize=500)
        self.job_cache = TTLCache(maxsize=100, ttl=60)  # Job results cache

        # Redis cache (if available)
        self.redis_client = None
        self.redis_available = False

        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                self.redis_available = True
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis not available, using in-memory cache only: {e}")
        elif redis_url and not REDIS_AVAILABLE:
            logger.warning(
                "Redis URL provided but Redis packages not available. Using in-memory cache only."
            )

    async def get_async_redis(self, redis_url: str):
        """Get async Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("aioredis not available, async Redis disabled")
            return None

        try:
            return await aioredis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Async Redis not available: {e}")
            return None

    def get(self, key: str, cache_type: str = "ttl") -> Optional[Any]:
        """Get value from cache with enhanced fallback"""
        try:
            # Try Redis first if available
            if self.redis_available and self.redis_client:
                try:
                    value = self.redis_client.get(f"{cache_type}:{key}")
                    if value:
                        # Handle Redis response properly - ensure string type
                        if isinstance(value, bytes):
                            value_str = value.decode('utf-8')
                        elif isinstance(value, str):
                            value_str = value
                        else:
                            # Convert to string if needed
                            value_str = str(value)
                        return json.loads(value_str)
                except Exception as e:
                    logger.warning(f"Redis get error for key '{key}': {e}")

            # Enhanced fallback to in-memory cache with validation
            try:
                if cache_type == "ttl" and hasattr(self, 'ttl_cache'):
                    value = self.ttl_cache.get(key)
                    if value is not None:
                        return value
                elif cache_type == "lru" and hasattr(self, 'lru_cache'):
                    value = self.lru_cache.get(key)
                    if value is not None:
                        return value
                elif cache_type == "job" and hasattr(self, 'job_cache'):
                    value = self.job_cache.get(key)
                    if value is not None:
                        return value
                
                # Log cache miss for debugging
                logger.debug(f"Cache miss for key '{key}' in cache type '{cache_type}'")
                
            except Exception as e:
                logger.warning(f"In-memory cache error for key '{key}': {e}")

        except Exception as e:
            logger.error(f"Critical cache get error for key '{key}': {e}")

        # Return None with explicit logging for monitoring
        logger.debug(f"Returning None for cache key '{key}' (type: {cache_type})")
        return None

    def set(self, key: str, value: Any, cache_type: str = "ttl", ttl: int = 300):
        """Set value in cache"""
        try:
            # Set in Redis if available
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.setex(
                        f"{cache_type}:{key}", ttl, json.dumps(value, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")

            # Set in in-memory cache
            if cache_type == "ttl":
                self.ttl_cache[key] = value
            elif cache_type == "lru":
                self.lru_cache[key] = value
            elif cache_type == "job":
                self.job_cache[key] = value

        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def delete(self, key: str, cache_type: str = "ttl"):
        """Delete key from cache"""
        try:
            # Delete from Redis
            if self.redis_available and self.redis_client:
                try:
                    self.redis_client.delete(f"{cache_type}:{key}")
                except Exception as e:
                    logger.warning(f"Redis delete error: {e}")

            # Delete from in-memory cache
            if cache_type == "ttl" and key in self.ttl_cache:
                del self.ttl_cache[key]
            elif cache_type == "lru" and key in self.lru_cache:
                del self.lru_cache[key]
            elif cache_type == "job" and key in self.job_cache:
                del self.job_cache[key]

        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def clear_all(self):
        """Clear all caches"""
        try:
            if self.redis_available and self.redis_client:
                self.redis_client.flushdb()

            self.ttl_cache.clear()
            self.lru_cache.clear()
            self.job_cache.clear()

            logger.info("All caches cleared")
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")


class DatabaseOptimizer:
    """Database query optimization and connection pooling"""

    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connection_pool = []
        self.pool_lock = threading.Lock()
        self._init_pool()

        # Query performance tracking
        self.query_metrics = defaultdict(
            lambda: {"count": 0, "total_time": 0.0, "avg_time": 0.0}
        )

    def _init_pool(self):
        """Initialize connection pool"""
        try:
            for _ in range(self.pool_size):
                conn = sqlite3.connect(
                    self.db_path, check_same_thread=False, timeout=30.0
                )
                conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                conn.execute("PRAGMA synchronous=NORMAL")  # Faster writes
                conn.execute("PRAGMA cache_size=10000")  # Larger cache
                conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp
                self.connection_pool.append(conn)

            logger.info(
                f"Database connection pool initialized with {self.pool_size} connections"
            )
        except Exception as e:
            logger.error(f"Error initializing database pool: {e}")

    @asynccontextmanager
    async def get_connection(self):
        """Get connection from pool"""
        conn = None
        try:
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()

            if conn is None:
                # Create new connection if pool is empty
                conn = sqlite3.connect(
                    self.db_path, check_same_thread=False, timeout=30.0
                )
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")

            yield conn

        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.pool_size:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()

    def execute_query(
        self, query: str, params: tuple = (), fetch: Optional[str] = None
    ) -> Any:
        """Execute database query with connection pooling"""
        start_time = time.time()
        conn = None  # Initialize conn variable
        
        try:
            # Get connection from pool or create new
            with self.pool_lock:
                if self.connection_pool:
                    conn = self.connection_pool.pop()
                else:
                    conn = sqlite3.connect(self.db_path, check_same_thread=False)

            cursor = conn.cursor()
            cursor.execute(query, params)

            result = None
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            elif fetch == "many":
                result = cursor.fetchmany(1000)  # Limit large result sets

            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                conn.commit()
                result = (
                    cursor.lastrowid
                    if query.strip().upper().startswith("INSERT")
                    else cursor.rowcount
                )

            # Record query performance
            duration = time.time() - start_time
            query_type = query.split()[0].upper()
            metrics = self.query_metrics[query_type]
            metrics["count"] += 1
            metrics["total_time"] += duration
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]

            return result

        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
        finally:
            if conn:
                with self.pool_lock:
                    if len(self.connection_pool) < self.pool_size:
                        self.connection_pool.append(conn)
                    else:
                        conn.close()

    def get_query_metrics(self) -> Dict[str, Any]:
        """Get database query performance metrics"""
        return dict(self.query_metrics)


class PerformanceMiddleware:
    """FastAPI middleware for performance monitoring"""

    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics

    async def __call__(self, request, call_next):
        start_time = time.time()

        # Execute request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        endpoint = f"{request.method} {request.url.path}"
        self.metrics.record_request(endpoint, duration, response.status_code)

        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = str(id(request))

        return response


# Global instances
performance_metrics = PerformanceMetrics()
cache_manager = CacheManager()
db_optimizer = None  # Will be initialized with actual DB path


# Decorator for caching function results
def cached(cache_type: str = "ttl", ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key, cache_type)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, cache_type, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached_result = cache_manager.get(cache_key, cache_type)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, cache_type, ttl)
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Performance monitoring functions
def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary"""
    return {
        "system": performance_metrics.get_system_metrics(),
        "endpoints": performance_metrics.get_endpoint_metrics(),
        "recent": performance_metrics.get_recent_performance(),
        "database": db_optimizer.get_query_metrics() if db_optimizer else {},
        "timestamp": datetime.utcnow().isoformat(),
    }


def optimize_database_indexes(db_path: str):
    """Create optimized database indexes for better performance"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create performance indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_jobs_created_by_status ON jobs(created_by, status)",
            "CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_job_results_job_id ON job_results(job_id)",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

        # Analyze tables for query optimization
        cursor.execute("ANALYZE")

        conn.commit()
        conn.close()

        logger.info("Database indexes optimized successfully")

    except Exception as e:
        logger.error(f"Error optimizing database indexes: {e}")


async def background_performance_monitor():
    """Background task to monitor system performance"""
    while True:
        try:
            # Update system metrics
            metrics = performance_metrics.get_system_metrics()

            # Log warnings for high resource usage
            if metrics["cpu_percent"] > 80:
                logger.warning(f"High CPU usage: {metrics['cpu_percent']}%")

            if metrics["memory_percent"] > 85:
                logger.warning(f"High memory usage: {metrics['memory_percent']}%")

            if metrics["errors_per_minute"] > 10:
                logger.warning(
                    f"High error rate: {metrics['errors_per_minute']} errors/minute"
                )

            # Clean old cache entries periodically
            if len(cache_manager.ttl_cache) > 800:
                logger.info("Cleaning cache due to high memory usage")
                # TTL cache will automatically clean expired entries

            await asyncio.sleep(30)  # Monitor every 30 seconds

        except Exception as e:
            logger.error(f"Error in performance monitor: {e}")
            await asyncio.sleep(60)  # Wait longer on error


def init_performance_system(db_path: str, redis_url: Optional[str] = None):
    """Initialize performance monitoring system"""
    global db_optimizer, cache_manager

    # Initialize database optimizer
    db_optimizer = DatabaseOptimizer(db_path)

    # Optimize database indexes
    optimize_database_indexes(db_path)

    # Initialize cache manager with Redis if available
    if redis_url:
        cache_manager = CacheManager(redis_url)

    logger.info("Performance monitoring system initialized")

    return performance_metrics, cache_manager, db_optimizer
