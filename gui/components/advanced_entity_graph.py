"""
Advanced Entity Graph System

Comprehensive graph-based entity relationship mapping, analysis, and visualization
for business intelligence investigations with support for multiple graph databases
and advanced analytics.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


# Graph libraries with fallbacks
try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import py2neo

    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import pyarango

    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Types of entities in the graph"""

    COMPANY = "company"
    PERSON = "person"
    ADDRESS = "address"
    FILING = "filing"
    ASSET = "asset"
    CONTRACT = "contract"
    EVENT = "event"
    ACCOUNT = "account"
    TRANSACTION = "transaction"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    """Types of relationships between entities"""

    HAS_OFFICER = "HAS_OFFICER"
    REGISTERED_AT = "REGISTERED_AT"
    OWNS = "OWNS"
    IS_SUBSIDIARY_OF = "IS_SUBSIDIARY_OF"
    FILED = "FILED"
    JOINT_VENTURE_WITH = "JOINT_VENTURE_WITH"
    LINKED_TO = "LINKED_TO"
    RELATED_TO = "RELATED_TO"
    CONTROLS = "CONTROLS"
    BENEFICIARY_OF = "BENEFICIARY_OF"
    OPERATES_FROM = "OPERATES_FROM"
    BOARD_MEMBER = "BOARD_MEMBER"
    SHAREHOLDER = "SHAREHOLDER"
    AUTHORIZED_SIGNATORY = "AUTHORIZED_SIGNATORY"
    SAME_AS = "SAME_AS"
    SIMILAR_TO = "SIMILAR_TO"


class GraphDatabase(str, Enum):
    """Supported graph database backends"""

    NETWORKX = "networkx"
    NEO4J = "neo4j"
    ARANGO = "arangodb"
    MEMORY = "memory"


@dataclass
class EntityNode:
    """Represents an entity node in the graph"""

    entity_id: str
    node_type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    coordinates: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    creation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    data_sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def display_name(self) -> str:
        """Get display name for the entity"""
        if "name" in self.properties:
            return self.properties["name"]
        elif "title" in self.properties:
            return self.properties["title"]
        else:
            return f"{self.node_type.value}_{self.entity_id[:8]}"


@dataclass
class EntityRelationship:
    """Represents a relationship between entities"""

    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    data_sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphAnalytics:
    """Results from graph analytics operations"""

    centrality_measures: Dict[str, Dict[str, float]] = field(default_factory=dict)
    community_detection: Dict[str, int] = field(default_factory=dict)
    shortest_paths: Dict[Tuple[str, str], List[str]] = field(default_factory=dict)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    temporal_analysis: Dict[str, Any] = field(default_factory=dict)
    network_metrics: Dict[str, float] = field(default_factory=dict)


class GraphDatabaseConnector:
    """Base class for graph database connectors"""

    def __init__(self, connection_config: Dict[str, Any]):
        self.config = connection_config
        self.connected = False

    async def connect(self) -> bool:
        """Connect to the graph database"""
        raise NotImplementedError

    async def disconnect(self):
        """Disconnect from the graph database"""
        raise NotImplementedError

    async def create_node(self, node: EntityNode) -> bool:
        """Create a node in the graph database"""
        raise NotImplementedError

    async def create_relationship(self, relationship: EntityRelationship) -> bool:
        """Create a relationship in the graph database"""
        raise NotImplementedError

    async def execute_query(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute a custom query"""
        raise NotImplementedError


class NetworkXConnector(GraphDatabaseConnector):
    """NetworkX in-memory graph connector"""

    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.graph = nx.MultiDiGraph() if NETWORKX_AVAILABLE else None
        self.nodes_data: Dict[str, EntityNode] = {}
        self.relationships_data: Dict[str, EntityRelationship] = {}

    async def connect(self) -> bool:
        """Connect to NetworkX (always available in memory)"""
        if not NETWORKX_AVAILABLE:
            return False
        self.connected = True
        return True

    async def disconnect(self):
        """Disconnect from NetworkX"""
        self.connected = False

    async def create_node(self, node: EntityNode) -> bool:
        """Create a node in NetworkX graph"""
        if not self.connected or not self.graph:
            return False

        try:
            self.graph.add_node(
                node.entity_id,
                node_type=node.node_type.value,
                properties=node.properties,
                confidence=node.confidence,
                creation_time=node.creation_time.isoformat(),
                data_sources=node.data_sources,
            )
            self.nodes_data[node.entity_id] = node
            return True
        except Exception as e:
            logger.error(f"Error creating node: {e}")
            return False

    async def create_relationship(self, relationship: EntityRelationship) -> bool:
        """Create a relationship in NetworkX graph"""
        if not self.connected or not self.graph:
            return False

        try:
            self.graph.add_edge(
                relationship.source_id,
                relationship.target_id,
                relationship_type=relationship.relationship_type.value,
                properties=relationship.properties,
                confidence=relationship.confidence,
                created_at=relationship.created_at.isoformat(),
                valid_from=(
                    relationship.valid_from.isoformat()
                    if relationship.valid_from
                    else None
                ),
                valid_to=(
                    relationship.valid_to.isoformat() if relationship.valid_to else None
                ),
                data_sources=relationship.data_sources,
            )

            rel_key = f"{relationship.source_id}-{relationship.target_id}-{relationship.relationship_type.value}"
            self.relationships_data[rel_key] = relationship
            return True
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False

    async def execute_query(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute a query-like operation on NetworkX graph"""
        if not self.connected or not self.graph:
            return []

        # Simple query parsing for common operations
        results = []

        try:
            if query.lower().startswith("find nodes"):
                # Find nodes by type or property
                for node_id, data in self.graph.nodes(data=True):
                    results.append({"node_id": node_id, "data": data})

            elif query.lower().startswith("find paths"):
                # Find shortest paths between nodes
                if parameters and "source" in parameters and "target" in parameters:
                    try:
                        path = nx.shortest_path(
                            self.graph, parameters["source"], parameters["target"]
                        )
                        results.append({"path": path})
                    except nx.NetworkXNoPath:
                        results.append({"path": []})

            elif query.lower().startswith("find communities"):
                # Community detection
                try:
                    communities = nx.community.greedy_modularity_communities(
                        self.graph.to_undirected()
                    )
                    for i, community in enumerate(communities):
                        results.append({"community_id": i, "nodes": list(community)})
                except:
                    logger.warning("Community detection failed")

        except Exception as e:
            logger.error(f"Error executing query: {e}")

        return results


class Neo4jConnector(GraphDatabaseConnector):
    """Neo4j graph database connector"""

    def __init__(self, connection_config: Dict[str, Any]):
        super().__init__(connection_config)
        self.driver = None
        self.session = None

    async def connect(self) -> bool:
        """Connect to Neo4j database"""
        if not NEO4J_AVAILABLE:
            logger.warning("Neo4j driver not available")
            return False

        try:
            from py2neo import Graph

            uri = self.config.get("uri", "bolt://localhost:7687")
            username = self.config.get("username", "neo4j")
            password = self.config.get("password", "password")

            self.driver = Graph(uri, auth=(username, password))
            self.connected = True
            logger.info("Connected to Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Neo4j"""
        if self.driver:
            self.driver = None
        self.connected = False

    async def create_node(self, node: EntityNode) -> bool:
        """Create a node in Neo4j"""
        if not self.connected:
            return False

        try:
            cypher = f"""
            CREATE (n:{node.node_type.value} {{
                entity_id: $entity_id,
                properties: $properties,
                confidence: $confidence,
                creation_time: $creation_time,
                data_sources: $data_sources
            }})
            """

            parameters = {
                "entity_id": node.entity_id,
                "properties": json.dumps(node.properties),
                "confidence": node.confidence,
                "creation_time": node.creation_time.isoformat(),
                "data_sources": node.data_sources,
            }

            self.driver.run(cypher, parameters)
            return True
        except Exception as e:
            logger.error(f"Error creating Neo4j node: {e}")
            return False

    async def create_relationship(self, relationship: EntityRelationship) -> bool:
        """Create a relationship in Neo4j"""
        if not self.connected:
            return False

        try:
            cypher = f"""
            MATCH (a {{entity_id: $source_id}})
            MATCH (b {{entity_id: $target_id}})
            CREATE (a)-[r:{relationship.relationship_type.value} {{
                properties: $properties,
                confidence: $confidence,
                created_at: $created_at,
                valid_from: $valid_from,
                valid_to: $valid_to,
                data_sources: $data_sources
            }}]->(b)
            """

            parameters = {
                "source_id": relationship.source_id,
                "target_id": relationship.target_id,
                "properties": json.dumps(relationship.properties),
                "confidence": relationship.confidence,
                "created_at": relationship.created_at.isoformat(),
                "valid_from": (
                    relationship.valid_from.isoformat()
                    if relationship.valid_from
                    else None
                ),
                "valid_to": (
                    relationship.valid_to.isoformat() if relationship.valid_to else None
                ),
                "data_sources": relationship.data_sources,
            }

            self.driver.run(cypher, parameters)
            return True
        except Exception as e:
            logger.error(f"Error creating Neo4j relationship: {e}")
            return False

    async def execute_query(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query"""
        if not self.connected:
            return []

        try:
            result = self.driver.run(query, parameters or {})
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query: {e}")
            return []


class GraphAnalyticsEngine:
    """Advanced graph analytics and machine learning"""

    def __init__(self, connector: GraphDatabaseConnector):
        self.connector = connector
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)

    async def calculate_centrality_measures(
        self, node_ids: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality measures"""
        if not NETWORKX_AVAILABLE or not isinstance(self.connector, NetworkXConnector):
            return {}

        graph = self.connector.graph
        if not graph or len(graph.nodes()) == 0:
            return {}

        try:
            # Calculate different centrality measures
            centrality_results = {}

            # Degree centrality
            degree_centrality = nx.degree_centrality(graph)
            centrality_results["degree"] = degree_centrality

            # Betweenness centrality
            betweenness_centrality = nx.betweenness_centrality(graph)
            centrality_results["betweenness"] = betweenness_centrality

            # Closeness centrality
            if nx.is_connected(graph.to_undirected()):
                closeness_centrality = nx.closeness_centrality(graph)
                centrality_results["closeness"] = closeness_centrality

            # Eigenvector centrality (for connected components)
            try:
                eigenvector_centrality = nx.eigenvector_centrality(graph, max_iter=1000)
                centrality_results["eigenvector"] = eigenvector_centrality
            except:
                logger.warning("Eigenvector centrality calculation failed")

            # PageRank
            pagerank = nx.pagerank(graph)
            centrality_results["pagerank"] = pagerank

            return centrality_results

        except Exception as e:
            logger.error(f"Error calculating centrality measures: {e}")
            return {}

    async def detect_communities(self) -> Dict[str, int]:
        """Detect communities/clusters in the graph"""
        if not NETWORKX_AVAILABLE or not isinstance(self.connector, NetworkXConnector):
            return {}

        graph = self.connector.graph
        if not graph or len(graph.nodes()) == 0:
            return {}

        try:
            # Convert to undirected graph for community detection
            undirected = graph.to_undirected()

            # Use different community detection algorithms
            communities = nx.community.greedy_modularity_communities(undirected)

            # Create node-to-community mapping
            community_mapping = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_mapping[node] = i

            return community_mapping

        except Exception as e:
            logger.error(f"Error detecting communities: {e}")
            return {}

    async def find_shortest_paths(
        self, source: str, target: str = None
    ) -> Dict[Tuple[str, str], List[str]]:
        """Find shortest paths between nodes"""
        if not NETWORKX_AVAILABLE or not isinstance(self.connector, NetworkXConnector):
            return {}

        graph = self.connector.graph
        if not graph or source not in graph.nodes():
            return {}

        paths = {}

        try:
            if target:
                # Find path to specific target
                try:
                    path = nx.shortest_path(graph, source, target)
                    paths[(source, target)] = path
                except nx.NetworkXNoPath:
                    paths[(source, target)] = []
            else:
                # Find paths to all reachable nodes
                try:
                    all_paths = nx.single_source_shortest_path(graph, source)
                    for target_node, path in all_paths.items():
                        if target_node != source:
                            paths[(source, target_node)] = path
                except:
                    logger.warning(f"Could not calculate paths from {source}")

            return paths

        except Exception as e:
            logger.error(f"Error finding shortest paths: {e}")
            return {}

    async def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in the graph"""
        if not NETWORKX_AVAILABLE or not isinstance(self.connector, NetworkXConnector):
            return []

        graph = self.connector.graph
        if not graph or len(graph.nodes()) == 0:
            return []

        anomalies = []

        try:
            # Calculate basic graph metrics
            degree_sequence = [d for n, d in graph.degree()]
            avg_degree = (
                sum(degree_sequence) / len(degree_sequence) if degree_sequence else 0
            )

            # Detect nodes with unusually high degree (hubs)
            for node, degree in graph.degree():
                if degree > avg_degree * 3:  # Threshold: 3x average
                    anomalies.append(
                        {
                            "type": "high_degree_node",
                            "node_id": node,
                            "degree": degree,
                            "avg_degree": avg_degree,
                            "severity": min(1.0, degree / (avg_degree * 5)),
                        }
                    )

            # Detect isolated components
            components = list(nx.weakly_connected_components(graph))
            largest_component_size = (
                max(len(c) for c in components) if components else 0
            )

            for component in components:
                if len(component) < 0.1 * largest_component_size and len(component) > 1:
                    anomalies.append(
                        {
                            "type": "isolated_component",
                            "nodes": list(component),
                            "size": len(component),
                            "severity": 0.5,
                        }
                    )

            # Detect nodes with unusual relationship patterns
            for node in graph.nodes():
                in_degree = graph.in_degree(node)
                out_degree = graph.out_degree(node)

                # Node with many incoming but few outgoing connections
                if in_degree > 10 and out_degree < 2:
                    anomalies.append(
                        {
                            "type": "sink_node",
                            "node_id": node,
                            "in_degree": in_degree,
                            "out_degree": out_degree,
                            "severity": min(1.0, in_degree / 20),
                        }
                    )

                # Node with many outgoing but few incoming connections
                elif out_degree > 10 and in_degree < 2:
                    anomalies.append(
                        {
                            "type": "source_node",
                            "node_id": node,
                            "in_degree": in_degree,
                            "out_degree": out_degree,
                            "severity": min(1.0, out_degree / 20),
                        }
                    )

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    async def temporal_analysis(self, time_window_days: int = 30) -> Dict[str, Any]:
        """Analyze temporal patterns in the graph"""
        if not isinstance(self.connector, NetworkXConnector):
            return {}

        graph = self.connector.graph
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(days=time_window_days)

        analysis = {
            "time_window_days": time_window_days,
            "node_creation_timeline": {},
            "relationship_creation_timeline": {},
            "activity_patterns": {},
            "growth_metrics": {},
        }

        try:
            # Analyze node creation patterns
            node_times = []
            for node_id, data in graph.nodes(data=True):
                if "creation_time" in data:
                    try:
                        creation_time = datetime.fromisoformat(
                            data["creation_time"].replace("Z", "+00:00")
                        )
                        if creation_time >= cutoff_time:
                            node_times.append(creation_time)
                    except:
                        continue

            # Group by day
            daily_node_counts = {}
            for dt in node_times:
                day_key = dt.date().isoformat()
                daily_node_counts[day_key] = daily_node_counts.get(day_key, 0) + 1

            analysis["node_creation_timeline"] = daily_node_counts

            # Analyze relationship creation patterns
            relationship_times = []
            for source, target, data in graph.edges(data=True):
                if "created_at" in data:
                    try:
                        creation_time = datetime.fromisoformat(
                            data["created_at"].replace("Z", "+00:00")
                        )
                        if creation_time >= cutoff_time:
                            relationship_times.append(creation_time)
                    except:
                        continue

            daily_rel_counts = {}
            for dt in relationship_times:
                day_key = dt.date().isoformat()
                daily_rel_counts[day_key] = daily_rel_counts.get(day_key, 0) + 1

            analysis["relationship_creation_timeline"] = daily_rel_counts

            # Calculate growth metrics
            if node_times:
                analysis["growth_metrics"]["nodes_added"] = len(node_times)
                analysis["growth_metrics"]["avg_nodes_per_day"] = (
                    len(node_times) / time_window_days
                )

            if relationship_times:
                analysis["growth_metrics"]["relationships_added"] = len(
                    relationship_times
                )
                analysis["growth_metrics"]["avg_relationships_per_day"] = (
                    len(relationship_times) / time_window_days
                )

            return analysis

        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return analysis


class GraphQueryEngine:
    """Query engine for executing complex graph queries"""

    def __init__(self, connector: GraphDatabaseConnector):
        self.connector = connector
        self.query_templates = self._load_query_templates()

    def _load_query_templates(self) -> Dict[str, str]:
        """Load predefined query templates"""
        return {
            "circular_ownership": """
                MATCH path = (c1:COMPANY)-[:OWNS*2..5]->(c1)
                WHERE c1.entity_id = $entity_id
                RETURN path
            """,
            "director_in_common": """
                MATCH (p:PERSON)-[:HAS_OFFICER]->(c1:COMPANY)
                MATCH (p)-[:HAS_OFFICER]->(c2:COMPANY)
                WHERE c1 <> c2 AND c1.entity_id = $entity_id
                RETURN p, c1, c2
            """,
            "ultimate_beneficial_owner": """
                MATCH path = (start:COMPANY)-[:OWNS*]->(end:PERSON)
                WHERE start.entity_id = $entity_id
                AND NOT (end)-[:OWNS]->()
                RETURN path ORDER BY length(path) DESC LIMIT 10
            """,
            "shell_company_detection": """
                MATCH (c:COMPANY)
                WHERE c.entity_id = $entity_id
                OPTIONAL MATCH (c)-[:HAS_OFFICER]->(officers)
                OPTIONAL MATCH (c)-[:REGISTERED_AT]->(addr:ADDRESS)
                WITH c, count(officers) as officer_count, collect(addr) as addresses
                WHERE officer_count <= 1 OR size(addresses) = 0
                RETURN c, officer_count, addresses
            """,
            "network_expansion": """
                MATCH (start {{entity_id: $entity_id}})
                MATCH path = (start)-[*1..$max_hops]-(connected)
                RETURN path, connected
                ORDER BY length(path)
                LIMIT $limit
            """,
            "risk_propagation": """
                MATCH path = (risk_entity {{entity_id: $entity_id}})-[*1..$depth]-(connected)
                WHERE any(rel in relationships(path) WHERE rel.confidence < 0.7)
                RETURN path, connected
                ORDER BY length(path)
            """,
        }

    async def execute_template_query(
        self, template_name: str, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute a predefined query template"""
        if template_name not in self.query_templates:
            logger.error(f"Query template '{template_name}' not found")
            return []

        query = self.query_templates[template_name]
        return await self.connector.execute_query(query, parameters)

    async def find_circular_ownership(
        self, entity_id: str, max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """Find circular ownership patterns"""
        return await self.execute_template_query(
            "circular_ownership", {"entity_id": entity_id, "max_depth": max_depth}
        )

    async def find_directors_in_common(self, entity_id: str) -> List[Dict[str, Any]]:
        """Find companies sharing directors with the given entity"""
        return await self.execute_template_query(
            "director_in_common", {"entity_id": entity_id}
        )

    async def find_ultimate_beneficial_owners(
        self, entity_id: str
    ) -> List[Dict[str, Any]]:
        """Find ultimate beneficial owners"""
        return await self.execute_template_query(
            "ultimate_beneficial_owner", {"entity_id": entity_id}
        )

    async def detect_shell_companies(self, entity_id: str) -> List[Dict[str, Any]]:
        """Detect potential shell companies"""
        return await self.execute_template_query(
            "shell_company_detection", {"entity_id": entity_id}
        )

    async def expand_network(
        self, entity_id: str, max_hops: int = 3, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Expand network around an entity"""
        return await self.execute_template_query(
            "network_expansion",
            {"entity_id": entity_id, "max_hops": max_hops, "limit": limit},
        )


class GraphVisualizationEngine:
    """Advanced graph visualization with interactive features"""

    def __init__(self):
        self.layout_algorithms = [
            "spring",
            "circular",
            "hierarchical",
            "fruchterman_reingold",
            "kamada_kawai",
        ]
        self.color_schemes = [
            "centrality",
            "node_type",
            "community",
            "confidence",
            "temporal",
        ]

    def create_interactive_plot(
        self,
        connector: GraphDatabaseConnector,
        layout: str = "spring",
        color_by: str = "node_type",
        show_labels: bool = True,
    ) -> Optional[str]:
        """Create interactive Plotly visualization"""
        if not PLOTLY_AVAILABLE or not isinstance(connector, NetworkXConnector):
            return None

        graph = connector.graph
        if not graph or len(graph.nodes()) == 0:
            return None

        try:
            # Calculate layout
            if layout == "spring":
                pos = nx.spring_layout(graph, k=1, iterations=50)
            elif layout == "circular":
                pos = nx.circular_layout(graph)
            elif layout == "hierarchical":
                pos = nx.shell_layout(graph)
            else:
                pos = nx.random_layout(graph)

            # Extract node information
            node_trace = go.Scatter(
                x=[pos[node][0] for node in graph.nodes()],
                y=[pos[node][1] for node in graph.nodes()],
                mode="markers+text" if show_labels else "markers",
                text=[
                    (
                        connector.nodes_data[node].display_name
                        if node in connector.nodes_data
                        else node
                    )
                    for node in graph.nodes()
                ],
                textposition="middle center",
                hovertemplate="%{text}<br>Connections: %{marker.size}<extra></extra>",
                marker=dict(
                    size=[graph.degree(node) * 5 + 10 for node in graph.nodes()],
                    color=self._get_node_colors(graph, connector, color_by),
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title=color_by.replace("_", " ").title()),
                    line=dict(width=2, color="white"),
                ),
            )

            # Extract edge information
            edge_x = []
            edge_y = []
            edge_info = []

            for edge in graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

                # Get edge data
                edge_data = graph.get_edge_data(edge[0], edge[1])
                if edge_data:
                    edge_info.append(
                        f"{edge[0]} -> {edge[1]}: {edge_data.get('relationship_type', 'RELATED')}"
                    )

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=1, color="lightgray"),
                hoverinfo="none",
                mode="lines",
            )

            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title=f"Entity Relationship Graph - {layout.title()} Layout",
                    titlefont_size=16,
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=20, l=5, r=5, t=40),
                    annotations=[
                        dict(
                            text="Drag nodes to explore relationships",
                            showarrow=False,
                            xref="paper",
                            yref="paper",
                            x=0.005,
                            y=-0.002,
                            xanchor="left",
                            yanchor="bottom",
                            font=dict(color="gray", size=12),
                        )
                    ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor="white",
                ),
            )

            # Return HTML
            return fig.to_html(include_plotlyjs=True)

        except Exception as e:
            logger.error(f"Error creating interactive plot: {e}")
            return None

    def _get_node_colors(
        self, graph, connector: GraphDatabaseConnector, color_by: str
    ) -> List[float]:
        """Get node colors based on the selected scheme"""
        node_colors = []

        try:
            if color_by == "node_type":
                # Color by node type
                type_mapping = {
                    "company": 0,
                    "person": 1,
                    "address": 2,
                    "filing": 3,
                    "asset": 4,
                    "contract": 5,
                    "event": 6,
                }

                for node in graph.nodes():
                    if (
                        isinstance(connector, NetworkXConnector)
                        and node in connector.nodes_data
                    ):
                        node_type = connector.nodes_data[node].node_type.value
                        node_colors.append(type_mapping.get(node_type, 7))
                    else:
                        node_colors.append(7)

            elif color_by == "centrality":
                # Color by degree centrality
                centrality = nx.degree_centrality(graph)
                for node in graph.nodes():
                    node_colors.append(centrality.get(node, 0))

            elif color_by == "confidence":
                # Color by confidence level
                for node in graph.nodes():
                    if (
                        isinstance(connector, NetworkXConnector)
                        and node in connector.nodes_data
                    ):
                        confidence = connector.nodes_data[node].confidence
                        node_colors.append(confidence)
                    else:
                        node_colors.append(0.5)

            else:
                # Default: degree
                for node in graph.nodes():
                    node_colors.append(graph.degree(node))

        except Exception as e:
            logger.error(f"Error calculating node colors: {e}")
            # Fallback to degree
            for node in graph.nodes():
                node_colors.append(graph.degree(node))

        return node_colors


class AdvancedEntityGraphSystem:
    """Main system for advanced entity graph operations"""

    def __init__(self):
        self.connector: Optional[GraphDatabaseConnector] = None
        self.analytics_engine: Optional[GraphAnalyticsEngine] = None
        self.query_engine: Optional[GraphQueryEngine] = None
        self.visualization_engine = GraphVisualizationEngine()
        self.config = {
            "database_type": GraphDatabase.NETWORKX,
            "connection_config": {},
            "auto_save": True,
            "cache_analytics": True,
        }

    async def initialize(
        self,
        database_type: GraphDatabase = GraphDatabase.NETWORKX,
        connection_config: Dict[str, Any] = None,
    ) -> bool:
        """Initialize the graph system"""
        try:
            self.config["database_type"] = database_type
            self.config["connection_config"] = connection_config or {}

            # Create appropriate connector
            if database_type == GraphDatabase.NETWORKX:
                self.connector = NetworkXConnector(self.config["connection_config"])
            elif database_type == GraphDatabase.NEO4J:
                self.connector = Neo4jConnector(self.config["connection_config"])
            else:
                logger.error(f"Unsupported database type: {database_type}")
                return False

            # Connect to database
            if not await self.connector.connect():
                logger.error("Failed to connect to graph database")
                return False

            # Initialize engines
            self.analytics_engine = GraphAnalyticsEngine(self.connector)
            self.query_engine = GraphQueryEngine(self.connector)

            logger.info(f"Graph system initialized with {database_type.value}")
            return True

        except Exception as e:
            logger.error(f"Error initializing graph system: {e}")
            return False

    async def add_entity(
        self,
        entity_id: str,
        node_type: NodeType,
        properties: Dict[str, Any] = None,
        confidence: float = 1.0,
        data_sources: List[str] = None,
    ) -> bool:
        """Add an entity to the graph"""
        if not self.connector:
            return False

        node = EntityNode(
            entity_id=entity_id,
            node_type=node_type,
            properties=properties or {},
            confidence=confidence,
            data_sources=data_sources or [],
        )

        return await self.connector.create_node(node)

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        properties: Dict[str, Any] = None,
        confidence: float = 1.0,
        valid_from: datetime = None,
        valid_to: datetime = None,
        data_sources: List[str] = None,
    ) -> bool:
        """Add a relationship to the graph"""
        if not self.connector:
            return False

        relationship = EntityRelationship(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            properties=properties or {},
            confidence=confidence,
            valid_from=valid_from,
            valid_to=valid_to,
            data_sources=data_sources or [],
        )

        return await self.connector.create_relationship(relationship)

    async def perform_analytics(self) -> GraphAnalytics:
        """Perform comprehensive graph analytics"""
        if not self.analytics_engine:
            return GraphAnalytics()

        analytics = GraphAnalytics()

        try:
            # Calculate centrality measures
            analytics.centrality_measures = (
                await self.analytics_engine.calculate_centrality_measures()
            )

            # Detect communities
            analytics.community_detection = (
                await self.analytics_engine.detect_communities()
            )

            # Detect anomalies
            analytics.anomalies = await self.analytics_engine.detect_anomalies()

            # Temporal analysis
            analytics.temporal_analysis = (
                await self.analytics_engine.temporal_analysis()
            )

            logger.info("Graph analytics completed")
            return analytics

        except Exception as e:
            logger.error(f"Error performing analytics: {e}")
            return analytics

    async def query_graph(
        self, query: str, parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Execute a custom graph query"""
        if not self.connector:
            return []

        return await self.connector.execute_query(query, parameters)

    def create_visualization(
        self,
        layout: str = "spring",
        color_by: str = "node_type",
        show_labels: bool = True,
    ) -> Optional[str]:
        """Create an interactive visualization"""
        return self.visualization_engine.create_interactive_plot(
            self.connector, layout, color_by, show_labels
        )

    async def shutdown(self):
        """Shutdown the graph system"""
        if self.connector:
            await self.connector.disconnect()


# Global instance
advanced_entity_graph = AdvancedEntityGraphSystem()
