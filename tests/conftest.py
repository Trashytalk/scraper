"""
Test Configuration and Fixtures for Business Intelligence Scraper

This module provides shared test fixtures, configuration, and utilities
for the comprehensive testing suite.

Features:
- Database test fixtures
- Mock service configurations
- Test data generators
- Security test utilities
- Performance test helpers
- API test clients

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

import asyncio
import json
import os
import shutil

# Local imports
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Generator, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Database and ORM imports
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from business_intel_scraper.backend.db.centralized_data import (
    AlertRecord,
    Base,
    CentralizedDataRecord,
    DataAnalytics,
    DataDeduplication,
    DataRepository,
    SystemMetrics,
    create_tables,
)

# === PYTEST CONFIGURATION ===


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Register custom markers
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "security: mark test as security test")
    config.addinivalue_line("markers", "performance: mark test as performance test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names"""
    for item in items:
        # Add slow marker to tests that typically take longer
        if any(
            keyword in item.name.lower()
            for keyword in ["load", "performance", "stress", "bulk"]
        ):
            item.add_marker(pytest.mark.slow)

        # Add integration marker to integration tests
        if "integration" in item.name.lower() or "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add security marker to security tests
        if "security" in item.name.lower() or "test_security" in str(item.fspath):
            item.add_marker(pytest.mark.security)

        # Add performance marker to performance tests
        if "performance" in item.name.lower() or "test_performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)


# === SHARED TEST FIXTURES ===


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_database_engine():
    """Create test database engine for the session"""
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )

    # Create all tables
    create_tables(engine)

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_database_engine):
    """Create fresh database session for each test"""
    Session = sessionmaker(bind=test_database_engine)
    session = Session()

    yield session

    # Cleanup
    session.rollback()
    session.close()


@pytest.fixture
def test_repository(test_session):
    """Create repository instance for testing"""
    return DataRepository(test_session)


@pytest.fixture
def temp_directory():
    """Create temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_external_services():
    """Mock external services for testing"""
    mocks = {
        "http_client": Mock(),
        "email_service": Mock(),
        "notification_service": Mock(),
        "cache_service": Mock(),
        "file_storage": Mock(),
        "analytics_service": Mock(),
    }

    # Configure common mock behaviors
    mocks["http_client"].get.return_value.status_code = 200
    mocks["http_client"].get.return_value.json.return_value = {"status": "success"}
    mocks["email_service"].send_email.return_value = True
    mocks["notification_service"].send_notification.return_value = {"sent": True}

    yield mocks


# === TEST DATA GENERATORS ===


@pytest.fixture
def sample_scraping_data():
    """Generate comprehensive sample scraping data"""
    base_time = datetime.utcnow()

    return {
        "news_article": {
            "source_job_id": 1,
            "source_job_name": "cnn_news_scraper",
            "source_job_type": "news",
            "source_url": "https://cnn.com/2025/07/24/politics/breaking-news",
            "source_domain": "cnn.com",
            "raw_data": {
                "html": "<article><h1>Breaking News</h1><p>Important news content...</p></article>",
                "metadata": {
                    "author": "Jane Reporter",
                    "publish_date": "2025-07-24T10:30:00Z",
                    "tags": ["politics", "breaking", "government"],
                },
                "images": [
                    "https://cnn.com/images/breaking-news-1.jpg",
                    "https://cnn.com/images/breaking-news-2.jpg",
                ],
            },
            "extracted_text": "Breaking News: Major political development announced today with significant implications for policy changes.",
            "title": "Breaking: Major Political Development Announced",
            "description": "Comprehensive coverage of todays major political announcement",
            "data_type": "news",
            "content_category": "politics",
            "language": "en",
            "word_count": 150,
            "link_count": 8,
            "image_count": 2,
            "video_count": 1,
            "scraped_at": base_time,
            "content_published_at": base_time - timedelta(hours=1),
            "view_count": 25000,
            "share_count": 450,
            "like_count": 1800,
            "comment_count": 150,
        },
        "blog_post": {
            "source_job_id": 2,
            "source_job_name": "tech_blog_scraper",
            "source_job_type": "blog",
            "source_url": "https://techblog.example.com/ai-trends-2025",
            "source_domain": "techblog.example.com",
            "raw_data": {
                "blog_metadata": {
                    "author": "Dr. Tech Expert",
                    "category": "Technology",
                    "reading_time": "12 minutes",
                    "tags": ["AI", "Machine Learning", "Technology Trends"],
                }
            },
            "extracted_text": "Comprehensive analysis of artificial intelligence trends for 2025, covering machine learning advances, industry applications, and future predictions with detailed technical insights.",
            "title": "AI Trends 2025: The Future of Machine Learning",
            "data_type": "blog",
            "content_category": "technology",
            "language": "en",
            "word_count": 3200,
            "link_count": 25,
            "image_count": 6,
            "scraped_at": base_time - timedelta(hours=2),
            "view_count": 5600,
            "share_count": 280,
            "like_count": 920,
        },
        "ecommerce_product": {
            "source_job_id": 3,
            "source_job_name": "amazon_product_scraper",
            "source_job_type": "ecommerce",
            "source_url": "https://amazon.com/dp/B08N5WRWNW",
            "source_domain": "amazon.com",
            "raw_data": {
                "product_info": {
                    "price": "$299.99",
                    "original_price": "$399.99",
                    "discount": "25%",
                    "rating": 4.5,
                    "review_count": 2347,
                    "availability": "In Stock",
                    "shipping": "Free Prime Shipping",
                },
                "product_details": {
                    "brand": "TechCorp",
                    "model": "TC-2025-Pro",
                    "category": "Electronics > Computers > Laptops",
                    "specifications": {
                        "processor": "Intel i7",
                        "memory": "16GB RAM",
                        "storage": "512GB SSD",
                    },
                },
            },
            "extracted_text": "TechCorp TC-2025-Pro laptop with high-performance specifications, excellent customer reviews, and competitive pricing.",
            "title": "TechCorp TC-2025-Pro High-Performance Laptop",
            "data_type": "ecommerce",
            "content_category": "electronics",
            "language": "en",
            "word_count": 85,
            "link_count": 12,
            "image_count": 15,
            "scraped_at": base_time - timedelta(hours=3),
            "view_count": 12000,
            "share_count": 95,
        },
    }


@pytest.fixture
def sample_system_metrics():
    """Generate sample system metrics data"""
    return {
        "current_metrics": {
            "cpu_percent": Decimal("65.4"),
            "memory_percent": Decimal("72.1"),
            "disk_percent": Decimal("45.8"),
            "avg_response_time_ms": Decimal("245.6"),
            "hostname": "app-server-prod-01",
            "environment": "production",
            "active_scraping_jobs": 8,
            "completed_jobs_last_hour": 156,
            "failed_jobs_last_hour": 3,
            "requests_per_minute": Decimal("387.2"),
            "error_rate_percent": Decimal("1.2"),
            "database_connections": 45,
            "cache_hit_rate": Decimal("94.6"),
        },
        "degraded_metrics": {
            "cpu_percent": Decimal("89.7"),
            "memory_percent": Decimal("91.3"),
            "disk_percent": Decimal("78.4"),
            "avg_response_time_ms": Decimal("1250.8"),
            "hostname": "app-server-prod-01",
            "environment": "production",
            "active_scraping_jobs": 25,
            "completed_jobs_last_hour": 67,
            "failed_jobs_last_hour": 18,
            "requests_per_minute": Decimal("156.3"),
            "error_rate_percent": Decimal("8.4"),
            "database_connections": 98,
            "cache_hit_rate": Decimal("67.2"),
        },
    }


@pytest.fixture
def sample_alerts():
    """Generate sample alert data"""
    return {
        "critical_alert": {
            "alert_type": "system",
            "severity": "critical",
            "category": "performance",
            "title": "Critical System Performance Degradation",
            "message": "System performance has degraded significantly with high CPU and memory usage",
            "source_component": "system_monitor",
            "source_hostname": "app-server-prod-01",
            "source_metric_name": "cpu_percent",
            "source_metric_value": Decimal("89.7"),
            "threshold_value": Decimal("85.0"),
            "correlation_key": "perf_degradation_2025_07_24",
            "affected_users": 500,
            "sla_breach": True,
            "escalation_level": 0,
            "notification_channels": ["email", "slack", "sms", "webhook"],
        },
        "warning_alert": {
            "alert_type": "quality",
            "severity": "medium",
            "category": "data_quality",
            "title": "Data Quality Score Below Threshold",
            "message": "Average data quality score has dropped below acceptable threshold",
            "source_component": "data_quality_monitor",
            "source_metric_name": "avg_quality_score",
            "source_metric_value": Decimal("72.3"),
            "threshold_value": Decimal("75.0"),
            "correlation_key": "quality_drop_2025_07_24",
        },
        "info_alert": {
            "alert_type": "operational",
            "severity": "low",
            "category": "maintenance",
            "title": "Scheduled Maintenance Window Starting",
            "message": "Scheduled maintenance window will begin in 30 minutes",
            "source_component": "maintenance_scheduler",
            "correlation_key": "maintenance_2025_07_24_22_00",
        },
    }


# === PERFORMANCE TEST HELPERS ===


@pytest.fixture
def performance_timer():
    """Performance timing context manager"""

    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration = None

        def __enter__(self):
            self.start_time = datetime.utcnow()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.end_time = datetime.utcnow()
            self.duration = (self.end_time - self.start_time).total_seconds()

        def assert_faster_than(self, max_seconds: float):
            """Assert that operation completed faster than specified time"""
            assert self.duration is not None, "Timer not properly used"
            assert (
                self.duration < max_seconds
            ), f"Operation took {self.duration}s, expected < {max_seconds}s"

    return PerformanceTimer


@pytest.fixture
def bulk_test_data_generator():
    """Generate bulk test data for performance testing"""

    def generate_records(count: int, data_type: str = "news") -> List[Dict[str, Any]]:
        """Generate specified number of test records"""
        records = []
        base_time = datetime.utcnow()

        for i in range(count):
            record = {
                "source_job_id": i % 10 + 1,
                "source_job_name": f"test_scraper_{i % 5}",
                "source_job_type": data_type,
                "source_url": f"https://example.com/article-{i}",
                "source_domain": f"site-{i % 3}.com",
                "raw_data": {
                    "content": f"Test content for article {i}",
                    "metadata": {"article_id": i},
                },
                "extracted_text": f"This is test content for article number {i} with some meaningful text.",
                "title": f"Test Article {i}: Sample Title",
                "data_type": data_type,
                "content_category": ["technology", "science", "business"][i % 3],
                "language": "en",
                "word_count": 50 + (i % 100),
                "link_count": i % 10,
                "image_count": i % 5,
                "scraped_at": base_time - timedelta(hours=i % 24),
                "view_count": 1000 + (i * 50),
                "share_count": 10 + (i % 50),
            }
            records.append(record)

        return records

    return generate_records


# === SECURITY TEST UTILITIES ===


@pytest.fixture
def security_test_utils():
    """Security testing utilities"""

    class SecurityTestUtils:
        @staticmethod
        def generate_malicious_payloads(payload_type: str) -> List[str]:
            """Generate malicious payloads for testing"""
            payloads = {
                "sql_injection": [
                    "'; DROP TABLE users; --",
                    "1' OR '1'='1",
                    "admin'--",
                    "' UNION SELECT * FROM information_schema.tables--",
                ],
                "xss": [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "javascript:alert('XSS')",
                    "<svg onload=alert('XSS')>",
                ],
                "path_traversal": [
                    "../../../etc/passwd",
                    "..\\..\\..\\windows\\system32\\config\\sam",
                    "....//....//....//etc//passwd",
                ],
            }
            return payloads.get(payload_type, [])

        @staticmethod
        def create_test_user_credentials() -> Dict[str, str]:
            """Create test user credentials"""
            return {
                "username": f"testuser_{uuid.uuid4().hex[:8]}",
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "TestP@ssw0rd123!",
            }

    return SecurityTestUtils


# === API TEST FIXTURES ===


@pytest.fixture
async def mock_api_client():
    """Mock API client for testing"""

    class MockAPIClient:
        def __init__(self):
            self.responses = {}
            self.requests_made = []

        def set_response(
            self, endpoint: str, response_data: Dict[str, Any], status_code: int = 200
        ):
            """Set mock response for endpoint"""
            self.responses[endpoint] = {
                "data": response_data,
                "status_code": status_code,
            }

        async def get(self, endpoint: str, **kwargs):
            """Mock GET request"""
            self.requests_made.append(("GET", endpoint, kwargs))
            return self.responses.get(endpoint, {"data": {}, "status_code": 404})

        async def post(self, endpoint: str, **kwargs):
            """Mock POST request"""
            self.requests_made.append(("POST", endpoint, kwargs))
            return self.responses.get(endpoint, {"data": {}, "status_code": 200})

    return MockAPIClient()


# === DATABASE TEST UTILITIES ===


@pytest.fixture
def database_test_utils(test_session):
    """Database testing utilities"""

    class DatabaseTestUtils:
        def __init__(self, session: Session):
            self.session = session

        def create_test_records(self, count: int = 10) -> List[CentralizedDataRecord]:
            """Create test data records"""
            records = []
            for i in range(count):
                record = CentralizedDataRecord(
                    source_url=f"https://test-{i}.com/article",
                    title=f"Test Article {i}",
                    extracted_text=f"Test content for article {i}",
                    data_type="test",
                    word_count=50 + i,
                )
                records.append(record)

            self.session.add_all(records)
            self.session.commit()
            return records

        def verify_record_count(
            self, expected_count: int, model_class=CentralizedDataRecord
        ):
            """Verify number of records in database"""
            actual_count = self.session.query(model_class).count()
            assert (
                actual_count == expected_count
            ), f"Expected {expected_count} records, found {actual_count}"

        def cleanup_test_data(self):
            """Clean up test data"""
            self.session.query(CentralizedDataRecord).delete()
            self.session.query(DataAnalytics).delete()
            self.session.query(SystemMetrics).delete()
            self.session.query(AlertRecord).delete()
            self.session.query(DataDeduplication).delete()
            self.session.commit()

    return DatabaseTestUtils(test_session)


# === CLEANUP FIXTURES ===


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test"""
    yield
    # Cleanup code runs after test
    # Clear any global state, temporary files, etc.
    pass
