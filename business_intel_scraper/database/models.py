"""
Database Models for Visual Analytics Platform
Enhanced with comprehensive entity relationships and metadata
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Entity(Base, TimestampMixin):
    """Core entity table for all network nodes"""
    __tablename__ = "entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label = Column(String(255), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # person, organization, location, etc.
    confidence = Column(Float, nullable=False, default=0.5)
    properties = Column(JSON, default=dict)
    
    # Metadata
    source = Column(String(100))  # data source identifier
    external_id = Column(String(255))  # original ID from source system
    status = Column(String(20), default='active')  # active, inactive, archived
    
    # Relationships
    source_connections = relationship("Connection", foreign_keys="Connection.source_id", back_populates="source_entity")
    target_connections = relationship("Connection", foreign_keys="Connection.target_id", back_populates="target_entity")
    events = relationship("Event", back_populates="entity")
    locations = relationship("Location", back_populates="entity")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, label={self.label}, type={self.entity_type})>"

class Connection(Base, TimestampMixin):
    """Relationships/edges between entities"""
    __tablename__ = "connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False, index=True)
    
    relationship_type = Column(String(50), nullable=False, index=True)  # connected_to, owns, etc.
    weight = Column(Float, default=1.0)
    confidence = Column(Float, nullable=False, default=0.5)
    direction = Column(String(20), default='undirected')  # directed, undirected
    
    # Metadata
    properties = Column(JSON, default=dict)
    source = Column(String(100))
    status = Column(String(20), default='active')
    
    # Relationships
    source_entity = relationship("Entity", foreign_keys=[source_id], back_populates="source_connections")
    target_entity = relationship("Entity", foreign_keys=[target_id], back_populates="target_connections")
    
    def __repr__(self):
        return f"<Connection(id={self.id}, type={self.relationship_type}, weight={self.weight})>"

class Event(Base, TimestampMixin):
    """Timeline events associated with entities"""
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), index=True)
    
    # Temporal data
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, index=True)
    duration_minutes = Column(Integer)
    
    # Metadata
    confidence = Column(Float, nullable=False, default=0.5)
    properties = Column(JSON, default=dict)
    source = Column(String(100))
    external_id = Column(String(255))
    status = Column(String(20), default='active')
    
    # Relationships
    entity = relationship("Entity", back_populates="events")
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, type={self.event_type})>"

class Location(Base, TimestampMixin):
    """Geospatial data points associated with entities"""
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    location_type = Column(String(50), nullable=False, index=True)  # office, residence, meeting, etc.
    
    # Coordinates
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    altitude = Column(Float)
    
    # Address components
    address = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100), index=True)
    country = Column(String(100), index=True)
    postal_code = Column(String(20))
    
    # Metadata
    confidence = Column(Float, nullable=False, default=0.5)
    properties = Column(JSON, default=dict)
    source = Column(String(100))
    external_id = Column(String(255))
    status = Column(String(20), default='active')
    
    # Relationships
    entity = relationship("Entity", back_populates="locations")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, type={self.location_type})>"

class DataSource(Base, TimestampMixin):
    """Track data sources and ingestion metadata"""
    __tablename__ = "data_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    source_type = Column(String(50), nullable=False)  # scraper, api, manual, etc.
    
    # Connection details
    config = Column(JSON, default=dict)  # connection parameters, credentials, etc.
    
    # Status tracking
    status = Column(String(20), default='active')  # active, inactive, error
    last_sync = Column(DateTime)
    next_sync = Column(DateTime)
    sync_frequency = Column(String(50))  # hourly, daily, weekly, etc.
    
    # Metrics
    total_records = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    error_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name}, type={self.source_type})>"

class SearchQuery(Base, TimestampMixin):
    """Track user search queries and analytics"""
    __tablename__ = "search_queries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(100))  # user identifier
    session_id = Column(String(100))  # session identifier
    
    # Query details
    query_text = Column(Text)
    filters = Column(JSON, default=dict)
    result_count = Column(Integer)
    execution_time_ms = Column(Float)
    
    # Analytics
    clicked_results = Column(JSON, default=list)  # track which results were clicked
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query={self.query_text[:50]}...)>"

# Indexes for performance optimization
from sqlalchemy import Index

# Composite indexes for common query patterns
Index('idx_entity_type_status', Entity.entity_type, Entity.status)
Index('idx_connection_entities', Connection.source_id, Connection.target_id)
Index('idx_event_entity_date', Event.entity_id, Event.start_date)
Index('idx_location_entity_type', Location.entity_id, Location.location_type)
Index('idx_location_coords', Location.latitude, Location.longitude)
