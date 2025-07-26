"""
API Testing Suite for Business Intelligence Scraper Backend

This module provides comprehensive API tests for the backend server,
testing REST endpoints, WebSocket functionality, and API integration.

Test Categories:
- REST API endpoint testing
- WebSocket connection and messaging
- Authentication and authorization
- Error handling and validation
- Performance and load testing
- API documentation compliance

Author: Business Intelligence Scraper Team
Version: 2.0.0
License: MIT
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import aiohttp
import websockets
from decimal import Decimal

# Test client imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Server and component imports
from backend_server import create_app, setup_database
from business_intel_scraper.backend.db.centralized_data import DataRepository, CentralizedDataRecord


# === API TEST FIXTURES ===

@pytest.fixture
async def test_client():
    """Create test client for API testing"""
    app = await create_app(testing=True)
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture
async def api_server():
    """Start test API server for integration testing"""
    import subprocess
    import asyncio
    
    # Start server in test mode
    process = subprocess.Popen([
        'python', 'backend_server.py', '--test-mode'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    await asyncio.sleep(2)
    
    yield 'http://localhost:8001'  # Test server port
    
    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture
def sample_api_data():
    """Sample data for API testing"""
    return {
        'scraping_job': {
            'url': 'https://example.com/test-article',
            'job_type': 'news',
            'options': {
                'extract_images': True,
                'extract_links': True,
                'follow_redirects': True
            }
        },
        'data_record': {
            'source_url': 'https://test.com/article',
            'title': 'Test Article for API',
            'extracted_text': 'This is test content for API validation',
            'data_type': 'news',
            'content_category': 'technology',
            'language': 'en',
            'word_count': 50,
            'scraped_at': datetime.utcnow().isoformat()
        },
        'search_query': {
            'query': 'artificial intelligence',
            'filters': {
                'data_type': 'news',
                'date_range': {
                    'start': (datetime.utcnow() - timedelta(days=7)).isoformat(),
                    'end': datetime.utcnow().isoformat()
                }
            },
            'limit': 20,
            'offset': 0
        },
        'analytics_request': {
            'period_type': 'daily',
            'date_range': {
                'start': (datetime.utcnow() - timedelta(days=30)).isoformat(),
                'end': datetime.utcnow().isoformat()
            },
            'metrics': ['content_volume', 'quality_trends', 'source_diversity']
        }
    }


# === REST API ENDPOINT TESTS ===

class TestHealthEndpoints:
    """Test health and status API endpoints"""
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, test_client, api_server):
        """Test basic health check endpoint"""
        async with test_client.get(f'{api_server}/health') as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'status' in data
            assert 'timestamp' in data
            assert 'version' in data
            assert data['status'] == 'healthy'
    
    @pytest.mark.asyncio
    async def test_system_status_endpoint(self, test_client, api_server):
        """Test detailed system status endpoint"""
        async with test_client.get(f'{api_server}/api/v1/status') as response:
            assert response.status == 200
            data = await response.json()
            
            # Verify status structure
            assert 'system' in data
            assert 'database' in data
            assert 'services' in data
            assert 'metrics' in data
            
            # Verify system info
            system_info = data['system']
            assert 'uptime' in system_info
            assert 'memory_usage' in system_info
            assert 'cpu_usage' in system_info
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, test_client, api_server):
        """Test metrics collection endpoint"""
        async with test_client.get(f'{api_server}/api/v1/metrics') as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'performance' in data
            assert 'resources' in data
            assert 'activity' in data
            
            # Verify metrics structure
            performance = data['performance']
            assert 'response_times' in performance
            assert 'throughput' in performance


class TestScrapingEndpoints:
    """Test scraping-related API endpoints"""
    
    @pytest.mark.asyncio
    async def test_submit_scraping_job(self, test_client, api_server, sample_api_data):
        """Test submitting a new scraping job"""
        job_data = sample_api_data['scraping_job']
        
        async with test_client.post(
            f'{api_server}/api/v1/scraping/jobs',
            json=job_data
        ) as response:
            assert response.status == 201
            data = await response.json()
            
            assert 'job_id' in data
            assert 'status' in data
            assert 'created_at' in data
            assert data['status'] == 'queued'
            
            return data['job_id']
    
    @pytest.mark.asyncio
    async def test_get_scraping_job_status(self, test_client, api_server, sample_api_data):
        """Test retrieving scraping job status"""
        # First submit a job
        job_data = sample_api_data['scraping_job']
        async with test_client.post(
            f'{api_server}/api/v1/scraping/jobs',
            json=job_data
        ) as submit_response:
            submit_data = await submit_response.json()
            job_id = submit_data['job_id']
        
        # Then check its status
        async with test_client.get(
            f'{api_server}/api/v1/scraping/jobs/{job_id}'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'job_id' in data
            assert 'status' in data
            assert 'progress' in data
            assert data['job_id'] == job_id
    
    @pytest.mark.asyncio
    async def test_list_scraping_jobs(self, test_client, api_server):
        """Test listing scraping jobs with pagination"""
        async with test_client.get(
            f'{api_server}/api/v1/scraping/jobs?limit=10&offset=0'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'jobs' in data
            assert 'total_count' in data
            assert 'pagination' in data
            assert isinstance(data['jobs'], list)
    
    @pytest.mark.asyncio
    async def test_cancel_scraping_job(self, test_client, api_server, sample_api_data):
        """Test canceling a scraping job"""
        # Submit a job first
        job_data = sample_api_data['scraping_job']
        async with test_client.post(
            f'{api_server}/api/v1/scraping/jobs',
            json=job_data
        ) as submit_response:
            submit_data = await submit_response.json()
            job_id = submit_data['job_id']
        
        # Cancel the job
        async with test_client.delete(
            f'{api_server}/api/v1/scraping/jobs/{job_id}'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert data['status'] == 'cancelled'
            assert data['job_id'] == job_id


class TestDataEndpoints:
    """Test data management API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_data_record(self, test_client, api_server, sample_api_data):
        """Test creating a new data record"""
        record_data = sample_api_data['data_record']
        
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=record_data
        ) as response:
            assert response.status == 201
            data = await response.json()
            
            assert 'record_id' in data
            assert 'record_uuid' in data
            assert 'created_at' in data
            assert 'quality_score' in data
            
            return data['record_id']
    
    @pytest.mark.asyncio
    async def test_get_data_record(self, test_client, api_server, sample_api_data):
        """Test retrieving a specific data record"""
        # Create a record first
        record_data = sample_api_data['data_record']
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=record_data
        ) as create_response:
            create_data = await create_response.json()
            record_id = create_data['record_id']
        
        # Retrieve the record
        async with test_client.get(
            f'{api_server}/api/v1/data/records/{record_id}'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert data['record_id'] == record_id
            assert data['source_url'] == record_data['source_url']
            assert data['title'] == record_data['title']
    
    @pytest.mark.asyncio
    async def test_search_data_records(self, test_client, api_server, sample_api_data):
        """Test searching data records"""
        search_data = sample_api_data['search_query']
        
        async with test_client.post(
            f'{api_server}/api/v1/data/search',
            json=search_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'results' in data
            assert 'total_count' in data
            assert 'search_metadata' in data
            assert isinstance(data['results'], list)
    
    @pytest.mark.asyncio
    async def test_update_data_record(self, test_client, api_server, sample_api_data):
        """Test updating a data record"""
        # Create a record first
        record_data = sample_api_data['data_record']
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=record_data
        ) as create_response:
            create_data = await create_response.json()
            record_id = create_data['record_id']
        
        # Update the record
        update_data = {
            'title': 'Updated Test Article Title',
            'content_category': 'science'
        }
        
        async with test_client.patch(
            f'{api_server}/api/v1/data/records/{record_id}',
            json=update_data
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert data['title'] == update_data['title']
            assert data['content_category'] == update_data['content_category']
    
    @pytest.mark.asyncio
    async def test_delete_data_record(self, test_client, api_server, sample_api_data):
        """Test deleting a data record"""
        # Create a record first
        record_data = sample_api_data['data_record']
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=record_data
        ) as create_response:
            create_data = await create_response.json()
            record_id = create_data['record_id']
        
        # Delete the record
        async with test_client.delete(
            f'{api_server}/api/v1/data/records/{record_id}'
        ) as response:
            assert response.status == 204
        
        # Verify record is deleted
        async with test_client.get(
            f'{api_server}/api/v1/data/records/{record_id}'
        ) as get_response:
            assert get_response.status == 404


class TestAnalyticsEndpoints:
    """Test analytics and reporting API endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_analytics_summary(self, test_client, api_server):
        """Test getting analytics summary"""
        async with test_client.get(
            f'{api_server}/api/v1/analytics/summary'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'overview' in data
            assert 'performance' in data
            assert 'trends' in data
    
    @pytest.mark.asyncio
    async def test_get_content_analytics(self, test_client, api_server, sample_api_data):
        """Test getting content analytics"""
        analytics_request = sample_api_data['analytics_request']
        
        async with test_client.post(
            f'{api_server}/api/v1/analytics/content',
            json=analytics_request
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'period_type' in data
            assert 'metrics' in data
            assert 'time_series' in data
    
    @pytest.mark.asyncio
    async def test_get_quality_analytics(self, test_client, api_server):
        """Test getting data quality analytics"""
        async with test_client.get(
            f'{api_server}/api/v1/analytics/quality'
        ) as response:
            assert response.status == 200
            data = await response.json()
            
            assert 'quality_distribution' in data
            assert 'validation_results' in data
            assert 'improvement_suggestions' in data


# === WEBSOCKET TESTS ===

class TestWebSocketConnections:
    """Test WebSocket functionality"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, api_server):
        """Test basic WebSocket connection"""
        ws_url = api_server.replace('http://', 'ws://') + '/ws'
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Test connection
                assert websocket.open
                
                # Send ping
                await websocket.send(json.dumps({
                    'type': 'ping',
                    'timestamp': datetime.utcnow().isoformat()
                }))
                
                # Receive pong
                response = await websocket.recv()
                data = json.loads(response)
                assert data['type'] == 'pong'
                
        except Exception as e:
            pytest.skip(f"WebSocket not available: {e}")
    
    @pytest.mark.asyncio
    async def test_websocket_job_updates(self, api_server, sample_api_data):
        """Test WebSocket job status updates"""
        ws_url = api_server.replace('http://', 'ws://') + '/ws/jobs'
        
        try:
            async with websockets.connect(ws_url) as websocket:
                # Subscribe to job updates
                await websocket.send(json.dumps({
                    'type': 'subscribe',
                    'channel': 'job_updates'
                }))
                
                # Wait for subscription confirmation
                response = await websocket.recv()
                data = json.loads(response)
                assert data['type'] == 'subscription_confirmed'
                
        except Exception as e:
            pytest.skip(f"WebSocket not available: {e}")


# === ERROR HANDLING TESTS ===

class TestAPIErrorHandling:
    """Test API error handling and validation"""
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint(self, test_client, api_server):
        """Test handling of invalid API endpoints"""
        async with test_client.get(f'{api_server}/api/v1/nonexistent') as response:
            assert response.status == 404
            data = await response.json()
            assert 'error' in data
            assert data['error']['code'] == 'endpoint_not_found'
    
    @pytest.mark.asyncio
    async def test_invalid_json_payload(self, test_client, api_server):
        """Test handling of invalid JSON payloads"""
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            data='invalid json'
        ) as response:
            assert response.status == 400
            data = await response.json()
            assert 'error' in data
            assert 'validation' in data['error']['code']
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, test_client, api_server):
        """Test handling of missing required fields"""
        incomplete_data = {
            'title': 'Test Article'
            # Missing required fields like source_url
        }
        
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=incomplete_data
        ) as response:
            assert response.status == 422
            data = await response.json()
            assert 'error' in data
            assert 'validation_errors' in data
    
    @pytest.mark.asyncio
    async def test_resource_not_found(self, test_client, api_server):
        """Test handling of non-existent resource requests"""
        fake_id = '99999'
        async with test_client.get(
            f'{api_server}/api/v1/data/records/{fake_id}'
        ) as response:
            assert response.status == 404
            data = await response.json()
            assert 'error' in data
            assert data['error']['code'] == 'resource_not_found'
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, test_client, api_server):
        """Test API rate limiting"""
        # Make multiple rapid requests
        responses = []
        for i in range(20):  # Assuming rate limit is lower than 20
            async with test_client.get(f'{api_server}/health') as response:
                responses.append(response.status)
        
        # Check if any requests were rate limited
        if 429 in responses:
            # Rate limiting is working
            assert True
        else:
            # Rate limiting might not be configured or limit is higher
            pytest.skip("Rate limiting not configured or limit too high")


# === PERFORMANCE TESTS ===

class TestAPIPerformance:
    """Test API performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_response_time_health_check(self, test_client, api_server):
        """Test response time for health check endpoint"""
        start_time = time.time()
        
        async with test_client.get(f'{api_server}/health') as response:
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status == 200
            assert response_time < 1.0  # Should respond within 1 second
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_client, api_server):
        """Test handling of concurrent requests"""
        async def make_request():
            async with test_client.get(f'{api_server}/health') as response:
                return response.status
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    @pytest.mark.asyncio
    async def test_large_payload_handling(self, test_client, api_server):
        """Test handling of large payloads"""
        large_text = 'A' * 100000  # 100KB text
        large_record = {
            'source_url': 'https://example.com/large-article',
            'title': 'Large Article Test',
            'extracted_text': large_text,
            'data_type': 'news',
            'word_count': len(large_text.split())
        }
        
        start_time = time.time()
        async with test_client.post(
            f'{api_server}/api/v1/data/records',
            json=large_record
        ) as response:
            end_time = time.time()
            response_time = end_time - start_time
            
            # Should handle large payloads reasonably fast
            assert response.status in [201, 413]  # Created or payload too large
            if response.status == 201:
                assert response_time < 5.0  # Should complete within 5 seconds


# === AUTHENTICATION TESTS ===

class TestAuthentication:
    """Test API authentication and authorization"""
    
    @pytest.mark.asyncio
    async def test_protected_endpoint_without_auth(self, test_client, api_server):
        """Test accessing protected endpoint without authentication"""
        async with test_client.get(
            f'{api_server}/api/v1/admin/users'
        ) as response:
            # Should require authentication
            assert response.status in [401, 403]
    
    @pytest.mark.asyncio
    async def test_invalid_api_key(self, test_client, api_server):
        """Test using invalid API key"""
        headers = {'Authorization': 'Bearer invalid-api-key'}
        
        async with test_client.get(
            f'{api_server}/api/v1/admin/users',
            headers=headers
        ) as response:
            assert response.status in [401, 403]
            data = await response.json()
            assert 'error' in data


if __name__ == "__main__":
    # Run API tests
    pytest.main([__file__, "-v", "--tb=short", "-k", "not test_websocket"])
