"""
Comprehensive Unit Tests for Repository Fixes
Tests all major implementations added during the polish phase
"""

import asyncio
import os
import shutil
import sqlite3

# Test our new implementations
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

sys.path.append(".")
sys.path.append("config")
sys.path.append("business_intel_scraper/backend/queue")

from config.database_manager import DatabaseConnectionPool, initialize_database_pool
from config.environment import EnvironmentConfig, get_config, get_test_credentials
from config.logging_config import StructuredLogger, get_logger


class TestEnvironmentConfig(unittest.TestCase):
    """Test centralized configuration management"""

    def setUp(self):
        """Set up test environment"""
        self.config = EnvironmentConfig()

    def test_default_configuration(self):
        """Test default configuration values"""
        self.assertEqual(self.config.API_HOST, "localhost")
        self.assertEqual(self.config.API_PORT, 8000)
        self.assertEqual(self.config.FRONTEND_PORT, 5173)
        self.assertEqual(self.config.DEFAULT_USERNAME, "admin")

    def test_api_base_url(self):
        """Test API base URL generation"""
        expected_url = f"http://{self.config.API_HOST}:{self.config.API_PORT}"
        self.assertEqual(self.config.API_BASE_URL, expected_url)

    def test_frontend_url(self):
        """Test frontend URL generation"""
        expected_url = f"http://{self.config.FRONTEND_HOST}:{self.config.FRONTEND_PORT}"
        self.assertEqual(self.config.FRONTEND_URL, expected_url)

    def test_login_credentials(self):
        """Test login credentials generation"""
        credentials = self.config.get_login_credentials()
        self.assertIn("username", credentials)
        self.assertIn("password", credentials)
        self.assertEqual(credentials["username"], self.config.DEFAULT_USERNAME)

    def test_auth_headers(self):
        """Test authentication headers generation"""
        test_token = "test_token_123"
        headers = self.config.get_auth_headers(test_token)
        self.assertEqual(headers["Authorization"], f"Bearer {test_token}")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_environment_detection(self):
        """Test environment detection methods"""
        # Test development mode (default)
        self.assertTrue(self.config.is_development())
        self.assertFalse(self.config.is_production())

    @patch.dict(os.environ, {"API_HOST": "test.example.com", "API_PORT": "9000"})
    def test_environment_override(self):
        """Test environment variable override"""
        config = EnvironmentConfig()
        self.assertEqual(config.API_HOST, "test.example.com")
        self.assertEqual(config.API_PORT, 9000)


class TestStructuredLogging(unittest.TestCase):
    """Test structured logging system"""

    def setUp(self):
        """Set up test logging"""
        self.logger = get_logger("test", "DEBUG")

    def test_logger_creation(self):
        """Test logger creation and setup"""
        self.assertIsInstance(self.logger, StructuredLogger)
        self.assertEqual(self.logger.name, "test")

    def test_log_levels(self):
        """Test different log levels"""
        # These should not raise exceptions
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")

    def test_context_logging(self):
        """Test logging with context"""
        # Test with context parameters
        self.logger.info("Test message", user="admin", action="test")
        self.logger.error("Error message", error=Exception("Test error"))

    def test_message_formatting(self):
        """Test message formatting with context"""
        message = self.logger._format_message("Test", key1="value1", key2="value2")
        self.assertIn("Test", message)
        self.assertIn("key1=value1", message)
        self.assertIn("key2=value2", message)


class TestDatabaseConnectionPool(unittest.TestCase):
    """Test database connection pool management"""

    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.pool = DatabaseConnectionPool(self.db_path, max_connections=3)

    def tearDown(self):
        """Clean up test database"""
        self.pool.close()
        shutil.rmtree(self.temp_dir)

    def test_pool_initialization(self):
        """Test connection pool initialization"""
        self.assertTrue(os.path.exists(self.db_path))
        self.assertGreater(len(self.pool._connections), 0)
        self.assertLessEqual(len(self.pool._connections), 3)

    def test_connection_acquisition(self):
        """Test connection acquisition and release"""
        with self.pool.get_connection() as conn:
            self.assertIsInstance(conn, sqlite3.Connection)
            # Test basic query
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_query_execution(self):
        """Test query execution methods"""
        # Create test table
        self.pool.execute_update(
            """
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """
        )

        # Insert test data
        affected = self.pool.execute_update(
            "INSERT INTO test_table (name) VALUES (?)", ("test_name",)
        )
        self.assertEqual(affected, 1)

        # Query test data
        results = self.pool.execute_query("SELECT * FROM test_table")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "test_name")

    def test_batch_operations(self):
        """Test batch query execution"""
        # Create test table
        self.pool.execute_update(
            """
            CREATE TABLE batch_test (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """
        )

        # Batch insert
        data = [("value1",), ("value2",), ("value3",)]
        affected = self.pool.execute_many(
            "INSERT INTO batch_test (value) VALUES (?)", data
        )
        self.assertEqual(affected, 3)

    def test_connection_pool_stats(self):
        """Test connection pool statistics"""
        stats = self.pool.get_stats()

        self.assertIn("total_connections", stats)
        self.assertIn("active_connections", stats)
        self.assertIn("max_connections", stats)
        self.assertIn("total_queries", stats)
        self.assertIn("avg_query_time_ms", stats)

        self.assertEqual(stats["max_connections"], 3)
        self.assertGreaterEqual(stats["total_connections"], 1)

    def test_health_check(self):
        """Test database health check"""
        health = self.pool.health_check()

        self.assertEqual(health["status"], "healthy")
        self.assertTrue(health["database_accessible"])
        self.assertTrue(health["query_test"])
        self.assertIn("stats", health)


class TestSQLiteQueueManager(unittest.TestCase):
    """Test SQLite queue manager implementation"""

    def setUp(self):
        """Set up test queue manager"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "queue_test.db")

        # Import and initialize queue manager
        try:
            from distributed_crawler import SQLiteQueueManager

            self.queue_manager = SQLiteQueueManager(self.db_path)
        except ImportError:
            self.skipTest("SQLiteQueueManager not available")

    def tearDown(self):
        """Clean up test files"""
        if hasattr(self, "queue_manager"):
            self.queue_manager.close()
        shutil.rmtree(self.temp_dir)

    def test_queue_initialization(self):
        """Test queue manager initialization"""
        self.assertTrue(os.path.exists(self.db_path))

        # Test that tables were created
        stats = self.queue_manager.get_queue_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("frontier_queue", stats)
        self.assertIn("parse_queue", stats)

    def test_queue_stats(self):
        """Test queue statistics functionality"""
        stats = self.queue_manager.get_queue_stats()

        expected_keys = ["frontier_queue", "parse_queue", "retry_queue", "dead_queue"]
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIn("count", stats[key])


class TestSystemIntegration(unittest.TestCase):
    """Integration tests for all new systems"""

    def test_config_and_logging_integration(self):
        """Test configuration and logging work together"""
        config = get_config()
        logger = get_logger("integration_test")

        # Test that config values are accessible
        self.assertIsNotNone(config.API_BASE_URL)

        # Test that logging works
        logger.info("Integration test", api_url=config.API_BASE_URL)

        # Test credentials
        credentials = get_test_credentials()
        self.assertIn("username", credentials)
        self.assertIn("password", credentials)

    @patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test_integration.db"})
    def test_database_integration(self):
        """Test database integration with configuration"""
        # Initialize database pool
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "integration.db")

        try:
            pool = initialize_database_pool(db_path, max_connections=2)

            # Test database operations
            health = pool.health_check()
            self.assertEqual(health["status"], "healthy")

            # Test global functions
            from config.database_manager import (
                database_health_check,
                get_database_stats,
            )

            stats = get_database_stats()
            self.assertIn("total_connections", stats)

            health_global = database_health_check()
            self.assertEqual(health_global["status"], "healthy")

        finally:
            from config.database_manager import close_database_pool

            close_database_pool()
            shutil.rmtree(temp_dir)


def run_comprehensive_tests():
    """Run all unit tests and return results"""
    print("🧪 Running Comprehensive Unit Tests for Repository Fixes")
    print("=" * 60)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestEnvironmentConfig,
        TestStructuredLogging,
        TestDatabaseConnectionPool,
        TestSQLiteQueueManager,
        TestSystemIntegration,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestClass(test_class)
        suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 60)
    print(f"🧪 TEST SUMMARY:")
    print(f"   ✅ Tests Run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🚫 Errors: {len(result.errors)}")
    print(f"   ⏭️  Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun
    ) * 100
    print(f"   📊 Success Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("   🎉 ALL TESTS PASSED!")
    else:
        print("   ⚠️  Some tests failed - check output above")

    return result


if __name__ == "__main__":
    run_comprehensive_tests()
