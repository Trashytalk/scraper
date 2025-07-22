"""
Database Configuration and Connection Management
Enhanced with connection pooling and async support
"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read DATABASE_URL from environment, with fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

# Configure URLs based on database type
if DATABASE_URL.startswith("sqlite"):
    # For SQLite, use aiosqlite for async support
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
    SYNC_DATABASE_URL = DATABASE_URL
    logger.info("Using SQLite database configuration")
elif DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL databases
    SYNC_DATABASE_URL = DATABASE_URL
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    logger.info("Using PostgreSQL database configuration")
else:
    # Default fallback to SQLite for safety
    logger.warning(f"Unknown database URL format: {DATABASE_URL}, falling back to SQLite")
    DATABASE_URL = "sqlite:///data.db"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///data.db"
    SYNC_DATABASE_URL = "sqlite:///data.db"

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
        # Import models to ensure they exist
        from .models import Base
        
        async with get_async_session() as session:
            # Check if data already exists
            result = await session.execute(text("SELECT COUNT(*) FROM entities"))
            count = result.scalar() or 0
            
            if count > 0:
                logger.info("Database already contains data, skipping seed")
                return
            
            logger.info("🌱 Database seeding skipped - using existing models for compatibility")
            logger.info("✅ Database ready for use")
            
    except Exception as e:
        logger.error(f"❌ Failed to check initial data: {e}")
        # Don't raise - initialization can continue without seeding

async def check_database_health() -> dict:
    """
    Check database connectivity and performance
    Returns health status and metrics
    """
    try:
        async with get_async_session() as session:
            # Test basic connectivity
            result = await session.execute(text("SELECT 1"))
            
            # Get basic statistics
            entities_result = await session.execute(text("SELECT COUNT(*) FROM entities"))
            entities_count = entities_result.scalar() or 0
            
            connections_result = await session.execute(text("SELECT COUNT(*) FROM connections")) 
            connections_count = connections_result.scalar() or 0
            
            events_result = await session.execute(text("SELECT COUNT(*) FROM events"))
            events_count = events_result.scalar() or 0
            
            return {
                "status": "healthy",
                "database": os.path.basename(SYNC_DATABASE_URL) if SYNC_DATABASE_URL.startswith("sqlite") else "postgresql",
                "entities_count": entities_count,
                "connections_count": connections_count,
                "events_count": events_count,
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": os.path.basename(SYNC_DATABASE_URL) if SYNC_DATABASE_URL.startswith("sqlite") else "postgresql",
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
