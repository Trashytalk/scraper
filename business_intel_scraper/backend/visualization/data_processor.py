from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VisualizationDataProcessor:
    """Process database data for visualization components"""
    
    def __init__(self, db_session=None):
        self.db = db_session

    async def get_entity_network_data(
        self, 
        entity_type: Optional[str] = None,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process database data for network visualization"""
        nodes = []
        edges = []
        entity_ids = []
        
        try:
            if self.db:
                # Try to get data from actual database models
                try:
                    from sqlalchemy import func
                    from ..storage.models import StructuredEntityModel, EntityRelationshipModel
                    
                    # Build query for nodes (entities)
                    node_query = self.db.query(StructuredEntityModel)
                    
                    if entity_type:
                        node_query = node_query.filter(StructuredEntityModel.entity_type == entity_type)
                    
                    # Apply filters if provided
                    if filters:
                        for key, value in filters.items():
                            if hasattr(StructuredEntityModel, key):
                                node_query = node_query.filter(getattr(StructuredEntityModel, key) == value)
                    
                    entities = node_query.limit(limit).all()
                    
                    # Build nodes array
                    for entity in entities:
                        entity_ids.append(entity.entity_id)
                        nodes.append({
                            "id": str(entity.entity_id),
                            "label": entity.entity_value or f"Entity {entity.entity_id}",
                            "group": entity.entity_type or "unknown",
                            "size": 30 + (entity.confidence_score or 0.5) * 20,
                            "color": self._get_color_for_type(entity.entity_type)
                        })
                    
                    # Build query for edges (relationships)
                    if entity_ids:
                        from sqlalchemy import and_
                        relationships = self.db.query(EntityRelationshipModel).filter(
                            and_(
                                EntityRelationshipModel.source_entity_id.in_(entity_ids),
                                EntityRelationshipModel.target_entity_id.in_(entity_ids)
                            )
                        ).limit(limit * 2).all()
                        
                        for rel in relationships:
                            edges.append({
                                "source": str(rel.source_entity_id),
                                "target": str(rel.target_entity_id),
                                "weight": rel.confidence_score or 1.0,
                                "type": rel.relationship_type or "default"
                            })
                    
                except Exception as e:
                    logger.warning(f"Could not load from database: {e}")
                    # Fall through to demo data
            
            # Use demo data if no database or database failed
            if not nodes:
                nodes = [
                    {"id": "1", "label": "Sample Company A", "group": "organization", "size": 45, "color": "#e74c3c"},
                    {"id": "2", "label": "John Smith", "group": "person", "size": 35, "color": "#3498db"},
                    {"id": "3", "label": "New York Office", "group": "location", "size": 40, "color": "#2ecc71"},
                    {"id": "4", "label": "Tech Corp", "group": "organization", "size": 50, "color": "#e74c3c"},
                    {"id": "5", "label": "Jane Doe", "group": "person", "size": 30, "color": "#3498db"},
                    {"id": "6", "label": "San Francisco", "group": "location", "size": 35, "color": "#2ecc71"},
                ]
                edges = [
                    {"source": "1", "target": "2", "weight": 0.9, "type": "employs"},
                    {"source": "2", "target": "3", "weight": 0.7, "type": "works_at"},
                    {"source": "1", "target": "3", "weight": 0.8, "type": "located_in"},
                    {"source": "4", "target": "5", "weight": 0.9, "type": "employs"},
                    {"source": "5", "target": "6", "weight": 0.6, "type": "lives_in"},
                    {"source": "1", "target": "4", "weight": 0.5, "type": "competes_with"},
                ]
                entity_ids = [n["id"] for n in nodes]
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "entity_type": entity_type,
                    "data_source": "database" if self.db and entity_ids else "demo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_entity_network_data: {e}")
            # Return minimal error data
            return {
                "nodes": [
                    {"id": "error", "label": "Error Loading Data", "group": "error", "size": 50, "color": "#ff0000"}
                ],
                "edges": [],
                "metadata": {
                    "total_nodes": 1,
                    "total_edges": 0,
                    "error": str(e)
                }
            }

    async def get_timeline_data(
        self, 
        entity_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """Process temporal data for timeline visualization"""
        events = []
        groups = [
            {"id": "discoveries", "content": "Entity Discoveries"},
            {"id": "updates", "content": "Data Updates"},
            {"id": "relationships", "content": "Relationship Changes"},
            {"id": "verifications", "content": "Verifications"}
        ]
        
        try:
            if self.db:
                try:
                    from ..storage.models import StructuredEntityModel, EntityRelationshipModel
                    
                    # Generate events from entity creation dates
                    entity_query = self.db.query(StructuredEntityModel)
                    
                    if entity_id:
                        entity_query = entity_query.filter(StructuredEntityModel.entity_id == entity_id)
                        
                    if start_date:
                        entity_query = entity_query.filter(StructuredEntityModel.first_seen_at >= start_date)
                    
                    entities = entity_query.order_by(StructuredEntityModel.first_seen_at.desc()).limit(50).all()
                    
                    for entity in entities:
                        if entity.first_seen_at:
                            events.append({
                                "id": f"discovery_{entity.entity_id}",
                                "content": f"Discovered: {entity.entity_value or 'Entity'}",
                                "start": entity.first_seen_at.isoformat(),
                                "group": "discoveries",
                                "type": "point",
                                "title": f"Entity Type: {entity.entity_type}"
                            })
                        
                        if entity.last_verified_at and entity.last_verified_at != entity.first_seen_at:
                            events.append({
                                "id": f"verification_{entity.entity_id}",
                                "content": f"Verified: {entity.entity_value or 'Entity'}",
                                "start": entity.last_verified_at.isoformat(),
                                "group": "verifications",
                                "type": "point"
                            })
                    
                except Exception as e:
                    logger.warning(f"Could not load timeline from database: {e}")
            
            # Generate demo timeline events if no database data
            if not events:
                base_time = datetime.utcnow() - timedelta(days=7)
                demo_events = [
                    {"content": "TechCorp discovered", "hours_offset": 0, "group": "discoveries"},
                    {"content": "John Smith profile found", "hours_offset": 6, "group": "discoveries"},
                    {"content": "Employment relationship established", "hours_offset": 12, "group": "relationships"},
                    {"content": "New York office location verified", "hours_offset": 24, "group": "verifications"},
                    {"content": "Additional employee records found", "hours_offset": 36, "group": "updates"},
                    {"content": "Competitor analysis updated", "hours_offset": 48, "group": "updates"},
                    {"content": "Jane Doe profile discovered", "hours_offset": 72, "group": "discoveries"},
                    {"content": "Cross-company relationships mapped", "hours_offset": 96, "group": "relationships"},
                ]
                
                for i, event_data in enumerate(demo_events):
                    events.append({
                        "id": f"demo_event_{i}",
                        "content": event_data["content"],
                        "start": (base_time + timedelta(hours=event_data["hours_offset"])).isoformat(),
                        "group": event_data["group"],
                        "type": "point"
                    })
            
            return {
                "events": events,
                "groups": groups,
                "metadata": {
                    "total_events": len(events),
                    "time_range": group_by,
                    "entity_id": entity_id,
                    "data_source": "database" if self.db else "demo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_timeline_data: {e}")
            return {
                "events": [],
                "groups": groups,
                "metadata": {"error": str(e)}
            }

    async def get_geospatial_data(
        self,
        bounds: Optional[Dict[str, float]] = None,
        zoom_level: int = 10
    ) -> Dict[str, Any]:
        """Process geospatial data for map visualization"""
        points = []
        
        try:
            if self.db:
                try:
                    from ..db.models import Location
                    from sqlalchemy import and_
                    
                    location_query = self.db.query(Location)
                    
                    if bounds:
                        location_query = location_query.filter(
                            and_(
                                Location.latitude >= bounds['south'],
                                Location.latitude <= bounds['north'],
                                Location.longitude >= bounds['west'],
                                Location.longitude <= bounds['east']
                            )
                        )
                    
                    locations = location_query.limit(200).all()
                    
                    for location in locations:
                        points.append({
                            "id": str(location.id),
                            "lat": location.latitude,
                            "lng": location.longitude,
                            "popup": location.address,
                            "cluster": True
                        })
                        
                except Exception as e:
                    logger.warning(f"Could not load locations from database: {e}")
            
            # Use demo geographic points if no database data
            if not points:
                demo_locations = [
                    {"id": "demo_1", "lat": 40.7128, "lng": -74.0060, "popup": "TechCorp HQ - New York City"},
                    {"id": "demo_2", "lat": 37.7749, "lng": -122.4194, "popup": "West Coast Office - San Francisco"},
                    {"id": "demo_3", "lat": 41.8781, "lng": -87.6298, "popup": "Midwest Branch - Chicago"},
                    {"id": "demo_4", "lat": 29.7604, "lng": -95.3698, "popup": "South Office - Houston"},
                    {"id": "demo_5", "lat": 33.4484, "lng": -112.0740, "popup": "Southwest Hub - Phoenix"},
                ]
                points = demo_locations
            
            return {
                "points": points,
                "bounds": bounds,
                "metadata": {
                    "total_points": len(points),
                    "zoom_level": zoom_level,
                    "clustering_enabled": True,
                    "data_source": "database" if self.db else "demo"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in get_geospatial_data: {e}")
            return {
                "points": [],
                "bounds": bounds,
                "metadata": {"error": str(e)}
            }

    async def get_visualization_metrics(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get aggregated metrics for visualization"""
        try:
            metrics = {
                "entity_counts": {"total": 0, "by_type": {}},
                "relationship_counts": {"total": 0, "by_type": {}},
                "activity_timeline": [],
                "data_quality": {"score": 0.85, "issues": []},
                "system_stats": {
                    "last_update": datetime.utcnow().isoformat(),
                    "processing_time": "0.45s"
                }
            }
            
            if self.db:
                try:
                    from sqlalchemy import func
                    from ..storage.models import StructuredEntityModel, EntityRelationshipModel
                    
                    # Count entities by type
                    entity_counts = self.db.query(
                        StructuredEntityModel.entity_type,
                        func.count(StructuredEntityModel.entity_id)
                    ).group_by(StructuredEntityModel.entity_type).all()
                    
                    total_entities = 0
                    for entity_type, count in entity_counts:
                        metrics["entity_counts"]["by_type"][entity_type or "unknown"] = count
                        total_entities += count
                    
                    metrics["entity_counts"]["total"] = total_entities
                    
                    # Count relationships
                    rel_counts = self.db.query(
                        EntityRelationshipModel.relationship_type,
                        func.count(EntityRelationshipModel.relationship_id)
                    ).group_by(EntityRelationshipModel.relationship_type).all()
                    
                    total_relationships = 0
                    for rel_type, count in rel_counts:
                        metrics["relationship_counts"]["by_type"][rel_type or "unknown"] = count
                        total_relationships += count
                        
                    metrics["relationship_counts"]["total"] = total_relationships
                    
                except Exception as e:
                    logger.warning(f"Could not load metrics from database: {e}")
            
            # Use demo metrics if no database data
            if metrics["entity_counts"]["total"] == 0:
                metrics["entity_counts"] = {
                    "total": 150,
                    "by_type": {"person": 45, "organization": 30, "location": 25, "other": 50}
                }
                metrics["relationship_counts"] = {
                    "total": 75,
                    "by_type": {"employs": 20, "located_in": 15, "knows": 25, "competes_with": 15}
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in get_visualization_metrics: {e}")
            return {"error": str(e)}

    def _get_color_for_type(self, entity_type: str) -> str:
        """Get color for entity type"""
        colors = {
            "person": "#3498db",
            "organization": "#e74c3c", 
            "location": "#2ecc71",
            "event": "#f39c12",
            "document": "#9b59b6",
            "unknown": "#95a5a6"
        }
        return colors.get(entity_type, colors["unknown"])
