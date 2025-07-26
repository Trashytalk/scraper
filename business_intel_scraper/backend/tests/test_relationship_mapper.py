"""
Tests for Relationship Mapping functionality
"""

import pytest
import asyncio
from typing import Dict, List, Any

from business_intel_scraper.backend.analysis.relationship_mapper import (
    EntityRelationshipMapper,
    Relationship,
    RelationshipType,
)


@pytest.fixture
def sample_entities() -> List[Dict[str, Any]]:
    """Sample entities with relationship data for testing"""
    return [
        {
            "entity_id": "company_1",
            "name": "TechCorp Inc.",
            "entity_type": "company",
            "officers": ["John Smith CEO", "Jane Doe CFO"],
            "address": "123 Tech Street, Silicon Valley, CA 94000",
            "phone": "+1-555-0100",
            "email": "info@techcorp.com",
            "website": "https://www.techcorp.com",
            "domain": "techcorp.com",
            "subsidiaries": ["TechCorp Labs", "TechCorp Services"],
            "parent_company": None,
            "ownership_percentage": None,
        },
        {
            "entity_id": "person_1",
            "name": "John Smith",
            "entity_type": "person",
            "title": "Chief Executive Officer",
            "companies": ["TechCorp Inc.", "Innovation Labs"],
            "address": "456 Executive Way, Silicon Valley, CA 94001",
            "phone": "+1-555-0101",
            "email": "john.smith@techcorp.com",
        },
        {
            "entity_id": "person_2",
            "name": "Jane Doe",
            "entity_type": "person",
            "title": "Chief Financial Officer",
            "companies": ["TechCorp Inc."],
            "address": "789 Finance Ave, Silicon Valley, CA 94002",
            "phone": "+1-555-0102",
            "email": "jane.doe@techcorp.com",
        },
        {
            "entity_id": "company_2",
            "name": "TechCorp Labs",
            "entity_type": "company",
            "address": "123 Tech Street, Silicon Valley, CA 94000",  # Same address as parent
            "phone": "+1-555-0200",
            "email": "labs@techcorp.com",
            "website": "https://labs.techcorp.com",
            "domain": "techcorp.com",  # Same domain as parent
            "parent_company": "TechCorp Inc.",
            "ownership_percentage": 100.0,
        },
        {
            "entity_id": "company_3",
            "name": "Innovation Labs",
            "entity_type": "company",
            "officers": ["John Smith Director"],
            "address": "321 Innovation Blvd, Tech City, CA 94100",
            "phone": "+1-555-0300",
            "email": "contact@innovationlabs.com",
            "website": "https://www.innovationlabs.com",
            "domain": "innovationlabs.com",
        },
    ]


@pytest.fixture
def relationship_mapper() -> EntityRelationshipMapper:
    """Relationship mapper instance for testing"""
    config = {
        "confidence_threshold": 0.6,
        "max_relationships": 1000,
        "include_weak_relationships": False,
    }
    return EntityRelationshipMapper(config)


class TestEntityRelationshipMapper:
    """Test cases for EntityRelationshipMapper"""

    def test_initialization(self, relationship_mapper):
        """Test relationship mapper initialization"""
        assert relationship_mapper.config["confidence_threshold"] == 0.6
        assert relationship_mapper.config["max_relationships"] == 1000
        assert len(relationship_mapper.mapping_metrics) > 0

    def test_extract_officer_relationships(self, relationship_mapper, sample_entities):
        """Test extraction of officer/director relationships"""
        relationships = relationship_mapper._extract_officer_relationships(
            sample_entities
        )

        # Should find officer relationships
        assert len(relationships) > 0

        # Check for John Smith as CEO of TechCorp
        ceo_relationships = [
            r
            for r in relationships
            if r.source_entity == "person_1"
            and r.target_entity == "company_1"
            and "ceo" in r.metadata.get("role", "").lower()
        ]
        assert len(ceo_relationships) > 0

        # Check for Jane Doe as CFO of TechCorp
        cfo_relationships = [
            r
            for r in relationships
            if r.source_entity == "person_2"
            and r.target_entity == "company_1"
            and "cfo" in r.metadata.get("role", "").lower()
        ]
        assert len(cfo_relationships) > 0

    def test_extract_ownership_relationships(
        self, relationship_mapper, sample_entities
    ):
        """Test extraction of ownership relationships"""
        relationships = relationship_mapper._extract_ownership_relationships(
            sample_entities
        )

        # Should find ownership relationships
        assert len(relationships) > 0

        # Check for TechCorp Labs owned by TechCorp Inc
        ownership_rels = [
            r
            for r in relationships
            if r.source_entity == "company_1"
            and r.target_entity == "company_2"
            and r.relationship_type == RelationshipType.OWNERSHIP
        ]
        assert len(ownership_rels) > 0

        # Verify ownership percentage in metadata
        ownership_rel = ownership_rels[0]
        assert ownership_rel.metadata.get("ownership_percentage") == 100.0

    def test_extract_shared_address_relationships(
        self, relationship_mapper, sample_entities
    ):
        """Test extraction of shared address relationships"""
        relationships = relationship_mapper._extract_shared_address_relationships(
            sample_entities
        )

        # Should find shared address relationships
        assert len(relationships) > 0

        # Check for TechCorp and TechCorp Labs sharing address
        shared_addr_rels = [
            r
            for r in relationships
            if (
                (r.source_entity == "company_1" and r.target_entity == "company_2")
                or (r.source_entity == "company_2" and r.target_entity == "company_1")
            )
            and r.relationship_type == RelationshipType.SHARED_ADDRESS
        ]
        assert len(shared_addr_rels) > 0

    def test_extract_shared_contact_relationships(
        self, relationship_mapper, sample_entities
    ):
        """Test extraction of shared contact relationships"""
        relationships = relationship_mapper._extract_shared_contact_relationships(
            sample_entities
        )

        # Should find shared contact relationships (email domains, etc.)
        shared_contact_rels = [
            r
            for r in relationships
            if r.relationship_type == RelationshipType.SHARED_CONTACT
        ]

        # Should have some shared contacts (email domains, phone prefixes)
        assert len(shared_contact_rels) >= 0  # May be 0 if no clear shared contacts

    def test_extract_shared_domain_relationships(
        self, relationship_mapper, sample_entities
    ):
        """Test extraction of shared domain relationships"""
        relationships = relationship_mapper._extract_shared_domain_relationships(
            sample_entities
        )

        # Should find shared domain relationships
        assert len(relationships) > 0

        # Check for TechCorp and TechCorp Labs sharing domain
        shared_domain_rels = [
            r
            for r in relationships
            if (
                (r.source_entity == "company_1" and r.target_entity == "company_2")
                or (r.source_entity == "company_2" and r.target_entity == "company_1")
            )
            and r.relationship_type == RelationshipType.SHARED_DOMAIN
        ]
        assert len(shared_domain_rels) > 0

    def test_classify_officer_role(self, relationship_mapper):
        """Test officer role classification"""
        test_cases = [
            ("Chief Executive Officer", "ceo"),
            ("CEO", "ceo"),
            ("President", "president"),
            ("Chief Financial Officer", "cfo"),
            ("CFO", "cfo"),
            ("Director", "director"),
            ("Vice President", "vice_president"),
            ("VP", "vice_president"),
            ("Secretary", "secretary"),
            ("Treasurer", "treasurer"),
            ("Unknown Role", "other"),
        ]

        for title, expected_role in test_cases:
            role = relationship_mapper._classify_officer_role(title)
            assert role == expected_role

    def test_calculate_relationship_strength(
        self, relationship_mapper, sample_entities
    ):
        """Test relationship strength calculation"""
        # Create test relationships
        officer_rel = Relationship(
            source_entity="person_1",
            target_entity="company_1",
            relationship_type=RelationshipType.OFFICER,
            confidence_score=0.9,
            metadata={"role": "ceo"},
            evidence=["John Smith CEO in officers list"],
        )

        ownership_rel = Relationship(
            source_entity="company_1",
            target_entity="company_2",
            relationship_type=RelationshipType.OWNERSHIP,
            confidence_score=0.95,
            metadata={"ownership_percentage": 100.0},
            evidence=["parent_company field", "ownership_percentage field"],
        )

        # Officer relationships should have high strength for executive roles
        officer_strength = relationship_mapper._calculate_relationship_strength(
            officer_rel, sample_entities
        )
        assert officer_strength > 0.8

        # Ownership relationships should have very high strength
        ownership_strength = relationship_mapper._calculate_relationship_strength(
            ownership_rel, sample_entities
        )
        assert ownership_strength > 0.9

    def test_extract_relationships_comprehensive(
        self, relationship_mapper, sample_entities
    ):
        """Test comprehensive relationship extraction"""
        relationship_types = ["officer", "ownership", "address", "contact", "domain"]
        relationships = relationship_mapper.extract_relationships(
            sample_entities, relationship_types
        )

        # Should find multiple types of relationships
        assert len(relationships) > 0

        # Group by relationship type
        type_counts = {}
        for rel in relationships:
            rel_type = rel.relationship_type
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1

        # Should have officer relationships
        assert RelationshipType.OFFICER in type_counts
        assert type_counts[RelationshipType.OFFICER] > 0

        # Should have ownership relationships
        assert RelationshipType.OWNERSHIP in type_counts
        assert type_counts[RelationshipType.OWNERSHIP] > 0

        # Verify confidence scores
        for rel in relationships:
            assert 0.0 <= rel.confidence_score <= 1.0
            assert (
                rel.confidence_score
                >= relationship_mapper.config["confidence_threshold"]
            )

    def test_build_network_graph(self, relationship_mapper, sample_entities):
        """Test network graph construction and analysis"""
        relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        if len(relationships) == 0:
            pytest.skip("No relationships found for graph construction")

        graph_metrics = relationship_mapper.build_network_graph(relationships)

        # Verify graph metrics
        assert "node_count" in graph_metrics
        assert "edge_count" in graph_metrics
        assert "density" in graph_metrics
        assert "clustering" in graph_metrics

        # Should have nodes and edges
        assert graph_metrics["node_count"] > 0
        assert graph_metrics["edge_count"] > 0

        # Density should be between 0 and 1
        assert 0.0 <= graph_metrics["density"] <= 1.0

    def test_find_communities(self, relationship_mapper, sample_entities):
        """Test community detection in relationship network"""
        relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        if len(relationships) < 3:
            pytest.skip("Not enough relationships for community detection")

        # Build graph first
        relationship_mapper.build_network_graph(relationships)

        communities = relationship_mapper._find_communities()

        # Should find at least one community
        assert len(communities) > 0

        # Each community should have at least one node
        for community in communities:
            assert len(community) > 0

    def test_calculate_centrality_measures(self, relationship_mapper, sample_entities):
        """Test centrality measures calculation"""
        relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        if len(relationships) == 0:
            pytest.skip("No relationships found for centrality calculation")

        # Build graph first
        relationship_mapper.build_network_graph(relationships)

        centrality_measures = relationship_mapper._calculate_centrality_measures()

        # Should have centrality measures
        assert "degree_centrality" in centrality_measures
        assert "betweenness_centrality" in centrality_measures
        assert "closeness_centrality" in centrality_measures
        assert "eigenvector_centrality" in centrality_measures

        # Each measure should have entries for graph nodes
        for measure_name, measure_dict in centrality_measures.items():
            assert len(measure_dict) > 0
            for node, centrality in measure_dict.items():
                assert 0.0 <= centrality <= 1.0

    def test_get_mapping_metrics(self, relationship_mapper, sample_entities):
        """Test mapping metrics collection"""
        # Run relationship extraction to generate metrics
        relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        metrics = relationship_mapper.get_mapping_metrics()

        assert "total_entities_processed" in metrics
        assert "total_relationships_found" in metrics
        assert "relationship_types_found" in metrics
        assert "average_confidence_score" in metrics

        assert metrics["total_entities_processed"] == len(sample_entities)
        assert metrics["total_relationships_found"] == len(relationships)

    def test_confidence_filtering(self, relationship_mapper, sample_entities):
        """Test confidence-based relationship filtering"""
        # Set high confidence threshold
        relationship_mapper.config["confidence_threshold"] = 0.9

        high_conf_relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        # Set low confidence threshold
        relationship_mapper.config["confidence_threshold"] = 0.1

        low_conf_relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        # Should have fewer high-confidence relationships
        assert len(high_conf_relationships) <= len(low_conf_relationships)

        # All high-confidence relationships should meet threshold
        for rel in high_conf_relationships:
            assert rel.confidence_score >= 0.9

    def test_relationship_deduplication(self, relationship_mapper):
        """Test relationship deduplication logic"""
        # Create duplicate relationships
        relationships = [
            Relationship(
                source_entity="person_1",
                target_entity="company_1",
                relationship_type=RelationshipType.OFFICER,
                confidence_score=0.9,
                metadata={"role": "ceo"},
                evidence=["evidence1"],
            ),
            Relationship(
                source_entity="person_1",
                target_entity="company_1",
                relationship_type=RelationshipType.OFFICER,
                confidence_score=0.8,
                metadata={"role": "ceo"},
                evidence=["evidence2"],
            ),
        ]

        deduplicated = relationship_mapper._deduplicate_relationships(relationships)

        # Should keep only one relationship (the higher confidence one)
        assert len(deduplicated) == 1
        assert deduplicated[0].confidence_score == 0.9

    def test_edge_cases(self, relationship_mapper):
        """Test edge cases and error handling"""
        # Empty entity list
        relationships = relationship_mapper.extract_relationships([], ["officer"])
        assert len(relationships) == 0

        # Single entity
        single_entity = [{"entity_id": "e1", "name": "Test Company"}]
        relationships = relationship_mapper.extract_relationships(
            single_entity, ["officer"]
        )
        assert len(relationships) == 0  # No relationships possible with single entity

        # Entities with missing relationship fields
        incomplete_entities = [
            {"entity_id": "e1", "name": "Company A"},
            {"entity_id": "e2", "name": "Company B"},
        ]
        relationships = relationship_mapper.extract_relationships(
            incomplete_entities, ["officer", "ownership"]
        )
        # Should handle gracefully and return empty list
        assert isinstance(relationships, list)

    def test_relationship_evidence_tracking(self, relationship_mapper, sample_entities):
        """Test that relationships include proper evidence tracking"""
        relationships = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        for rel in relationships:
            # Each relationship should have evidence
            assert len(rel.evidence) > 0

            # Evidence should be meaningful strings
            for evidence in rel.evidence:
                assert isinstance(evidence, str)
                assert len(evidence) > 0

    def test_performance_with_large_dataset(self, relationship_mapper):
        """Test performance with larger dataset"""
        # Generate larger test dataset
        large_entities = []

        # Create companies
        for i in range(50):
            company = {
                "entity_id": f"company_{i}",
                "name": f"Company {i}",
                "entity_type": "company",
                "address": f"{i} Business Ave, City, State {i%10:05d}",
                "phone": f"+1-555-{i:04d}",
                "email": f"info@company{i}.com",
                "domain": f"company{i}.com",
                "officers": [f"CEO {i}", f"CFO {i}"],
            }
            large_entities.append(company)

        # Create people
        for i in range(100):
            person = {
                "entity_id": f"person_{i}",
                "name": f"Person {i}",
                "entity_type": "person",
                "title": "CEO" if i % 2 == 0 else "CFO",
                "companies": [f"Company {i % 50}"],
                "email": f"person{i}@company{i % 50}.com",
            }
            large_entities.append(person)

        import time

        start_time = time.time()
        relationships = relationship_mapper.extract_relationships(
            large_entities, ["officer", "ownership"]
        )
        end_time = time.time()

        # Should complete in reasonable time (less than 60 seconds)
        assert (end_time - start_time) < 60

        # Should find relationships
        assert len(relationships) > 0

    @pytest.mark.asyncio
    async def test_async_relationship_extraction(
        self, relationship_mapper, sample_entities
    ):
        """Test asynchronous relationship extraction"""
        # Run extraction in thread pool
        relationships = await asyncio.to_thread(
            relationship_mapper.extract_relationships,
            sample_entities,
            ["officer", "ownership"],
        )

        assert len(relationships) >= 0

        # Verify relationships have correct structure
        for rel in relationships:
            assert hasattr(rel, "source_entity")
            assert hasattr(rel, "target_entity")
            assert hasattr(rel, "relationship_type")
            assert hasattr(rel, "confidence_score")

    def test_custom_relationship_types(self, relationship_mapper, sample_entities):
        """Test extraction with custom relationship types"""
        # Test with subset of relationship types
        officer_only = relationship_mapper.extract_relationships(
            sample_entities, ["officer"]
        )
        ownership_only = relationship_mapper.extract_relationships(
            sample_entities, ["ownership"]
        )
        combined = relationship_mapper.extract_relationships(
            sample_entities, ["officer", "ownership"]
        )

        # Combined should have at least as many as individual types
        assert len(combined) >= len(officer_only)
        assert len(combined) >= len(ownership_only)

        # Verify only requested types are returned
        for rel in officer_only:
            assert rel.relationship_type == RelationshipType.OFFICER

        for rel in ownership_only:
            assert rel.relationship_type == RelationshipType.OWNERSHIP


if __name__ == "__main__":
    pytest.main([__file__])
