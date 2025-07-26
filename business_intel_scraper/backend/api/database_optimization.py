"""
Database Optimization API Endpoints
Provides REST API for database performance monitoring and optimization
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

from ..db.optimization import (
    get_database_health,
    optimize_database_indexes, 
    get_query_performance_report,
    database_optimization_service
)
from ..database.config import get_database_health as get_db_health_config
from ..dependencies import require_token


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/database", tags=["Database Optimization"])


class OptimizationRequest(BaseModel):
    """Request model for database optimization"""
    analyze_indexes: bool = True
    optimize_cache: bool = True
    apply_recommendations: bool = False
    tables: Optional[List[str]] = None


class IndexRecommendationResponse(BaseModel):
    """Response model for index recommendations"""
    table_name: str
    columns: List[str]
    index_type: str
    priority: str
    estimated_benefit: float
    impact_reason: str
    create_statement: str


class DatabaseHealthResponse(BaseModel):
    """Response model for database health"""
    status: str
    connection_pool_active: int
    connection_pool_size: int
    avg_query_time_ms: float
    slow_query_count: int
    cache_hit_ratio: float
    total_queries: int
    database_size_mb: float
    recommendations: List[str]
    last_checked: datetime


@router.get("/health", dependencies=[Depends(require_token)])
async def get_database_health_endpoint() -> Dict[str, Any]:
    """Get comprehensive database health metrics"""
    try:
        # Get health from optimization service
        optimization_health = await get_database_health()
        
        # Get health from database config
        config_health = await get_db_health_config()
        
        # Combine both health reports
        combined_health = {
            "optimization_metrics": {
                "connection_pool_active": optimization_health.connection_pool_active,
                "connection_pool_size": optimization_health.connection_pool_size,
                "avg_query_time_ms": optimization_health.avg_query_time_ms,
                "slow_query_count": optimization_health.slow_query_count,
                "cache_hit_ratio": optimization_health.cache_hit_ratio,
                "total_queries": optimization_health.total_queries,
                "database_size_mb": optimization_health.database_size_mb,
                "recommendations": optimization_health.recommendations
            },
            "connection_status": config_health,
            "overall_status": "healthy" if config_health["status"] == "healthy" else "degraded",
            "last_checked": datetime.utcnow().isoformat()
        }
        
        return {"status": "success", "data": combined_health}
        
    except Exception as e:
        logger.error(f"Error getting database health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/performance/report", dependencies=[Depends(require_token)])
async def get_performance_report() -> Dict[str, Any]:
    """Get comprehensive query performance report"""
    try:
        report = await get_query_performance_report()
        
        return {
            "status": "success",
            "data": report,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating performance report: {e}")
        raise HTTPException(status_code=500, detail=f"Performance report failed: {str(e)}")


@router.get("/indexes/analyze", dependencies=[Depends(require_token)])
async def analyze_indexes() -> Dict[str, Any]:
    """Analyze database indexes and provide optimization recommendations"""
    try:
        analysis_result = await optimize_database_indexes()
        
        return {
            "status": "success",
            "data": analysis_result,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing indexes: {e}")
        raise HTTPException(status_code=500, detail=f"Index analysis failed: {str(e)}")


@router.post("/optimize", dependencies=[Depends(require_token)])
async def optimize_database(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """Run comprehensive database optimization"""
    try:
        optimization_results = {}
        
        if request.analyze_indexes:
            logger.info("Starting index analysis...")
            index_analysis = await optimize_database_indexes()
            optimization_results["index_analysis"] = index_analysis
            
        if request.optimize_cache:
            logger.info("Optimizing query cache...")
            cache_optimization = await database_optimization_service.optimize_query_cache()
            optimization_results["cache_optimization"] = cache_optimization
        
        # If apply_recommendations is True, schedule background application
        if request.apply_recommendations and "index_analysis" in optimization_results:
            background_tasks.add_task(
                _apply_index_recommendations,
                optimization_results["index_analysis"].get("recommendations", {}).get("high_priority", [])
            )
            optimization_results["recommendations_applied"] = "scheduled"
        
        return {
            "status": "success",
            "message": "Database optimization completed",
            "results": optimization_results,
            "optimized_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/cache/stats", dependencies=[Depends(require_token)])
async def get_cache_statistics() -> Dict[str, Any]:
    """Get query cache performance statistics"""
    try:
        cache_stats = database_optimization_service.query_optimizer.query_cache.get_stats()
        
        return {
            "status": "success",
            "data": cache_stats,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Cache stats failed: {str(e)}")


@router.post("/cache/clear", dependencies=[Depends(require_token)])
async def clear_query_cache(pattern: Optional[str] = None) -> Dict[str, Any]:
    """Clear query cache entries, optionally matching a pattern"""
    try:
        cache = database_optimization_service.query_optimizer.query_cache
        
        if pattern:
            cleared_count = cache.invalidate_pattern(pattern)
            message = f"Cleared {cleared_count} cache entries matching pattern '{pattern}'"
        else:
            cleared_count = len(cache.cache)
            cache.cache.clear()
            message = f"Cleared all {cleared_count} cache entries"
        
        return {
            "status": "success",
            "message": message,
            "entries_cleared": cleared_count,
            "cleared_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")


@router.get("/slow-queries", dependencies=[Depends(require_token)])
async def get_slow_queries(limit: int = 10) -> Dict[str, Any]:
    """Get list of slow queries with optimization suggestions"""
    try:
        performance_report = await get_query_performance_report()
        
        slow_queries = []
        if "top_slow_queries" in performance_report:
            slow_queries = performance_report["top_slow_queries"][:limit]
        
        return {
            "status": "success",
            "data": {
                "slow_queries": slow_queries,
                "total_slow_queries": len(slow_queries),
                "slow_query_threshold_ms": database_optimization_service.query_optimizer.slow_query_threshold
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        raise HTTPException(status_code=500, detail=f"Slow queries retrieval failed: {str(e)}")


@router.get("/optimization/history", dependencies=[Depends(require_token)])
async def get_optimization_history() -> Dict[str, Any]:
    """Get history of database optimizations"""
    try:
        history = database_optimization_service.optimization_history
        
        return {
            "status": "success",
            "data": {
                "optimization_count": len(history),
                "history": history[-20:]  # Last 20 optimizations
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting optimization history: {e}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")


@router.post("/maintenance/analyze", dependencies=[Depends(require_token)])
async def run_database_maintenance(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Run database maintenance tasks in the background"""
    try:
        # Schedule maintenance tasks
        background_tasks.add_task(_run_maintenance_tasks)
        
        return {
            "status": "success",
            "message": "Database maintenance scheduled",
            "scheduled_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling maintenance: {e}")
        raise HTTPException(status_code=500, detail=f"Maintenance scheduling failed: {str(e)}")


async def _apply_index_recommendations(recommendations: List[Dict[str, Any]]):
    """Apply high-priority index recommendations (background task)"""
    try:
        from ..database.config import AsyncSessionLocal
        
        applied_count = 0
        for rec in recommendations:
            try:
                async with AsyncSessionLocal() as session:
                    # Only apply CREATE INDEX statements, skip DROP statements for safety
                    if rec.get("create_statement", "").upper().startswith("CREATE INDEX"):
                        await session.execute(rec["create_statement"])
                        await session.commit()
                        applied_count += 1
                        logger.info(f"Applied index: {rec['create_statement']}")
                    
            except Exception as e:
                logger.error(f"Failed to apply index recommendation: {e}")
        
        # Record optimization in history
        optimization_record = {
            "type": "index_optimization",
            "applied_count": applied_count,
            "total_recommendations": len(recommendations),
            "timestamp": datetime.utcnow().isoformat()
        }
        database_optimization_service.optimization_history.append(optimization_record)
        
        logger.info(f"Applied {applied_count} index recommendations")
        
    except Exception as e:
        logger.error(f"Error applying index recommendations: {e}")


async def _run_maintenance_tasks():
    """Run database maintenance tasks (background task)"""
    try:
        from ..database.config import AsyncSessionLocal
        
        tasks_completed = []
        
        async with AsyncSessionLocal() as session:
            # Update table statistics
            try:
                await session.execute("ANALYZE")
                tasks_completed.append("table_statistics_updated")
            except Exception as e:
                logger.warning(f"Failed to update table statistics: {e}")
            
            # Vacuum for SQLite
            try:
                if "sqlite" in str(session.bind.url):
                    await session.execute("VACUUM")
                    tasks_completed.append("vacuum_completed")
            except Exception as e:
                logger.warning(f"Failed to vacuum database: {e}")
            
            await session.commit()
        
        # Record maintenance in history
        maintenance_record = {
            "type": "maintenance",
            "tasks_completed": tasks_completed,
            "timestamp": datetime.utcnow().isoformat()
        }
        database_optimization_service.optimization_history.append(maintenance_record)
        
        logger.info(f"Database maintenance completed: {tasks_completed}")
        
    except Exception as e:
        logger.error(f"Error running maintenance tasks: {e}")


# Helper function for testing database optimization
async def test_database_optimization():
    """Test database optimization functionality"""
    try:
        # Test health check
        health = await get_database_health()
        print(f"Database health: {health.total_queries} queries, {health.slow_query_count} slow")
        
        # Test index analysis
        index_analysis = await optimize_database_indexes()
        print(f"Index analysis: {index_analysis.get('total_recommendations', 0)} recommendations")
        
        # Test performance report
        performance = await get_query_performance_report()
        print(f"Performance report: {performance.get('total_queries_analyzed', 0)} queries analyzed")
        
        return True
        
    except Exception as e:
        logger.error(f"Database optimization test failed: {e}")
        return False
