from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from .data_processor_standalone import VisualizationDataProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize data processor without database for demo
data_processor = VisualizationDataProcessor()

@router.get("/network-data")
async def get_network_data(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(100, description="Maximum number of entities to return"),
) -> Dict[str, Any]:
    """
    Get network data for visualization
    
    Returns nodes and edges for network graph visualization
    """
    try:
        filters = {}
        result = await data_processor.get_entity_network_data(
            entity_type=entity_type,
            limit=limit,
            filters=filters
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching network data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timeline-data")
async def get_timeline_data(
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    start_date: Optional[str] = Query(None, description="Start date filter (ISO format)"),
    group_by: str = Query("day", description="Group events by time period"),
) -> Dict[str, Any]:
    """
    Get timeline data for visualization
    
    Returns events and groups for timeline visualization
    """
    try:
        start_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        result = await data_processor.get_timeline_data(
            entity_id=entity_id,
            start_date=start_dt,
            group_by=group_by
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching timeline data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/geospatial-data")
async def get_geospatial_data(
    north: Optional[float] = Query(None, description="Northern boundary"),
    south: Optional[float] = Query(None, description="Southern boundary"),
    east: Optional[float] = Query(None, description="Eastern boundary"),
    west: Optional[float] = Query(None, description="Western boundary"),
    zoom_level: int = Query(10, description="Map zoom level"),
) -> Dict[str, Any]:
    """
    Get geospatial data for map visualization
    
    Returns geographic points for map visualization
    """
    try:
        bounds = None
        if all([north, south, east, west]):
            bounds = {
                "north": north,
                "south": south, 
                "east": east,
                "west": west
            }
        
        result = await data_processor.get_geospatial_data(
            bounds=bounds,
            zoom_level=zoom_level
        )
        return result
    except Exception as e:
        logger.error(f"Error fetching geospatial data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_visualization_metrics(
    time_range: str = Query("24h", description="Time range for metrics"),
) -> Dict[str, Any]:
    """
    Get aggregated metrics for dashboard
    
    Returns entity counts, relationship counts, and system metrics
    """
    try:
        result = await data_processor.get_visualization_metrics(time_range=time_range)
        return result
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for visualization API"""
    return {
        "status": "healthy",
        "service": "visualization-api",
        "timestamp": datetime.utcnow().isoformat()
    }
