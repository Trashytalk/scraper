"""
Spider Marketplace API Endpoints
Provides REST API for spider discovery, installation, and management
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import tempfile
import shutil
from pathlib import Path

from . import SpiderMarketplace


# Pydantic models for API
class SpiderSearchRequest(BaseModel):
    query: str = ""
    category: str = ""
    tags: List[str] = []
    limit: int = Field(default=20, le=100)


class SpiderInstallRequest(BaseModel):
    name: str
    version: str = "latest"


class SpiderPublishRequest(BaseModel):
    name: str
    version: str
    author: str
    description: str
    category: str
    tags: List[str] = []
    requirements: List[str] = []
    entry_point: str
    license: str
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None


class SpiderResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


# Create router
router = APIRouter(prefix="/marketplace", tags=["marketplace"])

# Initialize marketplace
marketplace = SpiderMarketplace()


@router.get("/search", response_model=List[Dict[str, Any]])
async def search_spiders(
    query: str = Query("", description="Search query"),
    category: str = Query("", description="Filter by category"),
    tags: str = Query("", description="Comma-separated tags"),
    limit: int = Query(20, le=100, description="Maximum results"),
) -> List[Dict[str, Any]]:
    """Search for spiders in the marketplace"""
    try:
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []

        spiders = marketplace.search_spiders(
            query=query, category=category, tags=tag_list, limit=limit
        )

        return spiders

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/spider/{spider_name}", response_model=Dict[str, Any])
async def get_spider_info(spider_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific spider"""
    try:
        spider_info = marketplace.get_spider_info(spider_name)

        if not spider_info:
            raise HTTPException(
                status_code=404, detail=f"Spider {spider_name} not found"
            )

        return spider_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get spider info: {str(e)}"
        )


@router.post("/install", response_model=SpiderResponse)
async def install_spider(request: SpiderInstallRequest) -> SpiderResponse:
    """Install a spider from the marketplace"""
    try:
        result = marketplace.install_spider(request.name, request.version)

        return SpiderResponse(
            success=result["success"],
            message=result.get("message"),
            error=result.get("error"),
            data={"name": request.name, "version": request.version},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Installation failed: {str(e)}")


@router.delete("/uninstall/{spider_name}", response_model=SpiderResponse)
async def uninstall_spider(spider_name: str) -> SpiderResponse:
    """Uninstall a spider"""
    try:
        result = marketplace.uninstall_spider(spider_name)

        return SpiderResponse(
            success=result["success"],
            message=result.get("message"),
            error=result.get("error"),
            data={"name": spider_name},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Uninstallation failed: {str(e)}")


@router.get("/installed", response_model=List[Dict[str, Any]])
async def list_installed_spiders() -> List[Dict[str, Any]]:
    """List all installed spiders"""
    try:
        spiders = marketplace.list_installed_spiders()
        return spiders

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list spiders: {str(e)}")


@router.post("/validate", response_model=Dict[str, Any])
async def validate_spider_package(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Validate a spider package"""
    try:
        # Create temporary directory for uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save uploaded file
            filename = file.filename or "uploaded_file"
            file_path = temp_path / filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract if it's a zip file
            if filename.endswith(".zip"):
                import zipfile

                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(temp_path / "extracted")
                validation_path = temp_path / "extracted"
            else:
                validation_path = temp_path

            # Validate
            result = marketplace.validate_spider(str(validation_path))

            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/publish", response_model=SpiderResponse)
async def publish_spider(
    file: UploadFile = File(...),
    metadata: str = Query(..., description="JSON metadata for the spider"),
) -> SpiderResponse:
    """Publish a spider to the marketplace"""
    try:
        import json

        # Parse metadata
        try:
            spider_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON metadata")

        # Create temporary directory for uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save uploaded file
            filename = file.filename or "uploaded_spider"
            file_path = temp_path / filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Extract if it's a zip file
            if filename.endswith(".zip"):
                import zipfile

                with zipfile.ZipFile(file_path, "r") as zip_ref:
                    zip_ref.extractall(temp_path / "extracted")
                spider_path = temp_path / "extracted"
            else:
                spider_path = temp_path

            # Publish
            result = marketplace.publish_spider(str(spider_path), spider_metadata)

            return SpiderResponse(
                success=result["success"],
                message=result.get("message"),
                error=result.get("error"),
                data=spider_metadata,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")


@router.get("/categories", response_model=List[str])
async def get_categories() -> List[str]:
    """Get available spider categories"""
    try:
        return marketplace.get_categories()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get categories: {str(e)}"
        )


@router.get("/stats", response_model=Dict[str, Any])
async def get_marketplace_stats() -> Dict[str, Any]:
    """Get marketplace statistics"""
    try:
        return marketplace.get_marketplace_stats()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.get("/featured", response_model=List[Dict[str, Any]])
async def get_featured_spiders(limit: int = Query(10, le=20)) -> List[Dict[str, Any]]:
    """Get featured/popular spiders"""
    try:
        # Get popular spiders (highest rated and most downloaded)
        all_spiders = marketplace.search_spiders(limit=100)

        # Sort by rating and downloads
        featured = sorted(
            all_spiders,
            key=lambda x: (
                x.get("verified", False),
                x.get("rating", 0),
                x.get("downloads", 0),
            ),
            reverse=True,
        )

        return featured[:limit]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get featured spiders: {str(e)}"
        )


@router.post("/rate/{spider_name}")
async def rate_spider(
    spider_name: str,
    rating: float = Query(..., ge=1, le=5),
    comment: str = Query("", description="Optional review comment"),
) -> SpiderResponse:
    """Rate a spider (placeholder for future implementation)"""
    try:
        # In a real implementation, this would store the rating in the database
        # For now, just return success

        spider_info = marketplace.get_spider_info(spider_name)
        if not spider_info:
            raise HTTPException(
                status_code=404, detail=f"Spider {spider_name} not found"
            )

        return SpiderResponse(
            success=True,
            message=f"Rating submitted for {spider_name}",
            data={"rating": rating, "comment": comment},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rating failed: {str(e)}")


@router.get("/my-spiders", response_model=List[Dict[str, Any]])
async def get_my_spiders() -> List[Dict[str, Any]]:
    """Get spiders published by the current user (placeholder)"""
    try:
        # In a real implementation, this would filter by user authentication
        # For now, return published spiders from local registry

        cache_dir = Path("data/marketplace_cache/published")
        my_spiders = []

        if cache_dir.exists():
            for spider_dir in cache_dir.iterdir():
                if spider_dir.is_dir() and (spider_dir / "spider.yaml").exists():
                    try:
                        import yaml

                        with open(spider_dir / "spider.yaml", "r") as f:
                            spider_info = yaml.safe_load(f)
                            spider_info["published"] = True
                            spider_info["local_path"] = str(spider_dir)
                            my_spiders.append(spider_info)
                    except Exception as e:
                        print(f"Error loading published spider {spider_dir.name}: {e}")

        return my_spiders

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get user spiders: {str(e)}"
        )


# Health check for marketplace
@router.get("/health")
async def marketplace_health() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        stats = marketplace.get_marketplace_stats()

        return {
            "status": "healthy",
            "marketplace_accessible": True,
            "local_registry": True,
            "stats": stats,
        }

    except Exception as e:
        return {"status": "degraded", "marketplace_accessible": False, "error": str(e)}
