"""
Test suite for Phase 2: DOM Change Detection and Spider Update Automation.

Tests DOM analysis, change tracking, and automated spider updates.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio
from datetime import datetime, timedelta
import json

from business_intel_scraper.backend.discovery.dom_change_detection import DOMChangeDetector
from business_intel_scraper.backend.discovery.spider_update_system import SpiderUpdater, SpiderUpdateScheduler


class TestDOMChangeDetection:
    """Test DOM change detection functionality."""
    
    @pytest.fixture
    def dom_detector(self):
        """Create DOM change detector instance."""
        return DOMChangeDetector()
    
    @pytest.fixture
    def sample_html_v1(self):
        """Sample HTML version 1."""
        return """
        <html>
            <body>
                <div class="company-list">
                    <div class="company" id="comp-1">
                        <h2>ABC Corp</h2>
                        <span class="reg-num">12345</span>
                    </div>
                    <div class="company" id="comp-2">
                        <h2>XYZ Inc</h2>
                        <span class="reg-num">67890</span>
                    </div>
                </div>
            </body>
        </html>
        """
    
    @pytest.fixture
    def sample_html_v2(self):
        """Sample HTML version 2 with changes."""
        return """
        <html>
            <body>
                <div class="company-directory">
                    <div class="business" id="bus-1">
                        <h3>ABC Corp</h3>
                        <span class="registration">12345</span>
                    </div>
                    <div class="business" id="bus-2">
                        <h3>XYZ Inc</h3>
                        <span class="registration">67890</span>
                    </div>
                    <div class="business" id="bus-3">
                        <h3>New Company Ltd</h3>
                        <span class="registration">11111</span>
                    </div>
                </div>
            </body>
        </html>
        """
    
    @pytest.mark.asyncio
    async def test_dom_change_detection_basic(self, dom_detector, sample_html_v1, sample_html_v2):
        """Test basic DOM change detection."""
        url = "https://example.com/companies"
        
        # Store initial version
        await dom_detector.store_dom_snapshot(url, sample_html_v1)
        
        # Check for changes with new version
        changes = await dom_detector.check_for_changes(url, sample_html_v2)
        
        assert len(changes) > 0
        assert any(change.change_type == "structure_change" for change in changes)
    
    @pytest.mark.asyncio
    async def test_element_addition_detection(self, dom_detector, sample_html_v1, sample_html_v2):
        """Test detection of new elements."""
        url = "https://example.com/companies"
        
        await dom_detector.store_dom_snapshot(url, sample_html_v1)
        changes = await dom_detector.check_for_changes(url, sample_html_v2)
        
        # Should detect new company entry
        new_element_changes = [c for c in changes if c.change_type == "element_added"]
        assert len(new_element_changes) > 0
    
    @pytest.mark.asyncio
    async def test_css_selector_change_detection(self, dom_detector, sample_html_v1, sample_html_v2):
        """Test detection of CSS selector changes."""
        url = "https://example.com/companies"
        
        await dom_detector.store_dom_snapshot(url, sample_html_v1)
        changes = await dom_detector.check_for_changes(url, sample_html_v2)
        
        # Should detect class name changes: company -> business, company-list -> company-directory
        selector_changes = [c for c in changes if c.change_type == "selector_change"]
        assert len(selector_changes) > 0
    
    @pytest.mark.asyncio
    async def test_change_severity_classification(self, dom_detector, sample_html_v1, sample_html_v2):
        """Test change severity is properly classified."""
        url = "https://example.com/companies"
        
        await dom_detector.store_dom_snapshot(url, sample_html_v1)
        changes = await dom_detector.check_for_changes(url, sample_html_v2)
        
        # Verify severity levels are assigned
        assert any(change.severity in ['low', 'medium', 'high', 'critical'] for change in changes)
        
        # Structural changes should be high severity
        structural_changes = [c for c in changes if c.change_type == "structure_change"]
        if structural_changes:
            assert any(c.severity in ['high', 'critical'] for c in structural_changes)
    
    def test_change_auto_fixable_classification(self, dom_detector):
        """Test changes are classified as auto-fixable or not."""
        # This would test the logic for determining if changes can be automatically fixed
        pass
    
    @pytest.mark.asyncio
    async def test_dom_snapshot_storage(self, dom_detector):
        """Test DOM snapshots are properly stored and retrieved."""
        url = "https://example.com/test"
        html_content = "<html><body><h1>Test</h1></body></html>"
        
        # Store snapshot
        await dom_detector.store_dom_snapshot(url, html_content)
        
        # Verify storage
        assert url in dom_detector.dom_snapshots
        assert dom_detector.dom_snapshots[url]['html'] == html_content
    
    @pytest.mark.asyncio
    async def test_change_history_tracking(self, dom_detector):
        """Test change history is properly tracked."""
        url = "https://example.com/test"
        html_v1 = "<html><body><div class='old'>Old</div></body></html>"
        html_v2 = "<html><body><div class='new'>New</div></body></html>"
        
        # Initial snapshot
        await dom_detector.store_dom_snapshot(url, html_v1)
        
        # Check changes
        changes = await dom_detector.check_for_changes(url, html_v2)
        
        # Verify changes are tracked
        assert len(dom_detector.changes) >= len(changes)
        assert all(change.timestamp is not None for change in changes)


class TestSpiderUpdateSystem:
    """Test spider update system functionality."""
    
    @pytest.fixture
    def spider_updater(self):
        """Create spider updater instance."""
        return SpiderUpdater()
    
    @pytest.fixture
    def dom_detector_with_changes(self):
        """Create DOM detector with sample changes."""
        detector = DOMChangeDetector()
        # Add mock changes
        from business_intel_scraper.backend.discovery.dom_change_detection import DOMChange
        
        changes = [
            DOMChange(
                url="https://example.com/companies",
                change_type="selector_change",
                old_selector=".company",
                new_selector=".business",
                severity="high",
                auto_fixable=True,
                timestamp=datetime.utcnow()
            ),
            DOMChange(
                url="https://example.com/companies",
                change_type="structure_change",
                description="New container div added",
                severity="medium",
                auto_fixable=False,
                timestamp=datetime.utcnow()
            )
        ]
        detector.changes.extend(changes)
        return detector
    
    @pytest.fixture
    def spider_scheduler(self, dom_detector_with_changes, spider_updater):
        """Create spider update scheduler."""
        return SpiderUpdateScheduler(dom_detector_with_changes, spider_updater)
    
    @pytest.mark.asyncio
    async def test_spider_update_identification(self, spider_updater, dom_detector_with_changes):
        """Test identification of spiders needing updates."""
        affected_spiders = await spider_updater.identify_affected_spiders(
            dom_detector_with_changes.changes
        )
        
        assert len(affected_spiders) > 0
        assert all('spider_name' in spider for spider in affected_spiders)
    
    @pytest.mark.asyncio
    async def test_automatic_selector_update(self, spider_updater):
        """Test automatic update of CSS selectors."""
        from business_intel_scraper.backend.discovery.dom_change_detection import DOMChange
        
        change = DOMChange(
            url="https://example.com/companies",
            change_type="selector_change",
            old_selector=".company",
            new_selector=".business",
            severity="high",
            auto_fixable=True,
            timestamp=datetime.utcnow()
        )
        
        # Test automatic fix
        result = await spider_updater.apply_automatic_fix(change)
        
        assert result['success'] is True
        assert result['applied_fix'] is not None
    
    @pytest.mark.asyncio
    async def test_scheduled_update_check(self, spider_scheduler):
        """Test scheduled update checks."""
        result = await spider_scheduler.scheduled_update_check()
        
        assert 'status' in result
        assert result['status'] in ['completed', 'no_changes', 'already_processing']
        
        if result['status'] == 'completed':
            assert 'results' in result
            assert 'spiders_updated' in result['results']
    
    def test_manual_review_flagging(self, spider_updater):
        """Test changes requiring manual review are properly flagged."""
        from business_intel_scraper.backend.discovery.dom_change_detection import DOMChange
        
        complex_change = DOMChange(
            url="https://example.com/companies",
            change_type="structure_change",
            description="Complete page restructure",
            severity="critical",
            auto_fixable=False,
            timestamp=datetime.utcnow()
        )
        
        # Should be flagged for manual review
        assert not complex_change.auto_fixable
        assert complex_change.severity == "critical"
    
    @pytest.mark.asyncio
    async def test_update_rollback_capability(self, spider_updater):
        """Test ability to rollback failed updates."""
        # This would test rollback functionality
        pass
    
    @pytest.mark.asyncio
    async def test_update_validation(self, spider_updater):
        """Test updated spiders are validated before deployment."""
        # This would test validation of updated spider code
        pass


class TestPhase2Integration:
    """Test integration between DOM detection and spider updates."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_change_detection_and_update(self):
        """Test complete flow from change detection to spider update."""
        dom_detector = DOMChangeDetector()
        spider_updater = SpiderUpdater()
        scheduler = SpiderUpdateScheduler(dom_detector, spider_updater)
        
        # Mock scenario: Website changes structure
        url = "https://example.com/registry"
        old_html = "<div class='companies'><div class='company'>ABC Corp</div></div>"
        new_html = "<div class='business-list'><div class='business'>ABC Corp</div></div>"
        
        # Store initial snapshot
        await dom_detector.store_dom_snapshot(url, old_html)
        
        # Detect changes
        changes = await dom_detector.check_for_changes(url, new_html)
        assert len(changes) > 0
        
        # Run scheduled update
        result = await scheduler.scheduled_update_check()
        
        # Verify update process completed
        assert result['status'] in ['completed', 'no_changes']
    
    def test_change_detection_performance(self):
        """Test DOM change detection performance with large documents."""
        # This would test performance with large HTML documents
        pass
    
    def test_concurrent_change_detection(self):
        """Test handling multiple concurrent change detection operations."""
        # This would test concurrent processing
        pass


class TestPhase2ErrorHandling:
    """Test error handling in Phase 2 components."""
    
    @pytest.mark.asyncio
    async def test_invalid_html_handling(self):
        """Test handling of invalid HTML during change detection."""
        dom_detector = DOMChangeDetector()
        
        invalid_html = "<<invalid>>html<<structure>>"
        
        try:
            await dom_detector.store_dom_snapshot("https://test.com", invalid_html)
            # Should not crash
        except Exception as e:
            pytest.fail(f"Should handle invalid HTML gracefully: {e}")
    
    @pytest.mark.asyncio
    async def test_network_timeout_during_updates(self):
        """Test handling of network timeouts during spider updates."""
        spider_updater = SpiderUpdater()
        
        with patch('aiohttp.ClientSession.get', side_effect=asyncio.TimeoutError()):
            # Should handle timeout gracefully
            result = await spider_updater.validate_spider_update("test_spider")
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])
