"""
Comprehensive Integration Test for Complete Platform
Tests all implemented features: Database, Performance, Security, Compliance, etc.
"""

import asyncio
import os
import sys
from datetime import datetime

import pytest

# Add path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from business_intel_scraper.backend.utils.advanced_features import (
    CollaborationEvent,
    EventType,
    FilterCriteria,
    advanced_filters,
    dashboard_builder,
)
from business_intel_scraper.backend.utils.compliance import (
    ConsentRecord,
    ConsentType,
    DataCategory,
    DataSubject,
    cookie_consent_manager,
    gdpr_manager,
)
from business_intel_scraper.backend.utils.performance import (
    cache_manager,
    initialize_performance_optimization,
    performance_monitor,
    query_optimizer,
)
from business_intel_scraper.backend.utils.security import (
    InputValidator,
    SecurityEvent,
    SecurityLevel,
    ThreatType,
    audit_logger,
    encryption_manager,
    two_factor_auth,
)
from business_intel_scraper.database.config import get_async_session, init_database
from business_intel_scraper.database.models import Connection, Entity, Event, Location


class TestComprehensiveIntegration:
    """Comprehensive integration tests for the entire platform"""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        # Initialize database
        await init_database()

        # Initialize performance optimization
        await initialize_performance_optimization()

        # Initialize security audit logger
        await audit_logger.initialize_redis("redis://localhost:6379")

        # Initialize GDPR manager with encryption
        gdpr_manager.encryption_manager = encryption_manager

        yield

        # Cleanup
        # In a real test, you'd clean up the database

    async def test_database_operations(self):
        """Test complete database operations with the new models"""
        async with get_async_session() as session:
            # Test Entity creation
            entity1 = Entity(
                name="Acme Corporation",
                entity_type="organization",
                properties={
                    "industry": "Technology",
                    "employees": 500,
                    "founded": "2000-01-01",
                },
            )

            entity2 = Entity(
                name="Jane Smith",
                entity_type="person",
                properties={"role": "CEO", "email": "jane@acme.com"},
            )

            # Test Location creation
            location = Location(
                name="San Francisco Office",
                latitude=37.7749,
                longitude=-122.4194,
                address="123 Tech Street, San Francisco, CA",
                location_type="office",
                properties={"capacity": 200},
            )

            session.add_all([entity1, entity2, location])
            await session.commit()
            await session.refresh(entity1)
            await session.refresh(entity2)
            await session.refresh(location)

            # Test Connection creation
            connection = Connection(
                source_entity_id=entity1.id,
                target_entity_id=entity2.id,
                relationship_type="employment",
                strength=0.9,
                properties={"position": "CEO", "start_date": "2020-01-01"},
            )

            session.add(connection)
            await session.commit()

            # Test Event creation
            event = Event(
                entity_id=entity1.id,
                event_type="funding",
                timestamp=datetime.utcnow(),
                properties={
                    "amount": 10000000,
                    "round": "Series A",
                    "investors": ["VC Fund"],
                },
            )

            session.add(event)
            await session.commit()

            # Verify data was created
            entities = await session.execute("SELECT COUNT(*) FROM entities")
            entity_count = entities.scalar()
            assert entity_count == 2

            connections = await session.execute("SELECT COUNT(*) FROM connections")
            connection_count = connections.scalar()
            assert connection_count == 1

            events = await session.execute("SELECT COUNT(*) FROM events")
            event_count = events.scalar()
            assert event_count == 1

            locations = await session.execute("SELECT COUNT(*) FROM locations")
            location_count = locations.scalar()
            assert location_count == 1

        print("✅ Database operations test passed")

    async def test_performance_features(self):
        """Test performance optimization features"""
        # Test caching
        cache_key = "test_key"
        test_data = {
            "message": "Hello, World!",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Set cache
        await cache_manager.set(cache_key, test_data, ttl=60)

        # Get from cache
        cached_data = await cache_manager.get(cache_key)
        assert cached_data is not None
        assert cached_data["message"] == test_data["message"]

        # Test cache stats
        stats = cache_manager.get_stats()
        assert stats["hit_rate_percent"] > 0
        assert stats["total_requests"] > 0

        # Test query tracking
        async with query_optimizer.track_query("test_query"):
            # Simulate query execution
            await asyncio.sleep(0.01)

        query_stats = query_optimizer.get_query_stats()
        assert "test_query" in query_stats["queries"]
        assert query_stats["queries"]["test_query"]["count"] == 1

        # Test performance monitoring
        current_stats = performance_monitor.get_current_stats()
        assert "system" in current_stats
        assert "process" in current_stats
        assert "application" in current_stats

        print("✅ Performance features test passed")

    async def test_security_features(self):
        """Test security features"""
        # Test encryption
        original_data = "Sensitive information that needs encryption"
        encrypted_data = encryption_manager.encrypt_data(original_data)
        decrypted_data = encryption_manager.decrypt_data(encrypted_data)

        assert encrypted_data != original_data
        assert decrypted_data == original_data

        # Test password hashing
        password = "SecurePassword123!"
        hashed = encryption_manager.hash_password(password)
        assert encryption_manager.verify_password(password, hashed)
        assert not encryption_manager.verify_password("WrongPassword", hashed)

        # Test 2FA
        secret = two_factor_auth.generate_secret()
        assert len(secret) > 0

        qr_url = two_factor_auth.generate_qr_code_url("test@example.com", secret)
        assert "otpauth://totp/" in qr_url

        # Test input validation
        assert InputValidator.validate_email("test@example.com")
        assert not InputValidator.validate_email("invalid-email")

        valid, errors = InputValidator.validate_password("ValidPass123!")
        assert valid and len(errors) == 0

        valid, errors = InputValidator.validate_password("weak")
        assert not valid and len(errors) > 0

        # Test SQL injection detection
        assert InputValidator.detect_sql_injection("'; DROP TABLE users; --")
        assert not InputValidator.detect_sql_injection("normal search term")

        # Test XSS detection
        assert InputValidator.detect_xss("<script>alert('xss')</script>")
        assert not InputValidator.detect_xss("normal text content")

        # Test security event logging
        security_event = SecurityEvent(
            event_id="test-123",
            event_type=ThreatType.SUSPICIOUS_ACTIVITY,
            severity=SecurityLevel.MEDIUM,
            user_id="user123",
            ip_address="192.168.1.1",
            user_agent="Test Agent",
            timestamp=datetime.utcnow(),
            description="Test security event",
            metadata={"test": "data"},
        )

        await audit_logger.log_security_event(security_event)

        # Test failed attempt tracking
        is_brute_force = await audit_logger.track_failed_attempt(
            "192.168.1.100", "user456"
        )
        assert not is_brute_force  # First attempt shouldn't trigger brute force

        print("✅ Security features test passed")

    async def test_advanced_features(self):
        """Test advanced features like filtering and collaboration"""
        # Test advanced filtering
        filter1 = FilterCriteria(
            field="name", operator="contains", value="Corp", data_type="string"
        )

        advanced_filters.add_filter("test_group", filter1)

        summary = advanced_filters.get_filter_summary()
        assert summary["total_groups"] == 1
        assert summary["total_filters"] == 1
        assert "test_group" in summary["groups"]

        # Test collaboration event
        collab_event = CollaborationEvent(
            event_type=EventType.USER_JOINED,
            user_id="user123",
            session_id="session456",
            room_id="room789",
            timestamp=datetime.utcnow(),
            data={"username": "testuser"},
        )

        event_dict = collab_event.to_dict()
        assert event_dict["event_type"] == "user_joined"
        assert event_dict["user_id"] == "user123"

        # Test dashboard builder
        dashboard_id = dashboard_builder.create_dashboard(
            user_id="user123", name="Test Dashboard", template="default"
        )

        assert dashboard_id is not None

        dashboard = dashboard_builder.get_dashboard(dashboard_id)
        assert dashboard is not None
        assert dashboard["name"] == "Test Dashboard"
        assert dashboard["user_id"] == "user123"

        # Test adding widget
        widget_id = dashboard_builder.add_widget(
            dashboard_id, "network_graph", position={"x": 0, "y": 0, "w": 6, "h": 4}
        )

        assert widget_id is not None

        updated_dashboard = dashboard_builder.get_dashboard(dashboard_id)
        assert widget_id in updated_dashboard["widgets"]

        print("✅ Advanced features test passed")

    async def test_compliance_features(self):
        """Test GDPR compliance and cookie management"""
        # Test data subject registration
        data_subject = DataSubject(
            subject_id="subject123",
            email="user@example.com",
            registration_date=datetime.utcnow(),
            data_categories={
                DataCategory.PERSONAL_IDENTIFIABLE,
                DataCategory.BEHAVIORAL,
            },
            processing_purposes={
                DataProcessingPurpose.SERVICE_PROVISION,
                DataProcessingPurpose.ANALYTICS,
            },
        )

        gdpr_manager.register_data_subject(data_subject)

        # Test consent recording
        consent = ConsentRecord(
            consent_id="consent123",
            subject_id="subject123",
            consent_type=ConsentType.ANALYTICS,
            granted=True,
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            version="1.0",
        )

        gdpr_manager.record_consent(consent)

        # Test data export (Right to data portability)
        exported_data = gdpr_manager.export_subject_data("subject123")
        assert exported_data is not None
        assert "subject_information" in exported_data
        assert "consent_history" in exported_data

        # Test privacy report generation
        privacy_report = gdpr_manager.generate_privacy_report()
        assert "data_subjects" in privacy_report
        assert "consent_management" in privacy_report
        assert privacy_report["data_subjects"]["total"] >= 1

        # Test cookie consent management
        cookie_policy = cookie_consent_manager.get_cookie_policy()
        assert "categories" in cookie_policy
        assert "necessary" in cookie_policy["categories"]
        assert "analytics" in cookie_policy["categories"]

        user_consents = {"necessary": True, "analytics": True, "marketing": False}

        allowed_cookies = cookie_consent_manager.validate_consent(user_consents)
        assert "set" in allowed_cookies
        assert "remove" in allowed_cookies
        assert len(allowed_cookies["set"]) > 0

        print("✅ Compliance features test passed")

    async def test_data_seeding(self):
        """Test database seeding with sample data"""
        # Skip seeding test as it's handled in init_database

        async with get_async_session() as session:
            # Check that data was seeded
            entities = await session.execute("SELECT COUNT(*) FROM entities")
            entity_count = entities.scalar()

            connections = await session.execute("SELECT COUNT(*) FROM connections")
            connection_count = connections.scalar()

            locations = await session.execute("SELECT COUNT(*) FROM locations")
            location_count = locations.scalar()

            # Should have seeded data
            assert entity_count > 0
            assert connection_count > 0
            assert location_count > 0

        print("✅ Database seeding test passed")

    async def test_integration_workflow(self):
        """Test a complete workflow integrating multiple features"""
        # Step 1: Create user and register for GDPR
        user_id = "workflow_user123"
        data_subject = DataSubject(
            subject_id=user_id,
            email="workflow@example.com",
            registration_date=datetime.utcnow(),
            data_categories={
                DataCategory.PERSONAL_IDENTIFIABLE,
                DataCategory.BEHAVIORAL,
            },
            processing_purposes={DataProcessingPurpose.SERVICE_PROVISION},
        )
        gdpr_manager.register_data_subject(data_subject)

        # Step 2: Record consent
        consent = ConsentRecord(
            consent_id="workflow_consent",
            subject_id=user_id,
            consent_type=ConsentType.ANALYTICS,
            granted=True,
            timestamp=datetime.utcnow(),
            ip_address="192.168.1.1",
            user_agent="Workflow Test",
            version="1.0",
        )
        gdpr_manager.record_consent(consent)

        # Step 3: Create dashboard
        dashboard_id = dashboard_builder.create_dashboard(
            user_id=user_id, name="Workflow Dashboard", template="analysis_focused"
        )

        # Step 4: Add filters
        filter_criteria = FilterCriteria(
            field="entity_type", operator="eq", value="organization", data_type="string"
        )
        advanced_filters.add_filter("workflow_filters", filter_criteria)

        # Step 5: Test performance monitoring
        async with query_optimizer.track_query("workflow_query"):
            async with get_async_session() as session:
                result = await session.execute(
                    "SELECT COUNT(*) FROM entities WHERE entity_type = 'organization'"
                )
                count = result.scalar()

        # Step 6: Log security event
        security_event = SecurityEvent(
            event_id="workflow_security",
            event_type=ThreatType.SUSPICIOUS_ACTIVITY,
            severity=SecurityLevel.LOW,
            user_id=user_id,
            ip_address="192.168.1.1",
            user_agent="Workflow Test",
            timestamp=datetime.utcnow(),
            description="Workflow security test",
            metadata={"workflow": True},
        )
        await audit_logger.log_security_event(security_event)

        # Step 7: Verify everything works together
        dashboard = dashboard_builder.get_dashboard(dashboard_id)
        assert dashboard["user_id"] == user_id

        exported_data = gdpr_manager.export_subject_data(user_id)
        assert len(exported_data["consent_history"]) == 1

        query_stats = query_optimizer.get_query_stats()
        assert "workflow_query" in query_stats["queries"]

        print("✅ Integration workflow test passed")


@pytest.mark.asyncio
async def test_comprehensive_platform():
    """Run all comprehensive tests"""
    test_instance = TestComprehensiveIntegration()
    await test_instance.setup().__anext__()

    try:
        print("🚀 Starting comprehensive platform tests...")

        await test_instance.test_database_operations()
        await test_instance.test_performance_features()
        await test_instance.test_security_features()
        await test_instance.test_advanced_features()
        await test_instance.test_compliance_features()
        await test_instance.test_data_seeding()
        await test_instance.test_integration_workflow()

        print("🎉 All comprehensive tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_comprehensive_platform())
