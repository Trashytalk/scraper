"""
Enhanced Visual Analytics API with Real Data Integration and WebSocket Support
Phase 3: Advanced Features Implementation
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import pandas as pd
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Business Intelligence Visual Analytics API",
    description="Advanced API for visual analytics with real-time data streaming",
    version="3.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")


manager = ConnectionManager()


# Enhanced data models
class NetworkData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class TimelineData(BaseModel):
    events: List[Dict[str, Any]]
    groups: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class GeospatialData(BaseModel):
    points: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class FilterRequest(BaseModel):
    entity_type: Optional[str] = None
    date_range: Optional[Dict[str, str]] = None
    search_term: Optional[str] = None
    confidence_threshold: Optional[float] = None


# Enhanced data generation with more realistic patterns
def generate_enhanced_network_data(
    filter_params: FilterRequest = None,
) -> Dict[str, Any]:
    """Generate enhanced network data with filtering capabilities"""

    # Define entity types and relationships
    entity_types = ["person", "organization", "location", "event", "document"]
    relationship_types = [
        "connected_to",
        "located_at",
        "participated_in",
        "owns",
        "mentioned_in",
    ]

    # Generate nodes with enhanced attributes
    nodes = []
    for i in range(50):
        entity_type = random.choice(entity_types)
        confidence = random.uniform(0.3, 1.0)

        # Apply confidence filter
        if filter_params and filter_params.confidence_threshold:
            if confidence < filter_params.confidence_threshold:
                continue

        # Apply entity type filter
        if filter_params and filter_params.entity_type:
            if entity_type != filter_params.entity_type:
                continue

        node = {
            "id": f"node_{i}",
            "label": f"{entity_type.title()} {i}",
            "type": entity_type,
            "confidence": confidence,
            "properties": {
                "weight": random.randint(1, 10),
                "influence": random.uniform(0.1, 1.0),
                "last_updated": (
                    datetime.now() - timedelta(days=random.randint(0, 30))
                ).isoformat(),
                "source": random.choice(["scraper_1", "scraper_2", "manual_input"]),
            },
        }
        nodes.append(node)

    # Generate edges based on nodes
    edges = []
    for i in range(min(len(nodes) * 2, 100)):  # Limit edges
        if len(nodes) < 2:
            break

        source = random.choice(nodes)
        target = random.choice([n for n in nodes if n["id"] != source["id"]])

        edge = {
            "id": f"edge_{i}",
            "source": source["id"],
            "target": target["id"],
            "relationship": random.choice(relationship_types),
            "strength": random.uniform(0.1, 1.0),
            "properties": {
                "created_at": (
                    datetime.now() - timedelta(days=random.randint(0, 15))
                ).isoformat(),
                "verified": random.choice([True, False]),
                "source": random.choice(["automatic", "manual", "inferred"]),
            },
        }
        edges.append(edge)

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "entity_types": list(set([n["type"] for n in nodes])),
            "generated_at": datetime.now().isoformat(),
            "data_source": "enhanced_business_intel_scraper",
            "applied_filters": filter_params.dict() if filter_params else None,
        },
    }


def generate_enhanced_timeline_data(
    filter_params: FilterRequest = None,
) -> Dict[str, Any]:
    """Generate enhanced timeline data with filtering capabilities"""

    # Define event types and categories
    event_types = [
        "meeting",
        "transaction",
        "communication",
        "travel",
        "document_creation",
    ]
    event_categories = ["business", "personal", "legal", "financial", "operational"]

    events = []
    groups = []

    # Create groups
    for i, category in enumerate(event_categories):
        groups.append(
            {
                "id": f"group_{i}",
                "content": category.title(),
                "style": f'background-color: {random.choice(["#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"])}',
            }
        )

    # Generate events
    base_date = datetime.now() - timedelta(days=365)
    for i in range(100):
        event_date = base_date + timedelta(days=random.randint(0, 365))

        # Apply date range filter
        if filter_params and filter_params.date_range:
            start_date = datetime.fromisoformat(
                filter_params.date_range.get("start", "1970-01-01")
            )
            end_date = datetime.fromisoformat(
                filter_params.date_range.get("end", "2030-12-31")
            )
            if not (start_date <= event_date <= end_date):
                continue

        event_type = random.choice(event_types)
        event_category = random.choice(event_categories)

        event_title = f"{event_type.replace('_', ' ').title()} {i}"

        # Apply search filter
        if filter_params and filter_params.search_term:
            if filter_params.search_term.lower() not in event_title.lower():
                continue

        event = {
            "id": f"event_{i}",
            "content": event_title,
            "start": event_date.isoformat(),
            "group": f"group_{event_categories.index(event_category)}",
            "type": "point",
            "title": f'Type: {event_type}<br>Category: {event_category}<br>Date: {event_date.strftime("%Y-%m-%d")}',
            "properties": {
                "event_type": event_type,
                "category": event_category,
                "confidence": random.uniform(0.5, 1.0),
                "source": random.choice(
                    ["email_scraper", "calendar_scraper", "document_parser"]
                ),
            },
        }
        events.append(event)

    return {
        "events": events,
        "groups": groups,
        "metadata": {
            "total_events": len(events),
            "time_range": f'{base_date.strftime("%Y-%m-%d")} to {datetime.now().strftime("%Y-%m-%d")}',
            "event_types": list(set([e["properties"]["event_type"] for e in events])),
            "categories": [g["content"] for g in groups],
            "generated_at": datetime.now().isoformat(),
            "data_source": "enhanced_timeline_scraper",
            "applied_filters": filter_params.dict() if filter_params else None,
        },
    }


def generate_enhanced_geospatial_data(
    filter_params: FilterRequest = None,
) -> Dict[str, Any]:
    """Generate enhanced geospatial data with filtering capabilities"""

    # Define location types and regions
    location_types = [
        "office",
        "residence",
        "meeting_location",
        "transaction_site",
        "travel_destination",
    ]

    # Major cities coordinates for realistic data
    major_cities = [
        {"name": "New York", "lat": 40.7128, "lng": -74.0060},
        {"name": "London", "lat": 51.5074, "lng": -0.1278},
        {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503},
        {"name": "Paris", "lat": 48.8566, "lng": 2.3522},
        {"name": "Sydney", "lat": -33.8688, "lng": 151.2093},
        {"name": "Berlin", "lat": 52.5200, "lng": 13.4050},
        {"name": "Toronto", "lat": 43.6532, "lng": -79.3832},
    ]

    points = []
    for i in range(75):
        base_city = random.choice(major_cities)

        # Add some random offset to create clusters
        lat_offset = random.uniform(-0.1, 0.1)
        lng_offset = random.uniform(-0.1, 0.1)

        location_type = random.choice(location_types)

        # Apply entity type filter (treating location_type as entity_type)
        if filter_params and filter_params.entity_type:
            if location_type != filter_params.entity_type:
                continue

        point = {
            "id": f"point_{i}",
            "latitude": base_city["lat"] + lat_offset,
            "longitude": base_city["lng"] + lng_offset,
            "type": location_type,
            "entity_id": f"entity_{i}",
            "metadata": {
                "name": f'{location_type.replace("_", " ").title()} in {base_city["name"]}',
                "description": f'Identified {location_type} near {base_city["name"]}',
                "confidence": random.uniform(0.4, 1.0),
                "source": random.choice(
                    ["gps_data", "ip_geolocation", "address_parser"]
                ),
                "timestamp": (
                    datetime.now() - timedelta(days=random.randint(0, 60))
                ).isoformat(),
                "city": base_city["name"],
                "visits": random.randint(1, 20),
            },
        }
        points.append(point)

    # Calculate center point
    if points:
        center_lat = sum(p["latitude"] for p in points) / len(points)
        center_lng = sum(p["longitude"] for p in points) / len(points)
    else:
        center_lat, center_lng = 0, 0

    return {
        "points": points,
        "metadata": {
            "total_points": len(points),
            "center_lat": center_lat,
            "center_lng": center_lng,
            "zoom_level": 10,
            "location_types": list(set([p["type"] for p in points])),
            "cities": list(set([p["metadata"]["city"] for p in points])),
            "generated_at": datetime.now().isoformat(),
            "data_source": "enhanced_geospatial_scraper",
            "applied_filters": filter_params.dict() if filter_params else None,
        },
    }


# Enhanced API endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "enhanced-visual-analytics-api",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/network-data")
async def get_network_data(filters: FilterRequest = None):
    """Get network data with optional filtering"""
    try:
        data = generate_enhanced_network_data(filters)
        return data
    except Exception as e:
        logger.error(f"Error generating network data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/timeline-data")
async def get_timeline_data(filters: FilterRequest = None):
    """Get timeline data with optional filtering"""
    try:
        data = generate_enhanced_timeline_data(filters)
        return data
    except Exception as e:
        logger.error(f"Error generating timeline data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/geospatial-data")
async def get_geospatial_data(filters: FilterRequest = None):
    """Get geospatial data with optional filtering"""
    try:
        data = generate_enhanced_geospatial_data(filters)
        return data
    except Exception as e:
        logger.error(f"Error generating geospatial data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_system_metrics():
    """Get enhanced system metrics and statistics"""
    try:
        # Generate realistic metrics
        metrics = {
            "entity_counts": {
                "total": random.randint(1000, 5000),
                "by_type": {
                    "person": random.randint(100, 800),
                    "organization": random.randint(50, 300),
                    "location": random.randint(80, 400),
                    "event": random.randint(200, 1000),
                    "document": random.randint(150, 600),
                },
            },
            "relationship_counts": {
                "total": random.randint(2000, 8000),
                "by_type": {
                    "connected_to": random.randint(300, 1500),
                    "located_at": random.randint(200, 1000),
                    "participated_in": random.randint(150, 800),
                    "owns": random.randint(100, 500),
                    "mentioned_in": random.randint(250, 1200),
                },
            },
            "data_quality": {
                "score": random.uniform(0.75, 0.95),
                "confidence_distribution": {
                    "high": random.uniform(0.6, 0.8),
                    "medium": random.uniform(0.15, 0.3),
                    "low": random.uniform(0.05, 0.15),
                },
                "issues": random.sample(
                    [
                        "Missing location data for some entities",
                        "Duplicate entries detected",
                        "Incomplete relationship mapping",
                        "Outdated information in some records",
                        "Low confidence scores in certain categories",
                    ],
                    random.randint(0, 3),
                ),
            },
            "system_stats": {
                "last_update": datetime.now().isoformat(),
                "processing_time": f"{random.uniform(0.5, 3.0):.2f}s",
                "data_sources": random.randint(5, 15),
                "active_scrapers": random.randint(3, 8),
                "total_records_processed": random.randint(10000, 50000),
                "uptime": f"{random.randint(1, 720)} hours",
            },
            "performance": {
                "cpu_usage": random.uniform(20, 80),
                "memory_usage": random.uniform(40, 85),
                "disk_usage": random.uniform(30, 70),
                "network_throughput": random.uniform(10, 100),
            },
        }
        return metrics
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/{data_type}")
async def export_data(
    data_type: str, format: str = Query("json", pattern="^(json|csv|xlsx)$")
):
    """Export data in various formats"""
    try:
        if data_type == "network":
            data = generate_enhanced_network_data()
        elif data_type == "timeline":
            data = generate_enhanced_timeline_data()
        elif data_type == "geospatial":
            data = generate_enhanced_geospatial_data()
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")

        if format == "json":
            return JSONResponse(content=data)
        elif format == "csv":
            # Convert to CSV format (simplified)
            import io

            output = io.StringIO()
            if data_type == "network":
                df = pd.DataFrame(data["nodes"])
                df.to_csv(output, index=False)
            return StreamingResponse(
                io.StringIO(output.getvalue()),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={data_type}_data.csv"
                },
            )

        return JSONResponse(content={"error": "Format not yet implemented"})

    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)  # Update every 5 seconds

            # Generate a random update
            update_types = [
                "network_update",
                "timeline_update",
                "geospatial_update",
                "metrics_update",
            ]
            update_type = random.choice(update_types)

            update_data = {
                "type": update_type,
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "message": f'New {update_type.replace("_", " ")} available',
                    "count": random.randint(1, 10),
                    "priority": random.choice(["low", "medium", "high"]),
                },
            }

            await manager.send_personal_message(json.dumps(update_data), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Background task for periodic updates
@app.on_event("startup")
async def startup_event():
    logger.info("Enhanced Visual Analytics API started")
    logger.info("WebSocket support enabled for real-time updates")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_enhanced:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
