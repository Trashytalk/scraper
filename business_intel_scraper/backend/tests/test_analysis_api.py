"""
Tests for Analysis API endpoints
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from fastapi.testclient import TestClient
from fastapi import FastAPI

from business_intel_scraper.backend.api.analysis import analysis_router
from business_intel_scraper.backend.analysis.orchestrator import AnalysisResult


# Create test app
app = FastAPI()
app.include_router(analysis_router)
client = TestClient(app)


@pytest.fixture
def sample_entity_input():
    """Sample entity input for API testing"""
    return {
        "entity_id": "test_entity_1",
        "name": "Test Company Inc.",
        "entity_type": "company",
        "address": "123 Test Street, Test City, TC 12345",
        "phone": "+1-555-0100",
        "email": "info@testcompany.com",
        "website": "https://www.testcompany.com",
        "metadata": {"industry": "technology"},
    }


@pytest.fixture
def sample_analysis_request(sample_entity_input):
    """Sample analysis request for API testing"""
    return {
        "entities": [sample_entity_input],
        "analysis_types": ["entity_resolution", "relationship_mapping"],
        "enrichment_sources": ["sanctions", "contracts"],
        "relationship_types": ["officer", "ownership"],
        "confidence_threshold": 0.7,
        "include_low_confidence": False,
        "max_related_entities": 100,
        "metadata": {"test": True},
    }


@pytest.fixture
def mock_analysis_result():
    """Mock analysis result for testing"""
    return AnalysisResult(
        request_id="test_request_123",
        analysis_date=datetime.utcnow(),
        summary={"total_findings": 5, "risk_assessment": "LOW", "entities_analyzed": 1},
        entity_resolutions=[
            {
                "cluster_id": "cluster_1",
                "entities": [
                    {"entity_id": "test_entity_1", "name": "Test Company Inc."}
                ],
                "canonical_entity": {
                    "entity_id": "test_entity_1",
                    "name": "Test Company Inc.",
                },
                "confidence_score": 0.9,
            }
        ],
        relationships=[
            {
                "source_entity": "test_entity_1",
                "target_entity": "test_entity_2",
                "relationship_type": "officer",
                "confidence_score": 0.8,
            }
        ],
        enrichments=[
            {
                "entity_id": "test_entity_1",
                "source_name": "Test Source",
                "enrichment_type": "sanctions",
                "data": {"sanctioned": False},
                "confidence_score": 0.9,
                "cost": 0.1,
            }
        ],
        events=[
            {
                "event_id": "event_1",
                "entity_id": "test_entity_1",
                "event_type": "regulatory_filing",
                "category": "regulatory",
                "severity": "medium",
                "title": "New SEC Filing",
                "confidence_score": 0.8,
            }
        ],
        metrics={"duration_seconds": 5.2, "entities_processed": 1},
    )


class TestAnalysisAPI:
    """Test cases for Analysis API endpoints"""

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_comprehensive_analysis_success(
        self,
        mock_get_user,
        mock_get_orchestrator,
        sample_analysis_request,
        mock_analysis_result,
    ):
        """Test successful comprehensive analysis"""
        # Mock user authentication
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.run_comprehensive_analysis = AsyncMock(
            return_value=mock_analysis_result
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        # Make request
        response = client.post(
            "/api/v1/analysis/comprehensive", json=sample_analysis_request
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["request_id"] == "test_request_123"
        assert data["summary"]["total_findings"] == 5
        assert data["summary"]["risk_assessment"] == "LOW"
        assert len(data["entity_resolutions"]) == 1
        assert len(data["relationships"]) == 1

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_comprehensive_analysis_validation_error(
        self, mock_get_user, mock_get_orchestrator
    ):
        """Test comprehensive analysis with validation error"""
        mock_get_user.return_value = {"user_id": "test_user"}
        mock_get_orchestrator.return_value = Mock()

        # Invalid request - missing required fields
        invalid_request = {
            "entities": [],  # Empty entities list
            "analysis_types": ["invalid_type"],  # Invalid analysis type
        }

        response = client.post("/api/v1/analysis/comprehensive", json=invalid_request)

        # Should return validation error
        assert response.status_code == 422

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_entity_resolution_endpoint(
        self, mock_get_user, mock_get_orchestrator, sample_entity_input
    ):
        """Test entity resolution endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.entity_resolver.resolve_entities.return_value = {
            "cluster_1": {
                "entities": [sample_entity_input],
                "canonical_entity": sample_entity_input,
                "confidence_score": 0.9,
            }
        }
        mock_get_orchestrator.return_value = mock_orchestrator

        request_data = {
            "entities": [sample_entity_input],
            "similarity_threshold": 0.8,
            "clustering_method": "dbscan",
            "include_similarity_matrix": False,
        }

        response = client.post("/api/v1/analysis/entity-resolution", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "clusters" in data["data"]
        assert data["data"]["total_entities"] == 1
        assert data["data"]["total_clusters"] == 1

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_relationship_mapping_endpoint(
        self, mock_get_user, mock_get_orchestrator, sample_entity_input
    ):
        """Test relationship mapping endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock relationship
        mock_relationship = Mock()
        mock_relationship.source_entity = "entity_1"
        mock_relationship.target_entity = "entity_2"
        mock_relationship.relationship_type = "officer"
        mock_relationship.confidence_score = 0.8
        mock_relationship.metadata = {"role": "ceo"}
        mock_relationship.evidence = ["evidence_1"]

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.relationship_mapper.extract_relationships.return_value = [
            mock_relationship
        ]
        mock_get_orchestrator.return_value = mock_orchestrator

        request_data = {
            "entities": [sample_entity_input],
            "relationship_types": ["officer", "ownership"],
            "confidence_threshold": 0.6,
            "include_network_graph": False,
        }

        response = client.post(
            "/api/v1/analysis/relationship-mapping", json=request_data
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "relationships" in data["data"]
        assert data["data"]["total_relationships"] == 1

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_enrichment_endpoint(
        self, mock_get_user, mock_get_orchestrator, sample_entity_input
    ):
        """Test enrichment endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock enrichment result
        mock_enrichment = Mock()
        mock_enrichment.entity_id = "test_entity_1"
        mock_enrichment.source_name = "Test Source"
        mock_enrichment.enrichment_type = "sanctions"
        mock_enrichment.data = {"sanctioned": False}
        mock_enrichment.confidence_score = 0.9
        mock_enrichment.metadata = {"source_url": "https://test.com"}
        mock_enrichment.cost = 0.05
        mock_enrichment.created_at = datetime.utcnow()

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.enrichment_engine.enrich_entities = AsyncMock(
            return_value=[mock_enrichment]
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        request_data = {
            "entities": [sample_entity_input],
            "enrichment_sources": ["sanctions", "contracts"],
            "include_cached": True,
            "max_cost": 10.0,
        }

        response = client.post("/api/v1/analysis/enrichment", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "enrichments" in data["data"]
        assert data["data"]["total_enrichments"] == 1

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_enrichment_cost_limit_exceeded(
        self, mock_get_user, mock_get_orchestrator, sample_entity_input
    ):
        """Test enrichment endpoint with cost limit exceeded"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock high-cost enrichment
        mock_enrichment = Mock()
        mock_enrichment.cost = 15.0  # Exceeds max_cost of 10.0

        mock_orchestrator = Mock()
        mock_orchestrator.enrichment_engine.enrich_entities = AsyncMock(
            return_value=[mock_enrichment]
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        request_data = {
            "entities": [sample_entity_input],
            "enrichment_sources": ["sanctions"],
            "max_cost": 10.0,
        }

        response = client.post("/api/v1/analysis/enrichment", json=request_data)

        assert response.status_code == 400
        assert "cost" in response.json()["detail"].lower()

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_event_detection_endpoint(self, mock_get_user, mock_get_orchestrator):
        """Test event detection endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock event
        mock_event = Mock()
        mock_event.event_id = "event_1"
        mock_event.entity_id = "entity_1"
        mock_event.event_type = "regulatory_filing"
        mock_event.category.value = "regulatory"
        mock_event.severity.value = "medium"
        mock_event.title = "New SEC Filing"
        mock_event.description = "Company filed new 10-K"
        mock_event.event_date = datetime.utcnow()
        mock_event.detection_date = datetime.utcnow()
        mock_event.confidence_score = 0.8
        mock_event.source = "sec_filings"
        mock_event.source_url = "https://sec.gov/filing/123"
        mock_event.metadata = {"filing_type": "10-K"}
        mock_event.related_entities = ["entity_1"]

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.event_detector.detect_events = AsyncMock(
            return_value=[mock_event]
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        request_data = {
            "data_sources": [
                {
                    "type": "news_articles",
                    "data": [{"title": "Test", "content": "Test content"}],
                }
            ],
            "entity_names": ["Test Company"],
            "severity_filter": None,
            "time_range_hours": 24,
        }

        response = client.post("/api/v1/analysis/event-detection", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "events" in data["data"]
        assert data["data"]["total_events"] == 1

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_analysis_status_endpoint(self, mock_get_user, mock_get_orchestrator):
        """Test analysis status endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.get_analysis_status = AsyncMock(
            return_value={
                "status": "completed",
                "result": {"request_id": "test_123", "summary": {}},
            }
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/status/test_123")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["data"]["status"] == "completed"

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_analysis_status_not_found(self, mock_get_user, mock_get_orchestrator):
        """Test analysis status endpoint with not found request"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.get_analysis_status = AsyncMock(
            return_value={"status": "not_found"}
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/status/nonexistent")

        assert response.status_code == 404

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_export_results_json(self, mock_get_user, mock_get_orchestrator):
        """Test export results in JSON format"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.export_analysis_results = AsyncMock(
            return_value='{"test": "data"}'
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/export/test_123?format=json")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_export_results_summary(self, mock_get_user, mock_get_orchestrator):
        """Test export results in summary format"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.export_analysis_results = AsyncMock(
            return_value="Analysis Summary Report"
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/export/test_123?format=summary")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "Analysis Summary Report" in response.text

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_get_metrics_endpoint(self, mock_get_user, mock_get_orchestrator):
        """Test get metrics endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.get_orchestrator_metrics.return_value = {
            "total_requests": 100
        }
        mock_orchestrator.entity_resolver.get_resolution_metrics.return_value = {
            "total_entities_processed": 500
        }
        mock_orchestrator.enrichment_engine.get_enrichment_metrics.return_value = {
            "total_requests": 200
        }
        mock_orchestrator.event_detector.get_detection_metrics.return_value = {
            "events_detected": 50
        }
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "data" in data
        assert "orchestrator" in data["data"]
        assert "entity_resolver" in data["data"]
        assert "enrichment_engine" in data["data"]
        assert "event_detector" in data["data"]

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_clear_cache_endpoint(self, mock_get_user, mock_get_orchestrator):
        """Test clear cache endpoint"""
        mock_get_user.return_value = {"user_id": "test_user"}

        mock_orchestrator = Mock()
        mock_orchestrator.enrichment_engine.clear_cache.return_value = None
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.delete("/api/v1/analysis/cache")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert "cache cleared" in data["message"].lower()

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    def test_health_check_endpoint(self, mock_get_orchestrator):
        """Test health check endpoint"""
        mock_orchestrator = Mock()
        mock_orchestrator.get_orchestrator_metrics.return_value = {"total_requests": 10}
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.get("/api/v1/analysis/health")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] == True
        assert data["data"]["service"] == "analysis"
        assert data["data"]["status"] == "healthy"

    def test_invalid_analysis_types_validation(self):
        """Test validation of invalid analysis types"""
        invalid_request = {
            "entities": [{"entity_id": "test", "name": "test"}],
            "analysis_types": ["invalid_type", "another_invalid"],
        }

        response = client.post("/api/v1/analysis/comprehensive", json=invalid_request)
        assert response.status_code == 422

    def test_invalid_enrichment_sources_validation(self):
        """Test validation of invalid enrichment sources"""
        invalid_request = {
            "entities": [{"entity_id": "test", "name": "test"}],
            "enrichment_sources": ["invalid_source"],
        }

        response = client.post("/api/v1/analysis/enrichment", json=invalid_request)
        assert response.status_code == 422

    def test_confidence_threshold_validation(self):
        """Test confidence threshold validation"""
        # Test negative confidence threshold
        invalid_request = {
            "entities": [{"entity_id": "test", "name": "test"}],
            "confidence_threshold": -0.5,
        }

        response = client.post("/api/v1/analysis/comprehensive", json=invalid_request)
        assert response.status_code == 422

        # Test confidence threshold > 1.0
        invalid_request["confidence_threshold"] = 1.5
        response = client.post("/api/v1/analysis/comprehensive", json=invalid_request)
        assert response.status_code == 422

    @patch("business_intel_scraper.backend.api.analysis.get_analysis_orchestrator")
    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_error_handling(
        self, mock_get_user, mock_get_orchestrator, sample_analysis_request
    ):
        """Test error handling in API endpoints"""
        mock_get_user.return_value = {"user_id": "test_user"}

        # Mock orchestrator to raise exception
        mock_orchestrator = Mock()
        mock_orchestrator.run_comprehensive_analysis = AsyncMock(
            side_effect=Exception("Analysis failed")
        )
        mock_get_orchestrator.return_value = mock_orchestrator

        response = client.post(
            "/api/v1/analysis/comprehensive", json=sample_analysis_request
        )

        assert response.status_code == 500
        assert "Analysis failed" in response.json()["detail"]

    @patch("business_intel_scraper.backend.api.analysis.get_current_user")
    def test_authentication_required(self, mock_get_user, sample_analysis_request):
        """Test that authentication is required"""
        # Mock authentication failure
        mock_get_user.side_effect = Exception("Authentication failed")

        response = client.post(
            "/api/v1/analysis/comprehensive", json=sample_analysis_request
        )

        # Should return error due to authentication failure
        assert response.status_code == 500

    def test_request_validation_edge_cases(self):
        """Test request validation edge cases"""
        # Empty entities list
        response = client.post("/api/v1/analysis/comprehensive", json={"entities": []})
        assert response.status_code == 422

        # Missing required fields
        response = client.post("/api/v1/analysis/comprehensive", json={})
        assert response.status_code == 422

        # Invalid max_related_entities
        invalid_request = {
            "entities": [{"entity_id": "test", "name": "test"}],
            "max_related_entities": 0,  # Should be >= 1
        }
        response = client.post("/api/v1/analysis/comprehensive", json=invalid_request)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_async_endpoint_behavior(
        self, sample_analysis_request, mock_analysis_result
    ):
        """Test asynchronous behavior of endpoints"""
        with patch(
            "business_intel_scraper.backend.api.analysis.get_current_user"
        ) as mock_get_user:
            with patch(
                "business_intel_scraper.backend.api.analysis.get_analysis_orchestrator"
            ) as mock_get_orchestrator:
                mock_get_user.return_value = {"user_id": "test_user"}

                mock_orchestrator = Mock()
                mock_orchestrator.run_comprehensive_analysis = AsyncMock(
                    return_value=mock_analysis_result
                )
                mock_get_orchestrator.return_value = mock_orchestrator

                response = client.post(
                    "/api/v1/analysis/comprehensive", json=sample_analysis_request
                )

                assert response.status_code == 200
                # Verify async function was called
                mock_orchestrator.run_comprehensive_analysis.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
