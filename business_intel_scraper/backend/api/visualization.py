from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

# Database dependency
from ..db import get_db
from ..visualization.data_processor import VisualizationDataProcessor

router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.get("/network-data")
async def get_network_data(
    entity_type: str = Query("all", description="Entity type to visualize"),
    limit: int = Query(100, description="Maximum number of nodes"),
    filters: Optional[str] = Query(None, description="JSON filters"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get network graph data for visualization"""
    try:
        processor = VisualizationDataProcessor(db)

        # Parse filters if provided
        parsed_filters = {}
        if filters:
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in filters")

        # Get network data from processor
        network_data = await processor.get_entity_network_data(
            entity_type=entity_type if entity_type != "all" else None,
            limit=limit,
            filters=parsed_filters,
        )

        return {
            **network_data,
            "request_info": {
                "entity_type": entity_type,
                "limit": limit,
                "filters_applied": bool(parsed_filters),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating network data: {str(e)}"
        )


@router.get("/timeline-data")
async def get_timeline_data(
    entity_id: Optional[str] = Query(None, description="Specific entity ID"),
    time_range: str = Query("30d", description="Time range (e.g., 30d, 7d, 1h)"),
    group_by: str = Query("day", description="Group events by: hour, day, week, month"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get timeline data for temporal visualization"""
    try:
        processor = VisualizationDataProcessor(db)

        # Parse time range
        range_value = int(time_range[:-1])
        range_unit = time_range[-1]

        if range_unit == "d":
            start_date = datetime.utcnow() - timedelta(days=range_value)
        elif range_unit == "h":
            start_date = datetime.utcnow() - timedelta(hours=range_value)
        elif range_unit == "w":
            start_date = datetime.utcnow() - timedelta(weeks=range_value)
        else:
            start_date = datetime.utcnow() - timedelta(days=30)  # Default

        timeline_data = await processor.get_timeline_data(
            entity_id=entity_id, start_date=start_date, group_by=group_by
        )

        return {
            **timeline_data,
            "request_info": {
                "entity_id": entity_id,
                "time_range": time_range,
                "start_date": start_date.isoformat(),
                "group_by": group_by,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating timeline data: {str(e)}"
        )


@router.get("/geospatial-data")
async def get_geospatial_data(
    bounds: Optional[str] = Query(
        None, description="Geographic bounds as 'lat1,lng1,lat2,lng2'"
    ),
    zoom_level: int = Query(10, description="Map zoom level for clustering"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get geospatial data for map visualization"""
    try:
        processor = VisualizationDataProcessor(db)

        # Parse bounds if provided
        parsed_bounds = None
        if bounds:
            try:
                coords = [float(x.strip()) for x in bounds.split(",")]
                if len(coords) == 4:
                    parsed_bounds = {
                        "north": coords[0],
                        "west": coords[1],
                        "south": coords[2],
                        "east": coords[3],
                    }
            except (ValueError, IndexError):
                raise HTTPException(status_code=400, detail="Invalid bounds format")

        geo_data = await processor.get_geospatial_data(
            bounds=parsed_bounds, zoom_level=zoom_level
        )

        return {
            **geo_data,
            "request_info": {
                "bounds": parsed_bounds,
                "zoom_level": zoom_level,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating geospatial data: {str(e)}"
        )


@router.get("/metrics")
async def get_visualization_metrics(
    time_range: str = Query("24h", description="Time range for metrics"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get aggregated metrics for dashboard visualization"""
    try:
        processor = VisualizationDataProcessor(db)

        metrics_data = await processor.get_visualization_metrics(time_range)

        return {**metrics_data, "generated_at": datetime.utcnow().isoformat()}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating metrics: {str(e)}"
        )


@router.post("/save-config")
@router.post("/configs")
async def save_visualization_config(
    config: Dict[str, Any],
    name: str = Query(..., description="Configuration name"),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Save visualization configuration with proper authentication and storage"""
    try:
        from ..db.centralized_data import CentralizedDataRecord
        
        # Validate config structure
        required_fields = ['type', 'settings']
        if not all(field in config for field in required_fields):
            raise HTTPException(
                status_code=400, 
                detail=f"Config must contain: {required_fields}"
            )
        
        # Create configuration record
        config_record = CentralizedDataRecord(
            source_job_name=f"visualization_config_{name}",
            source_job_type="configuration",
            data_type="config",
            title=name,
            raw_data=config,
            processed_data={
                "config_name": name,
                "config_type": config.get("type", "unknown"),
                "settings": config.get("settings", {}),
                "created_at": datetime.utcnow().isoformat()
            },
            content_category="visualization_config",
            validation_status="valid"
        )
        
        # Save to database
        db.add(config_record)
        db.commit()
        db.refresh(config_record)
        
        return {
            "status": "success",
            "message": f"Configuration '{name}' saved successfully",
            "config_id": str(config_record.record_uuid),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error saving configuration: {str(e)}"
        )


@router.get("/configs")
async def get_visualization_configs(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get saved visualization configurations with proper database retrieval"""
    try:
        from ..db.centralized_data import CentralizedDataRecord
        
        # Query configurations from database
        configs = db.query(CentralizedDataRecord).filter(
            CentralizedDataRecord.data_type == "config",
            CentralizedDataRecord.content_category == "visualization_config"
        ).order_by(CentralizedDataRecord.centralized_at.desc()).all()
        
        config_list = []
        for config_record in configs:
            processed_data = config_record.processed_data or {}
            
            config_data = {
                "id": str(config_record.record_uuid),
                "name": config_record.title or "Unnamed Config",
                "type": processed_data.get("config_type", "unknown"),
                "created_at": config_record.centralized_at.isoformat() if hasattr(config_record.centralized_at, 'isoformat') else str(config_record.centralized_at),
                "settings": processed_data.get("settings", {}),
                "validation_status": config_record.validation_status
            }
            config_list.append(config_data)
        
        return {
            "configs": config_list,
            "total": len(config_list),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving configurations: {str(e)}"
        )
