"""
Advanced Database Optimization System
Provides comprehensive database performance optimization including:
- Intelligent query optimization and caching
- Advanced indexing strategies and recommendations
- Connection pooling with health monitoring
- Query performance analysis and tuning
- Database statistics and maintenance
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import hashlib
from contextlib import asynccontextmanager

from sqlalchemy import text, inspect, Index, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.engine import Engine
from sqlalchemy.sql import sqltypes
from sqlalchemy.dialects import postgresql, sqlite, mysql
import psutil

from ..database.config import get_async_session, async_engine
from ..database.models import Base, Entity, Connection, Event, Location, DataSource


logger = logging.getLogger(__name__)


@dataclass
class QueryAnalysis:
    """Query performance analysis results"""
    query_hash: str
    original_query: str
    execution_count: int = 0
    total_execution_time: float = 0.0
    avg_execution_time: float = 0.0
    min_execution_time: float = float('inf')
    max_execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    row_count: int = 0
    cache_hit_ratio: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)
    last_executed: Optional[datetime] = None
    is_slow_query: bool = False


@dataclass
class IndexRecommendation:
    """Database index recommendation"""
    table_name: str
    columns: List[str]
    index_type: str = "btree"
    priority: str = "medium"  # low, medium, high, critical
    estimated_benefit: float = 0.0
    impact_reason: str = ""
    create_statement: str = ""
    existing_indexes: List[str] = field(default_factory=list)


@dataclass
class DatabaseHealth:
    """Database health metrics"""
    connection_pool_active: int = 0
    connection_pool_size: int = 0
    connection_pool_overflow: int = 0
    avg_query_time_ms: float = 0.0
    slow_query_count: int = 0
    cache_hit_ratio: float = 0.0
    total_queries: int = 0
    database_size_mb: float = 0.0
    fragmentation_ratio: float = 0.0
    last_maintenance: Optional[datetime] = None
    recommendations: List[str] = field(default_factory=list)


class QueryCache:
    """Advanced query result caching with intelligent invalidation"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Tuple[Any, datetime, int]] = {}  # result, expires_at, access_count
        self.access_times: deque = deque(maxlen=10000)
        self.hit_count = 0
        self.miss_count = 0
        
    def get_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        """Generate cache key for query and parameters"""
        params_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.sha256(f"{query}:{params_str}".encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get cached query result"""
        if cache_key in self.cache:
            result, expires_at, access_count = self.cache[cache_key]
            if datetime.utcnow() < expires_at:
                # Update access information
                self.cache[cache_key] = (result, expires_at, access_count + 1)
                self.access_times.append(time.time())
                self.hit_count += 1
                return result
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        
        self.miss_count += 1
        return None
    
    def set(self, cache_key: str, result: Any, ttl: Optional[int] = None) -> None:
        """Cache query result"""
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        expires_at = datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl)
        self.cache[cache_key] = (result, expires_at, 1)
    
    def _evict_least_used(self) -> None:
        """Evict least recently used cache entries"""
        if not self.cache:
            return
            
        # Find entry with lowest access count
        least_used_key = min(self.cache.keys(), key=lambda k: self.cache[k][2])
        del self.cache[least_used_key]
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        removed_count = 0
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        
        for key in keys_to_remove:
            del self.cache[key]
            removed_count += 1
            
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_ratio = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_ratio": hit_ratio,
            "total_requests": total_requests
        }


class IndexAnalyzer:
    """Analyze database indexes and provide optimization recommendations"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.dialect_name = engine.dialect.name
        
    async def analyze_table_indexes(self, table_name: str) -> List[IndexRecommendation]:
        """Analyze indexes for a specific table"""
        recommendations = []
        
        try:
            # Get table metadata
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Analyze query patterns to suggest indexes
            query_patterns = await self._analyze_query_patterns(table_name)
            
            # Check for missing indexes on foreign keys
            for fk in foreign_keys:
                fk_columns = fk['constrained_columns']
                if not self._has_index_on_columns(indexes, fk_columns):
                    recommendations.append(IndexRecommendation(
                        table_name=table_name,
                        columns=fk_columns,
                        priority="high",
                        impact_reason="Foreign key without index causes slow joins",
                        create_statement=self._generate_index_statement(table_name, fk_columns, "fk")
                    ))
            
            # Analyze query patterns for composite indexes
            for pattern in query_patterns:
                if len(pattern['columns']) > 1:
                    if not self._has_index_on_columns(indexes, pattern['columns']):
                        priority = "high" if pattern['frequency'] > 100 else "medium"
                        recommendations.append(IndexRecommendation(
                            table_name=table_name,
                            columns=pattern['columns'],
                            priority=priority,
                            estimated_benefit=pattern['frequency'] * 0.01,
                            impact_reason=f"Frequent queries with {len(pattern['columns'])} column conditions",
                            create_statement=self._generate_index_statement(table_name, pattern['columns'], "composite")
                        ))
            
            # Check for unused indexes
            for index in indexes:
                if not self._is_index_used(table_name, index['name']):
                    recommendations.append(IndexRecommendation(
                        table_name=table_name,
                        columns=index['column_names'],
                        priority="low",
                        impact_reason="Index appears to be unused, consider dropping",
                        create_statement=f"DROP INDEX {index['name']}"
                    ))
                    
        except Exception as e:
            logger.error(f"Error analyzing indexes for table {table_name}: {e}")
            
        return recommendations
    
    async def _analyze_query_patterns(self, table_name: str) -> List[Dict[str, Any]]:
        """Analyze common query patterns for a table"""
        # This would typically analyze query logs or use query statistics
        # For now, we'll return common patterns based on model analysis
        
        patterns = []
        
        # Common WHERE clause patterns based on table structure
        if table_name == "entities":
            patterns.extend([
                {"columns": ["entity_type", "status"], "frequency": 150},
                {"columns": ["label"], "frequency": 100},
                {"columns": ["created_at"], "frequency": 80},
                {"columns": ["entity_type", "created_at"], "frequency": 60}
            ])
        elif table_name == "connections":
            patterns.extend([
                {"columns": ["source_id", "target_id"], "frequency": 200},
                {"columns": ["relationship_type"], "frequency": 120},
                {"columns": ["source_id", "relationship_type"], "frequency": 90}
            ])
        elif table_name == "events":
            patterns.extend([
                {"columns": ["entity_id", "start_date"], "frequency": 180},
                {"columns": ["event_type", "start_date"], "frequency": 100},
                {"columns": ["start_date"], "frequency": 80}
            ])
        elif table_name == "locations":
            patterns.extend([
                {"columns": ["entity_id", "location_type"], "frequency": 100},
                {"columns": ["latitude", "longitude"], "frequency": 150},
                {"columns": ["city", "state"], "frequency": 70}
            ])
            
        return patterns
    
    def _has_index_on_columns(self, indexes: List[Dict], columns: List[str]) -> bool:
        """Check if an index exists on specified columns"""
        for index in indexes:
            if set(index['column_names']) == set(columns):
                return True
        return False
    
    def _is_index_used(self, table_name: str, index_name: str) -> bool:
        """Check if an index is being used (simplified implementation)"""
        # In a real implementation, this would check query execution plans
        # and database statistics to determine index usage
        return True  # Assume indexes are used for now
    
    def _generate_index_statement(self, table_name: str, columns: List[str], index_type: str) -> str:
        """Generate CREATE INDEX statement"""
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        columns_str = ", ".join(columns)
        
        if self.dialect_name == "postgresql":
            return f"CREATE INDEX CONCURRENTLY {index_name} ON {table_name} ({columns_str});"
        else:
            return f"CREATE INDEX {index_name} ON {table_name} ({columns_str});"


class QueryOptimizer:
    """Advanced query optimization and performance analysis"""
    
    def __init__(self, engine: Engine):
        self.engine = engine
        self.query_cache = QueryCache()
        self.query_analyses: Dict[str, QueryAnalysis] = {}
        self.slow_query_threshold = 1000  # milliseconds
        
    async def execute_optimized_query(
        self, 
        session: AsyncSession,
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], QueryAnalysis]:
        """Execute query with optimization and performance tracking"""
        params = params or {}
        cache_key = self.query_cache.get_cache_key(query, params)
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        
        # Check cache first
        cached_result = self.query_cache.get(cache_key)
        if cached_result:
            analysis = self.query_analyses.get(query_hash, QueryAnalysis(
                query_hash=query_hash, 
                original_query=query
            ))
            analysis.cache_hit_ratio = min(1.0, analysis.cache_hit_ratio + 0.1)
            return cached_result, analysis
        
        # Execute query with performance tracking
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            result = await session.execute(text(query), params)
            rows = [dict(row._mapping) for row in result.fetchall()]
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            execution_time = (end_time - start_time) * 1000  # milliseconds
            memory_delta = end_memory - start_memory
            
            # Update query analysis
            analysis = self.query_analyses.get(query_hash, QueryAnalysis(
                query_hash=query_hash,
                original_query=query
            ))
            
            analysis.execution_count += 1
            analysis.total_execution_time += execution_time
            analysis.avg_execution_time = analysis.total_execution_time / analysis.execution_count
            analysis.min_execution_time = min(analysis.min_execution_time, execution_time)
            analysis.max_execution_time = max(analysis.max_execution_time, execution_time)
            analysis.memory_usage_mb = max(analysis.memory_usage_mb, memory_delta)
            analysis.row_count = len(rows)
            analysis.last_executed = datetime.utcnow()
            analysis.is_slow_query = execution_time > self.slow_query_threshold
            
            # Generate optimization suggestions
            if analysis.is_slow_query:
                analysis.optimization_suggestions = await self._generate_optimization_suggestions(
                    query, execution_time, len(rows)
                )
            
            self.query_analyses[query_hash] = analysis
            
            # Cache result if it's cacheable
            if self._is_cacheable_query(query):
                ttl = self._calculate_cache_ttl(query, len(rows))
                self.query_cache.set(cache_key, rows, ttl)
            
            return rows, analysis
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    async def _generate_optimization_suggestions(
        self, 
        query: str, 
        execution_time: float, 
        row_count: int
    ) -> List[str]:
        """Generate optimization suggestions for slow queries"""
        suggestions = []
        
        query_lower = query.lower()
        
        # Check for missing WHERE clauses
        if "where" not in query_lower and row_count > 1000:
            suggestions.append("Consider adding WHERE clause to limit result set")
        
        # Check for missing indexes
        if "join" in query_lower and execution_time > 2000:
            suggestions.append("Verify indexes exist on JOIN columns")
        
        # Check for SELECT *
        if "select *" in query_lower:
            suggestions.append("Avoid SELECT *, specify only needed columns")
        
        # Check for ORDER BY without LIMIT
        if "order by" in query_lower and "limit" not in query_lower and row_count > 100:
            suggestions.append("Consider adding LIMIT to ORDER BY queries")
        
        # Check for N+1 query patterns
        if execution_time < 100 and query_lower.count("where") > 0:
            suggestions.append("Check for N+1 query patterns, consider batch loading")
        
        return suggestions
    
    def _is_cacheable_query(self, query: str) -> bool:
        """Determine if query results should be cached"""
        query_lower = query.lower()
        
        # Don't cache writes
        if any(keyword in query_lower for keyword in ["insert", "update", "delete", "create", "drop", "alter"]):
            return False
        
        # Don't cache queries with current timestamp functions
        if any(func in query_lower for func in ["now()", "current_timestamp", "getdate()"]):
            return False
        
        return True
    
    def _calculate_cache_ttl(self, query: str, row_count: int) -> int:
        """Calculate appropriate cache TTL based on query characteristics"""
        base_ttl = 3600  # 1 hour
        
        query_lower = query.lower()
        
        # Shorter TTL for frequently changing data
        if "events" in query_lower or "logs" in query_lower:
            base_ttl = 300  # 5 minutes
        
        # Longer TTL for reference data
        if "entities" in query_lower and "where" in query_lower:
            base_ttl = 7200  # 2 hours
        
        # Adjust based on result size
        if row_count < 100:
            base_ttl *= 2
        elif row_count > 10000:
            base_ttl //= 2
        
        return base_ttl
    
    def get_query_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive query performance report"""
        total_queries = len(self.query_analyses)
        if total_queries == 0:
            return {"message": "No query data available"}
        
        slow_queries = [a for a in self.query_analyses.values() if a.is_slow_query]
        avg_execution_times = [a.avg_execution_time for a in self.query_analyses.values()]
        
        return {
            "total_queries_analyzed": total_queries,
            "slow_query_count": len(slow_queries),
            "slow_query_percentage": (len(slow_queries) / total_queries) * 100,
            "avg_execution_time_ms": statistics.mean(avg_execution_times),
            "median_execution_time_ms": statistics.median(avg_execution_times),
            "p95_execution_time_ms": statistics.quantiles(avg_execution_times, n=20)[18] if len(avg_execution_times) > 20 else max(avg_execution_times),
            "cache_stats": self.query_cache.get_stats(),
            "top_slow_queries": sorted(slow_queries, key=lambda x: x.avg_execution_time, reverse=True)[:10],
            "most_frequent_queries": sorted(
                self.query_analyses.values(), 
                key=lambda x: x.execution_count, 
                reverse=True
            )[:10]
        }


class DatabaseOptimizationService:
    """Main database optimization service coordinator"""
    
    def __init__(self):
        self.query_optimizer = QueryOptimizer(async_engine.sync_engine)
        self.index_analyzer = IndexAnalyzer(async_engine.sync_engine)
        self.optimization_history: List[Dict[str, Any]] = []
        
    async def get_database_health(self) -> DatabaseHealth:
        """Get comprehensive database health metrics"""
        health = DatabaseHealth()
        
        try:
            # Connection pool metrics
            pool = async_engine.pool
            health.connection_pool_size = pool.size()
            health.connection_pool_active = pool.checked_in()
            health.connection_pool_overflow = pool.overflow()
            
            # Query performance metrics
            performance_report = self.query_optimizer.get_query_performance_report()
            if "avg_execution_time_ms" in performance_report:
                health.avg_query_time_ms = performance_report["avg_execution_time_ms"]
                health.slow_query_count = performance_report["slow_query_count"]
                health.total_queries = performance_report["total_queries_analyzed"]
            
            # Cache metrics
            cache_stats = self.query_optimizer.query_cache.get_stats()
            health.cache_hit_ratio = cache_stats["hit_ratio"]
            
            # Database size (approximate)
            async with get_async_session() as session:
                try:
                    if async_engine.dialect.name == "postgresql":
                        result = await session.execute(text(
                            "SELECT pg_size_pretty(pg_database_size(current_database()))"
                        ))
                        size_str = result.scalar()
                        # Parse size string (e.g., "15 MB" -> 15.0)
                        if size_str:
                            size_parts = size_str.split()
                            if len(size_parts) >= 2:
                                health.database_size_mb = float(size_parts[0])
                                if "GB" in size_str.upper():
                                    health.database_size_mb *= 1024
                    else:
                        # For SQLite, get file size
                        import os
                        if os.path.exists("data.db"):
                            health.database_size_mb = os.path.getsize("data.db") / 1024 / 1024
                except Exception:
                    pass  # Size calculation failed, continue with other metrics
            
            # Generate recommendations
            health.recommendations = await self._generate_health_recommendations(health)
            
        except Exception as e:
            logger.error(f"Error calculating database health: {e}")
            health.recommendations.append(f"Health check failed: {e}")
        
        return health
    
    async def analyze_and_optimize_indexes(self) -> Dict[str, Any]:
        """Analyze all tables and provide index optimization recommendations"""
        all_recommendations = []
        tables_analyzed = 0
        
        try:
            # Get all table names from our models
            table_names = [
                "entities", "connections", "events", "locations", 
                "data_sources", "search_queries"
            ]
            
            for table_name in table_names:
                try:
                    recommendations = await self.index_analyzer.analyze_table_indexes(table_name)
                    all_recommendations.extend(recommendations)
                    tables_analyzed += 1
                except Exception as e:
                    logger.error(f"Error analyzing table {table_name}: {e}")
            
            # Prioritize recommendations
            high_priority = [r for r in all_recommendations if r.priority == "high"]
            medium_priority = [r for r in all_recommendations if r.priority == "medium"]
            low_priority = [r for r in all_recommendations if r.priority == "low"]
            
            return {
                "tables_analyzed": tables_analyzed,
                "total_recommendations": len(all_recommendations),
                "high_priority_count": len(high_priority),
                "medium_priority_count": len(medium_priority),
                "low_priority_count": len(low_priority),
                "recommendations": {
                    "high_priority": high_priority,
                    "medium_priority": medium_priority,
                    "low_priority": low_priority
                },
                "optimization_script": self._generate_optimization_script(all_recommendations)
            }
            
        except Exception as e:
            logger.error(f"Error in index analysis: {e}")
            return {"error": str(e)}
    
    async def optimize_query_cache(self) -> Dict[str, Any]:
        """Optimize query cache settings and clean up"""
        stats_before = self.query_optimizer.query_cache.get_stats()
        
        # Clear expired entries
        expired_count = 0
        current_time = datetime.utcnow()
        cache = self.query_optimizer.query_cache.cache
        
        expired_keys = []
        for key, (result, expires_at, access_count) in cache.items():
            if current_time >= expires_at:
                expired_keys.append(key)
        
        for key in expired_keys:
            del cache[key]
            expired_count += 1
        
        stats_after = self.query_optimizer.query_cache.get_stats()
        
        return {
            "expired_entries_removed": expired_count,
            "cache_size_before": stats_before["cache_size"],
            "cache_size_after": stats_after["cache_size"],
            "hit_ratio": stats_after["hit_ratio"],
            "total_requests": stats_after["total_requests"]
        }
    
    async def _generate_health_recommendations(self, health: DatabaseHealth) -> List[str]:
        """Generate health-based optimization recommendations"""
        recommendations = []
        
        # Connection pool recommendations
        pool_utilization = health.connection_pool_active / max(health.connection_pool_size, 1)
        if pool_utilization > 0.8:
            recommendations.append("High connection pool utilization detected. Consider increasing pool size.")
        
        # Query performance recommendations
        if health.avg_query_time_ms > 500:
            recommendations.append("Average query time is high. Review slow queries and consider optimizations.")
        
        if health.slow_query_count > health.total_queries * 0.1:  # More than 10% slow queries
            recommendations.append("High percentage of slow queries detected. Analyze query patterns and indexes.")
        
        # Cache recommendations
        if health.cache_hit_ratio < 0.7:
            recommendations.append("Low cache hit ratio. Review cache configuration and query patterns.")
        
        # Database size recommendations
        if health.database_size_mb > 1000:  # 1GB
            recommendations.append("Large database size detected. Consider archiving old data or partitioning.")
        
        return recommendations
    
    def _generate_optimization_script(self, recommendations: List[IndexRecommendation]) -> str:
        """Generate SQL script to implement index recommendations"""
        script_lines = [
            "-- Database Optimization Script",
            "-- Generated by Business Intelligence Scraper Database Optimizer",
            f"-- Generated at: {datetime.utcnow().isoformat()}",
            "",
            "-- High Priority Indexes",
        ]
        
        high_priority = [r for r in recommendations if r.priority == "high"]
        for rec in high_priority:
            script_lines.extend([
                f"-- {rec.impact_reason}",
                rec.create_statement,
                ""
            ])
        
        script_lines.extend([
            "-- Medium Priority Indexes",
        ])
        
        medium_priority = [r for r in recommendations if r.priority == "medium"]
        for rec in medium_priority:
            script_lines.extend([
                f"-- {rec.impact_reason}",
                rec.create_statement,
                ""
            ])
        
        return "\n".join(script_lines)


# Global database optimization service
database_optimization_service = DatabaseOptimizationService()


# Convenience functions for external use
async def get_database_health() -> DatabaseHealth:
    """Get current database health metrics"""
    return await database_optimization_service.get_database_health()


async def optimize_database_indexes() -> Dict[str, Any]:
    """Analyze and optimize database indexes"""
    return await database_optimization_service.analyze_and_optimize_indexes()


async def get_query_performance_report() -> Dict[str, Any]:
    """Get comprehensive query performance report"""
    return database_optimization_service.query_optimizer.get_query_performance_report()


async def execute_optimized_query(
    session: AsyncSession, 
    query: str, 
    params: Optional[Dict[str, Any]] = None
) -> Tuple[List[Dict[str, Any]], QueryAnalysis]:
    """Execute query with optimization and performance tracking"""
    return await database_optimization_service.query_optimizer.execute_optimized_query(
        session, query, params
    )
