#!/usr/bin/env python3
"""
Advanced Multi-Tier Caching System
Intelligent caching with Redis, memory cache, and database optimization
"""

import json
import time
import hashlib
import pickle
import gzip
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod
import threading
from functools import wraps
import weakref

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    hit_count: int = 0
    size_bytes: int = 0
    tags: List[str] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def serialize(self) -> bytes:
        """Serialize cache entry for storage"""
        return gzip.compress(pickle.dumps({
            'value': self.value,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'hit_count': self.hit_count,
            'tags': self.tags or []
        }))
    
    @classmethod
    def deserialize(cls, key: str, data: bytes) -> 'CacheEntry':
        """Deserialize cache entry from storage"""
        try:
            decompressed = gzip.decompress(data)
            obj = pickle.loads(decompressed)
            
            return cls(
                key=key,
                value=obj['value'],
                created_at=obj['created_at'],
                expires_at=obj.get('expires_at'),
                hit_count=obj.get('hit_count', 0),
                size_bytes=len(data),
                tags=obj.get('tags', [])
            )
        except Exception:
            # Return None for corrupted entries
            return None

class CacheBackend(ABC):
    """Abstract cache backend interface"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key"""
        pass
    
    @abstractmethod
    async def set(self, entry: CacheEntry, ttl: Optional[int] = None) -> bool:
        """Set cache entry"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        pass
    
    @abstractmethod
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching pattern"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        pass

class MemoryCache(CacheBackend):
    """In-memory cache backend with LRU eviction"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_usage': 0
        }
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry"""
        with self.lock:
            entry = self.cache.get(key)
            if entry and not entry.is_expired():
                # Update access order for LRU
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                entry.hit_count += 1
                self.stats['hits'] += 1
                return entry
            elif entry:
                # Remove expired entry
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
            
            self.stats['misses'] += 1
            return None
    
    async def set(self, entry: CacheEntry, ttl: Optional[int] = None) -> bool:
        """Set cache entry"""
        with self.lock:
            # Set expiration if TTL provided
            if ttl:
                entry.expires_at = datetime.now() + timedelta(seconds=ttl)
            
            # Calculate entry size
            entry.size_bytes = len(pickle.dumps(entry.value))
            
            # Check if we need to evict entries
            await self._evict_if_needed(entry.size_bytes)
            
            # Store entry
            self.cache[entry.key] = entry
            if entry.key in self.access_order:
                self.access_order.remove(entry.key)
            self.access_order.append(entry.key)
            
            self._update_memory_usage()
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                self._update_memory_usage()
                return True
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries"""
        with self.lock:
            if pattern is None:
                count = len(self.cache)
                self.cache.clear()
                self.access_order.clear()
                self.stats['memory_usage'] = 0
                return count
            else:
                # Pattern-based clearing (simple wildcard support)
                import fnmatch
                keys_to_delete = []
                for key in self.cache.keys():
                    if fnmatch.fnmatch(key, pattern):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.cache[key]
                    if key in self.access_order:
                        self.access_order.remove(key)
                
                self._update_memory_usage()
                return len(keys_to_delete)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        with self.lock:
            entry = self.cache.get(key)
            return entry is not None and not entry.is_expired()
    
    async def _evict_if_needed(self, new_entry_size: int):
        """Evict entries if needed for size/memory limits"""
        # Check size limit
        while len(self.cache) >= self.max_size and self.access_order:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
        
        # Check memory limit
        while (self.stats['memory_usage'] + new_entry_size > self.max_memory_bytes 
               and self.access_order):
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.cache:
                del self.cache[oldest_key]
                self.stats['evictions'] += 1
    
    def _update_memory_usage(self):
        """Update memory usage statistics"""
        self.stats['memory_usage'] = sum(
            entry.size_bytes for entry in self.cache.values()
        )

class RedisCache(CacheBackend):
    """Redis cache backend"""
    
    def __init__(self, redis_url: str, key_prefix: str = "cache:"):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.redis_client = None
        self._connection_lock = asyncio.Lock()
    
    async def _get_redis(self):
        """Get Redis connection with lazy initialization"""
        if self.redis_client is None:
            async with self._connection_lock:
                if self.redis_client is None:
                    try:
                        import redis.asyncio as redis
                        self.redis_client = redis.from_url(self.redis_url)
                        await self.redis_client.ping()
                    except Exception as e:
                        logging.error(f"Failed to connect to Redis: {e}")
                        return None
        return self.redis_client
    
    def _make_key(self, key: str) -> str:
        """Create Redis key with prefix"""
        return f"{self.key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry from Redis"""
        redis = await self._get_redis()
        if not redis:
            return None
        
        try:
            data = await redis.get(self._make_key(key))
            if data:
                entry = CacheEntry.deserialize(key, data)
                if entry and not entry.is_expired():
                    entry.hit_count += 1
                    return entry
                elif entry:
                    # Remove expired entry
                    await self.delete(key)
            return None
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None
    
    async def set(self, entry: CacheEntry, ttl: Optional[int] = None) -> bool:
        """Set cache entry in Redis"""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            data = entry.serialize()
            
            # Calculate TTL
            if ttl:
                expire_time = ttl
            elif entry.expires_at:
                expire_time = int((entry.expires_at - datetime.now()).total_seconds())
                if expire_time <= 0:
                    return False
            else:
                expire_time = None
            
            if expire_time:
                await redis.setex(self._make_key(entry.key), expire_time, data)
            else:
                await redis.set(self._make_key(entry.key), data)
            
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry from Redis"""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            result = await redis.delete(self._make_key(key))
            return result > 0
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries from Redis"""
        redis = await self._get_redis()
        if not redis:
            return 0
        
        try:
            if pattern is None:
                pattern = "*"
            
            search_pattern = f"{self.key_prefix}{pattern}"
            keys = await redis.keys(search_pattern)
            
            if keys:
                deleted = await redis.delete(*keys)
                return deleted
            return 0
        except Exception as e:
            logging.error(f"Redis clear error: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        redis = await self._get_redis()
        if not redis:
            return False
        
        try:
            result = await redis.exists(self._make_key(key))
            return result > 0
        except Exception as e:
            logging.error(f"Redis exists error: {e}")
            return False

class MultiTierCache:
    """Multi-tier cache with memory and Redis backends"""
    
    def __init__(self, 
                 memory_cache: MemoryCache,
                 redis_cache: Optional[RedisCache] = None,
                 default_ttl: int = 3600):
        self.memory_cache = memory_cache
        self.redis_cache = redis_cache
        self.default_ttl = default_ttl
        self.stats = {
            'l1_hits': 0,    # Memory cache hits
            'l2_hits': 0,    # Redis cache hits
            'misses': 0,     # Total misses
            'writes': 0,     # Total writes
            'evictions': 0   # Total evictions
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{prefix}:{json.dumps(args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str, tags: List[str] = None) -> Optional[Any]:
        """Get value from cache (L1 -> L2 -> miss)"""
        # Try L1 cache (memory) first
        entry = await self.memory_cache.get(key)
        if entry:
            self.stats['l1_hits'] += 1
            return entry.value
        
        # Try L2 cache (Redis) if available
        if self.redis_cache:
            entry = await self.redis_cache.get(key)
            if entry:
                self.stats['l2_hits'] += 1
                
                # Promote to L1 cache
                await self.memory_cache.set(entry)
                return entry.value
        
        self.stats['misses'] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                  tags: List[str] = None) -> bool:
        """Set value in cache (both tiers)"""
        if ttl is None:
            ttl = self.default_ttl
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl) if ttl else None,
            tags=tags or []
        )
        
        # Store in both tiers
        success_l1 = await self.memory_cache.set(entry, ttl)
        success_l2 = True
        
        if self.redis_cache:
            success_l2 = await self.redis_cache.set(entry, ttl)
        
        if success_l1 or success_l2:
            self.stats['writes'] += 1
            return True
        
        return False
    
    async def delete(self, key: str) -> bool:
        """Delete from both cache tiers"""
        success_l1 = await self.memory_cache.delete(key)
        success_l2 = True
        
        if self.redis_cache:
            success_l2 = await self.redis_cache.delete(key)
        
        return success_l1 or success_l2
    
    async def clear(self, pattern: Optional[str] = None, tags: List[str] = None) -> int:
        """Clear cache entries"""
        count_l1 = await self.memory_cache.clear(pattern)
        count_l2 = 0
        
        if self.redis_cache:
            count_l2 = await self.redis_cache.clear(pattern)
        
        return max(count_l1, count_l2)
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries by tags"""
        # This is a simplified implementation
        # In production, you'd want a more efficient tag-based invalidation system
        count = 0
        
        # For memory cache, we need to check each entry
        with self.memory_cache.lock:
            keys_to_delete = []
            for key, entry in self.memory_cache.cache.items():
                if entry.tags and any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                await self.delete(key)
                count += 1
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['misses']
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': (self.stats['l1_hits'] + self.stats['l2_hits']) / max(total_requests, 1),
            'l1_hit_rate': self.stats['l1_hits'] / max(total_requests, 1),
            'l2_hit_rate': self.stats['l2_hits'] / max(total_requests, 1),
            'memory_cache_stats': self.memory_cache.stats
        }

def cached(ttl: int = 3600, tags: List[str] = None, key_prefix: str = "func"):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        # Store cache instance as a weak reference to avoid circular references
        cache_ref = None
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal cache_ref
            
            # Get cache instance (you'd inject this in practice)
            if cache_ref is None or cache_ref() is None:
                # Use global cache instance or create one
                cache = getattr(async_wrapper, '_cache', None)
                if cache is None:
                    return await func(*args, **kwargs)
                cache_ref = weakref.ref(cache)
            
            cache = cache_ref()
            if cache is None:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache._generate_key(f"{key_prefix}:{func.__name__}", *args, **kwargs)
            
            # Try to get from cache
            result = await cache.get(cache_key, tags)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl, tags)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, run in event loop
            return asyncio.create_task(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Factory function to create cache instance
def create_cache_system(config: Dict[str, Any]) -> MultiTierCache:
    """Create multi-tier cache system from configuration"""
    # Memory cache configuration
    memory_config = config.get('memory', {})
    memory_cache = MemoryCache(
        max_size=memory_config.get('max_size', 1000),
        max_memory_mb=memory_config.get('max_memory_mb', 100)
    )
    
    # Redis cache configuration
    redis_cache = None
    redis_config = config.get('redis', {})
    if redis_config.get('enabled', False):
        redis_cache = RedisCache(
            redis_url=redis_config['url'],
            key_prefix=redis_config.get('key_prefix', 'cache:')
        )
    
    return MultiTierCache(
        memory_cache=memory_cache,
        redis_cache=redis_cache,
        default_ttl=config.get('default_ttl', 3600)
    )

if __name__ == "__main__":
    import asyncio
    
    # Example usage
    async def test_cache_system():
        config = {
            'memory': {
                'max_size': 1000,
                'max_memory_mb': 50
            },
            'redis': {
                'enabled': False,  # Set to True if Redis is available
                'url': 'redis://localhost:6379/0',
                'key_prefix': 'test_cache:'
            },
            'default_ttl': 300  # 5 minutes
        }
        
        cache = create_cache_system(config)
        
        print("🚀 Multi-Tier Cache System Test")
        print("=" * 40)
        
        # Test basic operations
        await cache.set('test_key', {'data': 'test_value', 'timestamp': time.time()})
        result = await cache.get('test_key')
        print(f"Cache test: {result}")
        
        # Test with tags
        await cache.set('user:123', {'name': 'John Doe'}, tags=['user', 'profile'])
        user_data = await cache.get('user:123')
        print(f"User data: {user_data}")
        
        # Show statistics
        stats = cache.get_stats()
        print(f"\nCache Statistics:")
        print(f"  Hit Rate: {stats['hit_rate']:.2%}")
        print(f"  L1 Hits: {stats['l1_hits']}")
        print(f"  L2 Hits: {stats['l2_hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Total Requests: {stats['total_requests']}")
    
    asyncio.run(test_cache_system())
