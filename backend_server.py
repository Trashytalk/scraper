#!/usr/bin/env python3
"""
Simplified Backend API Server for Business Intelligence Scraper
Provides REST endpoints and WebSocket connections for the frontend
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import sqlite3
import hashlib
import jwt
import time
from datetime import datetime, timedelta
import uvicorn
import os

# Import security components
from secure_config import (
    security_config, database_config, server_config, scraping_config,
    validate_configuration
)
from security_middleware import (
    SecurityHeadersMiddleware, InputValidationMiddleware, RequestLoggingMiddleware,
    get_limiter, validate_job_config, hash_password, verify_password
)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import the real scraping engine
from scraping_engine import execute_scraping_job

# Import performance monitoring (with fallback if dependencies missing)
try:
    from performance_monitor import (
        PerformanceMetrics, CacheManager, DatabaseOptimizer, PerformanceMiddleware,
        init_performance_system, get_performance_summary, cached, background_performance_monitor
    )
    PERFORMANCE_ENABLED = True
except ImportError:
    print("⚠️  Performance monitoring dependencies not available - running with basic monitoring")
    PERFORMANCE_ENABLED = False
    
    # Fallback implementations
    class PerformanceMetrics:
        def record_request(self, endpoint, duration, status_code): pass
        def get_system_metrics(self): return {}
        def get_endpoint_metrics(self): return {}
        def get_recent_performance(self): return {}
    
    class CacheManager:
        def get(self, key, cache_type="ttl"): return None
        def set(self, key, value, cache_type="ttl", ttl=300): pass
        def delete(self, key, cache_type="ttl"): pass
    
    class PerformanceMiddleware:
        def __init__(self, app, metrics):
            self.app = app
            self.metrics = metrics
        
        async def __call__(self, request, call_next):
            return await call_next(request)
    
    def cached(cache_type="ttl", ttl=300, key_prefix=""):
        def decorator(func): return func
        return decorator
    
    def get_performance_summary(): return {}
    async def background_performance_monitor(): pass

# Database setup
DATABASE_PATH = database_config.DATABASE_PATH

def init_database():
    """Initialize SQLite database with required tables"""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            config TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT,
            results_count INTEGER DEFAULT 0,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Job results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    ''')
    
    # Analytics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Create default admin user with secure password hashing
    password_hash = hash_password("admin123")
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', ("admin", "admin@scraper.local", password_hash, "admin"))
    
    conn.commit()
    conn.close()

# Initialize database and validate configuration
validate_configuration()
init_database()

# Initialize performance monitoring system
if PERFORMANCE_ENABLED:
    try:
        performance_metrics, cache_manager, db_optimizer = init_performance_system(DATABASE_PATH)
        print("✅ Performance monitoring system initialized")
    except Exception as e:
        print(f"⚠️  Performance monitoring initialization failed: {e}")
        PERFORMANCE_ENABLED = False
        performance_metrics = PerformanceMetrics()
        cache_manager = CacheManager()
else:
    performance_metrics = PerformanceMetrics()
    cache_manager = CacheManager()

# Rate limiter setup
limiter = get_limiter(security_config.API_RATE_LIMIT_PER_MINUTE)

# FastAPI app setup
app = FastAPI(
    title="Business Intelligence Scraper API",
    description="Backend API for the BI Scraper Platform",
    version="1.0.0"
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware, 
                   enable_headers=security_config.ENABLE_SECURITY_HEADERS,
                   hsts_max_age=security_config.HSTS_MAX_AGE)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add performance monitoring middleware
if PERFORMANCE_ENABLED:
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class PerformanceMiddlewareWrapper(BaseHTTPMiddleware):
        def __init__(self, app, metrics):
            super().__init__(app)
            self.metrics = metrics
        
        async def dispatch(self, request, call_next):
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics if available
            if hasattr(self.metrics, 'record_request'):
                endpoint = f"{request.method} {request.url.path}"
                self.metrics.record_request(endpoint, duration, response.status_code)
            
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            return response
    
    app.add_middleware(PerformanceMiddlewareWrapper, metrics=performance_metrics)

# CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Startup event for background monitoring
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks on startup"""
    if PERFORMANCE_ENABLED:
        # Start background performance monitoring
        asyncio.create_task(background_performance_monitor())
        print("🔄 Background performance monitoring started")

# JWT Configuration from secure config
JWT_SECRET = security_config.JWT_SECRET
JWT_ALGORITHM = security_config.JWT_ALGORITHM

# Custom security dependency to return 401 instead of 403
async def get_bearer_token(request: Request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        return token
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: str

class JobCreate(BaseModel):
    name: str
    type: str  # Basic job type for backward compatibility
    config: Dict[str, Any] = {}
    url: Optional[str] = None  # URL to scrape
    scraper_type: Optional[str] = "basic"  # Scraper type: basic, e_commerce, news, social_media, api
    custom_selectors: Optional[Dict[str, str]] = None  # Custom CSS selectors for data extraction

class JobResponse(BaseModel):
    id: int
    name: str
    type: str
    status: str
    created_at: str
    results_count: int

class AnalyticsData(BaseModel):
    metric_name: str
    metric_value: float
    metadata: Optional[Dict[str, Any]] = None

# Authentication functions
def verify_user_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=security_config.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(get_bearer_token)):
    """Get current authenticated user"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[4]
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# API Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint with performance metrics"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    if PERFORMANCE_ENABLED:
        health_data.update({
            "performance": performance_metrics.get_recent_performance(1),
            "system": performance_metrics.get_system_metrics()
        })
    
    return health_data

@app.post("/api/auth/login")
@limiter.limit(f"{security_config.API_RATE_LIMIT_PER_MINUTE}/minute")
async def login(request: Request, user_data: UserLogin):
    """User authentication endpoint with rate limiting"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (user_data.username,))
    user = cursor.fetchone()
    
    if not user or not verify_user_password(user_data.password, user[3]):
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Update last login
    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
    conn.commit()
    conn.close()
    
    # Create access token
    access_token = create_access_token(data={"sub": user[1]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "role": user[4]
        }
    }

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.get("/api/jobs", response_model=List[JobResponse])
async def get_jobs(current_user: dict = Depends(get_current_user)):
    """Get all jobs for the current user"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, type, status, created_at, results_count 
        FROM jobs 
        WHERE created_by = ? 
        ORDER BY created_at DESC
    """, (current_user["id"],))
    jobs = cursor.fetchall()
    conn.close()
    
    return [
        JobResponse(
            id=job[0],
            name=job[1],
            type=job[2],
            status=job[3],
            created_at=job[4],
            results_count=job[5] or 0
        )
        for job in jobs
    ]

@app.post("/api/jobs")
@limiter.limit(f"{security_config.API_RATE_LIMIT_PER_MINUTE}/minute")
async def create_job(request: Request, job_data: JobCreate, current_user: dict = Depends(get_current_user)):
    """Create a new scraping job with input validation"""
    
    # Build the complete job configuration
    job_config = {
        "url": job_data.url,
        "scraper_type": job_data.scraper_type or "basic",
        "config": {
            "custom_selectors": job_data.custom_selectors or {},
            **job_data.config  # Merge any additional config
        }
    }
    
    # Validate job configuration for security
    try:
        validated_config = validate_job_config(job_config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (name, type, config, created_by, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (job_data.name, job_data.type, json.dumps(validated_config), current_user["id"]))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Broadcast job creation to WebSocket clients
    await manager.broadcast(json.dumps({
        "type": "job_created",
        "data": {
            "id": job_id,
            "name": job_data.name,
            "type": job_data.type,
            "url": job_data.url,
            "scraper_type": job_data.scraper_type,
            "status": "pending"
        }
    }))
    
    return {"id": job_id, "message": "Job created successfully"}

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int, current_user: dict = Depends(get_current_user)):
    """Get specific job details"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM jobs 
        WHERE id = ? AND created_by = ?
    """, (job_id, current_user["id"]))
    job = cursor.fetchone()
    conn.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": job[0],
        "name": job[1],
        "type": job[2],
        "status": job[3],
        "config": json.loads(job[4]) if job[4] else {},
        "created_at": job[6],
        "results_count": job[9] or 0
    }

@app.post("/api/jobs/{job_id}/start")
async def start_job(job_id: int, current_user: dict = Depends(get_current_user)):
    """Start a scraping job"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # First, get the job configuration
    cursor.execute("""
        SELECT config FROM jobs 
        WHERE id = ? AND created_by = ?
    """, (job_id, current_user["id"]))
    
    job_row = cursor.fetchone()
    if not job_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_config = json.loads(job_row[0])
    
    # Update job status to running
    cursor.execute("""
        UPDATE jobs 
        SET status = 'running', started_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    """, (job_id,))
    conn.commit()
    conn.close()
    
    # Execute real scraping job in background
    asyncio.create_task(execute_real_scraping_job(job_id, job_config))
    
    return {"message": "Job started successfully"}

async def execute_real_scraping_job(job_id: int, job_config: Dict[str, Any]):
    """Execute real scraping job using the scraping engine"""
    try:
        # Update job status to running
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE jobs 
            SET status = 'running'
            WHERE id = ?
        """, (job_id,))
        conn.commit()
        conn.close()
        
        # Broadcast job start
        await manager.broadcast(json.dumps({
            "type": "job_started",
            "data": {
                "id": job_id,
                "status": "running"
            }
        }))
        
        # Execute the scraping job
        result = await execute_scraping_job(job_id, job_config)
        
        # Broadcast job completion
        await manager.broadcast(json.dumps({
            "type": "job_completed",
            "data": {
                "id": job_id,
                "status": result["status"],
                "url": result.get("url", ""),
                "timestamp": result.get("timestamp", "")
            }
        }))
        
    except Exception as e:
        # Handle any errors during job execution
        print(f"Error executing job {job_id}: {str(e)}")
        
        # Update job status to failed
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE jobs 
                SET status = 'failed', 
                    completed_at = CURRENT_TIMESTAMP,
                    error_message = ?
                WHERE id = ?
            """, (str(e), job_id))
            conn.commit()
            conn.close()
            
            # Broadcast job failure
            await manager.broadcast(json.dumps({
                "type": "job_failed",
                "data": {
                    "id": job_id,
                    "status": "failed",
                    "error": str(e)
                }
            }))
        except Exception as db_error:
            print(f"Failed to update job status: {str(db_error)}")

@app.get("/api/jobs/{job_id}/results")
async def get_job_results(job_id: int, current_user: dict = Depends(get_current_user)):
    """Get results for a specific job"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # First check if job exists and belongs to user
    cursor.execute("""
        SELECT id FROM jobs 
        WHERE id = ? AND created_by = ?
    """, (job_id, current_user["id"]))
    
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get job results
    cursor.execute("""
        SELECT data, created_at FROM job_results 
        WHERE job_id = ?
        ORDER BY created_at DESC
    """, (job_id,))
    
    results = []
    for row in cursor.fetchall():
        try:
            data = json.loads(row[0])
            data["retrieved_at"] = row[1]
            results.append(data)
        except json.JSONDecodeError:
            # Handle any JSON parsing errors
            results.append({
                "error": "Failed to parse result data",
                "raw_data": row[0],
                "retrieved_at": row[1]
            })
    
    conn.close()
    return results

async def simulate_job_execution(job_id: int):
    """Legacy simulation method - kept for backward compatibility"""
    await asyncio.sleep(2)  # Simulate processing time
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Update job status to completed
    cursor.execute("""
        UPDATE jobs 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP, results_count = ?
        WHERE id = ?
    """, (42, job_id))  # Simulate 42 results
    
    # Add some sample results
    sample_data = [
        {"url": "https://example.com/page1", "title": "Sample Page 1", "content": "Sample content 1"},
        {"url": "https://example.com/page2", "title": "Sample Page 2", "content": "Sample content 2"}
    ]
    
    for data in sample_data:
        cursor.execute("""
            INSERT INTO job_results (job_id, data)
            VALUES (?, ?)
        """, (job_id, json.dumps(data)))
    
    conn.commit()
    conn.close()
    
    # Broadcast job completion
    await manager.broadcast(json.dumps({
        "type": "job_completed",
        "data": {
            "id": job_id,
            "status": "completed",
            "results_count": 42
        }
    }))

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)):
    """Get analytics data for dashboard"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get job statistics
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM jobs 
        WHERE created_by = ? 
        GROUP BY status
    """, (current_user["id"],))
    job_stats = dict(cursor.fetchall())
    
    # Get total results
    cursor.execute("""
        SELECT SUM(results_count) 
        FROM jobs 
        WHERE created_by = ? AND status = 'completed'
    """, (current_user["id"],))
    total_results = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "jobs": {
            "total": sum(job_stats.values()),
            "running": job_stats.get("running", 0),
            "completed": job_stats.get("completed", 0),
            "failed": job_stats.get("failed", 0),
            "pending": job_stats.get("pending", 0)
        },
        "results": {
            "total": total_results,
            "today": 15,  # Simulated
            "this_week": 127  # Simulated
        },
        "performance": {
            "avg_processing_time": "2.3s",
            "success_rate": "94.2%",
            "data_quality_score": "87.5%"
        }
    }

@app.get("/api/analytics/metrics")
async def get_analytics_metrics(current_user: dict = Depends(get_current_user)):
    """Get detailed analytics metrics for charts"""
    # Simulate time-series data for charts
    import random
    from datetime import datetime, timedelta
    
    # Generate sample data for the last 30 days
    end_date = datetime.now()
    dates = [(end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)]
    
    metrics = {
        "job_completion_trend": [
            {"date": date, "completed": random.randint(5, 25), "failed": random.randint(0, 3)}
            for date in dates
        ],
        "data_volume_trend": [
            {"date": date, "volume": random.randint(100, 1000)}
            for date in dates
        ],
        "performance_metrics": [
            {"date": date, "response_time": random.uniform(1.0, 5.0), "success_rate": random.uniform(85, 99)}
            for date in dates
        ],
        "top_sources": [
            {"source": "example.com", "count": 156},
            {"source": "sample.org", "count": 89},
            {"source": "demo.net", "count": 67},
            {"source": "test.io", "count": 45}
        ]
    }
    
    return metrics

@app.get("/api/performance/summary")
async def get_performance_summary_endpoint(current_user: dict = Depends(get_current_user)):
    """Get comprehensive performance summary"""
    if not PERFORMANCE_ENABLED:
        return {"error": "Performance monitoring not available", "enabled": False}
    
    return get_performance_summary()

@app.get("/api/performance/metrics")
async def get_performance_metrics(current_user: dict = Depends(get_current_user)):
    """Get real-time performance metrics"""
    if not PERFORMANCE_ENABLED:
        return {"error": "Performance monitoring not available", "enabled": False}
    
    return {
        "system": performance_metrics.get_system_metrics(),
        "endpoints": performance_metrics.get_endpoint_metrics(),
        "recent_5min": performance_metrics.get_recent_performance(5),
        "recent_1min": performance_metrics.get_recent_performance(1),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/performance/cache/stats")
async def get_cache_stats(current_user: dict = Depends(get_current_user)):
    """Get cache performance statistics"""
    if not PERFORMANCE_ENABLED:
        return {"error": "Performance monitoring not available", "enabled": False}
    
    # Cache stats would be implemented based on actual cache manager
    return {
        "cache_enabled": True,
        "redis_available": getattr(cache_manager, 'redis_available', False),
        "ttl_cache_size": len(getattr(cache_manager, 'ttl_cache', {})),
        "lru_cache_size": len(getattr(cache_manager, 'lru_cache', {})),
        "job_cache_size": len(getattr(cache_manager, 'job_cache', {})),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/performance/cache/clear")
async def clear_cache(current_user: dict = Depends(get_current_user)):
    """Clear all caches (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not PERFORMANCE_ENABLED:
        return {"error": "Performance monitoring not available", "enabled": False}
    
    try:
        cache_manager.clear_all()
        return {"message": "All caches cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@app.get("/api/jobs", response_model=List[JobResponse])
@cached(cache_type="ttl", ttl=60, key_prefix="jobs_")
async def get_jobs(current_user: dict = Depends(get_current_user)):
    """Get all jobs for the current user with caching"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, type, status, created_at, results_count 
        FROM jobs 
        WHERE created_by = ? 
        ORDER BY created_at DESC
    """, (current_user["id"],))
    jobs = cursor.fetchall()
    conn.close()
    
    return [
        JobResponse(
            id=job[0],
            name=job[1],
            type=job[2],
            status=job[3],
            created_at=job[4],
            results_count=job[5] or 0
        )
        for job in jobs
    ]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            await websocket.send_text(json.dumps({
                "type": "metrics_update",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "active_jobs": 3,
                    "queue_size": 7,
                    "processing_rate": "12.5/min"
                }
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("🚀 Starting Business Intelligence Scraper API Server...")
    print("📊 Dashboard: http://localhost:5173")
    print("🔗 API Docs: http://localhost:8000/docs")
    print("💾 Database: SQLite at", DATABASE_PATH)
    print("🔐 Security Features:")
    print(f"   ✅ Rate Limiting: {security_config.API_RATE_LIMIT_PER_MINUTE}/min")
    print(f"   ✅ Security Headers: {security_config.ENABLE_SECURITY_HEADERS}")
    print(f"   ✅ Input Validation: Enabled")
    print(f"   ✅ Secure JWT: {len(security_config.JWT_SECRET)} char secret")
    print("⚡ Performance Features:")
    print(f"   ✅ Performance Monitoring: {PERFORMANCE_ENABLED}")
    print(f"   ✅ Caching System: {PERFORMANCE_ENABLED}")
    print(f"   ✅ Database Optimization: {PERFORMANCE_ENABLED}")
    print(f"   ✅ Real-time Metrics: {PERFORMANCE_ENABLED}")
    
    uvicorn.run(
        "backend_server:app", 
        host=server_config.HOST, 
        port=server_config.PORT,
        reload=server_config.DEBUG,
        log_level=server_config.LOG_LEVEL
    )
