#!/usr/bin/env python3
"""
Multi-Tier Caching System for Business Intelligence Scraper
Advanced caching with Redis, memory, and database tiers
"""

import asyncio
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import pickle
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class CacheType(Enum):
    """Cache tier types"""
    MEMORY = "memory"
    REDIS = "redis"
    DATABASE = "database"

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    cache_tier: str = "memory"
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self):
        """Update access information"""
        self.access_count += 1
        self.last_accessed = datetime.now()

class MemoryCache:
    """High-speed in-memory cache tier"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.current_memory_bytes = 0
        
    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of cached value"""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, dict)):
                return len(json.dumps(value))
            else:
                return len(str(value))
        except:
            return 100  # Default estimate
    
    def _evict_lru(self):
        """Evict least recently used items"""
        if not self.cache:
            return
            
        # Sort by last accessed time
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed or x[1].created_at
        )
        
        # Remove oldest 20% of entries
        remove_count = max(1, len(sorted_entries) // 5)
        for i in range(remove_count):
            key, entry = sorted_entries[i]
            self.current_memory_bytes -= entry.size_bytes
            del self.cache[key]
    
    def _ensure_capacity(self, new_size: int):
        """Ensure cache has capacity for new entry"""
        # Check size limits
        while (len(self.cache) >= self.max_size or 
               self.current_memory_bytes + new_size > self.max_memory_bytes):
            self._evict_lru()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from memory cache"""
        entry = self.cache.get(key)
        if entry is None:
            return None
            
        if entry.is_expired():
            await self.delete(key)
            return None
            
        entry.touch()
        return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache"""
        try:
            size_bytes = self._calculate_size(value)
            self._ensure_capacity(size_bytes)
            
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                cache_tier="memory",
                size_bytes=size_bytes
            )
            
            # Remove old entry if exists
            if key in self.cache:
                self.current_memory_bytes -= self.cache[key].size_bytes
            
            self.cache[key] = entry
            self.current_memory_bytes += size_bytes
            
            return True
            
        except Exception as e:
            logger.error(f"Memory cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from memory cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory_bytes -= entry.size_bytes
            del self.cache[key]
            return True
        return False
    
    async def clear(self):
        """Clear all memory cache"""
        self.cache.clear()
        self.current_memory_bytes = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
        
        return {
            "tier": "memory",
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "memory_usage_mb": round(self.current_memory_bytes / (1024 * 1024), 2),
            "memory_limit_mb": round(self.max_memory_bytes / (1024 * 1024), 2),
            "memory_utilization": round(self.current_memory_bytes / self.max_memory_bytes * 100, 2),
            "size_limit": self.max_size,
            "size_utilization": round(total_entries / self.max_size * 100, 2)
        }

class RedisCache:
    """Redis-based distributed cache tier"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            self.connected = True
            logger.info("✅ Redis cache connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        return json.dumps({
            "value": value,
            "type": type(value).__name__,
            "timestamp": datetime.now().isoformat()
        })
    
    def _deserialize_value(self, data: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            parsed = json.loads(data)
            return parsed["value"]
        except:
            return data  # Fallback to raw data
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.connected or not self.redis_client:
            return None
            
        try:
            cache_key = f"cache:{key}"
            data = await self.redis_client.get(cache_key)
            
            if data is None:
                return None
                
            return self._deserialize_value(data)
            
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self.connected or not self.redis_client:
            return False
            
        try:
            cache_key = f"cache:{key}"
            serialized_value = self._serialize_value(value)
            
            if ttl:
                await self.redis_client.setex(cache_key, ttl, serialized_value)
            else:
                await self.redis_client.set(cache_key, serialized_value)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        if not self.connected or not self.redis_client:
            return False
            
        try:
            cache_key = f"cache:{key}"
            result = await self.redis_client.delete(cache_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")
            return False
    
    async def clear(self):
        """Clear Redis cache (all cache: keys)"""
        if not self.connected or not self.redis_client:
            return
            
        try:
            keys = await self.redis_client.keys("cache:*")
            if keys:
                await self.redis_client.delete(*keys)
                
        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not self.connected or not self.redis_client:
            return {"tier": "redis", "connected": False}
            
        try:
            info = await self.redis_client.info("memory")
            keyspace = await self.redis_client.info("keyspace")
            cache_keys = await self.redis_client.keys("cache:*")
            
            return {
                "tier": "redis",
                "connected": True,
                "cache_entries": len(cache_keys),
                "memory_usage_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                "memory_peak_mb": round(info.get("used_memory_peak", 0) / (1024 * 1024), 2),
                "total_keys": sum(db.get("keys", 0) for db in keyspace.values() if isinstance(db, dict))
            }
            
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {"tier": "redis", "connected": True, "error": str(e)}

class DatabaseCache:
    """Database-backed persistent cache tier"""
    
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._init_cache_table()
    
    def _init_cache_table(self):
        """Initialize cache table in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS advanced_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    value_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    size_bytes INTEGER DEFAULT 0
                )
            """)
            
            # Create index for expiration cleanup
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_cache_expires 
                ON advanced_cache(expires_at)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database cache init error: {e}")
    
    def _serialize_value(self, value: Any) -> tuple:
        """Serialize value for database storage"""
        try:
            if isinstance(value, (dict, list)):
                return json.dumps(value), "json"
            elif isinstance(value, (int, float)):
                return str(value), type(value).__name__
            elif isinstance(value, str):
                return value, "str"
            else:
                return pickle.dumps(value).hex(), "pickle"
        except:
            return str(value), "str"
    
    def _deserialize_value(self, value: str, value_type: str) -> Any:
        """Deserialize value from database storage"""
        try:
            if value_type == "json":
                return json.loads(value)
            elif value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value)
            elif value_type == "pickle":
                return pickle.loads(bytes.fromhex(value))
            else:
                return value
        except:
            return value
    
    async def cleanup_expired(self):
        """Remove expired entries from database cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM advanced_cache 
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (datetime.now(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.debug(f"Cleaned up {deleted_count} expired cache entries")
                
        except Exception as e:
            logger.error(f"Database cache cleanup error: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from database cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT value, value_type, expires_at, access_count 
                FROM advanced_cache 
                WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            
            if row is None:
                conn.close()
                return None
            
            value, value_type, expires_at, access_count = row
            
            # Check expiration
            if expires_at:
                expires_datetime = datetime.fromisoformat(expires_at)
                if datetime.now() > expires_datetime:
                    cursor.execute("DELETE FROM advanced_cache WHERE key = ?", (key,))
                    conn.commit()
                    conn.close()
                    return None
            
            # Update access information
            cursor.execute("""
                UPDATE advanced_cache 
                SET access_count = ?, last_accessed = ?
                WHERE key = ?
            """, (access_count + 1, datetime.now(), key))
            
            conn.commit()
            conn.close()
            
            return self._deserialize_value(value, value_type)
            
        except Exception as e:
            logger.error(f"Database cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in database cache"""
        try:
            serialized_value, value_type = self._serialize_value(value)
            size_bytes = len(serialized_value)
            
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO advanced_cache 
                (key, value, value_type, created_at, expires_at, access_count, size_bytes)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (key, serialized_value, value_type, datetime.now(), expires_at, size_bytes))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Database cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from database cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM advanced_cache WHERE key = ?", (key,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return deleted
            
        except Exception as e:
            logger.error(f"Database cache delete error: {e}")
            return False
    
    async def clear(self):
        """Clear all database cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM advanced_cache")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database cache clear error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get database cache statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM advanced_cache")
            total_entries = cursor.fetchone()[0]
            
            # Expired entries
            cursor.execute("""
                SELECT COUNT(*) FROM advanced_cache 
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (datetime.now(),))
            expired_entries = cursor.fetchone()[0]
            
            # Total size
            cursor.execute("SELECT SUM(size_bytes) FROM advanced_cache")
            total_bytes = cursor.fetchone()[0] or 0
            
            # Most accessed
            cursor.execute("""
                SELECT key, access_count FROM advanced_cache 
                ORDER BY access_count DESC LIMIT 5
            """)
            top_accessed = cursor.fetchall()
            
            conn.close()
            
            return {
                "tier": "database",
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "total_size_mb": round(total_bytes / (1024 * 1024), 2),
                "top_accessed": dict(top_accessed)
            }
            
        except Exception as e:
            logger.error(f"Database cache stats error: {e}")
            return {"tier": "database", "error": str(e)}

class MultiTierCacheManager:
    """Multi-tier cache manager coordinating all cache layers"""
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379/1",
                 db_path: str = "data.db",
                 memory_max_size: int = 1000,
                 memory_max_mb: int = 100):
        
        self.memory_cache = MemoryCache(memory_max_size, memory_max_mb)
        self.redis_cache = RedisCache(redis_url)
        self.database_cache = DatabaseCache(db_path)
        
        self.hit_stats = {
            "memory": 0,
            "redis": 0,
            "database": 0,
            "miss": 0
        }
        
        self.write_through = True  # Write to all tiers
        self.read_through = True   # Read from next tier on miss
    
    async def initialize(self):
        """Initialize all cache tiers"""
        await self.redis_cache.connect()
        logger.info("✅ Multi-tier cache manager initialized")
    
    async def shutdown(self):
        """Shutdown all cache tiers"""
        await self.redis_cache.disconnect()
        logger.info("Multi-tier cache manager shutdown")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with tier fallback"""
        
        # Try memory cache first (fastest)
        value = await self.memory_cache.get(key)
        if value is not None:
            self.hit_stats["memory"] += 1
            return value
        
        # Try Redis cache (fast, distributed)
        value = await self.redis_cache.get(key)
        if value is not None:
            self.hit_stats["redis"] += 1
            # Promote to memory cache
            await self.memory_cache.set(key, value, ttl=300)  # 5 min in memory
            return value
        
        # Try database cache (slower, persistent)
        value = await self.database_cache.get(key)
        if value is not None:
            self.hit_stats["database"] += 1
            # Promote to higher tiers
            await self.memory_cache.set(key, value, ttl=300)
            await self.redis_cache.set(key, value, ttl=1800)  # 30 min in Redis
            return value
        
        # Cache miss
        self.hit_stats["miss"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in all cache tiers"""
        
        success_count = 0
        
        # Set in memory cache (short TTL)
        memory_ttl = min(ttl or 300, 300)  # Max 5 minutes in memory
        if await self.memory_cache.set(key, value, memory_ttl):
            success_count += 1
        
        # Set in Redis cache (medium TTL)
        redis_ttl = min(ttl or 1800, 1800)  # Max 30 minutes in Redis
        if await self.redis_cache.set(key, value, redis_ttl):
            success_count += 1
        
        # Set in database cache (long TTL or persistent)
        if await self.database_cache.set(key, value, ttl):
            success_count += 1
        
        return success_count > 0
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache tiers"""
        
        results = await asyncio.gather(
            self.memory_cache.delete(key),
            self.redis_cache.delete(key),
            self.database_cache.delete(key),
            return_exceptions=True
        )
        
        return any(result for result in results if not isinstance(result, Exception))
    
    async def clear_all(self):
        """Clear all cache tiers"""
        await asyncio.gather(
            self.memory_cache.clear(),
            self.redis_cache.clear(),
            self.database_cache.clear(),
            return_exceptions=True
        )
        
        logger.info("All cache tiers cleared")
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache tiers"""
        
        stats = await asyncio.gather(
            self.memory_cache.get_stats(),
            self.redis_cache.get_stats(),
            self.database_cache.get_stats(),
            return_exceptions=True
        )
        
        memory_stats, redis_stats, database_stats = stats
        
        total_hits = sum(self.hit_stats.values())
        hit_rate = (total_hits - self.hit_stats["miss"]) / max(total_hits, 1) * 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall": {
                "hit_rate_percent": round(hit_rate, 2),
                "total_requests": total_hits,
                "hit_distribution": self.hit_stats
            },
            "tiers": {
                "memory": memory_stats if not isinstance(memory_stats, Exception) else {"error": str(memory_stats)},
                "redis": redis_stats if not isinstance(redis_stats, Exception) else {"error": str(redis_stats)},
                "database": database_stats if not isinstance(database_stats, Exception) else {"error": str(database_stats)}
            }
        }
    
    async def cleanup_expired(self):
        """Clean up expired entries from all tiers"""
        await self.database_cache.cleanup_expired()
        logger.debug("Cache cleanup completed")

# Global cache manager instance
cache_manager: Optional[MultiTierCacheManager] = None

async def init_cache_system(redis_url: str = "redis://localhost:6379/1",
                           db_path: str = "data.db",
                           memory_max_size: int = 1000,
                           memory_max_mb: int = 100) -> MultiTierCacheManager:
    """Initialize the multi-tier cache system"""
    global cache_manager
    
    cache_manager = MultiTierCacheManager(
        redis_url=redis_url,
        db_path=db_path,
        memory_max_size=memory_max_size,
        memory_max_mb=memory_max_mb
    )
    
    await cache_manager.initialize()
    
    # Start cleanup task
    asyncio.create_task(background_cache_cleanup())
    
    logger.info("🚀 Multi-tier cache system initialized")
    return cache_manager

async def get_cache() -> Optional[MultiTierCacheManager]:
    """Get the global cache manager"""
    return cache_manager

# Background cleanup task
async def background_cache_cleanup():
    """Background task for cache maintenance"""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            
            if cache_manager:
                await cache_manager.cleanup_expired()
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error

# Cache decorators for easy use
def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator for caching function results"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            if not cache_manager:
                return await func(*args, **kwargs)
            
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, create a simple key and return uncached
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

if __name__ == "__main__":
    async def test_cache_system():
        """Test the multi-tier cache system"""
        print("🧪 Testing Multi-Tier Cache System")
        print("==================================")
        
        # Initialize cache
        cache = await init_cache_system()
        
        # Test data
        test_data = {
            "simple_string": "Hello, World!",
            "complex_dict": {"users": [1, 2, 3], "active": True, "score": 95.5},
            "large_list": list(range(1000))
        }
        
        # Test caching and retrieval
        for key, value in test_data.items():
            print(f"\n📝 Testing {key}...")
            
            # Set value
            success = await cache.set(key, value, ttl=60)
            print(f"   Set: {'✅' if success else '❌'}")
            
            # Get value
            retrieved = await cache.get(key)
            match = retrieved == value
            print(f"   Get: {'✅' if match else '❌'}")
            
            if not match:
                print(f"   Expected: {value}")
                print(f"   Got: {retrieved}")
        
        # Test cache miss
        missing = await cache.get("non_existent_key")
        print(f"\n🔍 Cache miss test: {'✅' if missing is None else '❌'}")
        
        # Get comprehensive stats
        stats = await cache.get_comprehensive_stats()
        print(f"\n📊 Cache Statistics:")
        print(f"   Hit Rate: {stats['overall']['hit_rate_percent']}%")
        print(f"   Total Requests: {stats['overall']['total_requests']}")
        print(f"   Hit Distribution: {stats['overall']['hit_distribution']}")
        
        for tier_name, tier_stats in stats['tiers'].items():
            if 'error' not in tier_stats:
                print(f"   {tier_name.title()}: {tier_stats.get('total_entries', 'N/A')} entries")
        
        # Cleanup
        await cache.shutdown()
        print("\n✅ Cache system test completed!")

    # Run the test
    asyncio.run(test_cache_system())
