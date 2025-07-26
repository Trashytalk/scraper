"""
Integration tests for the complete Analysis & Cross-Referencing Layer
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, Mock

from business_intel_scraper.backend.analysis import (
    AdvancedEntityResolver,
    EntityRelationshipMapper,
    DataEnrichmentEngine,
    BusinessEventDetector,
    AnalysisOrchestrator,
)
from business_intel_scraper.backend.analysis.orchestrator import AnalysisRequest


@pytest.fixture
def comprehensive_test_data() -> Dict[str, Any]:
    """Comprehensive test data for integration testing"""
    return {
        "entities": [
            {
                "entity_id": "company_1",
                "name": "TechCorp Inc.",
                "entity_type": "company",
                "address": "123 Innovation Drive, San Francisco, CA 94105",
                "phone": "+1-415-555-0100",
                "email": "info@techcorp.com",
                "website": "https://www.techcorp.com",
                "domain": "techcorp.com",
                "officers": ["John Smith CEO", "Sarah Johnson CTO"],
                "industry": "Technology",
                "founded": 2010,
                "employees": 500,
            },
            {
                "entity_id": "company_2",
                "name": "Tech Corp Inc",  # Similar name for resolution testing
                "entity_type": "company",
                "address": "123 Innovation Dr, San Francisco, CA 94105",  # Similar address
                "phone": "415-555-0100",  # Same phone, different format
                "email": "contact@techcorp.com",
                "website": "techcorp.com",
                "domain": "techcorp.com",
                "industry": "Software",
            },
            {
                "entity_id": "person_1",
                "name": "John Smith",
                "entity_type": "person",
                "title": "Chief Executive Officer",
                "companies": ["TechCorp Inc."],
                "address": "456 Executive Row, San Francisco, CA 94106",
                "phone": "+1-415-555-0101",
                "email": "john.smith@techcorp.com",
                "linkedin": "https://linkedin.com/in/johnsmith-ceo",
            },
            {
                "entity_id": "person_2",
                "name": "Sarah Johnson",
                "entity_type": "person",
                "title": "Chief Technology Officer",
                "companies": ["TechCorp Inc."],
                "address": "789 Tech Street, San Francisco, CA 94107",
                "phone": "+1-415-555-0102",
                "email": "sarah.johnson@techcorp.com",
            },
            {
                "entity_id": "company_3",
                "name": "TechCorp Labs",
                "entity_type": "company",
                "address": "123 Innovation Drive, San Francisco, CA 94105",  # Same as parent
                "phone": "+1-415-555-0200",
                "email": "labs@techcorp.com",
                "website": "https://labs.techcorp.com",
                "domain": "techcorp.com",  # Same domain as parent
                "parent_company": "TechCorp Inc.",
                "ownership_percentage": 100.0,
            },
            {
                "entity_id": "company_4",
                "name": "DataViz Solutions",
                "entity_type": "company",
                "address": "987 Analytics Ave, Palo Alto, CA 94301",
                "phone": "+1-650-555-0300",
                "email": "info@dataviz.com",
                "website": "https://www.dataviz.com",
                "domain": "dataviz.com",
                "officers": ["Michael Brown CEO"],
                "industry": "Data Analytics",
            },
        ],
        "data_sources": [
            {
                "type": "news_articles",
                "data": [
                    {
                        "title": "TechCorp Inc Announces Major Acquisition",
                        "content": "TechCorp Inc announced today that it has acquired DataViz Solutions for $50 million. The acquisition will strengthen TechCorp's data analytics capabilities.",
                        "published_date": "2024-01-15T10:00:00Z",
                        "entity_id": "company_1",
                        "url": "https://techcrunch.com/techcorp-acquisition",
                    },
                    {
                        "title": "New SEC Filing from TechCorp Inc",
                        "content": "TechCorp Inc filed form 8-K with the SEC today regarding changes in executive leadership.",
                        "published_date": "2024-01-20T14:30:00Z",
                        "entity_id": "company_1",
                        "url": "https://sec.gov/filing/techcorp-8k",
                    },
                ],
                "url": "https://newsapi.org",
            },
            {
                "type": "filings",
                "data": [
                    {
                        "type": "8-K",
                        "content": "Current Report pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934. TechCorp Inc announces appointment of new Chief Technology Officer.",
                        "date": "2024-01-20T14:30:00Z",
                        "entity_id": "company_1",
                    }
                ],
            },
        ],
    }


@pytest.fixture
def integration_config() -> Dict[str, Any]:
    """Configuration for integration testing"""
    return {
        "entity_resolution": {
            "similarity_threshold": 0.7,
            "clustering_eps": 0.3,
            "min_samples": 2,
            "use_ml_clustering": True,
            "field_weights": {"name": 0.4, "address": 0.3, "phone": 0.2, "email": 0.1},
        },
        "relationship_mapping": {
            "confidence_threshold": 0.6,
            "max_relationships": 1000,
            "include_weak_relationships": True,
            "relationship_weights": {
                "officer": 1.0,
                "ownership": 0.9,
                "shared_address": 0.7,
                "shared_contact": 0.6,
                "shared_domain": 0.8,
            },
        },
        "enrichment": {
            "cache_ttl_hours": 1,  # Short TTL for testing
            "max_concurrent_requests": 5,
            "max_cost_per_request": 1.0,
            "enabled_sources": ["sanctions", "contracts", "financial"],
        },
        "event_detection": {
            "deduplication_window_hours": 1,  # Short window for testing
            "min_confidence": 0.6,
            "max_events_per_scan": 100,
            "enabled_patterns": [
                "ownership_acquisition",
                "regulatory_filing",
                "executive_change",
            ],
        },
    }


class TestAnalysisIntegration:
    """Integration tests for the complete analysis pipeline"""

    def test_full_analysis_pipeline(self, comprehensive_test_data, integration_config):
        """Test the complete analysis pipeline end-to-end"""
        # Create orchestrator
        orchestrator = AnalysisOrchestrator(integration_config)

        # Create analysis request
        request = AnalysisRequest(
            request_id="integration_test_001",
            entities=comprehensive_test_data["entities"],
            analysis_types=[
                "entity_resolution",
                "relationship_mapping",
                "enrichment",
                "event_detection",
            ],
            enrichment_sources=["sanctions", "contracts"],
            relationship_types=["officer", "ownership", "address", "contact", "domain"],
            confidence_threshold=0.6,
            include_low_confidence=False,
            max_related_entities=100,
        )

        # Run analysis
        result = asyncio.run(orchestrator.run_comprehensive_analysis(request))

        # Verify results
        assert result.request_id == "integration_test_001"
        assert len(result.errors) == 0  # No errors should occur

        # Check entity resolution results
        assert len(result.entity_resolutions) > 0

        # Should detect TechCorp duplicates
        techcorp_clusters = [
            r
            for r in result.entity_resolutions
            if "techcorp" in r["canonical_entity"]["name"].lower()
        ]
        assert len(techcorp_clusters) > 0

        # Check relationship mapping results
        assert len(result.relationships) > 0

        # Should find officer relationships
        officer_rels = [
            r for r in result.relationships if r["relationship_type"] == "officer"
        ]
        assert len(officer_rels) > 0

        # Should find ownership relationships
        ownership_rels = [
            r for r in result.relationships if r["relationship_type"] == "ownership"
        ]
        assert len(ownership_rels) > 0

        # Check summary
        assert result.summary["entities_analyzed"] == len(
            comprehensive_test_data["entities"]
        )
        assert result.summary["total_findings"] > 0
        assert "risk_assessment" in result.summary

        # Check metrics
        assert result.metrics["duration_seconds"] > 0
        assert result.metrics["entities_processed"] == len(
            comprehensive_test_data["entities"]
        )

    @patch(
        "business_intel_scraper.backend.analysis.enrichment_engine.aiohttp.ClientSession"
    )
    def test_enrichment_integration(
        self, mock_session, comprehensive_test_data, integration_config
    ):
        """Test enrichment integration with mocked external APIs"""
        # Mock HTTP responses
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = asyncio.coroutine(lambda: {"status": "success"})

        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = (
            mock_response
        )

        enrichment_engine = DataEnrichmentEngine(integration_config["enrichment"])

        # Run enrichment
        enrichments = asyncio.run(
            enrichment_engine.enrich_entities(
                comprehensive_test_data["entities"][:2],  # Test with subset
                ["sanctions", "contracts"],
            )
        )

        # Should have some enrichment results (even if simulated)
        assert isinstance(enrichments, list)

        # Check enrichment metrics
        metrics = enrichment_engine.get_enrichment_metrics()
        assert "total_requests" in metrics

    def test_event_detection_integration(
        self, comprehensive_test_data, integration_config
    ):
        """Test event detection integration"""
        event_detector = BusinessEventDetector(integration_config["event_detection"])

        # Run event detection
        events = asyncio.run(
            event_detector.detect_events(
                comprehensive_test_data["data_sources"],
                [entity["name"] for entity in comprehensive_test_data["entities"]],
            )
        )

        # Should detect some events
        assert len(events) > 0

        # Should detect acquisition event
        acquisition_events = [e for e in events if "acquisition" in e.title.lower()]
        assert len(acquisition_events) > 0

        # Should detect regulatory filing event
        filing_events = [
            e for e in events if "filing" in e.title.lower() or "sec" in e.title.lower()
        ]
        assert len(filing_events) > 0

    def test_component_integration(self, comprehensive_test_data, integration_config):
        """Test integration between individual components"""
        # Initialize components
        entity_resolver = AdvancedEntityResolver(
            integration_config["entity_resolution"]
        )
        relationship_mapper = EntityRelationshipMapper(
            integration_config["relationship_mapping"]
        )

        # Step 1: Resolve entities
        entity_clusters = entity_resolver.resolve_entities(
            comprehensive_test_data["entities"]
        )

        # Step 2: Use resolved entities for relationship mapping
        resolved_entities = []
        for cluster_data in entity_clusters.values():
            resolved_entities.extend(cluster_data["entities"])

        relationships = relationship_mapper.extract_relationships(
            resolved_entities, ["officer", "ownership", "address"]
        )

        # Verify integration
        assert len(entity_clusters) > 0
        assert len(relationships) > 0

        # Should have fewer entity clusters than original entities (due to duplicates)
        assert len(entity_clusters) < len(comprehensive_test_data["entities"])

    def test_performance_with_large_dataset(self, integration_config):
        """Test performance with larger dataset"""
        # Generate larger dataset
        large_entities = []

        # Create companies
        for i in range(100):
            company = {
                "entity_id": f"company_{i}",
                "name": f'Company {i} {"Inc" if i % 2 == 0 else "Corp"}',
                "entity_type": "company",
                "address": f"{i} Business Street, City {i % 10}, State {i % 5:02d}",
                "phone": f"+1-{555 + i % 100:03d}-{i % 1000:03d}-{i % 10000:04d}",
                "email": f"info@company{i}.com",
                "domain": f"company{i}.com",
                "officers": [f"CEO {i}", f"CFO {i}"] if i % 3 == 0 else [],
            }
            large_entities.append(company)

        # Add some duplicates
        for i in range(20):
            duplicate = large_entities[i].copy()
            duplicate["entity_id"] = f"dup_{i}"
            duplicate["name"] = duplicate["name"].replace("Inc", "Incorporated")
            large_entities.append(duplicate)

        # Test with orchestrator
        orchestrator = AnalysisOrchestrator(integration_config)

        request = AnalysisRequest(
            request_id="performance_test_001",
            entities=large_entities,
            analysis_types=["entity_resolution", "relationship_mapping"],
            confidence_threshold=0.7,
        )

        import time

        start_time = time.time()
        result = asyncio.run(orchestrator.run_comprehensive_analysis(request))
        end_time = time.time()

        # Performance assertions
        duration = end_time - start_time
        assert duration < 120  # Should complete within 2 minutes

        # Quality assertions
        assert len(result.entity_resolutions) > 0
        assert len(result.entity_resolutions) < len(
            large_entities
        )  # Should detect duplicates

        # Should detect some relationships
        assert len(result.relationships) > 0

    def test_error_handling_integration(self, integration_config):
        """Test error handling across components"""
        orchestrator = AnalysisOrchestrator(integration_config)

        # Test with problematic data
        problematic_entities = [
            {"entity_id": "e1"},  # Missing name
            {"name": "Test Company"},  # Missing entity_id
            {"entity_id": "e3", "name": ""},  # Empty name
            {"entity_id": "e4", "name": "Valid Company"},  # Valid entity
        ]

        request = AnalysisRequest(
            request_id="error_test_001",
            entities=problematic_entities,
            analysis_types=["entity_resolution", "relationship_mapping"],
            confidence_threshold=0.7,
        )

        # Should handle errors gracefully
        result = asyncio.run(orchestrator.run_comprehensive_analysis(request))

        # Should complete despite errors
        assert result.request_id == "error_test_001"

        # Should report errors but continue processing
        if result.errors:
            assert len(result.errors) > 0

        # Should still process valid entities
        assert result.metrics["entities_processed"] >= 1

    def test_caching_integration(self, comprehensive_test_data, integration_config):
        """Test caching behavior across components"""
        # Set short cache TTL for testing
        integration_config["enrichment"]["cache_ttl_hours"] = 0.1  # 6 minutes

        enrichment_engine = DataEnrichmentEngine(integration_config["enrichment"])

        # First enrichment request
        entities_subset = comprehensive_test_data["entities"][:2]
        enrichments1 = asyncio.run(
            enrichment_engine.enrich_entities(entities_subset, ["sanctions"])
        )

        # Get initial metrics
        metrics1 = enrichment_engine.get_enrichment_metrics()
        cache_hits1 = metrics1.get("cache_hits", 0)

        # Second enrichment request (should use cache)
        enrichments2 = asyncio.run(
            enrichment_engine.enrich_entities(entities_subset, ["sanctions"])
        )

        # Get updated metrics
        metrics2 = enrichment_engine.get_enrichment_metrics()
        cache_hits2 = metrics2.get("cache_hits", 0)

        # Should have cache hits on second request
        assert cache_hits2 > cache_hits1

    def test_concurrent_analysis_requests(
        self, comprehensive_test_data, integration_config
    ):
        """Test handling of concurrent analysis requests"""
        orchestrator = AnalysisOrchestrator(integration_config)

        # Create multiple requests
        requests = []
        for i in range(3):
            request = AnalysisRequest(
                request_id=f"concurrent_test_{i}",
                entities=comprehensive_test_data["entities"][
                    :3
                ],  # Smaller subset for speed
                analysis_types=["entity_resolution"],
                confidence_threshold=0.7,
            )
            requests.append(request)

        # Run concurrent requests
        async def run_concurrent():
            tasks = [orchestrator.run_comprehensive_analysis(req) for req in requests]
            return await asyncio.gather(*tasks, return_exceptions=True)

        results = asyncio.run(run_concurrent())

        # All requests should complete
        assert len(results) == 3

        # Should handle concurrent requests without errors
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent request failed: {result}")
            else:
                assert hasattr(result, "request_id")

    def test_export_functionality(self, comprehensive_test_data, integration_config):
        """Test result export functionality"""
        orchestrator = AnalysisOrchestrator(integration_config)

        request = AnalysisRequest(
            request_id="export_test_001",
            entities=comprehensive_test_data["entities"][:3],
            analysis_types=["entity_resolution", "relationship_mapping"],
            confidence_threshold=0.6,
        )

        # Run analysis
        result = asyncio.run(orchestrator.run_comprehensive_analysis(request))

        # Test JSON export
        json_export = asyncio.run(
            orchestrator.export_analysis_results("export_test_001", "json")
        )
        assert json_export is not None

        # Should be valid JSON
        exported_data = json.loads(json_export)
        assert "request_id" in exported_data
        assert exported_data["request_id"] == "export_test_001"

        # Test summary export
        summary_export = asyncio.run(
            orchestrator.export_analysis_results("export_test_001", "summary")
        )
        assert summary_export is not None
        assert "BUSINESS INTELLIGENCE ANALYSIS REPORT" in summary_export
        assert "export_test_001" in summary_export

    def test_cli_integration(self, comprehensive_test_data):
        """Test CLI integration with temporary files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input file
            input_file = Path(temp_dir) / "entities.json"
            with open(input_file, "w") as f:
                json.dump(comprehensive_test_data["entities"], f)

            output_file = Path(temp_dir) / "results.json"

            # Import CLI module
            from business_intel_scraper.backend.cli.analysis import (
                load_entities_from_file,
            )

            # Test file loading
            loaded_entities = load_entities_from_file(str(input_file))
            assert len(loaded_entities) == len(comprehensive_test_data["entities"])
            assert (
                loaded_entities[0]["entity_id"]
                == comprehensive_test_data["entities"][0]["entity_id"]
            )

    def test_metrics_aggregation(self, comprehensive_test_data, integration_config):
        """Test metrics aggregation across all components"""
        orchestrator = AnalysisOrchestrator(integration_config)

        request = AnalysisRequest(
            request_id="metrics_test_001",
            entities=comprehensive_test_data["entities"],
            analysis_types=[
                "entity_resolution",
                "relationship_mapping",
                "enrichment",
                "event_detection",
            ],
            confidence_threshold=0.6,
        )

        # Run analysis
        result = asyncio.run(orchestrator.run_comprehensive_analysis(request))

        # Get comprehensive metrics
        orchestrator_metrics = orchestrator.get_orchestrator_metrics()
        entity_resolver_metrics = orchestrator.entity_resolver.get_resolution_metrics()
        enrichment_metrics = orchestrator.enrichment_engine.get_enrichment_metrics()
        event_detector_metrics = orchestrator.event_detector.get_detection_metrics()

        # Verify metrics are collected
        assert orchestrator_metrics["total_requests"] > 0
        assert orchestrator_metrics["successful_analyses"] > 0

        if entity_resolver_metrics["total_entities_processed"] > 0:
            assert entity_resolver_metrics["total_entities_processed"] == len(
                comprehensive_test_data["entities"]
            )

        # Verify metrics consistency
        assert result.metrics["entities_processed"] == len(
            comprehensive_test_data["entities"]
        )

    def test_configuration_flexibility(self, comprehensive_test_data):
        """Test system behavior with different configurations"""
        # High precision configuration
        high_precision_config = {
            "entity_resolution": {"similarity_threshold": 0.9, "clustering_eps": 0.1},
            "relationship_mapping": {"confidence_threshold": 0.8},
            "enrichment": {"cache_ttl_hours": 24},
            "event_detection": {"min_confidence": 0.8},
        }

        # Low precision configuration
        low_precision_config = {
            "entity_resolution": {"similarity_threshold": 0.5, "clustering_eps": 0.5},
            "relationship_mapping": {"confidence_threshold": 0.4},
            "enrichment": {"cache_ttl_hours": 1},
            "event_detection": {"min_confidence": 0.5},
        }

        # Test high precision
        high_precision_orchestrator = AnalysisOrchestrator(high_precision_config)
        high_request = AnalysisRequest(
            request_id="high_precision_test",
            entities=comprehensive_test_data["entities"],
            analysis_types=["entity_resolution", "relationship_mapping"],
            confidence_threshold=0.8,
        )

        high_result = asyncio.run(
            high_precision_orchestrator.run_comprehensive_analysis(high_request)
        )

        # Test low precision
        low_precision_orchestrator = AnalysisOrchestrator(low_precision_config)
        low_request = AnalysisRequest(
            request_id="low_precision_test",
            entities=comprehensive_test_data["entities"],
            analysis_types=["entity_resolution", "relationship_mapping"],
            confidence_threshold=0.4,
        )

        low_result = asyncio.run(
            low_precision_orchestrator.run_comprehensive_analysis(low_request)
        )

        # Low precision should typically find more relationships
        assert len(low_result.relationships) >= len(high_result.relationships)


if __name__ == "__main__":
    pytest.main([__file__])
