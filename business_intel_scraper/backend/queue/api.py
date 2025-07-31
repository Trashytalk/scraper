"""
Queue Management API Endpoints

Provides REST API for managing distributed crawling queues:
- Frontier queue management
- Parsing queue management  
- Retry and dead letter queue monitoring
- System statistics and health
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..auth.middleware import require_token
from .distributed_crawler import (
    DistributedCrawlSystem, 
    CrawlURL, 
    ParseTask,
    QueueBackend,
    URLStatus
)

router = APIRouter(prefix="/queue", tags=["Queue Management"])

# Global queue system instance
queue_system: Optional[DistributedCrawlSystem] = None


class QueueConfigRequest(BaseModel):
    """Queue system configuration"""
    queue_backend: str = Field(..., description="Queue backend: redis, kafka, sqs, or memory")
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    database_url: Optional[str] = Field(default=None, description="Database URL for crawl tracking")
    num_crawl_workers: int = Field(default=5, description="Number of crawl workers")
    num_parse_workers: int = Field(default=3, description="Number of parse workers")
    storage_config: Optional[Dict[str, Any]] = Field(default=None, description="Storage configuration")


class SeedURLRequest(BaseModel):
    """Request to add seed URLs"""
    urls: List[str] = Field(..., description="List of seed URLs to crawl")
    job_id: str = Field(..., description="Job ID for tracking")
    priority: int = Field(default=5, description="Priority level (1-10, higher = more priority)")


class CrawlURLResponse(BaseModel):
    """Crawl URL response model"""
    url: str
    source_url: Optional[str]
    depth: int
    priority: int
    created_at: str
    scheduled_at: str
    retry_count: int
    max_retries: int
    domain: str
    job_id: Optional[str]
    metadata: Dict[str, Any]


class ParseTaskResponse(BaseModel):
    """Parse task response model"""
    task_id: str
    url: str
    raw_id: str
    storage_location: str
    content_type: str
    priority: int
    created_at: str
    retry_count: int
    max_retries: int
    requires_ocr: bool
    metadata: Dict[str, Any]


class QueueStatsResponse(BaseModel):
    """Queue statistics response"""
    system_status: Dict[str, Any]
    queue_stats: Dict[str, int]
    crawl_metrics: Dict[str, Any]
    parse_metrics: Dict[str, Any]
    timestamp: str


class WorkerStatsResponse(BaseModel):
    """Worker statistics response"""
    worker_id: str
    worker_type: str
    is_active: bool
    metrics: Dict[str, Any]


# System Management Endpoints

@router.post("/system/initialize", dependencies=[Depends(require_token)])
async def initialize_queue_system(config: QueueConfigRequest) -> Dict[str, Any]:
    """Initialize the distributed queue system"""
    global queue_system
    
    try:
        # Validate queue backend
        try:
            backend = QueueBackend(config.queue_backend)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid queue backend: {config.queue_backend}. Must be one of: redis, kafka, sqs, memory"
            )
        
        # Stop existing system if running
        if queue_system and queue_system.is_running:
            await queue_system.stop()
        
        # Initialize new system
        queue_system = DistributedCrawlSystem(
            queue_backend=backend,
            redis_url=config.redis_url,
            database_url=config.database_url,
            storage_config=config.storage_config,
            num_crawl_workers=config.num_crawl_workers,
            num_parse_workers=config.num_parse_workers
        )
        
        # Start the system
        await queue_system.start()
        
        return {
            "status": "success",
            "message": "Queue system initialized successfully",
            "config": {
                "queue_backend": config.queue_backend,
                "num_crawl_workers": config.num_crawl_workers,
                "num_parse_workers": config.num_parse_workers,
                "is_running": queue_system.is_running
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize queue system: {str(e)}")


@router.post("/system/start", dependencies=[Depends(require_token)])
async def start_queue_system() -> Dict[str, Any]:
    """Start the queue system"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized. Call /queue/system/initialize first")
    
    try:
        if queue_system.is_running:
            return {
                "status": "info",
                "message": "Queue system is already running"
            }
        
        await queue_system.start()
        
        return {
            "status": "success",
            "message": "Queue system started successfully",
            "is_running": queue_system.is_running
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start queue system: {str(e)}")


@router.post("/system/stop", dependencies=[Depends(require_token)])
async def stop_queue_system() -> Dict[str, Any]:
    """Stop the queue system"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        if not queue_system.is_running:
            return {
                "status": "info",
                "message": "Queue system is not running"
            }
        
        await queue_system.stop()
        
        return {
            "status": "success",
            "message": "Queue system stopped successfully",
            "is_running": queue_system.is_running
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop queue system: {str(e)}")


@router.get("/system/status")
async def get_system_status() -> QueueStatsResponse:
    """Get comprehensive system status and statistics"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        stats = await queue_system.get_system_stats()
        
        return QueueStatsResponse(
            system_status=stats["system_status"],
            queue_stats=stats["queue_stats"],
            crawl_metrics=stats["crawl_metrics"],
            parse_metrics=stats["parse_metrics"],
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


# URL Management Endpoints

@router.post("/urls/seed", dependencies=[Depends(require_token)])
async def add_seed_urls(request: SeedURLRequest) -> Dict[str, Any]:
    """Add seed URLs to the frontier queue"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    if not queue_system.is_running:
        raise HTTPException(status_code=400, detail="Queue system is not running")
    
    try:
        # Validate URLs
        if not request.urls:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        if len(request.urls) > 1000:
            raise HTTPException(status_code=400, detail="Too many URLs. Maximum 1000 URLs per request")
        
        # Validate priority
        if not 1 <= request.priority <= 10:
            raise HTTPException(status_code=400, detail="Priority must be between 1 and 10")
        
        # Add URLs to queue
        added_count = await queue_system.add_seed_urls(
            urls=request.urls,
            job_id=request.job_id,
            priority=request.priority
        )
        
        return {
            "status": "success",
            "message": f"Added {added_count} seed URLs to frontier queue",
            "urls_requested": len(request.urls),
            "urls_added": added_count,
            "job_id": request.job_id,
            "priority": request.priority
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add seed URLs: {str(e)}")


@router.get("/urls/frontier")
async def get_frontier_queue_status(
    limit: int = Query(default=100, description="Maximum number of URLs to return"),
    priority_only: bool = Query(default=False, description="Only return high-priority URLs")
) -> Dict[str, Any]:
    """Get frontier queue status and preview URLs"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        queue_stats = await queue_system.queue_manager.get_queue_stats()
        
        # For now, just return stats (getting actual URLs would require queue inspection)
        return {
            "status": "success",
            "queue_stats": {
                "frontier_queue_size": queue_stats.get("frontier_queue_size", 0),
                "frontier_priority_queue_size": queue_stats.get("frontier_priority_queue_size", 0),
                "total_frontier_size": queue_stats.get("total_frontier_size", 0)
            },
            "message": "Frontier queue status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get frontier queue status: {str(e)}")


@router.get("/tasks/parsing")
async def get_parsing_queue_status(
    limit: int = Query(default=100, description="Maximum number of tasks to return")
) -> Dict[str, Any]:
    """Get parsing queue status and preview tasks"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        queue_stats = await queue_system.queue_manager.get_queue_stats()
        
        return {
            "status": "success",
            "queue_stats": {
                "parse_queue_size": queue_stats.get("parse_queue_size", 0),
                "parse_priority_queue_size": queue_stats.get("parse_priority_queue_size", 0),
                "total_parse_size": queue_stats.get("total_parse_size", 0)
            },
            "message": "Parsing queue status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get parsing queue status: {str(e)}")


# Retry and Dead Letter Queue Management

@router.get("/urls/retry")
async def get_retry_queue_status() -> Dict[str, Any]:
    """Get retry queue status"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        queue_stats = await queue_system.queue_manager.get_queue_stats()
        
        return {
            "status": "success",
            "retry_queue_size": queue_stats.get("retry_queue_size", 0),
            "urls_retried": queue_stats.get("urls_retried", 0),
            "message": "Retry queue status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get retry queue status: {str(e)}")


@router.get("/urls/dead")
async def get_dead_queue_status() -> Dict[str, Any]:
    """Get dead letter queue status"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        queue_stats = await queue_system.queue_manager.get_queue_stats()
        
        return {
            "status": "success",
            "dead_queue_size": queue_stats.get("dead_queue_size", 0),
            "urls_dead": queue_stats.get("urls_dead", 0),
            "message": "Dead letter queue status retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dead queue status: {str(e)}")


@router.post("/urls/retry/process", dependencies=[Depends(require_token)])
async def process_retry_queue() -> Dict[str, Any]:
    """Process retry queue to requeue URLs ready for retry"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        if hasattr(queue_system.queue_manager, 'process_retry_queue'):
            processed = await queue_system.queue_manager.process_retry_queue()
            
            return {
                "status": "success",
                "urls_requeued": processed,
                "message": f"Processed retry queue, requeued {processed} URLs"
            }
        else:
            return {
                "status": "info",
                "message": "Retry queue processing not supported by current queue backend"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process retry queue: {str(e)}")


# Worker Management

@router.get("/workers/status")
async def get_worker_status() -> Dict[str, Any]:
    """Get status of all workers"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        crawl_workers = []
        for worker in queue_system.crawl_workers:
            crawl_workers.append({
                "worker_id": worker.worker_id,
                "worker_type": "crawl",
                "is_active": worker.is_running,
                "active_tasks": len(worker.active_tasks),
                "max_concurrent": worker.max_concurrent,
                "metrics": worker.metrics
            })
        
        parse_workers = []
        for worker in queue_system.parse_workers:
            parse_workers.append({
                "worker_id": worker.worker_id,
                "worker_type": "parse",
                "is_active": worker.is_running,
                "active_tasks": len(worker.active_tasks),
                "max_concurrent": worker.max_concurrent,
                "metrics": worker.metrics
            })
        
        return {
            "status": "success",
            "crawl_workers": crawl_workers,
            "parse_workers": parse_workers,
            "total_workers": len(crawl_workers) + len(parse_workers),
            "active_workers": sum(1 for w in crawl_workers + parse_workers if w["is_active"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")


# Health and Monitoring

@router.get("/health")
async def get_queue_health() -> Dict[str, Any]:
    """Get queue system health status"""
    global queue_system
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    try:
        if not queue_system:
            health_status["status"] = "unhealthy"
            health_status["components"]["queue_system"] = {
                "status": "down",
                "message": "Queue system not initialized"
            }
            return health_status
        
        # Check system status
        if queue_system.is_running:
            health_status["components"]["queue_system"] = {
                "status": "up",
                "message": "Queue system is running"
            }
        else:
            health_status["status"] = "degraded"
            health_status["components"]["queue_system"] = {
                "status": "down",
                "message": "Queue system is not running"
            }
        
        # Check queue backend connectivity
        try:
            if hasattr(queue_system.queue_manager, 'redis_client'):
                # Test Redis connection
                await queue_system.queue_manager.redis_client.ping()
                health_status["components"]["queue_backend"] = {
                    "status": "up",
                    "type": "redis",
                    "message": "Redis connection healthy"
                }
            else:
                health_status["components"]["queue_backend"] = {
                    "status": "up",
                    "type": "memory",
                    "message": "In-memory queue active"
                }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["queue_backend"] = {
                "status": "down",
                "message": f"Queue backend connection failed: {str(e)}"
            }
        
        # Check worker status
        if queue_system.is_running:
            active_crawl_workers = sum(1 for w in queue_system.crawl_workers if w.is_running)
            active_parse_workers = sum(1 for w in queue_system.parse_workers if w.is_running)
            
            health_status["components"]["workers"] = {
                "status": "up" if active_crawl_workers > 0 and active_parse_workers > 0 else "degraded",
                "crawl_workers": {
                    "active": active_crawl_workers,
                    "total": len(queue_system.crawl_workers)
                },
                "parse_workers": {
                    "active": active_parse_workers,
                    "total": len(queue_system.parse_workers)
                }
            }
        
        return health_status
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        return health_status


# Advanced Queue Operations

@router.post("/urls/bulk-add", dependencies=[Depends(require_token)])
async def bulk_add_urls(
    job_id: str,
    priority: int = 5,
    urls: List[str] = []
) -> Dict[str, Any]:
    """Bulk add URLs with batching for large datasets"""
    global queue_system
    
    if not queue_system or not queue_system.is_running:
        raise HTTPException(status_code=400, detail="Queue system not running")
    
    try:
        if len(urls) > 10000:
            raise HTTPException(status_code=400, detail="Maximum 10,000 URLs per bulk operation")
        
        # Process in batches of 100
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            added = await queue_system.add_seed_urls(batch, job_id, priority)
            total_added += added
        
        return {
            "status": "success",
            "message": f"Bulk operation completed",
            "urls_requested": len(urls),
            "urls_added": total_added,
            "job_id": job_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk add operation failed: {str(e)}")


@router.get("/metrics/summary")
async def get_metrics_summary() -> Dict[str, Any]:
    """Get summarized metrics across all components"""
    global queue_system
    
    if not queue_system:
        raise HTTPException(status_code=400, detail="Queue system not initialized")
    
    try:
        stats = await queue_system.get_system_stats()
        
        # Calculate derived metrics
        crawl_metrics = stats["crawl_metrics"]
        parse_metrics = stats["parse_metrics"]
        queue_stats = stats["queue_stats"]
        
        total_crawled = crawl_metrics.get("urls_crawled", 0)
        total_failed = crawl_metrics.get("urls_failed", 0)
        success_rate = (total_crawled / (total_crawled + total_failed) * 100) if (total_crawled + total_failed) > 0 else 0
        
        return {
            "status": "success",
            "summary": {
                "system_uptime": queue_system.is_running,
                "total_urls_processed": total_crawled,
                "success_rate_percent": round(success_rate, 2),
                "active_queues": {
                    "frontier": queue_stats.get("total_frontier_size", 0),
                    "parsing": queue_stats.get("total_parse_size", 0),
                    "retry": queue_stats.get("retry_queue_size", 0),
                    "dead": queue_stats.get("dead_queue_size", 0)
                },
                "throughput": {
                    "urls_per_worker": round(total_crawled / len(queue_system.crawl_workers), 2) if queue_system.crawl_workers else 0,
                    "avg_response_time_ms": round(crawl_metrics.get("avg_response_time", 0) * 1000, 2),
                    "total_bytes_downloaded": crawl_metrics.get("bytes_downloaded", 0)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")
