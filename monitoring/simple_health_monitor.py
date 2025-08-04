#!/usr/bin/env python3
"""
Enhanced Health Monitoring Integration for Backend Server
Simple integration that works with existing infrastructure
"""

import asyncio
import logging
import time
import psutil
import sqlite3
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class SimpleHealthMonitor:
    """Lightweight health monitoring for the backend server"""
    
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = None
        
    def record_request(self, endpoint: str, duration: float, status_code: int):
        """Record a request for monitoring"""
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get basic system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used // (1024 * 1024),
                "memory_total_mb": memory.total // (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used // (1024 ** 3),
                "disk_total_gb": disk.total // (1024 ** 3)
            }
        except Exception as e:
            logging.warning(f"Could not get system metrics: {e}")
            return {"error": "System metrics unavailable"}
    
    def get_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and basic stats"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Test basic connectivity
            cursor.execute("SELECT 1")
            
            # Get table counts
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            table_stats = {}
            for (table_name,) in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    table_stats[table_name] = count
                except Exception:
                    table_stats[table_name] = "Error"
            
            conn.close()
            
            return {
                "status": "healthy",
                "tables": len(tables),
                "table_stats": table_stats,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        uptime = datetime.now() - self.start_time
        error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
        
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0],  # Remove microseconds
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "requests_per_minute": round(self.request_count / max(uptime.total_seconds() / 60, 1), 2)
        }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        self.last_health_check = datetime.now()
        
        health_data = {
            "timestamp": self.last_health_check.isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # System health
        try:
            health_data["checks"]["system"] = self.get_system_metrics()
        except Exception as e:
            health_data["checks"]["system"] = {"status": "error", "message": str(e)}
            health_data["status"] = "degraded"
        
        # Database health
        try:
            health_data["checks"]["database"] = self.get_database_health()
            if health_data["checks"]["database"]["status"] != "healthy":
                health_data["status"] = "unhealthy"
        except Exception as e:
            health_data["checks"]["database"] = {"status": "error", "message": str(e)}
            health_data["status"] = "unhealthy"
        
        # API metrics
        try:
            health_data["checks"]["api"] = self.get_api_metrics()
        except Exception as e:
            health_data["checks"]["api"] = {"status": "error", "message": str(e)}
            health_data["status"] = "degraded"
        
        return health_data

class SimplePerformanceMiddleware:
    """Lightweight performance monitoring middleware"""
    
    def __init__(self, health_monitor: SimpleHealthMonitor):
        self.health_monitor = health_monitor
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        endpoint = f"{request.method} {request.url.path}"
        self.health_monitor.record_request(endpoint, duration, response.status_code)
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = str(time.time())
        
        return response

# Global instances
health_monitor = None

def init_simple_monitoring(db_path: str = "data.db") -> SimpleHealthMonitor:
    """Initialize simple health monitoring"""
    global health_monitor
    health_monitor = SimpleHealthMonitor(db_path)
    logging.info("✅ Simple health monitoring initialized")
    return health_monitor

def get_health_monitor() -> Optional[SimpleHealthMonitor]:
    """Get the global health monitor instance"""
    return health_monitor

# Background monitoring task
async def background_health_monitoring():
    """Background task for periodic health monitoring"""
    if not health_monitor:
        return
    
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            health_data = await health_monitor.comprehensive_health_check()
            
            # Log critical issues
            if health_data["status"] == "unhealthy":
                logging.error(f"🚨 System health critical: {health_data}")
            elif health_data["status"] == "degraded":
                logging.warning(f"⚠️ System health degraded: {health_data}")
            else:
                logging.debug(f"✅ System health good")
                
        except Exception as e:
            logging.error(f"Health monitoring error: {e}")
            await asyncio.sleep(10)  # Shorter retry on error
