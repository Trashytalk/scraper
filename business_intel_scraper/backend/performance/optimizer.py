"""
Performance Optimization Module for Business Intelligence Scraper

This module provides comprehensive performance optimizations including:
- Database query optimization with connection pooling
- Redis caching layer with intelligent cache management  
- Background task optimization with queue management
- Memory optimization with efficient data structures
- CPU optimization with parallel processing
- Network optimization with connection pooling and compression
"""

import asyncio
import logging
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import weakref
import gzip
import pickle
from functools import wraps, lru_cache
import threading
from collections import defaultdict, deque
import psutil  # type: ignore[import-untyped]
import json

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from sqlalchemy.pool import QueuePool, StaticPool
    from sqlalchemy import create_engine, text
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for performance optimizations."""
    
    # Database optimization
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    
    # Cache optimization
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_max_memory: int = 128 * 1024 * 1024  # 128MB
    cache_compression: bool = True
    
    # Task optimization
    max_workers: int = 8
    task_queue_size: int = 1000
    batch_processing_size: int = 100
    
    # Memory optimization
    memory_threshold: float = 0.8  # 80% memory usage
    gc_interval: int = 300  # 5 minutes
    object_pool_size: int = 1000
    
    # Network optimization
    connection_pool_size: int = 100
    request_timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.3


class PerformanceCache:
    """High-performance caching layer with compression and TTL support."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.local_cache: Dict[str, Any] = {}
        self.cache_stats: defaultdict[str, int] = defaultdict(int)
        self.redis_client = None
        
        if REDIS_AVAILABLE and config.cache_enabled:
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    decode_responses=False,
                    max_connections=50,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30
                )
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None
        
        # Start cache cleanup task
        self._cleanup_task: Optional[asyncio.Task[Any]] = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self) -> None:
        """Start background cache cleanup task."""
        try:
            loop = asyncio.get_event_loop()
            self._cleanup_task = loop.create_task(self._periodic_cleanup())
        except RuntimeError:
            logger.warning("No event loop available for cache cleanup")
    
    async def _periodic_cleanup(self) -> None:
        """Periodically clean up expired cache entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean every 5 minutes
                
                # Clean local cache
                current_time = time.time()
                expired_keys = []
                
                for key, (value, timestamp, ttl) in self.local_cache.items():
                    if current_time - timestamp > ttl:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.local_cache[key]
                
                if expired_keys:
                    logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize and optionally compress data."""
        serialized = pickle.dumps(data)
        
        if self.config.cache_compression and len(serialized) > 1024:  # Compress if > 1KB
            serialized = gzip.compress(serialized)
            
        return serialized
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize and optionally decompress data."""
        try:
            # Try to decompress first
            if self.config.cache_compression:
                try:
                    data = gzip.decompress(data)
                except (gzip.BadGzipFile, OSError):
                    # Not compressed, use as-is
                    pass
            
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Failed to deserialize cache data: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with fallback hierarchy."""
        self.cache_stats['gets'] += 1
        
        # Check local cache first
        if key in self.local_cache:
            value, timestamp, ttl = self.local_cache[key]
            if time.time() - timestamp <= ttl:
                self.cache_stats['local_hits'] += 1
                return value
            else:
                del self.local_cache[key]
        
        # Check Redis cache
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    value = self._deserialize_data(cached_data)
                    if value is not None:
                        # Store in local cache for faster access
                        self.local_cache[key] = (value, time.time(), self.config.cache_ttl)
                        self.cache_stats['redis_hits'] += 1
                        return value
            except Exception as e:
                logger.error(f"Redis cache get error: {e}")
        
        self.cache_stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        ttl = ttl or self.config.cache_ttl
        
        try:
            # Store in local cache
            self.local_cache[key] = (value, time.time(), ttl)
            
            # Store in Redis cache
            if self.redis_client:
                try:
                    serialized = self._serialize_data(value)
                    self.redis_client.setex(key, ttl, serialized)
                except Exception as e:
                    logger.error(f"Redis cache set error: {e}")
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        deleted = False
        
        # Remove from local cache
        if key in self.local_cache:
            del self.local_cache[key]
            deleted = True
        
        # Remove from Redis cache
        if self.redis_client:
            try:
                redis_deleted = self.redis_client.delete(key)
                deleted = deleted or bool(redis_deleted)
            except Exception as e:
                logger.error(f"Redis cache delete error: {e}")
        
        if deleted:
            self.cache_stats['deletes'] += 1
        
        return deleted
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        count = 0
        
        # Clear local cache
        keys_to_delete = [k for k in self.local_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.local_cache[key]
            count += 1
        
        # Clear Redis cache
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"*{pattern}*")
                if keys:
                    count += self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis pattern clear error: {e}")
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total_requests = self.cache_stats['gets']
        hit_rate = 0.0
        
        if total_requests > 0:
            total_hits = self.cache_stats['local_hits'] + self.cache_stats['redis_hits']
            hit_rate = total_hits / total_requests
        
        return {
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'local_hits': self.cache_stats['local_hits'],
            'redis_hits': self.cache_stats['redis_hits'],
            'misses': self.cache_stats['misses'],
            'sets': self.cache_stats['sets'],
            'deletes': self.cache_stats['deletes'],
            'local_cache_size': len(self.local_cache),
            'redis_connected': self.redis_client is not None
        }


class DatabaseOptimizer:
    """Database performance optimization with connection pooling and query optimization."""
    
    def __init__(self, config: OptimizationConfig, database_url: str):
        self.config = config
        self.database_url = database_url
        self.engine: Optional[Any] = None
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: defaultdict[str, Dict[str, Union[int, float]]] = defaultdict(lambda: {'count': 0, 'total_time': 0.0})
        
        if SQLALCHEMY_AVAILABLE:
            self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize optimized database engine with connection pooling."""
        try:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.config.db_pool_size,
                max_overflow=self.config.db_max_overflow,
                pool_timeout=self.config.db_pool_timeout,
                pool_recycle=self.config.db_pool_recycle,
                echo=False,
                future=True
            )
            logger.info("Optimized database engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Any, None]:
        """Get database connection with automatic cleanup."""
        if not self.engine:
            raise RuntimeError("Database engine not initialized")
        
        conn = None
        try:
            conn = self.engine.connect()
            yield conn
        finally:
            if conn:
                conn.close()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute optimized database query with caching and metrics."""
        start_time = time.time()
        query_key = f"{query}:{hash(str(params))}"
        
        # Check query cache
        if query_key in self.query_cache:
            cached_result, cached_time = self.query_cache[query_key]
            if time.time() - cached_time < 300:  # 5-minute cache
                self.query_stats[query]['count'] = int(self.query_stats[query]['count']) + 1
                if isinstance(cached_result, list):
                    return cached_result
                return []
        
        try:
            async with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                rows: List[Dict[str, Any]] = [dict(row._mapping) for row in result.fetchall()]
                
                # Cache result
                self.query_cache[query_key] = (rows, time.time())
                
                # Update stats
                execution_time = time.time() - start_time
                self.query_stats[query]['count'] = int(self.query_stats[query]['count']) + 1
                self.query_stats[query]['total_time'] = float(self.query_stats[query]['total_time']) + execution_time
                
                return rows
                
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
    
    async def execute_batch(self, query: str, batch_params: List[Dict[str, Any]]) -> bool:
        """Execute batch queries for improved performance."""
        if not batch_params:
            return True
        
        try:
            async with self.get_connection() as conn:
                conn.execute(text(query), batch_params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Batch query error: {e}")
            return False
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get database query performance statistics."""
        stats = {}
        total_queries = 0
        total_time = 0.0
        
        for query, data in self.query_stats.items():
            count = int(data['count'])
            total_queries += count
            total_time += float(data['total_time'])
            
            stats[query[:100]] = {  # Truncate query for readability
                'count': count,
                'avg_time': float(data['total_time']) / count if count > 0 else 0,
                'total_time': float(data['total_time'])
            }
        
        return {
            'total_queries': total_queries,
            'avg_query_time': total_time / total_queries if total_queries > 0 else 0,
            'query_details': stats,
            'cache_size': len(self.query_cache)
        }


class TaskOptimizer:
    """Background task processing optimization with intelligent queuing."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.task_queue: asyncio.Queue[tuple[Any, tuple[Any, ...], Dict[str, Any], str]] = asyncio.Queue(maxsize=config.task_queue_size)
        self.priority_queue: asyncio.PriorityQueue[tuple[int, Any, tuple[Any, ...], Dict[str, Any], str]] = asyncio.PriorityQueue()
        self.thread_pool = ThreadPoolExecutor(max_workers=config.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=min(4, config.max_workers))
        self.task_stats: defaultdict[str, Dict[str, Union[int, float]]] = defaultdict(lambda: {'count': 0, 'total_time': 0.0, 'errors': 0})
        self.active_tasks: int = 0
        self._worker_tasks: List[asyncio.Task[None]] = []
        
        # Start task workers
        self._start_workers()
    
    def _start_workers(self) -> None:
        """Start background task workers."""
        try:
            loop = asyncio.get_event_loop()
            
            # Start queue workers
            for i in range(self.config.max_workers):
                worker_task = loop.create_task(self._queue_worker(f"worker-{i}"))
                self._worker_tasks.append(worker_task)
                
            # Start priority queue worker
            priority_worker = loop.create_task(self._priority_worker())
            self._worker_tasks.append(priority_worker)
            
            logger.info(f"Started {len(self._worker_tasks)} task workers")
            
        except RuntimeError:
            logger.warning("No event loop available for task workers")
    
    async def _queue_worker(self, worker_name: str) -> None:
        """Background task queue worker."""
        while True:
            try:
                # Get task from queue with timeout
                try:
                    task_func, args, kwargs, task_name = await asyncio.wait_for(
                        self.task_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Execute task
                start_time = time.time()
                self.active_tasks += 1
                
                try:
                    if asyncio.iscoroutinefunction(task_func):
                        await task_func(*args, **kwargs)
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool, task_func, *args, **kwargs
                        )
                    
                    # Update success stats
                    execution_time = time.time() - start_time
                    self.task_stats[task_name]['count'] += 1
                    self.task_stats[task_name]['total_time'] += execution_time
                    
                except Exception as e:
                    logger.error(f"Task {task_name} failed: {e}")
                    self.task_stats[task_name]['errors'] += 1
                
                finally:
                    self.active_tasks -= 1
                    self.task_queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
    
    async def _priority_worker(self) -> None:
        """Priority task queue worker."""
        while True:
            try:
                try:
                    priority, task_func, args, kwargs, task_name = await asyncio.wait_for(
                        self.priority_queue.get(), timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Execute high-priority task immediately
                start_time = time.time()
                self.active_tasks += 1
                
                try:
                    if asyncio.iscoroutinefunction(task_func):
                        await task_func(*args, **kwargs)
                    else:
                        await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool, task_func, *args, **kwargs
                        )
                    
                    # Update success stats
                    execution_time = time.time() - start_time
                    self.task_stats[f"priority_{task_name}"]['count'] += 1
                    self.task_stats[f"priority_{task_name}"]['total_time'] += execution_time
                    
                except Exception as e:
                    logger.error(f"Priority task {task_name} failed: {e}")
                    self.task_stats[f"priority_{task_name}"]['errors'] += 1
                
                finally:
                    self.active_tasks -= 1
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Priority worker error: {e}")
    
    async def submit_task(self, task_func: Any, *args: Any, task_name: str = "unknown", **kwargs: Any) -> None:
        """Submit task to queue for background processing."""
        try:
            await self.task_queue.put((task_func, args, kwargs, task_name))
        except asyncio.QueueFull:
            logger.warning(f"Task queue full, dropping task: {task_name}")
    
    async def submit_priority_task(self, task_func: Any, *args: Any, priority: int = 0, task_name: str = "unknown", **kwargs: Any) -> None:
        """Submit high-priority task for immediate processing."""
        await self.priority_queue.put((priority, task_func, args, kwargs, task_name))
    
    async def process_batch(self, task_func: Any, items: List[Any], batch_size: Optional[int] = None) -> None:
        """Process items in optimized batches."""
        batch_size = batch_size or self.config.batch_processing_size
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        # Process batches concurrently
        tasks = []
        for i, batch in enumerate(batches):
            task = self.submit_task(task_func, batch, task_name=f"batch_{i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task processing performance statistics."""
        total_tasks = sum(stats['count'] for stats in self.task_stats.values())
        total_time = sum(stats['total_time'] for stats in self.task_stats.values())
        total_errors = sum(stats['errors'] for stats in self.task_stats.values())
        
        return {
            'total_tasks': total_tasks,
            'active_tasks': self.active_tasks,
            'avg_task_time': total_time / total_tasks if total_tasks > 0 else 0,
            'error_rate': total_errors / total_tasks if total_tasks > 0 else 0,
            'queue_size': self.task_queue.qsize(),
            'priority_queue_size': self.priority_queue.qsize(),
            'task_details': dict(self.task_stats)
        }


class MemoryOptimizer:
    """Memory usage optimization with garbage collection and object pooling."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.object_pools: Dict[str, Dict[str, Any]] = {}
        self.memory_stats: deque[Dict[str, Union[float, int]]] = deque(maxlen=100)
        self.gc_stats: Dict[str, int] = {'collections': 0, 'freed_objects': 0}
        
        # Start memory monitoring
        self._start_memory_monitoring()
    
    def _start_memory_monitoring(self) -> None:
        """Start background memory monitoring."""
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self._memory_monitor())
        except RuntimeError:
            logger.warning("No event loop available for memory monitoring")
    
    async def _memory_monitor(self) -> None:
        """Monitor memory usage and trigger optimizations."""
        import gc
        
        while True:
            try:
                # Get memory stats
                memory_info = psutil.virtual_memory()
                process = psutil.Process()
                process_memory = process.memory_info()
                
                memory_stat = {
                    'timestamp': time.time(),
                    'system_memory_percent': memory_info.percent,
                    'process_memory_mb': process_memory.rss / 1024 / 1024,
                    'available_memory_mb': memory_info.available / 1024 / 1024
                }
                
                self.memory_stats.append(memory_stat)
                
                # Trigger GC if memory usage is high
                if memory_info.percent > self.config.memory_threshold * 100:
                    collected = gc.collect()
                    self.gc_stats['collections'] += 1
                    self.gc_stats['freed_objects'] += collected
                    
                    logger.info(f"Memory threshold exceeded, freed {collected} objects")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(60)
    
    def get_object_pool(self, pool_name: str, factory_func: Any) -> Any:
        """Get or create object pool for reusing expensive objects."""
        if pool_name not in self.object_pools:
            self.object_pools[pool_name] = {
                'objects': deque(maxlen=self.config.object_pool_size),
                'factory': factory_func,
                'created': 0,
                'reused': 0
            }
        
        pool = self.object_pools[pool_name]
        
        if pool['objects']:
            pool['reused'] += 1
            return pool['objects'].popleft()
        else:
            pool['created'] += 1
            return pool['factory']()
    
    def return_object(self, pool_name: str, obj: Any) -> None:
        """Return object to pool for reuse."""
        if pool_name in self.object_pools:
            # Reset object state if needed
            if hasattr(obj, 'reset'):
                obj.reset()
            
            self.object_pools[pool_name]['objects'].append(obj)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory optimization statistics."""
        if not self.memory_stats:
            return {'error': 'No memory stats available'}
        
        recent_stats = list(self.memory_stats)[-10:]  # Last 10 measurements
        
        return {
            'current_memory_percent': recent_stats[-1]['system_memory_percent'] if recent_stats else 0,
            'current_process_memory_mb': recent_stats[-1]['process_memory_mb'] if recent_stats else 0,
            'avg_memory_percent': statistics.mean([s['system_memory_percent'] for s in recent_stats]),
            'peak_memory_percent': max([s['system_memory_percent'] for s in recent_stats]),
            'gc_collections': self.gc_stats['collections'],
            'objects_freed': self.gc_stats['freed_objects'],
            'object_pools': {
                name: {
                    'pool_size': len(pool['objects']),
                    'objects_created': pool['created'],
                    'objects_reused': pool['reused'],
                    'reuse_rate': pool['reused'] / (pool['created'] + pool['reused']) if (pool['created'] + pool['reused']) > 0 else 0
                }
                for name, pool in self.object_pools.items()
            }
        }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self, database_url: Optional[str] = None, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.cache = PerformanceCache(self.config)
        self.task_optimizer = TaskOptimizer(self.config)
        self.memory_optimizer = MemoryOptimizer(self.config)
        self.database_optimizer: Optional[DatabaseOptimizer] = None
        
        if database_url and SQLALCHEMY_AVAILABLE:
            self.database_optimizer = DatabaseOptimizer(self.config, database_url)
        
        # Performance metrics
        self.performance_metrics: Dict[str, Union[float, int]] = {
            'optimization_start_time': time.time(),
            'total_optimizations': 0
        }
        
        logger.info("Performance optimization system initialized")
    
    # Decorators for automatic optimization
    def cached(self, ttl: Optional[int] = None, key_func: Optional[Any] = None) -> Any:
        """Decorator for automatic function result caching."""
        def decorator(func: Any) -> Any:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = f"{func.__name__}:{hash(str(args))}{hash(str(kwargs))}"
                
                # Try to get from cache
                result = await self.cache.get(cache_key)
                if result is not None:
                    return result
                
                # Execute function and cache result
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                await self.cache.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def optimized_task(self, task_name: Optional[str] = None, priority: bool = False) -> Any:
        """Decorator for automatic task optimization."""
        def decorator(func: Any) -> Any:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> None:
                name = task_name or func.__name__
                
                if priority:
                    await self.task_optimizer.submit_priority_task(func, *args, task_name=name, **kwargs)
                else:
                    await self.task_optimizer.submit_task(func, *args, task_name=name, **kwargs)
            
            return wrapper
        return decorator
    
    def memory_optimized(self, pool_name: Optional[str] = None) -> Any:
        """Decorator for automatic memory optimization."""
        def decorator(func: Any) -> Any:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Use object pooling if specified
                if pool_name and hasattr(func, '_object_factory'):
                    obj = self.memory_optimizer.get_object_pool(pool_name, func._object_factory)
                    try:
                        return func(obj, *args, **kwargs)
                    finally:
                        self.memory_optimizer.return_object(pool_name, obj)
                else:
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    async def optimize_database_queries(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze and optimize database queries."""
        if not self.database_optimizer:
            return {'error': 'Database optimizer not available'}
        
        optimization_results: Dict[str, Dict[str, Any]] = {}
        
        for query in queries:
            start_time = time.time()
            
            try:
                # Execute query and measure performance
                result = await self.database_optimizer.execute_query(query)
                execution_time = time.time() - start_time
                
                optimization_results[query[:100]] = {
                    'execution_time': execution_time,
                    'row_count': len(result),
                    'status': 'success'
                }
                
            except Exception as e:
                optimization_results[query[:100]] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return optimization_results
    
    async def run_performance_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis."""
        analysis = {
            'timestamp': time.time(),
            'cache_performance': self.cache.get_stats(),
            'task_performance': self.task_optimizer.get_task_stats(),
            'memory_performance': self.memory_optimizer.get_memory_stats(),
            'system_performance': self._get_system_performance()
        }
        
        if self.database_optimizer:
            analysis['database_performance'] = self.database_optimizer.get_query_stats()
        
        return analysis
    
    def _get_system_performance(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            }
        except Exception as e:
            return {'error': f'Failed to get system metrics: {e}'}
    
    async def apply_optimizations(self, optimization_profile: str = 'balanced') -> Dict[str, Any]:
        """Apply optimization profile to the system."""
        profiles: Dict[str, OptimizationConfig] = {
            'memory_focused': OptimizationConfig(
                db_pool_size=10,
                cache_max_memory=64 * 1024 * 1024,  # 64MB
                max_workers=4,
                batch_processing_size=50
            ),
            'performance_focused': OptimizationConfig(
                db_pool_size=50,
                cache_max_memory=256 * 1024 * 1024,  # 256MB
                max_workers=16,
                batch_processing_size=200
            ),
            'balanced': self.config  # Current config
        }
        
        if optimization_profile in profiles:
            new_config = profiles[optimization_profile]
            
            # Apply new configuration
            optimization_results: Dict[str, Any] = {
                'profile_applied': optimization_profile,
                'changes': []
            }
            
            if new_config.cache_max_memory != self.config.cache_max_memory:
                optimization_results['changes'].append(f"Cache memory limit: {new_config.cache_max_memory // (1024*1024)}MB")
            
            if new_config.max_workers != self.config.max_workers:
                optimization_results['changes'].append(f"Worker threads: {new_config.max_workers}")
            
            self.config = new_config
            self.performance_metrics['total_optimizations'] += 1
            
            return optimization_results
        
        return {'error': f'Unknown optimization profile: {optimization_profile}'}
    
    async def cleanup_resources(self) -> None:
        """Clean up optimization resources."""
        logger.info("Cleaning up performance optimization resources...")
        
        # Stop cache cleanup
        if hasattr(self.cache, '_cleanup_task') and self.cache._cleanup_task:
            self.cache._cleanup_task.cancel()
        
        # Stop task workers
        for worker_task in self.task_optimizer._worker_tasks:
            worker_task.cancel()
        
        # Close thread pools
        self.task_optimizer.thread_pool.shutdown(wait=False)
        self.task_optimizer.process_pool.shutdown(wait=False)
        
        # Close database connections
        if self.database_optimizer and self.database_optimizer.engine:
            self.database_optimizer.engine.dispose()
        
        logger.info("Performance optimization cleanup completed")


# Global performance optimizer instance
performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer(database_url: Optional[str] = None, config: Optional[OptimizationConfig] = None) -> PerformanceOptimizer:
    """Get or create global performance optimizer instance."""
    global performance_optimizer
    
    if performance_optimizer is None:
        performance_optimizer = PerformanceOptimizer(database_url, config)
    
    return performance_optimizer


# Utility functions for common optimizations
async def optimize_batch_processing(items: List[Any], processor_func: Any, batch_size: int = 100) -> None:
    """Optimize batch processing with intelligent batching."""
    optimizer = get_performance_optimizer()
    await optimizer.task_optimizer.process_batch(processor_func, items, batch_size)


@lru_cache(maxsize=1000)
def cached_computation(input_data: str) -> Any:
    """Example of LRU cached computation for expensive operations."""
    # Placeholder for expensive computation
    return hash(input_data)


def memory_efficient_data_processing(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process data with memory-efficient techniques."""
    # Use generators for large datasets
    def process_item(item: Dict[str, Any]) -> Dict[str, Any]:
        # Process individual item
        return {k: v.strip() if isinstance(v, str) else v for k, v in item.items()}
    
    # Process in chunks to avoid memory spikes
    chunk_size = 1000
    results: List[Dict[str, Any]] = []
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        processed_chunk = [process_item(item) for item in chunk]
        results.extend(processed_chunk)
    
    return results


# Performance monitoring utilities
class PerformanceMonitor:
    """Context manager for monitoring function performance."""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
    
    def __enter__(self) -> 'PerformanceMonitor':
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.start_time is not None:
            execution_time = time.time() - self.start_time
        else:
            execution_time = 0.0
        logger.info(f"Performance: {self.operation_name} completed in {execution_time:.3f}s")
        
        # Record performance metric
        optimizer = get_performance_optimizer()
        if optimizer:
            # Could add to optimizer's metrics here
            pass
