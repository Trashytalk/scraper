"""
Comprehensive Test Suite for Backend API
Tests all endpoints with various scenarios and edge cases
"""

import pytest
import pytest_asyncio
import httpx
import asyncio
from datetime import datetime, timedelta
from faker import Faker
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

# Initialize Faker for generating test data
fake = Faker()

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test basic health check"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
            
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert data["service"] == "enhanced-visual-analytics-api"
    
    @pytest.mark.asyncio
    async def test_health_check_response_time(self):
        """Test health check response time"""
        start_time = datetime.now()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second

class TestNetworkDataEndpoint:
    """Test network data endpoint with filtering"""
    
    @pytest.mark.asyncio
    async def test_network_data_no_filters(self):
        """Test network data without filters"""
        payload = {}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/network-data", 
                json=payload, 
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert "edges" in data
        assert "metadata" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        assert len(data["nodes"]) > 0
    
    @pytest.mark.asyncio
    async def test_network_data_with_filters(self):
        """Test network data with various filters"""
        test_cases = [
            {
                "entity_type": "person",
                "confidence_threshold": 0.8,
            },
            {
                "entity_type": "organization", 
                "search_term": "corp",
            },
            {
                "confidence_threshold": 0.5,
                "search_term": "analyst",
            }
        ]
        
        for payload in test_cases:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/network-data",
                    json=payload,
                    timeout=TEST_TIMEOUT
                )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "nodes" in data
            assert "edges" in data
            assert "metadata" in data
            
            # Verify filter application in metadata
            if payload:
                assert data["metadata"]["applied_filters"] == payload
    
    @pytest.mark.asyncio
    async def test_network_data_invalid_input(self):
        """Test network data with invalid input"""
        invalid_payloads = [
            {"confidence_threshold": 1.5},  # Invalid confidence > 1
            {"confidence_threshold": -0.1},  # Invalid confidence < 0
            {"entity_type": "invalid_type"},  # Non-existent entity type
        ]
        
        for payload in invalid_payloads:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/network-data",
                    json=payload,
                    timeout=TEST_TIMEOUT
                )
            
            # Should still return 200 but with filtered results
            assert response.status_code == 200

class TestTimelineDataEndpoint:
    """Test timeline data endpoint"""
    
    @pytest.mark.asyncio
    async def test_timeline_data_success(self):
        """Test timeline data retrieval"""
        payload = {}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/timeline-data",
                json=payload,
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "groups" in data
        assert "metadata" in data
        assert isinstance(data["events"], list)
        assert isinstance(data["groups"], list)
    
    @pytest.mark.asyncio
    async def test_timeline_data_with_filters(self):
        """Test timeline data with date range filtering"""
        payload = {
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-12-31"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/timeline-data",
                json=payload,
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "metadata" in data

class TestGeospatialDataEndpoint:
    """Test geospatial data endpoint"""
    
    @pytest.mark.asyncio
    async def test_geospatial_data_success(self):
        """Test geospatial data retrieval"""
        payload = {}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/geospatial-data",
                json=payload,
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "locations" in data
        assert "metadata" in data
        assert isinstance(data["locations"], list)

class TestExportEndpoints:
    """Test data export functionality"""
    
    @pytest.mark.asyncio
    async def test_export_network_json(self):
        """Test network data export in JSON format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/export/network?format=json",
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert "edges" in data
        assert "metadata" in data
    
    @pytest.mark.asyncio
    async def test_export_timeline_json(self):
        """Test timeline data export in JSON format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/export/timeline?format=json",
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert "metadata" in data
    
    @pytest.mark.asyncio
    async def test_export_geospatial_json(self):
        """Test geospatial data export in JSON format"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/export/geospatial?format=json",
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "locations" in data
        assert "metadata" in data
    
    @pytest.mark.asyncio
    async def test_export_csv_format(self):
        """Test CSV export format"""
        endpoints = ["network", "timeline", "geospatial"]
        
        for endpoint in endpoints:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/export/{endpoint}?format=csv",
                    timeout=TEST_TIMEOUT
                )
            
            assert response.status_code == 200
            # CSV response should have text/csv content type
            content_type = response.headers.get("content-type", "")
            assert "text/csv" in content_type or "application/csv" in content_type

class TestWebSocketEndpoint:
    """Test WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        import websockets
        
        try:
            # Test connection establishment
            uri = f"ws://localhost:8000/ws"
            
            async with websockets.connect(uri, timeout=10) as websocket:
                # Should be able to connect without errors
                assert websocket.open
                
                # Try to receive a message (with timeout)
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    # Verify message structure
                    assert "type" in data
                    assert "timestamp" in data
                    
                except asyncio.TimeoutError:
                    # No message received, which is also acceptable
                    pass
                    
        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {e}")

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoints(self):
        """Test invalid endpoint requests"""
        invalid_endpoints = [
            "/invalid-endpoint",
            "/network-data-invalid",
            "/export/invalid-type",
        ]
        
        for endpoint in invalid_endpoints:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}{endpoint}", timeout=TEST_TIMEOUT)
            
            assert response.status_code in [404, 405, 422]
    
    @pytest.mark.asyncio
    async def test_malformed_json(self):
        """Test malformed JSON payload handling"""
        async with httpx.AsyncClient() as client:
            # Send malformed JSON
            response = await client.post(
                f"{BASE_URL}/network-data",
                content="{invalid_json}",
                headers={"content-type": "application/json"},
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code in [400, 422]  # Bad request or validation error

class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health", timeout=TEST_TIMEOUT)
            return response.status_code
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    @pytest.mark.asyncio
    async def test_large_payload(self):
        """Test handling of large payloads"""
        # Generate large search term
        large_search_term = fake.text(max_nb_chars=1000)
        
        payload = {
            "search_term": large_search_term,
            "confidence_threshold": 0.5
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/network-data",
                json=payload,
                timeout=TEST_TIMEOUT
            )
        
        assert response.status_code == 200

# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Test runner configuration
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=business_intel_scraper.backend",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])
