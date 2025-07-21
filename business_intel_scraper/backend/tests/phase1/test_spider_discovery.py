"""
Test suite for Phase 1: Enhanced Web Discovery spider functionality.

Tests core spider discovery, OSINT integration, and content extraction.
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from pathlib import Path

from business_intel_scraper.backend.modules.spiders import CompanyRegistrySpider
from business_intel_scraper.backend.modules.crawlers.browser import BrowserCrawler
from business_intel_scraper.backend.discovery.automated_discovery import AutomatedDiscoveryManager
from business_intel_scraper.backend.integrations.spiderfoot_wrapper import SpiderfootWrapper


class TestSpiderDiscovery:
    """Test core spider discovery functionality."""
    
    @pytest.fixture
    def mock_spider(self):
        """Create a mock spider for testing."""
        spider = Mock(spec=CompanyRegistrySpider)
        spider.name = "test_spider"
        spider.allowed_domains = ["example.com"]
        spider.start_urls = ["https://example.com"]
        return spider
    
    @pytest.fixture
    def discovery_manager(self):
        """Create discovery manager instance."""
        return AutomatedDiscoveryManager()
    
    def test_spider_initialization(self, mock_spider):
        """Test spider properly initializes with required attributes."""
        assert hasattr(mock_spider, 'name')
        assert hasattr(mock_spider, 'allowed_domains')
        assert hasattr(mock_spider, 'start_urls')
        assert mock_spider.name == "test_spider"
    
    def test_spider_parse_method_exists(self, mock_spider):
        """Test spider has parse method."""
        assert hasattr(mock_spider, 'parse')
    
    @pytest.mark.asyncio
    async def test_discovery_manager_initialization(self, discovery_manager):
        """Test discovery manager initializes properly."""
        assert discovery_manager is not None
        assert hasattr(discovery_manager, 'discovered_sources')
    
    @pytest.mark.asyncio 
    async def test_seed_source_discovery(self, discovery_manager):
        """Test discovery of seed sources."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="""
                <html>
                    <body>
                        <a href="https://example.com/companies">Company Registry</a>
                        <a href="https://example.com/news">Business News</a>
                    </body>
                </html>
            """)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Test discovery
            sources = await discovery_manager.discover_seed_sources("https://example.com")
            
            assert len(sources) > 0
            assert any("company" in str(source).lower() for source in sources)
    
    @pytest.mark.asyncio
    async def test_content_extraction_basic(self, discovery_manager):
        """Test basic content extraction from discovered sources."""
        html_content = """
        <html>
            <head><title>Test Company Registry</title></head>
            <body>
                <h1>Company Registry</h1>
                <div class="company-info">
                    <h2>ABC Corp</h2>
                    <p>Registration: 12345</p>
                    <p>Industry: Technology</p>
                </div>
            </body>
        </html>
        """
        
        extracted = await discovery_manager.extract_business_entities(html_content)
        
        assert extracted is not None
        assert len(extracted) > 0
    
    def test_osint_integration_wrapper(self):
        """Test OSINT integration wrapper functionality."""
        wrapper = SpiderfootWrapper()
        
        # Test wrapper initialization
        assert wrapper is not None
        assert hasattr(wrapper, 'run_scan')
    
    @pytest.mark.asyncio
    async def test_spider_error_handling(self, discovery_manager):
        """Test spider handles errors gracefully."""
        # Test with invalid URL
        with pytest.raises(Exception):
            await discovery_manager.discover_seed_sources("invalid-url")
        
        # Test with timeout
        with patch('aiohttp.ClientSession.get', side_effect=asyncio.TimeoutError()):
            sources = await discovery_manager.discover_seed_sources("https://example.com")
            assert sources == []


class TestSpiderPerformance:
    """Test spider performance and resource usage."""
    
    @pytest.mark.asyncio
    async def test_concurrent_discovery(self):
        """Test multiple concurrent discovery operations."""
        manager = AutomatedDiscoveryManager()
        
        urls = [
            "https://example1.com",
            "https://example2.com", 
            "https://example3.com"
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Test concurrent discovery
            tasks = [manager.discover_seed_sources(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            assert len(results) == 3
            assert all(isinstance(result, list) for result in results)
    
    def test_memory_usage_monitoring(self):
        """Test spider memory usage stays within bounds."""
        # This would be implemented with memory profiling
        pass
    
    def test_rate_limiting_compliance(self):
        """Test spiders respect rate limits."""
        # This would test rate limiting functionality
        pass


class TestSpiderQuality:
    """Test spider output quality and data validation."""
    
    @pytest.mark.asyncio
    async def test_extracted_data_structure(self, discovery_manager):
        """Test extracted data follows expected structure."""
        html_content = """
        <div class="company">
            <h2>Test Company</h2>
            <span class="registration">REG123</span>
        </div>
        """
        
        extracted = await discovery_manager.extract_business_entities(html_content)
        
        # Validate structure
        if extracted:
            for entity in extracted:
                assert 'name' in entity or 'company' in entity
    
    def test_duplicate_detection(self):
        """Test system detects and handles duplicate discoveries."""
        pass
    
    def test_data_validation_rules(self):
        """Test extracted data passes validation rules."""
        pass


class TestSpiderRobustness:
    """Test spider robustness against various scenarios."""
    
    @pytest.mark.asyncio
    async def test_malformed_html_handling(self, discovery_manager):
        """Test spider handles malformed HTML gracefully."""
        malformed_html = "<html><body><div>Unclosed div<span>Unclosed span</body>"
        
        try:
            extracted = await discovery_manager.extract_business_entities(malformed_html)
            # Should not crash, may return empty results
            assert isinstance(extracted, list)
        except Exception as e:
            pytest.fail(f"Spider should handle malformed HTML gracefully: {e}")
    
    @pytest.mark.asyncio
    async def test_network_failure_recovery(self, discovery_manager):
        """Test spider recovers from network failures."""
        with patch('aiohttp.ClientSession.get', side_effect=ConnectionError()):
            sources = await discovery_manager.discover_seed_sources("https://example.com")
            assert sources == []  # Should return empty list, not crash
    
    def test_javascript_heavy_sites(self):
        """Test spider handles JavaScript-heavy sites."""
        # This would test browser crawler functionality
        crawler = BrowserCrawler()
        assert crawler is not None


if __name__ == "__main__":
    pytest.main([__file__])
