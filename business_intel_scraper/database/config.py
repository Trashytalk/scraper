"""
Database Configuration and Connection Management
Enhanced with connection pooling and async support
"""

import os
from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

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
    logger.warning(
        f"Unknown database URL format: {DATABASE_URL}, falling back to SQLite"
    )
    DATABASE_URL = "sqlite:///data.db"
    ASYNC_DATABASE_URL = "sqlite+aiosqlite:///data.db"
    SYNC_DATABASE_URL = "sqlite:///data.db"

# Async Engine with enhanced connection pooling and optimization
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=25,  # Increased pool size for better concurrency
    max_overflow=40,  # Higher overflow for peak loads
    pool_timeout=45,  # Longer timeout for high-load scenarios
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before use
    pool_reset_on_return="commit",  # Reset connection state on return
    echo=os.getenv("DEBUG", "false").lower() == "true",  # Log SQL queries in debug mode
    # Performance optimizations
    future=True,  # Use SQLAlchemy 2.0 style
    connect_args={
        "command_timeout": 60,  # Query timeout
        "server_settings": {
            "jit": "off",  # For PostgreSQL, disable JIT for faster startup
            "application_name": "business_intel_scraper",
        }
    } if ASYNC_DATABASE_URL.startswith("postgresql") else {
        "check_same_thread": False,  # For SQLite
        "timeout": 30,
    }
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

        async with get_async_session() as session:
            # Check if data already exists
            result = await session.execute(text("SELECT COUNT(*) FROM entities"))
            count = result.scalar() or 0

            if count > 0:
                logger.info("Database already contains data, skipping seed")
                return

            logger.info(
                "🌱 Database seeding skipped - using existing models for compatibility"
            )
            logger.info("✅ Database ready for use")

    except Exception as e:
        logger.error(f"❌ Failed to check initial data: {e}")
        # Don't raise - initialization can continue without seeding


async def get_database_health() -> Dict[str, Any]:
    """Get comprehensive database health metrics"""
    health_info = {
        "status": "unknown",
        "connection_pool": {},
        "performance": {},
        "error": None
    }
    
    try:
        # Test basic connectivity
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            health_info["status"] = "healthy"
        
        # Connection pool information
        pool = async_engine.pool
        health_info["connection_pool"] = {
            "pool_size": getattr(pool, '_pool_size', 25),
            "current_connections": getattr(pool, '_current_checked_in', 0),
            "overflow_connections": getattr(pool, '_current_overflow', 0),
            "pool_status": "active" if pool else "inactive",
        }
        
        # Performance metrics
        health_info["performance"] = {
            "database_url_type": "postgresql" if ASYNC_DATABASE_URL.startswith("postgresql") else "sqlite",
            "pool_timeout": 45,
            "pool_recycle_hours": 1,
        }
        
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_info


async def optimize_database_settings():
    """Apply database-specific optimization settings"""
    try:
        async with AsyncSessionLocal() as session:
            if ASYNC_DATABASE_URL.startswith("postgresql"):
                # PostgreSQL optimizations
                optimizations = [
                    "SET work_mem = '256MB'",  # Increase work memory for complex queries
                    "SET maintenance_work_mem = '512MB'",  # Increase maintenance memory
                    "SET effective_cache_size = '1GB'",  # Assume 1GB available for caching
                    "SET random_page_cost = 1.1",  # SSD-optimized random access cost
                    "SET checkpoint_completion_target = 0.9",  # Spread checkpoints
                ]
                
                for optimization in optimizations:
                    try:
                        await session.execute(text(optimization))
                        logger.debug(f"Applied optimization: {optimization}")
                    except Exception as e:
                        logger.warning(f"Failed to apply optimization '{optimization}': {e}")
                        
            elif ASYNC_DATABASE_URL.startswith("sqlite"):
                # SQLite optimizations
                optimizations = [
                    "PRAGMA journal_mode = WAL",  # Write-Ahead Logging for better concurrency
                    "PRAGMA synchronous = NORMAL",  # Balance between safety and performance
                    "PRAGMA cache_size = 10000",  # Increase cache size
                    "PRAGMA temp_store = MEMORY",  # Store temporary tables in memory
                    "PRAGMA mmap_size = 268435456",  # 256MB memory-mapped I/O
                ]
                
                for optimization in optimizations:
                    try:
                        await session.execute(text(optimization))
                        logger.debug(f"Applied optimization: {optimization}")
                    except Exception as e:
                        logger.warning(f"Failed to apply optimization '{optimization}': {e}")
            
            await session.commit()
            logger.info("Database optimizations applied successfully")
            
    except Exception as e:
        logger.error(f"Failed to apply database optimizations: {e}")


# Initialize database optimizations on import
import asyncio

def _apply_optimizations():
    """Apply database optimizations asynchronously"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, schedule the optimization
            loop.create_task(optimize_database_settings())
        else:
            # If no loop is running, run it directly
            asyncio.run(optimize_database_settings())
    except Exception as e:
        logger.warning(f"Could not apply database optimizations on import: {e}")

# Apply optimizations when module is imported
_apply_optimizations()


# Export for easy imports
__all__ = [
    "async_engine",
    "AsyncSessionLocal", 
    "get_async_session",
    "get_database_health",
    "optimize_database_settings"
]
