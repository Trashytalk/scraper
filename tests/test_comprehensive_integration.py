"""
Comprehensive Integration Testing Suite for Business Intelligence Scraper

This module provides comprehensive integration tests that validate the interaction
between different components of the system, including database operations,
business logic integration, and end-to-end workflows.

Test Categories:
- Repository integration with database
- Business logic workflow testing
- Data pipeline integration
- Error handling and recovery
- Cross-component interaction validation

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

import os

# Local imports
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from business_intel_scraper.backend.db.centralized_data import (
    AlertRecord,
    Base,
    CentralizedDataRecord,
    DataAnalytics,
    DataConstants,
    DataDeduplication,
    DataRepository,
    SystemMetrics,
    create_tables,
    get_model_summary,
)

# === INTEGRATION TEST FIXTURES ===


@pytest.fixture(scope="session")
def integration_engine():
    """Create database engine for integration testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_tables(engine)
    return engine


@pytest.fixture(scope="function")
def integration_session(integration_engine):
    """Create fresh database session for each integration test"""
    Session = sessionmaker(bind=integration_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def integration_repository(integration_session):
    """Create repository instance for integration testing"""
    return DataRepository(integration_session)


@pytest.fixture
def sample_scraping_data():
    """Comprehensive sample data simulating real scraping results"""
    return {
        "basic_news_article": {
            "source_job_id": 1,
            "source_job_name": "news_scraper_cnn",
            "source_job_type": "news",
            "source_url": "https://cnn.com/politics/article-123",
            "source_domain": "cnn.com",
            "raw_data": {
                "html_content": "<article><h1>Breaking News</h1><p>Content...</p></article>",
                "metadata": {"author": "John Doe", "publish_date": "2025-07-24"},
                "images": ["https://cnn.com/image1.jpg", "https://cnn.com/image2.jpg"],
            },
            "extracted_text": "Breaking News: This is a comprehensive news article about current events with substantial content for analysis.",
            "title": "Breaking News: Major Political Development",
            "data_type": "news",
            "content_category": "politics",
            "language": "en",
            "word_count": 150,
            "link_count": 5,
            "image_count": 2,
            "scraped_at": datetime.utcnow(),
            "content_published_at": datetime.utcnow() - timedelta(hours=2),
            "view_count": 15000,
            "share_count": 250,
            "like_count": 1200,
            "comment_count": 85,
        },
        "ecommerce_product": {
            "source_job_id": 2,
            "source_job_name": "ecommerce_scraper_amazon",
            "source_job_type": "ecommerce",
            "source_url": "https://amazon.com/product/B08N5WRWNW",
            "source_domain": "amazon.com",
            "raw_data": {
                "product_details": {
                    "price": "$299.99",
                    "rating": 4.5,
                    "reviews_count": 1247,
                    "availability": "In Stock",
                },
                "specifications": {
                    "brand": "TechCorp",
                    "model": "TC-2025",
                    "category": "Electronics",
                },
            },
            "extracted_text": "High-quality electronic device with excellent features and customer reviews.",
            "title": "TechCorp TC-2025 Premium Electronic Device",
            "data_type": "ecommerce",
            "content_category": "electronics",
            "language": "en",
            "word_count": 45,
            "link_count": 3,
            "image_count": 8,
            "scraped_at": datetime.utcnow(),
            "view_count": 8500,
            "share_count": 120,
        },
    }


# === END-TO-END WORKFLOW INTEGRATION TESTS ===


class TestDataIngestionWorkflow:
    """Test complete data ingestion and processing workflow"""

    def test_complete_article_processing_workflow(
        self, integration_repository, sample_scraping_data
    ):
        """Test end-to-end article processing from ingestion to analytics"""
        # Step 1: Ingest article data
        article_data = sample_scraping_data["basic_news_article"]
        article = integration_repository.create_data_record(article_data)

        # Verify article creation
        assert article.id is not None
        assert article.record_uuid is not None
        assert article.content_hash is not None
        assert article.data_quality_score > 0
        assert article.validation_status in ["valid", "flagged", "pending"]

        # Step 2: Verify quality scoring
        assert article.completeness_score > 70  # Should have good completeness
        assert article.reliability_score > 0  # Should have some reliability score

        # Step 3: Test computed properties
        assert article.overall_quality_score > 0
        assert article.engagement_score > 0
        assert article.content_richness > 0

        # Step 4: Verify data integrity validation
        validation_result = article.validate_data_integrity()
        assert isinstance(validation_result, dict)
        assert "is_valid" in validation_result

        # Step 5: Test duplicate detection
        content_hash = article.content_hash
        duplicates = integration_repository.find_duplicates(content_hash)
        assert len(duplicates) == 1  # Should find itself
        assert duplicates[0].id == article.id

    def test_multi_source_data_aggregation(
        self, integration_repository, sample_scraping_data
    ):
        """Test aggregating data from multiple sources"""
        # Ingest data from multiple sources
        ingested_records = []
        for source_name, data in sample_scraping_data.items():
            record = integration_repository.create_data_record(data)
            ingested_records.append(record)

        assert len(ingested_records) == 2

        # Verify different data types are handled correctly
        data_types = [record.data_type for record in ingested_records]
        assert "news" in data_types
        assert "ecommerce" in data_types

        # Test cross-source analytics
        high_quality_records = integration_repository.get_high_quality_records(limit=10)
        # Should return records if any meet the quality threshold

        # Test source diversity
        unique_domains = set(record.source_domain for record in ingested_records)
        assert len(unique_domains) == 2  # Two different domains


class TestSystemMetricsIntegration:
    """Test system metrics collection and analysis integration"""

    def test_system_health_monitoring_workflow(self, integration_repository):
        """Test complete system health monitoring workflow"""
        # Step 1: Record initial system metrics
        initial_metrics = {
            "cpu_percent": Decimal("45.2"),
            "memory_percent": Decimal("62.8"),
            "avg_response_time_ms": Decimal("150.5"),
            "hostname": "app-server-01",
            "environment": "production",
            "active_scraping_jobs": 5,
            "completed_jobs_last_hour": 42,
            "failed_jobs_last_hour": 2,
            "requests_per_minute": Decimal("125.3"),
            "error_rate_percent": Decimal("0.8"),
        }

        initial_record = integration_repository.record_system_metrics(initial_metrics)
        assert initial_record.id is not None

        # Step 2: Record degraded performance metrics
        degraded_metrics = {
            "cpu_percent": Decimal("85.6"),
            "memory_percent": Decimal("78.3"),
            "avg_response_time_ms": Decimal("450.2"),
            "hostname": "app-server-01",
            "environment": "production",
            "active_scraping_jobs": 12,
            "completed_jobs_last_hour": 18,
            "failed_jobs_last_hour": 8,
            "requests_per_minute": Decimal("89.7"),
            "error_rate_percent": Decimal("3.2"),
        }

        degraded_record = integration_repository.record_system_metrics(degraded_metrics)

        # Step 3: Test health scoring
        assert initial_record.system_health_score > degraded_record.system_health_score
        assert degraded_record.resource_pressure_level in ["high", "critical"]
        assert initial_record.resource_pressure_level in ["low", "medium"]


class TestAlertManagementIntegration:
    """Test comprehensive alert management integration"""

    def test_alert_lifecycle_management(self, integration_repository):
        """Test complete alert lifecycle from creation to resolution"""
        # Step 1: Create initial alert
        alert_data = {
            "alert_type": "system",
            "severity": "critical",
            "category": "database_connection",
            "title": "Database Connection Pool Exhausted",
            "message": "All database connections are in use, new requests are being queued",
            "source_component": "database_monitor",
            "source_hostname": "db-server-01",
            "correlation_key": "db_connection_issues_2025_07_24",
        }

        alert = integration_repository.create_alert(alert_data)
        assert alert.status == "active"
        assert alert.occurrence_count == 1

        # Step 2: Create correlated alert (should increment occurrence count)
        correlated_alert = integration_repository.create_alert(alert_data)
        assert correlated_alert.id == alert.id  # Same alert
        assert correlated_alert.occurrence_count == 2

        # Step 3: Test alert retrieval and filtering
        active_alerts = integration_repository.get_active_alerts()
        assert len(active_alerts) >= 1

        critical_alerts = integration_repository.get_active_alerts(
            severity_filter="critical"
        )
        assert len(critical_alerts) >= 1
        assert alert in critical_alerts


class TestErrorHandlingIntegration:
    """Test error handling and recovery scenarios"""

    def test_database_constraint_error_handling(self, integration_repository):
        """Test handling of database constraint violations"""
        # Create record with specific UUID
        unique_uuid = str(uuid.uuid4())
        first_record = CentralizedDataRecord(
            record_uuid=unique_uuid, source_url="https://example.com/first"
        )
        integration_repository.session.add(first_record)
        integration_repository.session.commit()

        # Attempt to create duplicate UUID (should handle gracefully)
        duplicate_record = CentralizedDataRecord(
            record_uuid=unique_uuid, source_url="https://example.com/duplicate"
        )
        integration_repository.session.add(duplicate_record)

        with pytest.raises(IntegrityError):
            integration_repository.session.commit()

        # Verify session can recover
        integration_repository.session.rollback()

        # Should be able to create new record after rollback
        new_record = CentralizedDataRecord(
            source_url="https://example.com/new-after-error"
        )
        integration_repository.session.add(new_record)
        integration_repository.session.commit()

        assert new_record.id is not None

    def test_data_validation_error_recovery(self, integration_repository):
        """Test recovery from data validation errors"""
        # Create record with problematic data
        problematic_data = {
            "source_url": "",  # Empty URL
            "extracted_text": "x",  # Very short content
            "title": "",  # Empty title
            "word_count": -1,  # Invalid count
        }

        record = CentralizedDataRecord(**problematic_data)
        validation_result = record.validate_data_integrity()

        # Should detect validation errors
        assert not validation_result["is_valid"]
        assert len(validation_result["errors"]) > 0
        assert record.validation_status == "invalid"

        # Should still be able to save record for review
        integration_repository.session.add(record)
        integration_repository.session.commit()

        assert record.id is not None
        assert record.validation_status == "invalid"


class TestCrossComponentIntegration:
    """Test integration between different system components"""

    def test_repository_model_integration(
        self, integration_repository, sample_scraping_data
    ):
        """Test integration between repository and all model types"""
        # Test CentralizedDataRecord integration
        article_data = sample_scraping_data["basic_news_article"]
        article = integration_repository.create_data_record(article_data)

        # Test SystemMetrics integration
        metrics_data = {
            "cpu_percent": Decimal("75.0"),
            "memory_percent": Decimal("60.0"),
            "hostname": "test-server",
        }
        metrics = integration_repository.record_system_metrics(metrics_data)

        # Test AlertRecord integration
        alert_data = {
            "alert_type": "integration_test",
            "severity": "low",
            "title": "Integration Test Alert",
        }
        alert = integration_repository.create_alert(alert_data)

        # Test DataAnalytics integration
        analytics = integration_repository.create_analytics_snapshot(
            "daily", datetime.utcnow()
        )

        # Verify all records are created and accessible
        assert article.id is not None
        assert metrics.id is not None
        assert alert.id is not None
        assert analytics.id is not None

        # Test repository queries work across all models
        high_quality = integration_repository.get_high_quality_records()
        active_alerts = integration_repository.get_active_alerts()
        latest_analytics = integration_repository.get_latest_analytics("daily")

        # All queries should execute without errors
        assert isinstance(high_quality, list)
        assert isinstance(active_alerts, list)
        assert latest_analytics is not None


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
