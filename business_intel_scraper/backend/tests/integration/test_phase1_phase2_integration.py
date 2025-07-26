"""
Integration tests for Phase 1 and Phase 2 systems.

Tests cross-phase functionality and end-to-end workflows.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch, AsyncMock
import asyncio
from datetime import datetime

from business_intel_scraper.backend.discovery.automated_discovery import (
    AutomatedDiscoveryManager,
)
from business_intel_scraper.backend.discovery.dom_change_detection import (
    DOMChangeDetector,
)
from business_intel_scraper.backend.discovery.spider_update_system import (
    SpiderUpdater,
    SpiderUpdateScheduler,
)


class TestPhaseIntegration:
    """Test integration between Phase 1 and Phase 2 systems."""

    @pytest.fixture
    def discovery_manager(self):
        """Create discovery manager instance."""
        return AutomatedDiscoveryManager()

    @pytest.fixture
    def dom_detector(self):
        """Create DOM detector instance."""
        return DOMChangeDetector()

    @pytest.fixture
    def spider_updater(self):
        """Create spider updater instance."""
        return SpiderUpdater()

    @pytest.mark.asyncio
    async def test_discovery_to_monitoring_pipeline(
        self, discovery_manager, dom_detector
    ):
        """Test pipeline from discovery to monitoring."""
        # Phase 1: Discover sources
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(
                return_value="""
                <html>
                    <body>
                        <div class="registry">
                            <a href="/companies">Company Registry</a>
                        </div>
                    </body>
                </html>
            """
            )
            mock_get.return_value.__aenter__.return_value = mock_response

            # Discover sources
            sources = await discovery_manager.discover_seed_sources(
                "https://example.com"
            )
            assert len(sources) > 0

            # Phase 2: Add discovered sources to monitoring
            for source in sources[:3]:  # Monitor first 3 sources
                await dom_detector.add_monitoring_source(source.url)

            assert len(dom_detector.monitoring_sources) >= min(len(sources), 3)

    @pytest.mark.asyncio
    async def test_change_detection_triggers_spider_update(
        self, dom_detector, spider_updater
    ):
        """Test that detected changes trigger spider updates."""
        scheduler = SpiderUpdateScheduler(dom_detector, spider_updater)

        # Add a high-severity change
        from business_intel_scraper.backend.discovery.dom_change_detection import (
            DOMChange,
        )

        critical_change = DOMChange(
            url="https://example.com/companies",
            change_type="selector_change",
            old_selector=".company-entry",
            new_selector=".business-entry",
            severity="critical",
            auto_fixable=True,
            timestamp=datetime.utcnow(),
        )

        dom_detector.changes.append(critical_change)

        # Run scheduled check
        result = await scheduler.scheduled_update_check()

        # Should trigger updates for critical changes
        assert result["status"] in ["completed", "already_processing"]

        if result["status"] == "completed":
            assert "spiders_updated" in result["results"]

    @pytest.mark.asyncio
    async def test_spider_validation_after_update(self, spider_updater):
        """Test spider validation after automatic updates."""
        # Create a mock updated spider
        mock_spider_code = """
        import scrapy
        
        class TestSpider(scrapy.Spider):
            name = "test_spider"
            
            def parse(self, response):
                # Updated selector
                for item in response.css('.business-entry'):
                    yield {
                        'name': item.css('.business-name::text').get(),
                        'id': item.css('.business-id::text').get()
                    }
        """

        # Validate updated spider
        validation_result = await spider_updater.validate_spider_code(
            "test_spider", mock_spider_code
        )

        assert validation_result["valid"] is True
        assert "syntax_errors" in validation_result
        assert validation_result["syntax_errors"] == []

    @pytest.mark.asyncio
    async def test_monitoring_source_quality_assessment(
        self, discovery_manager, dom_detector
    ):
        """Test quality assessment of monitoring sources."""
        # Discover sources with quality metrics
        sources = await discovery_manager.discover_seed_sources("https://example.com")

        # Add high-quality sources to monitoring
        high_quality_sources = [s for s in sources if s.confidence_score > 0.8]

        for source in high_quality_sources:
            await dom_detector.add_monitoring_source(
                source.url, quality_score=source.confidence_score
            )

        # Verify quality-based monitoring
        assert len(dom_detector.monitoring_sources) <= len(sources)
        assert all(
            source.quality_score > 0.8
            for source in dom_detector.monitoring_sources.values()
        )


class TestSystemReliability:
    """Test system reliability and error recovery."""

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_failures(self):
        """Test system continues operating when components fail."""
        discovery_manager = AutomatedDiscoveryManager()
        dom_detector = DOMChangeDetector()

        # Test discovery continues even if some sources fail
        with patch("aiohttp.ClientSession.get") as mock_get:

            def side_effect(*args, **kwargs):
                url = args[0] if args else kwargs.get("url", "")
                if "fail.com" in str(url):
                    raise ConnectionError("Connection failed")

                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.text = AsyncMock(
                    return_value="<html><body>Success</body></html>"
                )
                return mock_response

            mock_get.return_value.__aenter__.side_effect = side_effect

            # Should succeed for working URLs and gracefully handle failures
            sources = await discovery_manager.discover_seed_sources(
                "https://success.com"
            )
            assert isinstance(sources, list)  # Should return empty list, not crash

    @pytest.mark.asyncio
    async def test_recovery_from_corrupted_snapshots(self, dom_detector):
        """Test recovery from corrupted DOM snapshots."""
        url = "https://example.com/test"

        # Corrupt the snapshot data
        dom_detector.dom_snapshots[url] = {"html": None, "timestamp": None}

        # Should handle corruption gracefully
        new_html = "<html><body>New content</body></html>"
        try:
            changes = await dom_detector.check_for_changes(url, new_html)
            assert isinstance(changes, list)  # Should return empty list, not crash
        except Exception as e:
            pytest.fail(f"Should handle corrupted snapshots gracefully: {e}")

    def test_resource_cleanup(self):
        """Test proper cleanup of system resources."""
        # This would test memory cleanup, file handle cleanup, etc.
        pass


class TestPerformanceIntegration:
    """Test performance of integrated systems."""

    @pytest.mark.asyncio
    async def test_concurrent_discovery_and_monitoring(self):
        """Test concurrent discovery and monitoring operations."""
        discovery_manager = AutomatedDiscoveryManager()
        dom_detector = DOMChangeDetector()

        # Run discovery and monitoring concurrently
        discovery_task = discovery_manager.discover_seed_sources("https://example.com")
        monitoring_task = dom_detector.check_all_monitoring_sources()

        try:
            discovery_result, monitoring_result = await asyncio.gather(
                discovery_task, monitoring_task, return_exceptions=True
            )

            # Both should complete without interfering
            assert not isinstance(discovery_result, Exception)
            assert not isinstance(monitoring_result, Exception)
        except Exception as e:
            pytest.fail(f"Concurrent operations should not interfere: {e}")

    @pytest.mark.asyncio
    async def test_scalability_with_many_sources(self):
        """Test system scalability with many monitoring sources."""
        dom_detector = DOMChangeDetector()

        # Add many monitoring sources
        urls = [f"https://example{i}.com" for i in range(100)]

        for url in urls:
            await dom_detector.add_monitoring_source(url)

        assert len(dom_detector.monitoring_sources) == 100

        # Test batch processing performance
        start_time = datetime.utcnow()

        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(
                return_value="<html><body>Test</body></html>"
            )
            mock_get.return_value.__aenter__.return_value = mock_response

            # Should complete in reasonable time
            await dom_detector.check_monitoring_sources_batch(batch_size=10)

        elapsed = (datetime.utcnow() - start_time).total_seconds()
        assert elapsed < 60  # Should complete within 60 seconds


class TestDataConsistency:
    """Test data consistency across phases."""

    @pytest.mark.asyncio
    async def test_discovered_source_tracking(self):
        """Test discovered sources are consistently tracked."""
        discovery_manager = AutomatedDiscoveryManager()

        # Discover sources
        sources = await discovery_manager.discover_seed_sources("https://example.com")

        # Track in discovery manager
        for source in sources:
            await discovery_manager.track_discovered_source(source)

        # Verify consistent tracking
        tracked_sources = discovery_manager.get_discovered_sources()
        assert len(tracked_sources) == len(sources)

    def test_change_history_consistency(self):
        """Test change history remains consistent."""
        dom_detector = DOMChangeDetector()

        # Add changes
        from business_intel_scraper.backend.discovery.dom_change_detection import (
            DOMChange,
        )

        changes = [
            DOMChange(
                url=f"https://example.com/page{i}",
                change_type="selector_change",
                severity="medium",
                timestamp=datetime.utcnow(),
            )
            for i in range(10)
        ]

        for change in changes:
            dom_detector.changes.append(change)

        # Verify history consistency
        assert len(dom_detector.changes) >= 10
        assert all(
            change.timestamp is not None for change in dom_detector.changes[-10:]
        )

    def test_spider_update_audit_trail(self):
        """Test spider updates maintain audit trail."""
        # This would test audit trail functionality
        pass


if __name__ == "__main__":
    pytest.main([__file__])
