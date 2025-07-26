from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import visualization router
from .visualization import router as visualization_router

# Create FastAPI app
app = FastAPI(
    title="Business Intelligence Scraper API",
    description="API for visual analytics and data visualization",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include visualization router
app.include_router(
    visualization_router, prefix="/api/visualization", tags=["visualization"]
)


@app.get("/")
async def root():
    return {"message": "Visual Analytics API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "visual-analytics-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
