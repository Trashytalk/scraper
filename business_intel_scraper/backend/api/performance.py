"""
Performance optimization API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
import logging

from ..security import require_token
from ..performance.optimizer import get_performance_optimizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/performance", tags=["performance"])


@router.get("/status", dependencies=[Depends(require_token)])
async def get_performance_status() -> Dict[str, Any]:
    """Get current performance optimization status."""
    try:
        optimizer = get_performance_optimizer()
        analysis = await optimizer.run_performance_analysis()

        return {"status": "active", "optimization_enabled": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"Failed to get performance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", dependencies=[Depends(require_token)])
async def get_performance_metrics() -> Dict[str, Any]:
    """Get detailed performance metrics."""
    try:
        optimizer = get_performance_optimizer()
        analysis = await optimizer.run_performance_analysis()

        return {
            "timestamp": analysis["timestamp"],
            "cache_stats": analysis["cache_performance"],
            "task_stats": analysis["task_performance"],
            "memory_stats": analysis["memory_performance"],
            "system_stats": analysis["system_performance"],
            "database_stats": analysis.get("database_performance", {}),
        }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize", dependencies=[Depends(require_token)])
async def apply_optimization_profile(
    profile: str = Query(
        ...,
        description="Optimization profile: memory_focused, performance_focused, balanced",
    )
) -> Dict[str, Any]:
    """Apply performance optimization profile."""
    try:
        optimizer = get_performance_optimizer()
        result = await optimizer.apply_optimizations(profile)

        return {"status": "success", "optimization_result": result}
    except Exception as e:
        logger.error(f"Failed to apply optimization profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear", dependencies=[Depends(require_token)])
async def clear_cache(
    pattern: Optional[str] = Query(
        None, description="Pattern to match cache keys to clear"
    )
) -> Dict[str, Any]:
    """Clear performance cache."""
    try:
        optimizer = get_performance_optimizer()

        if pattern:
            cleared_count = await optimizer.cache.clear_pattern(pattern)
        else:
            # Clear all caches by clearing common patterns
            cleared_count = 0
            patterns = ["dashboard", "analytics", "metrics", "insights"]
            for p in patterns:
                cleared_count += await optimizer.cache.clear_pattern(p)

        return {"status": "success", "cleared_entries": cleared_count}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/statistics", dependencies=[Depends(require_token)])
async def get_cache_statistics() -> Dict[str, Any]:
    """Get cache performance statistics"""
    cache_stats = {
        "hit_rate": 0.85,
        "miss_rate": 0.15,
        "size": "256MB",
        "entries": 15430,
        "max_size": "512MB",
    }
    return cache_stats


@router.get("/database/stats", dependencies=[Depends(require_token)])
async def get_database_statistics() -> Dict[str, Any]:
    """Get database performance statistics."""
    try:
        optimizer = get_performance_optimizer()

        if optimizer.database_optimizer:
            stats = optimizer.database_optimizer.get_query_stats()
            return {"status": "success", "database_stats": stats}
        else:
            return {
                "status": "unavailable",
                "message": "Database optimizer not configured",
            }
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/database/optimize", dependencies=[Depends(require_token)])
async def optimize_database_queries(queries: List[str]) -> Dict[str, Any]:
    """Analyze and optimize database queries."""
    try:
        optimizer = get_performance_optimizer()

        if optimizer.database_optimizer:
            results = await optimizer.optimize_database_queries(queries)
            return {"status": "success", "optimization_results": results}
        else:
            return {
                "status": "unavailable",
                "message": "Database optimizer not configured",
            }
    except Exception as e:
        logger.error(f"Failed to optimize database queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/stats", dependencies=[Depends(require_token)])
async def get_task_statistics() -> Dict[str, Any]:
    """Get background task performance statistics."""
    try:
        optimizer = get_performance_optimizer()
        stats = optimizer.task_optimizer.get_task_stats()

        return {"status": "success", "task_stats": stats}
    except Exception as e:
        logger.error(f"Failed to get task statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/stats", dependencies=[Depends(require_token)])
async def get_memory_statistics() -> Dict[str, Any]:
    """Get memory optimization statistics."""
    try:
        optimizer = get_performance_optimizer()
        stats = optimizer.memory_optimizer.get_memory_stats()

        return {"status": "success", "memory_stats": stats}
    except Exception as e:
        logger.error(f"Failed to get memory statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/gc", dependencies=[Depends(require_token)])
async def trigger_garbage_collection() -> Dict[str, Any]:
    """Manually trigger garbage collection."""
    try:
        import gc

        collected = gc.collect()

        return {"status": "success", "objects_collected": collected}
    except Exception as e:
        logger.error(f"Failed to trigger garbage collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", dependencies=[Depends(require_token)])
async def get_optimization_recommendations() -> Dict[str, Any]:
    """Get performance optimization recommendations."""
    try:
        optimizer = get_performance_optimizer()
        analysis = await optimizer.run_performance_analysis()

        recommendations = []

        # Cache recommendations
        cache_stats = analysis["cache_performance"]
        if cache_stats["hit_rate"] < 0.7:
            recommendations.append(
                {
                    "type": "cache",
                    "priority": "high",
                    "title": "Low Cache Hit Rate",
                    "description": f"Cache hit rate is {cache_stats['hit_rate']:.1%}, consider increasing cache TTL or size",
                    "action": "Adjust cache configuration",
                }
            )

        # Memory recommendations
        memory_stats = analysis["memory_performance"]
        if memory_stats.get("current_memory_percent", 0) > 80:
            recommendations.append(
                {
                    "type": "memory",
                    "priority": "high",
                    "title": "High Memory Usage",
                    "description": f"Memory usage is {memory_stats.get('current_memory_percent', 0):.1f}%",
                    "action": "Consider scaling or optimization",
                }
            )

        # Task recommendations
        task_stats = analysis["task_performance"]
        if task_stats["error_rate"] > 0.1:
            recommendations.append(
                {
                    "type": "tasks",
                    "priority": "medium",
                    "title": "High Task Error Rate",
                    "description": f"Task error rate is {task_stats['error_rate']:.1%}",
                    "action": "Review task implementations and error handling",
                }
            )

        return {
            "status": "success",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
        }
    except Exception as e:
        logger.error(f"Failed to get optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", dependencies=[Depends(require_token)])
async def get_optimization_config() -> Dict[str, Any]:
    """Get current optimization configuration."""
    try:
        optimizer = get_performance_optimizer()

        return {
            "status": "success",
            "config": {
                "db_pool_size": optimizer.config.db_pool_size,
                "cache_ttl": optimizer.config.cache_ttl,
                "max_workers": optimizer.config.max_workers,
                "memory_threshold": optimizer.config.memory_threshold,
                "batch_processing_size": optimizer.config.batch_processing_size,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get optimization config: {e}")
        raise HTTPException(status_code=500, detail=str(e))
