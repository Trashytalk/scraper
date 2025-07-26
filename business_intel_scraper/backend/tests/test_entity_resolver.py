"""
Tests for Entity Resolution functionality
"""

import pytest
import asyncio
from typing import Dict, List, Any

from business_intel_scraper.backend.analysis.entity_resolver import (
    AdvancedEntityResolver,
)


@pytest.fixture
def sample_entities() -> List[Dict[str, Any]]:
    """Sample entities for testing"""
    return [
        {
            "entity_id": "e1",
            "name": "Apple Inc.",
            "address": "1 Apple Park Way, Cupertino, CA 95014",
            "phone": "+1-408-996-1010",
            "email": "contact@apple.com",
            "website": "https://www.apple.com",
        },
        {
            "entity_id": "e2",
            "name": "Apple Incorporated",
            "address": "1 Apple Park Way, Cupertino, California 95014",
            "phone": "408-996-1010",
            "email": "info@apple.com",
            "website": "apple.com",
        },
        {
            "entity_id": "e3",
            "name": "Microsoft Corporation",
            "address": "One Microsoft Way, Redmond, WA 98052",
            "phone": "+1-425-882-8080",
            "email": "info@microsoft.com",
            "website": "https://www.microsoft.com",
        },
        {
            "entity_id": "e4",
            "name": "Google LLC",
            "address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
            "phone": "+1-650-253-0000",
            "email": "press@google.com",
            "website": "https://www.google.com",
        },
        {
            "entity_id": "e5",
            "name": "Apple Computer Inc",  # Another Apple variant
            "address": "1 Apple Park Way, Cupertino CA",
            "phone": "408.996.1010",
            "email": "support@apple.com",
            "website": "www.apple.com",
        },
    ]


@pytest.fixture
def entity_resolver() -> AdvancedEntityResolver:
    """Entity resolver instance for testing"""
    config = {
        "similarity_threshold": 0.7,
        "clustering_eps": 0.3,
        "min_samples": 2,
        "max_entities": 10000,
    }
    return AdvancedEntityResolver(config)


class TestAdvancedEntityResolver:
    """Test cases for AdvancedEntityResolver"""

    def test_initialization(self, entity_resolver):
        """Test entity resolver initialization"""
        assert entity_resolver.config["similarity_threshold"] == 0.7
        assert entity_resolver.config["clustering_eps"] == 0.3
        assert len(entity_resolver.resolution_metrics) > 0

    def test_normalize_business_name(self, entity_resolver):
        """Test business name normalization"""
        test_cases = [
            ("Apple Inc.", "apple inc"),
            ("Microsoft Corporation", "microsoft corp"),
            ("Google LLC", "google llc"),
            ("IBM Corp.", "ibm corp"),
            ("Amazon.com, Inc.", "amazon com inc"),
        ]

        for input_name, expected in test_cases:
            result = entity_resolver._normalize_business_name(input_name)
            assert result == expected

    def test_normalize_address(self, entity_resolver):
        """Test address normalization"""
        test_cases = [
            ("123 Main Street, Suite 100", "123 main st suite 100"),
            (
                "1 Apple Park Way, Cupertino, CA 95014",
                "1 apple park way cupertino ca 95014",
            ),
            ("One Microsoft Way", "1 microsoft way"),
        ]

        for input_addr, expected in test_cases:
            result = entity_resolver._normalize_address(input_addr)
            assert result == expected

    def test_normalize_phone(self, entity_resolver):
        """Test phone number normalization"""
        test_cases = [
            ("+1-408-996-1010", "14089961010"),
            ("408-996-1010", "4089961010"),
            ("408.996.1010", "4089961010"),
            ("(408) 996-1010", "4089961010"),
        ]

        for input_phone, expected in test_cases:
            result = entity_resolver._normalize_phone(input_phone)
            assert result == expected

    def test_calculate_name_similarity(self, entity_resolver):
        """Test name similarity calculation"""
        # High similarity - same company
        similarity = entity_resolver._calculate_name_similarity(
            "Apple Inc.", "Apple Incorporated"
        )
        assert similarity > 0.8

        # Medium similarity - similar but different companies
        similarity = entity_resolver._calculate_name_similarity(
            "Apple Inc.", "Apple Computer"
        )
        assert 0.6 < similarity < 0.9

        # Low similarity - different companies
        similarity = entity_resolver._calculate_name_similarity(
            "Apple Inc.", "Microsoft Corporation"
        )
        assert similarity < 0.5

    def test_calculate_multi_field_similarity(self, entity_resolver, sample_entities):
        """Test multi-field similarity calculation"""
        entity1 = sample_entities[0]  # Apple Inc.
        entity2 = sample_entities[1]  # Apple Incorporated

        similarity = entity_resolver._calculate_multi_field_similarity(entity1, entity2)
        assert similarity.overall_score > 0.8
        assert similarity.name_score > 0.8
        assert similarity.address_score > 0.8

    def test_apply_blocking_strategy(self, entity_resolver, sample_entities):
        """Test blocking strategy for performance optimization"""
        blocks = entity_resolver._apply_blocking_strategy(sample_entities)

        # Should create blocks based on name prefix and location
        assert len(blocks) > 0

        # Apple entities should be in same block
        apple_entities = [e for e in sample_entities if "apple" in e["name"].lower()]
        if len(apple_entities) > 1:
            # Find blocks containing Apple entities
            apple_blocks = []
            for block_entities in blocks.values():
                if any(
                    e["entity_id"] in [ae["entity_id"] for ae in apple_entities]
                    for e in block_entities
                ):
                    apple_blocks.append(block_entities)

            # At least one block should contain multiple Apple entities
            assert any(
                len([e for e in block if "apple" in e["name"].lower()]) > 1
                for block in apple_blocks
            )

    def test_resolve_entities_basic(self, entity_resolver, sample_entities):
        """Test basic entity resolution"""
        clusters = entity_resolver.resolve_entities(sample_entities)

        # Should have fewer clusters than entities (due to Apple duplicates)
        assert len(clusters) < len(sample_entities)

        # Should identify Apple duplicates
        apple_cluster = None
        for cluster_id, cluster_data in clusters.items():
            if "apple" in cluster_data["canonical_entity"]["name"].lower():
                apple_cluster = cluster_data
                break

        assert apple_cluster is not None
        assert len(apple_cluster["entities"]) >= 2  # At least 2 Apple entities

    def test_resolve_entities_with_clustering(self, entity_resolver, sample_entities):
        """Test entity resolution with ML clustering"""
        # Enable ML clustering
        entity_resolver.config["use_ml_clustering"] = True

        clusters = entity_resolver.resolve_entities(sample_entities)

        # Verify clustering results
        assert len(clusters) > 0

        # Check that similar entities are clustered together
        for cluster_id, cluster_data in clusters.items():
            entities = cluster_data["entities"]
            if len(entities) > 1:
                # Verify entities in cluster are actually similar
                for i in range(len(entities)):
                    for j in range(i + 1, len(entities)):
                        similarity = entity_resolver._calculate_multi_field_similarity(
                            entities[i], entities[j]
                        )
                        assert (
                            similarity.overall_score
                            >= entity_resolver.config["similarity_threshold"]
                        )

    def test_calculate_similarity_matrix(self, entity_resolver, sample_entities):
        """Test similarity matrix calculation"""
        # Use smaller subset for testing
        test_entities = sample_entities[:3]

        matrix = entity_resolver.calculate_similarity_matrix(test_entities)

        # Verify matrix dimensions
        assert len(matrix) == len(test_entities)
        assert len(matrix[0]) == len(test_entities)

        # Verify diagonal is 1.0 (entity similar to itself)
        for i in range(len(test_entities)):
            assert matrix[i][i] == 1.0

        # Verify matrix is symmetric
        for i in range(len(test_entities)):
            for j in range(len(test_entities)):
                assert matrix[i][j] == matrix[j][i]

    def test_get_resolution_metrics(self, entity_resolver, sample_entities):
        """Test resolution metrics collection"""
        # Run resolution to generate metrics
        entity_resolver.resolve_entities(sample_entities)

        metrics = entity_resolver.get_resolution_metrics()

        assert "total_entities_processed" in metrics
        assert "total_clusters_created" in metrics
        assert "average_cluster_size" in metrics
        assert "duplicate_detection_rate" in metrics
        assert metrics["total_entities_processed"] == len(sample_entities)

    def test_phonetic_matching(self, entity_resolver):
        """Test phonetic matching functionality"""
        # Test similar sounding names
        similarity1 = entity_resolver._calculate_phonetic_similarity("Smith", "Smyth")
        assert similarity1 > 0.8

        similarity2 = entity_resolver._calculate_phonetic_similarity(
            "Johnson", "Jonson"
        )
        assert similarity2 > 0.8

        # Test different sounding names
        similarity3 = entity_resolver._calculate_phonetic_similarity("Smith", "Brown")
        assert similarity3 < 0.5

    def test_edge_cases(self, entity_resolver):
        """Test edge cases and error handling"""
        # Empty entity list
        clusters = entity_resolver.resolve_entities([])
        assert len(clusters) == 0

        # Single entity
        single_entity = [{"entity_id": "e1", "name": "Test Company"}]
        clusters = entity_resolver.resolve_entities(single_entity)
        assert len(clusters) == 1

        # Entities with missing fields
        incomplete_entities = [
            {"entity_id": "e1", "name": "Company A"},
            {"entity_id": "e2", "name": "Company B", "address": "123 Main St"},
            {"entity_id": "e3"},  # Missing name
        ]
        clusters = entity_resolver.resolve_entities(incomplete_entities)
        assert len(clusters) > 0  # Should handle gracefully

    def test_confidence_scoring(self, entity_resolver, sample_entities):
        """Test confidence scoring for entity clusters"""
        clusters = entity_resolver.resolve_entities(sample_entities)

        for cluster_id, cluster_data in clusters.items():
            # Confidence score should be between 0 and 1
            assert 0.0 <= cluster_data["confidence_score"] <= 1.0

            # Clusters with multiple entities should have similarity scores
            if len(cluster_data["entities"]) > 1:
                assert "similarity_scores" in cluster_data
                assert len(cluster_data["similarity_scores"]) > 0

    def test_performance_with_large_dataset(self, entity_resolver):
        """Test performance with larger dataset"""
        # Generate larger test dataset
        large_entities = []
        for i in range(100):
            large_entities.append(
                {
                    "entity_id": f"e{i}",
                    "name": f"Company {i}",
                    "address": f"{i} Business Ave, City, State {i%50:05d}",
                    "phone": f"+1-{i%1000:03d}-{i%1000:03d}-{i%10000:04d}",
                    "email": f"contact{i}@company{i}.com",
                }
            )

        # Add some duplicates
        for i in range(10):
            duplicate = large_entities[i].copy()
            duplicate["entity_id"] = f"dup_{i}"
            duplicate["name"] = duplicate["name"].replace(
                "Company", "Corp"
            )  # Slight variation
            large_entities.append(duplicate)

        import time

        start_time = time.time()
        clusters = entity_resolver.resolve_entities(large_entities)
        end_time = time.time()

        # Should complete in reasonable time (less than 30 seconds)
        assert (end_time - start_time) < 30

        # Should detect some duplicates
        assert len(clusters) < len(large_entities)

        # Should have reasonable duplicate detection
        duplicate_ratio = 1.0 - (len(clusters) / len(large_entities))
        assert duplicate_ratio > 0  # Should detect at least some duplicates

    @pytest.mark.asyncio
    async def test_async_resolution(self, entity_resolver, sample_entities):
        """Test asynchronous entity resolution"""
        # Run resolution in thread pool
        clusters = await asyncio.to_thread(
            entity_resolver.resolve_entities, sample_entities
        )

        assert len(clusters) > 0
        assert len(clusters) <= len(sample_entities)

    def test_custom_similarity_weights(self, sample_entities):
        """Test entity resolution with custom similarity weights"""
        config = {
            "similarity_threshold": 0.7,
            "field_weights": {"name": 0.5, "address": 0.3, "phone": 0.1, "email": 0.1},
        }

        resolver = AdvancedEntityResolver(config)
        clusters = resolver.resolve_entities(sample_entities)

        assert len(clusters) > 0

        # Verify custom weights are used in similarity calculation
        assert resolver.config["field_weights"]["name"] == 0.5
        assert resolver.config["field_weights"]["address"] == 0.3


if __name__ == "__main__":
    pytest.main([__file__])
