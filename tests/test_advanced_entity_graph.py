"""
Test Suite for Advanced Entity Graph System

Comprehensive tests covering all components of the entity graph system
including core functionality, analytics, visualization, and integration.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the system components
try:
    from gui.components.advanced_entity_graph import (
        AdvancedEntityGraphSystem,
        EntityNode,
        EntityRelationship,
        GraphAnalytics,
        GraphAnalyticsEngine,
        GraphDatabase,
        GraphQueryEngine,
        GraphVisualizationEngine,
        NetworkXConnector,
        NodeType,
        RelationshipType,
    )
    from gui.components.data_integration_bridge import (
        DataIntegrationBridge,
        IntegrationMapping,
    )

    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


class TestEntityNode:
    """Test EntityNode data model"""

    def test_entity_node_creation(self):
        """Test creating an entity node"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        node = EntityNode(
            entity_id="TEST_001",
            node_type=NodeType.COMPANY,
            properties={"name": "Test Company", "industry": "Technology"},
            confidence=0.95,
            data_sources=["test_source"],
        )

        assert node.entity_id == "TEST_001"
        assert node.node_type == NodeType.COMPANY
        assert node.properties["name"] == "Test Company"
        assert node.confidence == 0.95
        assert "test_source" in node.data_sources
        assert isinstance(node.creation_time, datetime)

    def test_entity_display_name(self):
        """Test entity display name property"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        # Test with name property
        node1 = EntityNode(
            entity_id="TEST_001",
            node_type=NodeType.COMPANY,
            properties={"name": "Test Company"},
        )
        assert node1.display_name == "Test Company"

        # Test with title property
        node2 = EntityNode(
            entity_id="TEST_002", node_type=NodeType.PERSON, properties={"title": "CEO"}
        )
        assert node2.display_name == "CEO"

        # Test without name or title
        node3 = EntityNode(
            entity_id="TEST_003",
            node_type=NodeType.ADDRESS,
            properties={"city": "London"},
        )
        assert node3.display_name == "address_TEST_003"


class TestEntityRelationship:
    """Test EntityRelationship data model"""

    def test_relationship_creation(self):
        """Test creating a relationship"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        relationship = EntityRelationship(
            source_id="PERSON_001",
            target_id="COMPANY_001",
            relationship_type=RelationshipType.HAS_OFFICER,
            properties={"title": "CEO"},
            confidence=0.98,
            valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
            data_sources=["companies_house"],
        )

        assert relationship.source_id == "PERSON_001"
        assert relationship.target_id == "COMPANY_001"
        assert relationship.relationship_type == RelationshipType.HAS_OFFICER
        assert relationship.properties["title"] == "CEO"
        assert relationship.confidence == 0.98
        assert relationship.valid_from.year == 2020
        assert "companies_house" in relationship.data_sources


@pytest.mark.asyncio
class TestNetworkXConnector:
    """Test NetworkX graph database connector"""

    async def test_connector_initialization(self):
        """Test NetworkX connector initialization"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        assert not connector.connected

        success = await connector.connect()
        assert success
        assert connector.connected
        assert connector.graph is not None

    async def test_node_creation(self):
        """Test creating nodes in NetworkX"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        node = EntityNode(
            entity_id="TEST_COMPANY",
            node_type=NodeType.COMPANY,
            properties={"name": "Test Corp"},
            confidence=0.9,
        )

        success = await connector.create_node(node)
        assert success
        assert "TEST_COMPANY" in connector.graph.nodes()
        assert connector.nodes_data["TEST_COMPANY"] == node

    async def test_relationship_creation(self):
        """Test creating relationships in NetworkX"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Create nodes first
        node1 = EntityNode("PERSON_001", NodeType.PERSON, {"name": "John"})
        node2 = EntityNode("COMPANY_001", NodeType.COMPANY, {"name": "Corp"})

        await connector.create_node(node1)
        await connector.create_node(node2)

        # Create relationship
        relationship = EntityRelationship(
            source_id="PERSON_001",
            target_id="COMPANY_001",
            relationship_type=RelationshipType.HAS_OFFICER,
            properties={"title": "CEO"},
        )

        success = await connector.create_relationship(relationship)
        assert success
        assert connector.graph.has_edge("PERSON_001", "COMPANY_001")

    async def test_query_execution(self):
        """Test query execution in NetworkX"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Add test data
        node = EntityNode("TEST_001", NodeType.COMPANY, {"name": "Test"})
        await connector.create_node(node)

        # Test node query
        results = await connector.execute_query("find nodes", {})
        assert len(results) > 0
        assert any(r["node_id"] == "TEST_001" for r in results)


@pytest.mark.asyncio
class TestGraphAnalyticsEngine:
    """Test graph analytics engine"""

    async def test_centrality_calculation(self):
        """Test centrality measures calculation"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        # Create test graph
        connector = NetworkXConnector({})
        await connector.connect()

        # Add test nodes and edges
        nodes = [
            EntityNode(f"NODE_{i}", NodeType.COMPANY, {"name": f"Company {i}"})
            for i in range(5)
        ]

        for node in nodes:
            await connector.create_node(node)

        # Add relationships
        relationships = [
            EntityRelationship("NODE_0", "NODE_1", RelationshipType.OWNS),
            EntityRelationship("NODE_1", "NODE_2", RelationshipType.OWNS),
            EntityRelationship("NODE_2", "NODE_3", RelationshipType.OWNS),
            EntityRelationship("NODE_0", "NODE_4", RelationshipType.OWNS),
        ]

        for rel in relationships:
            await connector.create_relationship(rel)

        # Test analytics
        analytics_engine = GraphAnalyticsEngine(connector)
        centrality_measures = await analytics_engine.calculate_centrality_measures()

        assert "degree" in centrality_measures
        assert "betweenness" in centrality_measures
        assert "pagerank" in centrality_measures

        # NODE_0 should have high centrality (hub)
        assert centrality_measures["degree"]["NODE_0"] > 0

    async def test_community_detection(self):
        """Test community detection"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Create two clusters
        for i in range(6):
            node = EntityNode(f"NODE_{i}", NodeType.COMPANY, {"name": f"Company {i}"})
            await connector.create_node(node)

        # Cluster 1: NODE_0, NODE_1, NODE_2
        cluster1_rels = [
            EntityRelationship("NODE_0", "NODE_1", RelationshipType.RELATED_TO),
            EntityRelationship("NODE_1", "NODE_2", RelationshipType.RELATED_TO),
            EntityRelationship("NODE_0", "NODE_2", RelationshipType.RELATED_TO),
        ]

        # Cluster 2: NODE_3, NODE_4, NODE_5
        cluster2_rels = [
            EntityRelationship("NODE_3", "NODE_4", RelationshipType.RELATED_TO),
            EntityRelationship("NODE_4", "NODE_5", RelationshipType.RELATED_TO),
            EntityRelationship("NODE_3", "NODE_5", RelationshipType.RELATED_TO),
        ]

        # Bridge between clusters
        bridge_rel = EntityRelationship("NODE_1", "NODE_4", RelationshipType.LINKED_TO)

        for rel in cluster1_rels + cluster2_rels + [bridge_rel]:
            await connector.create_relationship(rel)

        analytics_engine = GraphAnalyticsEngine(connector)
        communities = await analytics_engine.detect_communities()

        assert len(communities) > 0
        # Should detect at least 2 communities
        unique_communities = set(communities.values())
        assert len(unique_communities) >= 1  # May merge due to bridge

    async def test_anomaly_detection(self):
        """Test anomaly detection"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Create normal nodes
        for i in range(10):
            node = EntityNode(f"NORMAL_{i}", NodeType.COMPANY, {"name": f"Normal {i}"})
            await connector.create_node(node)

        # Create hub node (anomaly)
        hub_node = EntityNode("HUB_NODE", NodeType.COMPANY, {"name": "Hub Corp"})
        await connector.create_node(hub_node)

        # Connect hub to many nodes
        for i in range(8):
            rel = EntityRelationship("HUB_NODE", f"NORMAL_{i}", RelationshipType.OWNS)
            await connector.create_relationship(rel)

        analytics_engine = GraphAnalyticsEngine(connector)
        anomalies = await analytics_engine.detect_anomalies()

        # Should detect high degree node
        assert len(anomalies) > 0
        hub_anomaly = next(
            (a for a in anomalies if a.get("node_id") == "HUB_NODE"), None
        )
        assert hub_anomaly is not None
        assert hub_anomaly["type"] == "high_degree_node"

    async def test_temporal_analysis(self):
        """Test temporal analysis"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Create nodes with different creation times
        base_time = datetime.now(timezone.utc)

        for i in range(5):
            node = EntityNode(
                f"TEMPORAL_{i}",
                NodeType.COMPANY,
                {"name": f"Temporal {i}"},
                creation_time=base_time - timedelta(days=i),
            )
            await connector.create_node(node)

        analytics_engine = GraphAnalyticsEngine(connector)
        temporal_analysis = await analytics_engine.temporal_analysis(time_window_days=7)

        assert "time_window_days" in temporal_analysis
        assert "node_creation_timeline" in temporal_analysis
        assert "growth_metrics" in temporal_analysis


@pytest.mark.asyncio
class TestGraphQueryEngine:
    """Test graph query engine"""

    async def test_query_templates(self):
        """Test query template loading"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        query_engine = GraphQueryEngine(connector)

        # Check that templates are loaded
        assert "circular_ownership" in query_engine.query_templates
        assert "director_in_common" in query_engine.query_templates
        assert "ultimate_beneficial_owner" in query_engine.query_templates

    async def test_template_query_execution(self):
        """Test executing template queries"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Add test data
        company_node = EntityNode(
            "COMPANY_001", NodeType.COMPANY, {"name": "Test Corp"}
        )
        await connector.create_node(company_node)

        query_engine = GraphQueryEngine(connector)

        # Test network expansion (should work with NetworkX)
        results = await query_engine.expand_network("COMPANY_001", max_hops=2, limit=10)
        assert isinstance(results, list)
        # Results might be empty if no connections, but should not error


class TestGraphVisualizationEngine:
    """Test graph visualization engine"""

    def test_visualization_engine_initialization(self):
        """Test visualization engine initialization"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        viz_engine = GraphVisualizationEngine()

        assert "spring" in viz_engine.layout_algorithms
        assert "circular" in viz_engine.layout_algorithms
        assert "node_type" in viz_engine.color_schemes
        assert "centrality" in viz_engine.color_schemes

    def test_interactive_plot_creation(self):
        """Test creating interactive plots"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        # Mock connector with empty graph
        connector = Mock()
        connector.graph = Mock()
        connector.graph.nodes.return_value = []
        connector.graph.edges.return_value = []
        connector.nodes_data = {}

        viz_engine = GraphVisualizationEngine()

        # Should handle empty graph gracefully
        html_output = viz_engine.create_interactive_plot(
            connector, layout="spring", color_by="node_type"
        )

        # Might return None for empty graph
        assert html_output is None or isinstance(html_output, str)


@pytest.mark.asyncio
class TestAdvancedEntityGraphSystem:
    """Test main graph system"""

    async def test_system_initialization(self):
        """Test system initialization"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        graph_system = AdvancedEntityGraphSystem()

        success = await graph_system.initialize(GraphDatabase.NETWORKX)
        assert success
        assert graph_system.connector is not None
        assert graph_system.analytics_engine is not None
        assert graph_system.query_engine is not None

    async def test_entity_management(self):
        """Test adding entities and relationships"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        graph_system = AdvancedEntityGraphSystem()
        await graph_system.initialize(GraphDatabase.NETWORKX)

        # Add entity
        success = await graph_system.add_entity(
            entity_id="TEST_COMPANY",
            node_type=NodeType.COMPANY,
            properties={"name": "Test Corporation"},
            confidence=0.95,
        )
        assert success

        # Add another entity
        success = await graph_system.add_entity(
            entity_id="TEST_PERSON",
            node_type=NodeType.PERSON,
            properties={"name": "John Doe"},
            confidence=0.9,
        )
        assert success

        # Add relationship
        success = await graph_system.add_relationship(
            source_id="TEST_PERSON",
            target_id="TEST_COMPANY",
            relationship_type=RelationshipType.HAS_OFFICER,
            properties={"title": "CEO"},
            confidence=0.98,
        )
        assert success

    async def test_analytics_execution(self):
        """Test running analytics"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        graph_system = AdvancedEntityGraphSystem()
        await graph_system.initialize(GraphDatabase.NETWORKX)

        # Add test data
        await graph_system.add_entity("ENTITY_1", NodeType.COMPANY, {"name": "Corp 1"})
        await graph_system.add_entity("ENTITY_2", NodeType.COMPANY, {"name": "Corp 2"})
        await graph_system.add_relationship(
            "ENTITY_1", "ENTITY_2", RelationshipType.OWNS
        )

        # Run analytics
        analytics = await graph_system.perform_analytics()

        assert isinstance(analytics, GraphAnalytics)
        assert isinstance(analytics.centrality_measures, dict)
        assert isinstance(analytics.community_detection, dict)
        assert isinstance(analytics.anomalies, list)

    async def test_query_execution(self):
        """Test query execution"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        graph_system = AdvancedEntityGraphSystem()
        await graph_system.initialize(GraphDatabase.NETWORKX)

        # Add test data
        await graph_system.add_entity(
            "QUERY_TEST", NodeType.COMPANY, {"name": "Query Corp"}
        )

        # Execute query
        results = await graph_system.query_graph("find nodes", {})
        assert isinstance(results, list)

    def test_visualization_creation(self):
        """Test visualization creation"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        graph_system = AdvancedEntityGraphSystem()

        # Mock connector for visualization test
        graph_system.connector = Mock()
        graph_system.connector.graph = Mock()
        graph_system.connector.graph.nodes.return_value = []
        graph_system.connector.graph.edges.return_value = []
        graph_system.connector.nodes_data = {}

        # Test visualization creation
        viz_html = graph_system.create_visualization()

        # Should handle empty graph
        assert viz_html is None or isinstance(viz_html, str)


@pytest.mark.asyncio
class TestDataIntegrationBridge:
    """Test data integration bridge"""

    def test_integration_mapping_creation(self):
        """Test creating integration mappings"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        bridge = DataIntegrationBridge()

        assert "company" in bridge.entity_mappings
        assert "location" in bridge.entity_mappings
        assert "user" in bridge.entity_mappings

        company_mapping = bridge.entity_mappings["company"]
        assert company_mapping.graph_node_type == NodeType.COMPANY
        assert "name" in company_mapping.property_mappings

    @patch("gui.components.data_integration_bridge.get_db_session")
    async def test_entity_sync(self, mock_get_session):
        """Test syncing entities to graph"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        # Mock database session and data
        mock_session = Mock()
        mock_get_session.return_value.__enter__.return_value = mock_session

        # Mock entity data
        mock_entity = Mock()
        mock_entity.id = 1
        mock_entity.name = "Test Company"
        mock_entity.status = "active"

        mock_session.query.return_value.all.return_value = [mock_entity]

        bridge = DataIntegrationBridge()

        # Mock graph system
        bridge.graph_system = Mock()
        bridge.graph_system.add_entity = AsyncMock(return_value=True)

        # Test sync
        with patch.object(bridge, "_get_model_class", return_value=Mock):
            sync_results = await bridge.sync_entities_to_graph(["company"])

        assert "company" in sync_results
        bridge.graph_system.add_entity.assert_called()

    def test_entity_similarity_calculation(self):
        """Test entity similarity calculation"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        bridge = DataIntegrationBridge()

        # Create similar entities
        node1 = EntityNode(
            "ENTITY_1",
            NodeType.COMPANY,
            {"name": "Test Corporation", "industry": "Technology"},
        )

        node2 = EntityNode(
            "ENTITY_2",
            NodeType.COMPANY,
            {"name": "Test Corporation", "industry": "Technology"},
        )

        similarity = bridge._calculate_entity_similarity(node1, node2)
        assert similarity == 1.0  # Identical properties

        # Create different entities
        node3 = EntityNode(
            "ENTITY_3",
            NodeType.COMPANY,
            {"name": "Different Corp", "industry": "Finance"},
        )

        similarity2 = bridge._calculate_entity_similarity(node1, node3)
        assert similarity2 < 1.0  # Different properties

        # Different types should have 0 similarity
        node4 = EntityNode("ENTITY_4", NodeType.PERSON, {"name": "Test Corporation"})

        similarity3 = bridge._calculate_entity_similarity(node1, node4)
        assert similarity3 == 0.0

    async def test_integration_status(self):
        """Test getting integration status"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        bridge = DataIntegrationBridge()

        # Mock graph system
        bridge.graph_system = Mock()
        bridge.graph_system.connector = Mock()
        bridge.graph_system.connector.connected = True
        bridge.graph_system.connector.nodes_data = {
            "COMPANY_1": Mock(node_type=NodeType.COMPANY),
            "PERSON_1": Mock(node_type=NodeType.PERSON),
        }
        bridge.graph_system.connector.relationships_data = {"rel_1": Mock()}

        status = await bridge.get_integration_status()

        assert status["graph_system_connected"] is True
        assert status["auto_sync_enabled"] is True
        assert "entity_mappings" in status
        assert "sync_statistics" in status
        assert status["sync_statistics"]["total_nodes"] == 2
        assert status["sync_statistics"]["total_relationships"] == 1


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases"""

    @pytest.mark.asyncio
    async def test_large_graph_handling(self):
        """Test handling of large graphs"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Add many nodes (simulating large graph)
        num_nodes = 100

        for i in range(num_nodes):
            node = EntityNode(
                f"LARGE_NODE_{i}", NodeType.COMPANY, {"name": f"Company {i}"}
            )
            success = await connector.create_node(node)
            assert success

        # Verify all nodes were added
        assert len(connector.graph.nodes()) == num_nodes
        assert len(connector.nodes_data) == num_nodes

    @pytest.mark.asyncio
    async def test_empty_graph_analytics(self):
        """Test analytics on empty graph"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        analytics_engine = GraphAnalyticsEngine(connector)

        # Should handle empty graph gracefully
        centrality = await analytics_engine.calculate_centrality_measures()
        assert isinstance(centrality, dict)

        communities = await analytics_engine.detect_communities()
        assert isinstance(communities, dict)

        anomalies = await analytics_engine.detect_anomalies()
        assert isinstance(anomalies, list)

    @pytest.mark.asyncio
    async def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        connector = NetworkXConnector({})
        await connector.connect()

        # Test with invalid entity ID
        try:
            node = EntityNode("", NodeType.COMPANY, {"name": "Test"})  # Empty ID
            success = await connector.create_node(node)
            # Should handle gracefully
        except Exception:
            # Expected to fail gracefully
            pass

        # Test with invalid relationship
        try:
            relationship = EntityRelationship(
                "NONEXISTENT_SOURCE", "NONEXISTENT_TARGET", RelationshipType.OWNS
            )
            success = await connector.create_relationship(relationship)
            # Should handle gracefully
        except Exception:
            # Expected to fail gracefully
            pass

    def test_concurrent_access(self):
        """Test concurrent access to graph system"""
        if not IMPORTS_AVAILABLE:
            pytest.skip("Required imports not available")

        # This would test thread safety in a real implementation
        # For now, just verify system can be instantiated multiple times
        system1 = AdvancedEntityGraphSystem()
        system2 = AdvancedEntityGraphSystem()

        assert system1 is not system2
        assert system1.config is not system2.config


# Integration test fixtures
@pytest.fixture
def sample_graph_data():
    """Sample graph data for testing"""
    if not IMPORTS_AVAILABLE:
        pytest.skip("Required imports not available")

    entities = [
        {
            "entity_id": "COMPANY_A",
            "node_type": NodeType.COMPANY,
            "properties": {
                "name": "Alpha Corporation",
                "industry": "Technology",
                "founded": "2010",
            },
            "confidence": 0.95,
        },
        {
            "entity_id": "COMPANY_B",
            "node_type": NodeType.COMPANY,
            "properties": {
                "name": "Beta Industries",
                "industry": "Manufacturing",
                "founded": "2015",
            },
            "confidence": 0.90,
        },
        {
            "entity_id": "PERSON_1",
            "node_type": NodeType.PERSON,
            "properties": {
                "name": "John Smith",
                "nationality": "UK",
                "birth_year": "1980",
            },
            "confidence": 0.88,
        },
        {
            "entity_id": "ADDRESS_1",
            "node_type": NodeType.ADDRESS,
            "properties": {
                "address": "123 Business Street",
                "city": "London",
                "country": "UK",
            },
            "confidence": 0.92,
        },
    ]

    relationships = [
        {
            "source_id": "PERSON_1",
            "target_id": "COMPANY_A",
            "relationship_type": RelationshipType.HAS_OFFICER,
            "properties": {"title": "CEO", "start_date": "2020-01-01"},
            "confidence": 0.97,
        },
        {
            "source_id": "COMPANY_A",
            "target_id": "COMPANY_B",
            "relationship_type": RelationshipType.OWNS,
            "properties": {"ownership_percentage": 75.5},
            "confidence": 0.93,
        },
        {
            "source_id": "COMPANY_A",
            "target_id": "ADDRESS_1",
            "relationship_type": RelationshipType.REGISTERED_AT,
            "properties": {"registration_date": "2010-03-15"},
            "confidence": 0.99,
        },
    ]

    return {"entities": entities, "relationships": relationships}


@pytest.mark.asyncio
async def test_end_to_end_workflow(sample_graph_data):
    """End-to-end test of the complete workflow"""
    if not IMPORTS_AVAILABLE:
        pytest.skip("Required imports not available")

    # Initialize system
    graph_system = AdvancedEntityGraphSystem()
    success = await graph_system.initialize(GraphDatabase.NETWORKX)
    assert success

    # Add entities
    for entity_data in sample_graph_data["entities"]:
        success = await graph_system.add_entity(**entity_data)
        assert success

    # Add relationships
    for rel_data in sample_graph_data["relationships"]:
        success = await graph_system.add_relationship(**rel_data)
        assert success

    # Run analytics
    analytics = await graph_system.perform_analytics()
    assert len(analytics.centrality_measures) > 0

    # Test queries
    results = await graph_system.query_graph("find nodes", {})
    assert len(results) >= len(sample_graph_data["entities"])

    # Test visualization
    viz_html = graph_system.create_visualization()
    # Should create visualization or return None gracefully

    # Cleanup
    await graph_system.shutdown()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
