"""
Performance and Load Testing Suite for Business Intelligence Scraper

This module provides specialized performance tests to validate system behavior
under load, measure response times, and identify performance bottlenecks.

Test Categories:
- Database performance under load
- Query optimization validation
- Memory usage patterns
- Concurrent operation testing
- Scalability benchmarks

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

import gc
import os
import statistics

# Local imports
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List

import psutil
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from business_intel_scraper.backend.db.centralized_data import (
    AlertRecord,
    Base,
    CentralizedDataRecord,
    DataAnalytics,
    DataRepository,
    SystemMetrics,
)


class PerformanceMetrics:
    """Helper class to collect and analyze performance metrics"""

    def __init__(self):
        self.execution_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.start_time: float = 0
        self.end_time: float = 0

    def start_measurement(self):
        """Start performance measurement"""
        self.start_time = time.time()
        gc.collect()  # Clean up before measurement

    def end_measurement(self):
        """End performance measurement"""
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        self.execution_times.append(execution_time)

        # Memory usage in MB
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.memory_usage.append(memory_mb)

            # CPU usage percentage
            cpu_percent = process.cpu_percent()
            self.cpu_usage.append(cpu_percent)
        except:
            # Fallback if psutil is not available
            self.memory_usage.append(0.0)
            self.cpu_usage.append(0.0)

        return execution_time

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        if not self.execution_times:
            return {}

        return {
            "execution_time": {
                "mean": statistics.mean(self.execution_times),
                "median": statistics.median(self.execution_times),
                "min": min(self.execution_times),
                "max": max(self.execution_times),
                "std_dev": (
                    statistics.stdev(self.execution_times)
                    if len(self.execution_times) > 1
                    else 0
                ),
            },
            "memory_usage_mb": {
                "mean": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max": max(self.memory_usage) if self.memory_usage else 0,
                "min": min(self.memory_usage) if self.memory_usage else 0,
            },
            "cpu_usage_percent": {
                "mean": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                "max": max(self.cpu_usage) if self.cpu_usage else 0,
            },
            "total_operations": len(self.execution_times),
            "operations_per_second": (
                len(self.execution_times) / sum(self.execution_times)
                if sum(self.execution_times) > 0
                else 0
            ),
        }


@pytest.fixture(scope="session")
def performance_engine():
    """Create dedicated database engine for performance testing"""
    # Use SQLite with optimizations for performance testing
    engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def performance_session(performance_engine):
    """Create session optimized for performance testing"""
    Session = sessionmaker(bind=performance_engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def performance_repository(performance_session):
    """Create repository for performance testing"""
    return DataRepository(performance_session)


class TestBulkOperationPerformance:
    """Test performance of bulk database operations"""

    def test_bulk_insert_performance(self, performance_session):
        """Test bulk insertion performance"""
        metrics = PerformanceMetrics()
        record_counts = [100, 500, 1000]

        for count in record_counts:
            metrics.start_measurement()

            # Create records
            records = []
            for i in range(count):
                record = CentralizedDataRecord(
                    source_url=f"https://example.com/article/{i}",
                    title=f"Performance Test Article {i}",
                    extracted_text=f"This is test content for article {i}. " * 20,
                    data_type="news",
                    content_category="technology",
                    language="en",
                    word_count=20,
                    scraped_at=datetime.utcnow(),
                    view_count=i * 10,
                    share_count=i,
                    like_count=i * 2,
                )
                records.append(record)

            # Bulk insert
            performance_session.add_all(records)
            performance_session.commit()

            execution_time = metrics.end_measurement()
            print(f"Inserted {count} records in {execution_time:.3f} seconds")

            # Performance assertions
            records_per_second = count / execution_time
            assert records_per_second > 10  # Should insert at least 10 records/second

            # Cleanup for next iteration
            performance_session.query(CentralizedDataRecord).delete()
            performance_session.commit()

        stats = metrics.get_statistics()
        print(f"Bulk Insert Performance: {stats}")


class TestQueryPerformance:
    """Test query performance with various data sizes and patterns"""

    def setup_method(self):
        """Setup test data for query performance testing"""
        self.test_data_created = False

    def create_test_data(self, session, record_count=500):
        """Create test data for query performance testing"""
        if self.test_data_created:
            return

        records = []
        for i in range(record_count):
            record = CentralizedDataRecord(
                source_url=f"https://domain{i % 20}.com/article/{i}",
                title=f"Query Test Article {i}",
                extracted_text=f"Content for performance testing article {i}. " * 15,
                data_type=["news", "blog", "ecommerce", "social_media"][i % 4],
                content_category=["technology", "business", "sports", "entertainment"][
                    i % 4
                ],
                language=["en", "es", "fr"][i % 3],
                data_quality_score=float(50 + (i % 50)),
                view_count=i * 100,
                share_count=i % 100,
                scraped_at=datetime.utcnow() - timedelta(hours=i % 168),  # Last week
                validation_status=["valid", "flagged", "pending"][i % 3],
            )
            records.append(record)

        session.add_all(records)
        session.commit()
        self.test_data_created = True

    def test_indexed_query_performance(self, performance_session):
        """Test performance of queries using indexed fields"""
        self.create_test_data(performance_session)
        metrics = PerformanceMetrics()

        # Test various indexed queries
        query_tests = [
            # Data type queries (indexed)
            lambda: performance_session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.data_type == "news")
            .all(),
            # Quality score range queries (indexed)
            lambda: performance_session.query(CentralizedDataRecord)
            .filter(CentralizedDataRecord.data_quality_score >= 80.0)
            .all(),
            # Time-based queries (indexed)
            lambda: performance_session.query(CentralizedDataRecord)
            .filter(
                CentralizedDataRecord.scraped_at
                >= datetime.utcnow() - timedelta(days=1)
            )
            .all(),
        ]

        for i, query_func in enumerate(query_tests):
            metrics.start_measurement()
            results = query_func()
            execution_time = metrics.end_measurement()

            print(
                f"Query {i+1}: {len(results)} results in {execution_time:.3f} seconds"
            )
            assert execution_time < 1.0  # Indexed queries should be reasonably fast

        stats = metrics.get_statistics()
        print(f"Query Performance: {stats}")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])
