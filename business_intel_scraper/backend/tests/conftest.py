"""
Test configuration and fixtures for Phase 1 and Phase 2 testing.

Provides shared fixtures and configuration for all test suites.
"""
from __future__ import annotations

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_html_response():
    """Mock HTML response for testing."""
    return """
    <html>
        <head><title>Test Business Registry</title></head>
        <body>
            <div class="company-list">
                <div class="company" id="comp-1">
                    <h2>ABC Corporation</h2>
                    <span class="reg-num">123456</span>
                    <p class="address">123 Business St, City, State</p>
                </div>
                <div class="company" id="comp-2">
                    <h2>XYZ Industries</h2>
                    <span class="reg-num">789012</span>
                    <p class="address">456 Industry Ave, City, State</p>
                </div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def mock_osint_response():
    """Mock OSINT tool response."""
    return {
        'target': 'example.com',
        'results': [
            {'type': 'domain', 'value': 'example.com', 'source': 'DNS'},
            {'type': 'email', 'value': 'contact@example.com', 'source': 'Website'},
            {'type': 'social', 'value': 'twitter.com/example', 'source': 'Social Media'}
        ],
        'status': 'completed',
        'scan_time': '2024-01-01T12:00:00Z'
    }


@pytest.fixture  
def sample_spider_code():
    """Sample spider code for testing."""
    return '''
import scrapy

class TestBusinessSpider(scrapy.Spider):
    name = "test_business"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/companies"]
    
    def parse(self, response):
        for company in response.css('.company'):
            yield {
                'name': company.css('.company-name::text').get(),
                'registration': company.css('.reg-num::text').get(),
                'address': company.css('.address::text').get()
            }
    '''


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="<html><body>Test</body></html>")
    mock_session.get.return_value.__aenter__.return_value = mock_response
    return mock_session


# Test markers for organizing test execution
pytest.mark.unit = pytest.mark.mark("unit")
pytest.mark.integration = pytest.mark.mark("integration")  
pytest.mark.performance = pytest.mark.mark("performance")
pytest.mark.load_test = pytest.mark.mark("load_test")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests") 
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "load_test: marks tests as load tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
