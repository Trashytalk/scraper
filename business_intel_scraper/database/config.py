"""
Database Configuration and Connection Management
Enhanced with connection pooling and async support
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "visual_analytics"),
    "username": os.getenv("DB_USER", "va_user"),
    "password": os.getenv("DB_PASSWORD", "secure_password_123"),
}

# Connection URLs
SYNC_DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Async Engine with connection pooling
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=os.getenv("DEBUG", "false").lower() == "true",  # Log SQL queries in debug mode
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# Synchronous Engine (for migrations and admin tasks)
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    echo=os.getenv("DEBUG", "false").lower() == "true",
)

# Sync Session Factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions
    Ensures proper cleanup and error handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

def get_sync_session():
    """
    Generator function for synchronous database sessions
    Used with FastAPI dependency injection
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

async def init_database():
    """
    Initialize database tables and perform setup
    """
    try:
        from .models import Base
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
        
        # Perform initial data seeding if needed
        await seed_initial_data()
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

async def seed_initial_data():
    """
    Seed the database with initial data for development/testing
    """
    try:
        from .models import Entity, Connection, Event, Location, DataSource
        
        async with get_async_session() as session:
            # Check if data already exists
            result = await session.execute("SELECT COUNT(*) FROM entities")
            count = result.scalar()
            
            if count > 0:
                logger.info("Database already contains data, skipping seed")
                return
            
            logger.info("🌱 Seeding initial database data...")
            
            # Create sample entities
            sample_entities = [
                Entity(
                    label="John Doe",
                    entity_type="person",
                    confidence=0.9,
                    properties={"role": "analyst", "department": "finance"},
                    source="seed_data"
                ),
                Entity(
                    label="TechCorp Inc",
                    entity_type="organization", 
                    confidence=0.95,
                    properties={"industry": "technology", "employees": 500},
                    source="seed_data"
                ),
                Entity(
                    label="New York Office",
                    entity_type="location",
                    confidence=0.85,
                    properties={"type": "office", "capacity": 200},
                    source="seed_data"
                ),
            ]
            
            session.add_all(sample_entities)
            await session.flush()  # Get IDs without committing
            
            # Create sample connections
            sample_connection = Connection(
                source_id=sample_entities[0].id,
                target_id=sample_entities[1].id,
                relationship_type="works_for",
                weight=0.8,
                confidence=0.9,
                properties={"start_date": "2023-01-01"},
                source="seed_data"
            )
            
            session.add(sample_connection)
            
            # Create sample event
            sample_event = Event(
                entity_id=sample_entities[0].id,
                title="Team Meeting",
                description="Weekly team sync meeting",
                event_type="meeting",
                category="work",
                start_date=datetime.now(),
                confidence=0.8,
                properties={"attendees": 5, "duration": 60},
                source="seed_data"
            )
            
            session.add(sample_event)
            
            # Create sample location
            sample_location = Location(
                entity_id=sample_entities[2].id,
                name="TechCorp NY Office",
                location_type="office",
                latitude=40.7128,
                longitude=-74.0060,
                address="123 Broadway, New York, NY 10001",
                city="New York",
                state="New York",
                country="USA",
                confidence=0.95,
                source="seed_data"
            )
            
            session.add(sample_location)
            
            # Create sample data source
            sample_source = DataSource(
                name="manual_seed",
                description="Initial seed data for development",
                source_type="manual",
                config={"created_by": "system"},
                status="active",
                total_records=len(sample_entities)
            )
            
            session.add(sample_source)
            
        logger.info("✅ Initial data seeded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to seed initial data: {e}")
        raise

async def check_database_health() -> dict:
    """
    Check database connectivity and performance
    Returns health status and metrics
    """
    try:
        async with get_async_session() as session:
            # Test basic connectivity
            result = await session.execute("SELECT 1")
            
            # Get basic statistics
            entities_result = await session.execute("SELECT COUNT(*) FROM entities")
            entities_count = entities_result.scalar() or 0
            
            connections_result = await session.execute("SELECT COUNT(*) FROM connections") 
            connections_count = connections_result.scalar() or 0
            
            events_result = await session.execute("SELECT COUNT(*) FROM events")
            events_count = events_result.scalar() or 0
            
            return {
                "status": "healthy",
                "database": DATABASE_CONFIG["database"],
                "host": DATABASE_CONFIG["host"],
                "entities_count": entities_count,
                "connections_count": connections_count,
                "events_count": events_count,
                "connection_pool": {
                    "size": async_engine.pool.size(),
                    "overflow": async_engine.pool.overflow(),
                    "invalid": async_engine.pool.invalidated(),
                }
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": DATABASE_CONFIG["database"],
            "host": DATABASE_CONFIG["host"],
        }

# Export for easy imports
__all__ = [
    "get_async_session",
    "get_sync_session", 
    "init_database",
    "check_database_health",
    "async_engine",
    "sync_engine",
]
