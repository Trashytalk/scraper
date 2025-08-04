"""
Centralized Database Connection Management
Provides connection pooling, lifecycle management, and monitoring
"""

import asyncio
import logging
import sqlite3
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.logging_config import get_logger

logger = get_logger("database")


@dataclass
class ConnectionStats:
    """Connection statistics for monitoring"""

    total_connections: int = 0
    active_connections: int = 0
    max_connections: int = 10
    total_queries: int = 0
    failed_queries: int = 0
    avg_query_time: float = 0.0
    connection_errors: int = 0


class DatabaseConnectionPool:
    """Thread-safe SQLite connection pool with lifecycle management"""

    def __init__(self, database_path: str, max_connections: int = 10):
        self.database_path = database_path
        self.max_connections = max_connections
        self._connections: List[sqlite3.Connection] = []
        self._available_connections: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
        self._stats = ConnectionStats(max_connections=max_connections)

        # Ensure database directory exists
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize connection pool
        self._initialize_pool()

        logger.info(
            f"Database connection pool initialized",
            database=database_path,
            max_connections=max_connections,
        )

    def _initialize_pool(self):
        """Initialize the connection pool with base connections"""
        try:
            # Create initial connections (half of max)
            initial_connections = max(1, self.max_connections // 2)

            for _ in range(initial_connections):
                conn = self._create_connection()
                if conn:
                    self._connections.append(conn)
                    self._available_connections.append(conn)
                    self._stats.total_connections += 1

            logger.info(f"Initialized {len(self._connections)} database connections")

        except Exception as e:
            logger.error("Failed to initialize connection pool", error=e)
            raise

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection with optimal settings"""
        try:
            conn = sqlite3.connect(
                self.database_path,
                timeout=30.0,
                isolation_level=None,  # Autocommit mode
                check_same_thread=False,
            )

            # Optimize SQLite settings
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB

            conn.row_factory = sqlite3.Row  # Named column access

            return conn

        except Exception as e:
            logger.error("Failed to create database connection", error=e)
            self._stats.connection_errors += 1
            return None

    @contextmanager
    def get_connection(self):
        """Get a connection from the pool with automatic cleanup"""
        conn = None
        start_time = time.time()

        try:
            conn = self._acquire_connection()
            self._stats.active_connections += 1

            yield conn

        except Exception as e:
            self._stats.failed_queries += 1
            logger.error("Database operation failed", error=e)
            raise

        finally:
            if conn:
                self._release_connection(conn)
                self._stats.active_connections -= 1

                # Update query timing statistics
                query_time = time.time() - start_time
                self._update_query_stats(query_time)

    def _acquire_connection(self) -> sqlite3.Connection:
        """Acquire a connection from the pool"""
        with self._lock:
            # Try to get an available connection
            if self._available_connections:
                return self._available_connections.pop()

            # Create new connection if under limit
            if len(self._connections) < self.max_connections:
                conn = self._create_connection()
                if conn:
                    self._connections.append(conn)
                    self._stats.total_connections += 1
                    return conn

            # Wait for connection to become available
            logger.warning(
                "Connection pool exhausted, waiting for available connection"
            )

        # Retry after short wait
        time.sleep(0.1)
        return self._acquire_connection()

    def _release_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool"""
        with self._lock:
            if conn in self._connections:
                self._available_connections.append(conn)

    def _update_query_stats(self, query_time: float):
        """Update query timing statistics"""
        self._stats.total_queries += 1

        # Calculate rolling average
        if self._stats.total_queries == 1:
            self._stats.avg_query_time = query_time
        else:
            alpha = 0.1  # Smoothing factor
            self._stats.avg_query_time = (
                alpha * query_time + (1 - alpha) * self._stats.avg_query_time
            )

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor.fetchall()

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            return cursor.rowcount

    def execute_many(self, query: str, param_list: List[tuple]) -> int:
        """Execute multiple queries with different parameters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, param_list)
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self._lock:
            return {
                "total_connections": self._stats.total_connections,
                "active_connections": self._stats.active_connections,
                "available_connections": len(self._available_connections),
                "max_connections": self._stats.max_connections,
                "total_queries": self._stats.total_queries,
                "failed_queries": self._stats.failed_queries,
                "avg_query_time_ms": round(self._stats.avg_query_time * 1000, 2),
                "connection_errors": self._stats.connection_errors,
                "pool_utilization": round(
                    (self._stats.active_connections / self._stats.max_connections)
                    * 100,
                    1,
                ),
            }

    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the connection pool"""
        try:
            # Test basic query
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            stats = self.get_stats()

            return {
                "status": "healthy",
                "database_accessible": True,
                "query_test": result is not None,
                "stats": stats,
            }

        except Exception as e:
            logger.error("Database health check failed", error=e)
            return {
                "status": "unhealthy",
                "database_accessible": False,
                "error": str(e),
                "stats": self.get_stats(),
            }

    def close(self):
        """Close all connections in the pool"""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.error("Error closing database connection", error=e)

            self._connections.clear()
            self._available_connections.clear()

        logger.info("Database connection pool closed")


# Global connection pool instance
_connection_pool: Optional[DatabaseConnectionPool] = None


def initialize_database_pool(
    database_path: str, max_connections: int = 10
) -> DatabaseConnectionPool:
    """Initialize the global database connection pool"""
    global _connection_pool

    if _connection_pool is None:
        _connection_pool = DatabaseConnectionPool(database_path, max_connections)
        logger.info("Global database connection pool initialized")

    return _connection_pool


def get_database_pool() -> DatabaseConnectionPool:
    """Get the global database connection pool"""
    if _connection_pool is None:
        raise RuntimeError(
            "Database pool not initialized. Call initialize_database_pool() first."
        )

    return _connection_pool


def execute_query(query: str, params: Optional[tuple] = None) -> List[sqlite3.Row]:
    """Execute a SELECT query using the global pool"""
    return get_database_pool().execute_query(query, params)


def execute_update(query: str, params: Optional[tuple] = None) -> int:
    """Execute an INSERT/UPDATE/DELETE query using the global pool"""
    return get_database_pool().execute_update(query, params)


def get_database_stats() -> Dict[str, Any]:
    """Get database connection statistics"""
    return get_database_pool().get_stats()


def database_health_check() -> Dict[str, Any]:
    """Perform database health check"""
    return get_database_pool().health_check()


def close_database_pool():
    """Close the global database connection pool"""
    global _connection_pool

    if _connection_pool:
        _connection_pool.close()
        _connection_pool = None
        logger.info("Global database connection pool closed")
