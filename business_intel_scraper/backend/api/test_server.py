#!/usr/bin/env python3
"""Simple API server for testing job management functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers with absolute path
from business_intel_scraper.backend.api.jobs import router as jobs_router

# Create FastAPI app
app = FastAPI(
    title="Business Intelligence Scraper API",
    description="API for job management and scraping operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include jobs router
app.include_router(jobs_router)

@app.get("/")
async def root():
    return {"message": "Business Intelligence Scraper API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "bi-scraper-api"}

if __name__ == "__main__":
    print("🚀 Starting Business Intelligence Scraper API...")
    print("📡 API will be available at: http://localhost:8000")
    print("📊 Jobs endpoint: http://localhost:8000/jobs/")
    print("📚 API docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "test_server:app", 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
