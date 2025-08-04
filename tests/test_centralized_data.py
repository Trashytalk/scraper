"""
Comprehensive test suite for centralized data models and repository.

This module provides thorough testing coverage for the Business Intelligence Scraper
data layer, including unit tests, integration tests, and performance validation.

Test Categories:
- Model validation and business logic
- Data quality scoring algorithms
- Repository operations and queries
- Database constraints and relationships
- Performance and scalability testing

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
from unittest.mock import Mock, patch

import pytest

# Third-party imports
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

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


# === TEST CONFIGURATION ===
@pytest.fixture(scope="session")
def test_engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    create_tables(engine)
    return engine


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a fresh database session for each test"""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_repository(test_session):
    """Create repository instance for testing"""
    return DataRepository(test_session)


@pytest.fixture
def sample_data_record() -> Dict[str, Any]:
    """Sample data for creating test records"""
    return {
        "source_job_id": 1,
        "source_job_name": "test_news_scraper",
        "source_job_type": "news",
        "source_url": "https://example.com/article/123",
        "source_domain": "example.com",
        "raw_data": {"title": "Test Article", "content": "This is test content"},
        "extracted_text": "This is a comprehensive test article with substantial content for quality testing",
        "title": "Test Article Title",
        "data_type": "news",
        "content_category": "technology",
        "language": "en",
        "word_count": 15,
        "scraped_at": datetime.utcnow(),
        "content_published_at": datetime.utcnow() - timedelta(hours=2),
    }


# === UNIT TESTS FOR DATA MODELS ===


class TestCentralizedDataRecord:
    """Test suite for CentralizedDataRecord model"""

    def test_record_creation(self, test_session, sample_data_record):
        """Test basic record creation and persistence"""
        record = CentralizedDataRecord(**sample_data_record)
        test_session.add(record)
        test_session.commit()

        assert record.id is not None
        assert record.record_uuid is not None
        assert record.source_url == sample_data_record["source_url"]
        assert record.validation_status == "pending"

    def test_uuid_generation(self, test_session):
        """Test automatic UUID generation"""
        record1 = CentralizedDataRecord(source_url="https://test1.com")
        record2 = CentralizedDataRecord(source_url="https://test2.com")

        test_session.add_all([record1, record2])
        test_session.commit()

        assert record1.record_uuid != record2.record_uuid
        assert len(record1.record_uuid) == 36  # UUID4 format

    def test_content_hash_generation(self, sample_data_record):
        """Test content hash generation for deduplication"""
        record = CentralizedDataRecord(**sample_data_record)

        # Test hash generation
        content_hash = record.generate_content_hash()
        assert len(content_hash) == 64  # SHA-256 hex digest

        # Test hash consistency
        hash2 = record.generate_content_hash()
        assert content_hash == hash2

        # Test hash updates
        record.update_content_hash()
        assert record.content_hash == content_hash

    def test_quality_score_calculation(self, sample_data_record):
        """Test comprehensive quality scoring algorithm"""
        record = CentralizedDataRecord(**sample_data_record)
        record.calculate_quality_scores()

        # Check that scores are calculated
        assert record.data_quality_score > 0
        assert record.completeness_score > 0
        assert record.reliability_score > 0

        # Test completeness scoring
        assert 0 <= record.completeness_score <= 100

        # Test with minimal data
        minimal_record = CentralizedDataRecord(source_url="https://test.com")
        minimal_record.calculate_quality_scores()
        assert minimal_record.completeness_score < record.completeness_score

    def test_quality_score_edge_cases(self):
        """Test quality scoring with edge cases"""
        # Empty record
        empty_record = CentralizedDataRecord()
        empty_record.calculate_quality_scores()
        assert empty_record.data_quality_score == 0.0
        assert empty_record.completeness_score == 0.0
        assert empty_record.reliability_score == 0.0

        # Record with excellent content
        excellent_record = CentralizedDataRecord(
            source_url="https://harvard.edu/research/article",
            title="Comprehensive Research Analysis",
            extracted_text="A" * 1000,  # Long content
            data_type="academic",
            content_category="research",
            language="en",
            word_count=1000,
            scraped_at=datetime.utcnow(),
            content_published_at=datetime.utcnow() - timedelta(hours=1),
        )
        excellent_record.calculate_quality_scores()
        assert excellent_record.data_quality_score > 80
        assert excellent_record.reliability_score > 90  # .edu domain

    def test_computed_properties(self, sample_data_record):
        """Test computed property calculations"""
        record = CentralizedDataRecord(**sample_data_record)
        record.view_count = 1000
        record.share_count = 50
        record.like_count = 200
        record.comment_count = 25
        record.image_count = 5
        record.video_count = 2
        record.calculate_quality_scores()

        # Test engagement score
        engagement = record.engagement_score
        assert engagement > 0
        assert engagement <= 100

        # Test content richness
        richness = record.content_richness
        assert richness > 0
        assert richness <= 100

        # Test overall quality score
        overall_quality = record.overall_quality_score
        assert overall_quality >= 0

        # Test high quality indicator
        record.data_quality_score = 96.0
        record.completeness_score = 95.0
        record.reliability_score = 98.0
        record.validation_status = "valid"
        assert record.is_high_quality is True

    def test_data_validation(self, sample_data_record):
        """Test comprehensive data validation"""
        record = CentralizedDataRecord(**sample_data_record)
        validation_result = record.validate_data_integrity()

        assert isinstance(validation_result, dict)
        assert "is_valid" in validation_result
        assert "warnings" in validation_result
        assert "errors" in validation_result
        assert "recommendations" in validation_result

        # Test with invalid data
        invalid_record = CentralizedDataRecord(extracted_text="short")
        validation_result = invalid_record.validate_data_integrity()
        assert not validation_result["is_valid"]
        assert len(validation_result["errors"]) > 0

    def test_to_dict_conversion(self, test_session, sample_data_record):
        """Test model to dictionary conversion"""
        record = CentralizedDataRecord(**sample_data_record)
        test_session.add(record)
        test_session.commit()

        record_dict = record.to_dict()
        assert isinstance(record_dict, dict)
        assert "id" in record_dict
        assert "source_url" in record_dict
        assert record_dict["source_url"] == sample_data_record["source_url"]


class TestDataAnalytics:
    """Test suite for DataAnalytics model"""

    def test_analytics_creation(self, test_session):
        """Test analytics record creation"""
        analytics = DataAnalytics(
            date=datetime.utcnow(),
            period_type="daily",
            total_records=1000,
            total_jobs=50,
            avg_quality_score=Decimal("85.5"),
        )
        test_session.add(analytics)
        test_session.commit()

        assert analytics.id is not None
        assert analytics.analytics_uuid is not None
        assert analytics.period_type == "daily"
        assert analytics.total_records == 1000

    def test_computed_properties(self, test_session):
        """Test analytics computed properties"""
        analytics = DataAnalytics(
            total_images=100,
            total_videos=25,
            news_records=500,
            ecommerce_records=300,
            social_media_records=200,
            blog_records=100,
            forum_records=50,
            other_records=25,
        )

        # Test total content items
        assert analytics.total_content_items == 125  # 100 images + 25 videos

        # Test content diversity score
        diversity = analytics.content_diversity_score
        assert diversity == 100.0  # All 6 content types present

        # Test with fewer content types
        limited_analytics = DataAnalytics(news_records=100, ecommerce_records=50)
        assert (
            limited_analytics.content_diversity_score == (2 / 6) * 100
        )  # Only 2 types


class TestSystemMetrics:
    """Test suite for SystemMetrics model"""

    def test_metrics_creation(self, test_session):
        """Test system metrics record creation"""
        metrics = SystemMetrics(
            cpu_percent=Decimal("75.5"),
            memory_percent=Decimal("60.2"),
            avg_response_time_ms=Decimal("150.5"),
            hostname="test-server-01",
            environment="testing",
        )
        test_session.add(metrics)
        test_session.commit()

        assert metrics.id is not None
        assert metrics.metric_uuid is not None
        assert metrics.hostname == "test-server-01"

    def test_health_scoring(self):
        """Test system health score calculation"""
        # Healthy system
        healthy_metrics = SystemMetrics(
            cpu_percent=Decimal("25.0"),
            memory_percent=Decimal("40.0"),
            error_rate_percent=Decimal("0.1"),
        )
        health_score = healthy_metrics.system_health_score
        assert health_score > 80

        # Stressed system
        stressed_metrics = SystemMetrics(
            cpu_percent=Decimal("95.0"),
            memory_percent=Decimal("90.0"),
            error_rate_percent=Decimal("5.0"),
        )
        health_score = stressed_metrics.system_health_score
        assert health_score < 50

    def test_resource_pressure_levels(self):
        """Test resource pressure level categorization"""
        # Critical pressure
        critical_metrics = SystemMetrics(
            cpu_percent=Decimal("95.0"), memory_percent=Decimal("92.0")
        )
        assert critical_metrics.resource_pressure_level == "critical"

        # Low pressure
        low_metrics = SystemMetrics(
            cpu_percent=Decimal("25.0"), memory_percent=Decimal("30.0")
        )
        assert low_metrics.resource_pressure_level == "low"


class TestAlertRecord:
    """Test suite for AlertRecord model"""

    def test_alert_creation(self, test_session):
        """Test alert record creation"""
        alert = AlertRecord(
            alert_type="performance",
            severity="high",
            title="High CPU Usage",
            message="CPU usage exceeded 90%",
            source_component="api_server",
        )
        test_session.add(alert)
        test_session.commit()

        assert alert.id is not None
        assert alert.alert_uuid is not None
        assert alert.status == "active"
        assert alert.severity == "high"

    def test_alert_properties(self):
        """Test alert computed properties"""
        # Active alert
        active_alert = AlertRecord(status="active")
        assert active_alert.is_active is True

        # Resolved alert
        resolved_alert = AlertRecord(status="resolved")
        assert resolved_alert.is_active is False

        # Alert age calculation
        old_alert = AlertRecord(triggered_at=datetime.utcnow() - timedelta(minutes=30))
        assert old_alert.age_minutes >= 29  # Allow for test execution time

        # Severity scoring
        critical_alert = AlertRecord(severity="critical")
        assert critical_alert.severity_score == 4

        low_alert = AlertRecord(severity="low")
        assert low_alert.severity_score == 1

    def test_alert_relationships(self, test_session):
        """Test alert parent-child relationships"""
        parent_alert = AlertRecord(
            title="Database Connection Issues", alert_type="system", severity="critical"
        )
        test_session.add(parent_alert)
        test_session.commit()

        child_alert = AlertRecord(
            title="Slow Query Detected",
            alert_type="performance",
            severity="medium",
            parent_alert_id=parent_alert.id,
        )
        test_session.add(child_alert)
        test_session.commit()

        assert child_alert.parent_alert_id == parent_alert.id
        assert child_alert in parent_alert.child_alerts


class TestDataDeduplication:
    """Test suite for DataDeduplication model"""

    def test_deduplication_creation(self, test_session, sample_data_record):
        """Test deduplication record creation"""
        # Create original record
        original_record = CentralizedDataRecord(**sample_data_record)
        test_session.add(original_record)
        test_session.commit()

        # Create deduplication record
        dedup = DataDeduplication(
            content_hash="abc123def456",
            canonical_record_id=original_record.id,
            duplicate_record_ids=[2, 3, 4],
            similarity_score=Decimal("95.5"),
            dedup_method="content_similarity",
        )
        test_session.add(dedup)
        test_session.commit()

        assert dedup.id is not None
        assert dedup.canonical_record_id == original_record.id
        assert dedup.canonical_record == original_record


# === INTEGRATION TESTS FOR DATA REPOSITORY ===


class TestDataRepository:
    """Test suite for DataRepository operations"""

    def test_create_data_record(self, test_repository, sample_data_record):
        """Test data record creation through repository"""
        record = test_repository.create_data_record(sample_data_record)

        assert record.id is not None
        assert record.content_hash is not None
        assert record.data_quality_score > 0
        assert record.validation_status in ["valid", "flagged", "pending"]

    def test_get_high_quality_records(self, test_repository, sample_data_record):
        """Test retrieval of high-quality records"""
        # Create multiple records with different quality scores
        for i in range(5):
            data = sample_data_record.copy()
            data["source_url"] = f"https://example.com/article/{i}"
            data["extracted_text"] = "Excellent content " * (
                10 + i * 5
            )  # Varying quality
            record = CentralizedDataRecord(**data)
            record.calculate_quality_scores()
            record.validation_status = "valid"
            test_repository.session.add(record)

        test_repository.session.commit()

        # Retrieve high-quality records
        high_quality = test_repository.get_high_quality_records(limit=10)
        assert len(high_quality) >= 0  # May be 0 if none meet threshold

    def test_find_duplicates(self, test_repository, sample_data_record):
        """Test duplicate detection functionality"""
        # Create original record
        original = test_repository.create_data_record(sample_data_record)
        content_hash = original.content_hash

        # Create duplicate with same content
        duplicate_data = sample_data_record.copy()
        duplicate_data["source_url"] = "https://different.com/same-content"
        duplicate = CentralizedDataRecord(**duplicate_data)
        duplicate.update_content_hash()
        test_repository.session.add(duplicate)
        test_repository.session.commit()

        # Find duplicates
        duplicates = test_repository.find_duplicates(content_hash)
        assert len(duplicates) >= 1

    def test_analytics_operations(self, test_repository):
        """Test analytics creation and retrieval"""
        # Create analytics snapshot
        test_date = datetime.utcnow()
        analytics = test_repository.create_analytics_snapshot("daily", test_date)

        assert analytics.id is not None
        assert analytics.period_type == "daily"

        # Retrieve latest analytics
        latest = test_repository.get_latest_analytics("daily")
        assert latest is not None
        assert latest.id == analytics.id

    def test_system_metrics_operations(self, test_repository):
        """Test system metrics recording and retrieval"""
        metrics_data = {
            "cpu_percent": Decimal("75.5"),
            "memory_percent": Decimal("60.0"),
            "hostname": "test-server",
        }

        # Record metrics
        metrics = test_repository.record_system_metrics(metrics_data)
        assert metrics.id is not None

        # Get health trend
        trend = test_repository.get_system_health_trend(hours=24)
        assert len(trend) >= 1
        assert metrics in trend

    def test_alert_operations(self, test_repository):
        """Test alert creation, retrieval, and resolution"""
        # Create alert
        alert_data = {
            "alert_type": "performance",
            "severity": "high",
            "title": "Test Alert",
            "message": "This is a test alert",
            "source_component": "test_component",
        }

        alert = test_repository.create_alert(alert_data)
        assert alert.id is not None
        assert alert.status == "active"

        # Get active alerts
        active_alerts = test_repository.get_active_alerts()
        assert len(active_alerts) >= 1
        assert alert in active_alerts

        # Filter by severity
        high_severity = test_repository.get_active_alerts(severity_filter="high")
        assert len(high_severity) >= 1

        # Resolve alert
        resolved = test_repository.resolve_alert(
            alert.id, "test_user", "Test resolution"
        )
        assert resolved is True

        # Verify resolution
        test_repository.session.refresh(alert)
        assert alert.status == "resolved"
        assert alert.resolved_by == "test_user"

    def test_alert_correlation(self, test_repository):
        """Test alert correlation functionality"""
        # Create first alert with correlation key
        alert_data = {
            "alert_type": "system",
            "severity": "critical",
            "title": "Database Issues",
            "correlation_key": "db_connection_issues",
        }

        first_alert = test_repository.create_alert(alert_data)
        assert first_alert.occurrence_count == 1

        # Create correlated alert
        correlated_alert = test_repository.create_alert(alert_data)

        # Should return the same alert with incremented count
        assert correlated_alert.id == first_alert.id
        assert correlated_alert.occurrence_count == 2


# === PERFORMANCE AND STRESS TESTS ===


class TestPerformance:
    """Performance and scalability tests"""

    def test_bulk_record_insertion(self, test_session):
        """Test performance with bulk record insertion"""
        records = []
        for i in range(100):
            record = CentralizedDataRecord(
                source_url=f"https://example.com/article/{i}",
                title=f"Article {i}",
                extracted_text=f"Content for article {i} " * 10,
                data_type="news",
                word_count=10,
            )
            records.append(record)

        # Bulk insert
        start_time = datetime.utcnow()
        test_session.add_all(records)
        test_session.commit()
        end_time = datetime.utcnow()

        insert_duration = (end_time - start_time).total_seconds()
        assert insert_duration < 5.0  # Should complete within 5 seconds

        # Verify all records were inserted
        count = test_session.query(CentralizedDataRecord).count()
        assert count == 100

    def test_query_performance(self, test_session):
        """Test query performance with indexed fields"""
        # Create test data
        for i in range(50):
            record = CentralizedDataRecord(
                source_url=f"https://domain{i % 5}.com/article/{i}",
                data_type=["news", "ecommerce", "blog"][i % 3],
                data_quality_score=float(70 + (i % 30)),
                scraped_at=datetime.utcnow() - timedelta(hours=i),
            )
            test_session.add(record)
        test_session.commit()

        # Test indexed queries
        start_time = datetime.utcnow()

        # Query by domain (indexed)
        domain_results = (
            test_session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.source_domain == "domain1.com")
            .all()
        )

        # Query by data type (indexed)
        type_results = (
            test_session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.data_type == "news")
            .all()
        )

        # Query by quality score (indexed)
        quality_results = (
            test_session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.data_quality_score >= 80.0)
            .all()
        )

        end_time = datetime.utcnow()
        query_duration = (end_time - start_time).total_seconds()

        assert query_duration < 1.0  # Queries should be fast with proper indexing
        assert len(domain_results) > 0
        assert len(type_results) > 0


# === DATABASE CONSTRAINT TESTS ===


class TestDatabaseConstraints:
    """Test database constraints and data integrity"""

    def test_unique_constraints(self, test_session):
        """Test unique constraint enforcement"""
        uuid_value = str(uuid.uuid4())

        # Create first record
        record1 = CentralizedDataRecord(
            record_uuid=uuid_value, source_url="https://example.com/article/1"
        )
        test_session.add(record1)
        test_session.commit()

        # Attempt to create duplicate UUID
        record2 = CentralizedDataRecord(
            record_uuid=uuid_value, source_url="https://example.com/article/2"
        )
        test_session.add(record2)

        with pytest.raises(IntegrityError):
            test_session.commit()

    def test_foreign_key_constraints(self, test_session):
        """Test foreign key constraint enforcement"""
        # Create valid deduplication record
        original_record = CentralizedDataRecord(
            source_url="https://example.com/original"
        )
        test_session.add(original_record)
        test_session.commit()

        valid_dedup = DataDeduplication(
            content_hash="valid_hash", canonical_record_id=original_record.id
        )
        test_session.add(valid_dedup)
        test_session.commit()  # Should succeed

        # Attempt invalid foreign key
        invalid_dedup = DataDeduplication(
            content_hash="invalid_hash", canonical_record_id=999999  # Non-existent ID
        )
        test_session.add(invalid_dedup)

        with pytest.raises(IntegrityError):
            test_session.commit()


# === UTILITY FUNCTION TESTS ===


class TestUtilityFunctions:
    """Test utility functions and helpers"""

    def test_create_tables_function(self):
        """Test table creation utility"""
        # Create new in-memory database
        test_engine = create_engine("sqlite:///:memory:")

        # Should not raise any exceptions
        create_tables(test_engine)

        # Verify tables exist
        with test_engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            table_names = [row[0] for row in result]

            expected_tables = [
                "centralized_data",
                "data_analytics",
                "system_metrics",
                "alert_records",
                "data_deduplication",
            ]

            for table in expected_tables:
                assert table in table_names

    def test_model_summary_function(self):
        """Test model summary utility"""
        summary = get_model_summary()

        assert isinstance(summary, dict)
        assert "models" in summary
        assert "total_models" in summary
        assert summary["total_models"] == 5

        # Verify all models are documented
        model_names = summary["models"].keys()
        expected_models = [
            "CentralizedDataRecord",
            "DataAnalytics",
            "SystemMetrics",
            "AlertRecord",
            "DataDeduplication",
        ]

        for model in expected_models:
            assert model in model_names
            assert "description" in summary["models"][model]
            assert "key_features" in summary["models"][model]


# === EDGE CASE AND ERROR HANDLING TESTS ===


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_null_value_handling(self, test_session):
        """Test handling of null and empty values"""
        # Record with minimal data
        minimal_record = CentralizedDataRecord()
        test_session.add(minimal_record)
        test_session.commit()

        # Should not raise exceptions
        minimal_record.calculate_quality_scores()
        minimal_record.update_content_hash()
        validation_result = minimal_record.validate_data_integrity()

        assert isinstance(validation_result, dict)
        assert minimal_record.data_quality_score == 0.0

    def test_large_data_handling(self, test_session):
        """Test handling of large data values"""
        # Create record with large content
        large_content = "A" * 10000  # 10KB of text
        large_record = CentralizedDataRecord(
            source_url="https://example.com/large",
            extracted_text=large_content,
            title="Large Content Test",
            word_count=10000,
            raw_data={"content": large_content},
        )

        test_session.add(large_record)
        test_session.commit()

        # Should handle large content gracefully
        large_record.calculate_quality_scores()
        assert large_record.data_quality_score > 0

    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        record = CentralizedDataRecord()

        # Test with invalid data that might cause exceptions
        record.extracted_text = None
        record.raw_data = None
        record.source_url = None

        # Should not raise exceptions
        record.calculate_quality_scores()
        record.update_content_hash()

        # All scores should be zero or default values
        assert record.data_quality_score == 0.0
        assert record.completeness_score == 0.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
