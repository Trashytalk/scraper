# Advanced Entity Graph System

## Overview

The Advanced Entity Graph System is a comprehensive business intelligence tool that provides sophisticated entity relationship mapping, graph-based analytics, and investigative discovery capabilities. It integrates seamlessly with the existing Data Quality & Provenance Intelligence system to provide a complete picture of business entity relationships and network analysis.

## Key Features

### 🎯 Core Capabilities
- **Multi-Database Support**: NetworkX (in-memory), Neo4j, ArangoDB, JanusGraph
- **Advanced Analytics**: Centrality measures, community detection, anomaly detection
- **Temporal Analysis**: Time-based relationship tracking and evolution analysis
- **Interactive Visualization**: 2D/3D graph visualizations with multiple layout algorithms
- **Query Engine**: Cypher-compatible queries with pre-built templates

### 🔍 Investigative Features
- **Circular Ownership Detection**: Identify complex ownership loops
- **Shell Company Detection**: Flag potential shell companies based on network patterns
- **Ultimate Beneficial Owner Discovery**: Trace ownership chains to final beneficiaries
- **Directors in Common**: Find shared leadership across companies
- **Risk Propagation Analysis**: Track how risks spread through networks

### 🧠 Machine Learning & AI
- **Graph Embeddings**: Node2Vec, DeepWalk for entity representations
- **Community Detection**: Louvain, Leiden algorithms for cluster identification
- **Anomaly Detection**: Statistical and ML-based outlier identification
- **Identity Disambiguation**: Entity resolution and duplicate detection
- **Relationship Prediction**: ML-powered link prediction

### 📊 Data Integration
- **Quality-Aware Graphs**: Integration with Data Quality & Provenance system
- **Automatic Synchronization**: Real-time sync between database and graph
- **Provenance Tracking**: Full lineage tracking for all graph entities
- **Multi-Source Fusion**: Combine data from multiple sources with confidence scoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GUI Layer                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │ Graph Controls  │ │  Visualization  │ │   Analytics     ││
│  │    & Queries    │ │     Engine      │ │    Results      ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Advanced Entity Graph System                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │  Graph Query    │ │   Analytics     │ │  Visualization  ││
│  │     Engine      │ │     Engine      │ │     Engine      ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Graph Database Connectors                  ││
│  │    NetworkX  │    Neo4j    │   ArangoDB  │  JanusGraph  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Data Integration Bridge                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐│
│  │   Entity Sync   │ │  Quality Sync   │ │ Provenance Sync ││
│  └─────────────────┘ └─────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│          Data Quality & Provenance Intelligence             │
│                    (Existing System)                       │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Quick Start
```bash
# Install the complete system
python setup_graph_system.py

# Install with optional components (GPU support, advanced ML)
python setup_graph_system.py --optional

# Install with Neo4j database setup
python setup_graph_system.py --neo4j
```

### Manual Installation
```bash
# Core dependencies
pip install networkx plotly pandas numpy scipy scikit-learn
pip install py2neo pyarango community python-louvain
pip install dash dash-cytoscape spacy nltk fuzzywuzzy
```

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install graphviz graphviz-dev pkg-config python3-dev

# macOS
brew install graphviz pkg-config

# Download spaCy models
python -m spacy download en_core_web_sm
```

## Configuration

### Graph System Configuration (`config/graph_system/graph_config.json`)
```json
{
  "graph_system": {
    "default_database": "networkx",
    "auto_sync_enabled": true,
    "auto_sync_interval": 300,
    "max_nodes_in_memory": 10000
  },
  "databases": {
    "neo4j": {
      "uri": "bolt://localhost:7687",
      "username": "neo4j", 
      "password": "graphsystem123"
    }
  },
  "analytics": {
    "enable_ml_features": true,
    "community_detection_algorithm": "louvain",
    "anomaly_detection_threshold": 0.8
  }
}
```

### Database Connections

#### Neo4j Setup
```bash
# Using Docker
docker run --name neo4j-graph-system \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/graphsystem123 \
  -d neo4j:5.13-community
```

#### ArangoDB Setup
```bash
# Using Docker
docker run --name arangodb-graph-system \
  -p 8529:8529 \
  -e ARANGO_NO_AUTH=1 \
  -d arangodb/arangodb:3.11
```

## Usage

### Basic Operations

#### 1. Initialize the System
```python
from gui.components.advanced_entity_graph import advanced_entity_graph
from gui.components.advanced_entity_graph import GraphDatabase, NodeType, RelationshipType

# Initialize with NetworkX (in-memory)
await advanced_entity_graph.initialize(GraphDatabase.NETWORKX)

# Or with Neo4j
await advanced_entity_graph.initialize(
    GraphDatabase.NEO4J,
    {"uri": "bolt://localhost:7687", "username": "neo4j", "password": "password"}
)
```

#### 2. Add Entities
```python
# Add a company
await advanced_entity_graph.add_entity(
    entity_id="COMPANY_001",
    node_type=NodeType.COMPANY,
    properties={
        "name": "Example Corp",
        "registration_number": "12345678",
        "status": "active",
        "industry": "Technology"
    },
    confidence=0.95,
    data_sources=["companies_house", "manual_entry"]
)

# Add a person
await advanced_entity_graph.add_entity(
    entity_id="PERSON_001", 
    node_type=NodeType.PERSON,
    properties={
        "name": "John Smith",
        "title": "CEO",
        "nationality": "UK"
    }
)
```

#### 3. Add Relationships
```python
# Add ownership relationship
await advanced_entity_graph.add_relationship(
    source_id="PERSON_001",
    target_id="COMPANY_001", 
    relationship_type=RelationshipType.HAS_OFFICER,
    properties={"title": "Chief Executive Officer", "appointment_date": "2020-01-01"},
    confidence=0.98
)
```

#### 4. Run Analytics
```python
# Comprehensive analytics
analytics = await advanced_entity_graph.perform_analytics()

# Access results
centrality_scores = analytics.centrality_measures
communities = analytics.community_detection
anomalies = analytics.anomalies
```

### Advanced Queries

#### Circular Ownership Detection
```cypher
MATCH path = (c1:COMPANY)-[:OWNS*2..5]->(c1)
WHERE c1.entity_id = $entity_id
RETURN path
```

#### Ultimate Beneficial Owner
```cypher
MATCH path = (start:COMPANY)-[:OWNS*]->(end:PERSON)
WHERE start.entity_id = $entity_id
AND NOT (end)-[:OWNS]->()
RETURN path ORDER BY length(path) DESC LIMIT 10
```

#### Directors in Common
```cypher
MATCH (p:PERSON)-[:HAS_OFFICER]->(c1:COMPANY)
MATCH (p)-[:HAS_OFFICER]->(c2:COMPANY)
WHERE c1 <> c2 AND c1.entity_id = $entity_id
RETURN p, c1, c2
```

#### Shell Company Detection
```cypher
MATCH (c:COMPANY)
WHERE c.entity_id = $entity_id
OPTIONAL MATCH (c)-[:HAS_OFFICER]->(officers)
OPTIONAL MATCH (c)-[:REGISTERED_AT]->(addr:ADDRESS)
WITH c, count(officers) as officer_count, collect(addr) as addresses
WHERE officer_count <= 1 OR size(addresses) = 0
RETURN c, officer_count, addresses
```

### GUI Usage

#### 1. Launch the Application
```bash
python -m gui.main
```

#### 2. Navigate to Entity Graphs Tab
- Select the "Entity Graphs" tab in the main interface
- Configure database connection using the dropdown menu
- Click "Connect" to establish connection

#### 3. Entity Management
- Use "Add Entity" button to create new entities
- Fill in entity details: ID, type, properties, confidence level
- Use "Add Relationship" to connect entities

#### 4. Analytics Operations
- Click "Run Full Analytics" for comprehensive analysis
- Use quick analytics buttons for specific measures:
  - **Centrality**: Calculate importance scores
  - **Communities**: Detect clusters and groups
  - **Anomalies**: Find unusual patterns
  - **Temporal**: Analyze time-based trends

#### 5. Visualization
- Select layout algorithm: Spring, Circular, Hierarchical
- Choose color scheme: Node Type, Centrality, Confidence
- Toggle labels and adjust display options
- Interactive graph with zoom, pan, and selection

#### 6. Query Interface
- Select from pre-built query templates
- Enter custom Cypher queries
- Provide parameters in JSON format
- View results in structured format

### Data Integration

#### Automatic Synchronization
```python
from gui.components.data_integration_bridge import data_integration_bridge

# Initialize integration
await data_integration_bridge.initialize_integration()

# Sync entities from database to graph
sync_results = await data_integration_bridge.sync_entities_to_graph()

# Sync quality assessments
await data_integration_bridge.sync_quality_assessments_to_graph()

# Sync provenance information  
await data_integration_bridge.sync_provenance_to_graph()
```

#### Quality-Aware Analytics
```python
# Identify duplicates using graph analytics
duplicates = await data_integration_bridge.identify_entity_duplicates()

# Create relationships based on data quality patterns
relationship_count = await data_integration_bridge.create_quality_based_relationships()

# Get integration status
status = await data_integration_bridge.get_integration_status()
```

## Analytics Features

### Centrality Measures
- **Degree Centrality**: Number of direct connections
- **Betweenness Centrality**: Bridge between other nodes
- **Closeness Centrality**: Average distance to all other nodes
- **Eigenvector Centrality**: Influence based on connections' importance
- **PageRank**: Google's algorithm adapted for business networks

### Community Detection
- **Louvain Algorithm**: Modularity optimization
- **Leiden Algorithm**: Improved modularity optimization
- **Greedy Modularity**: Fast community detection
- **Label Propagation**: Network-based clustering

### Anomaly Detection
- **High Degree Nodes**: Entities with unusually many connections
- **Isolated Components**: Disconnected network segments
- **Sink/Source Nodes**: Unusual in/out connection patterns
- **Statistical Outliers**: Nodes deviating from network norms

### Temporal Analysis
- **Node Creation Timeline**: Entity addition patterns over time
- **Relationship Evolution**: How connections change over time
- **Growth Metrics**: Network expansion statistics
- **Activity Patterns**: Temporal clustering of events

## Visualization

### Layout Algorithms
- **Spring Layout**: Force-directed positioning
- **Circular Layout**: Nodes arranged in circles
- **Hierarchical Layout**: Tree-like structure
- **Fruchterman-Reingold**: Balanced force-directed layout
- **Kamada-Kawai**: Distance-based positioning

### Color Schemes
- **Node Type**: Different colors for entity types
- **Centrality**: Color intensity based on importance
- **Confidence**: Color saturation based on data confidence
- **Community**: Different colors for detected communities
- **Temporal**: Colors based on creation time

### Interactive Features
- **Zoom and Pan**: Navigate large graphs
- **Node Selection**: Click to highlight connections
- **Hover Information**: Detailed entity properties
- **Edge Filtering**: Show/hide relationship types
- **Export Options**: Save as PNG, SVG, or HTML

## Performance Optimization

### Memory Management
- **Node Limit**: Configure maximum nodes in memory
- **Lazy Loading**: Load graph data on demand
- **Caching**: Cache analytics results
- **Incremental Updates**: Only process changed data

### Database Optimization
- **Indexing**: Proper database indexes for fast queries
- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Group multiple operations
- **Query Optimization**: Efficient Cypher queries

### Visualization Performance
- **Level of Detail**: Simplify display for large graphs
- **Pagination**: Break large graphs into pages
- **WebGL Rendering**: Hardware-accelerated graphics
- **Data Reduction**: Aggregate less important nodes

## Troubleshooting

### Common Issues

#### 1. Installation Problems
```bash
# Missing system dependencies
sudo apt-get install graphviz graphviz-dev

# Python package conflicts
pip install --upgrade pip
pip install --force-reinstall networkx
```

#### 2. Database Connection Issues
```python
# Test Neo4j connection
from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))
print(graph.run("RETURN 1").data())
```

#### 3. Memory Issues
```json
{
  "graph_system": {
    "max_nodes_in_memory": 5000,
    "enable_caching": false
  }
}
```

#### 4. Performance Issues
- Reduce node display limit
- Use simpler layout algorithms
- Enable data pagination
- Optimize database queries

### Logging and Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system status
status = await advanced_entity_graph.get_integration_status()
print(json.dumps(status, indent=2))
```

## API Reference

### Core Classes

#### AdvancedEntityGraphSystem
Main system class for graph operations.

```python
class AdvancedEntityGraphSystem:
    async def initialize(database_type, connection_config)
    async def add_entity(entity_id, node_type, properties, confidence, data_sources)
    async def add_relationship(source_id, target_id, relationship_type, properties, confidence)
    async def perform_analytics()
    async def query_graph(query, parameters)
    def create_visualization(layout, color_by, show_labels)
```

#### GraphAnalyticsEngine
Analytics and machine learning operations.

```python
class GraphAnalyticsEngine:
    async def calculate_centrality_measures(node_ids)
    async def detect_communities()
    async def find_shortest_paths(source, target)
    async def detect_anomalies()
    async def temporal_analysis(time_window_days)
```

#### GraphQueryEngine
Query execution and template management.

```python
class GraphQueryEngine:
    async def execute_template_query(template_name, parameters)
    async def find_circular_ownership(entity_id, max_depth)
    async def find_directors_in_common(entity_id)
    async def find_ultimate_beneficial_owners(entity_id)
    async def detect_shell_companies(entity_id)
```

### Data Models

#### EntityNode
```python
@dataclass
class EntityNode:
    entity_id: str
    node_type: NodeType
    properties: Dict[str, Any]
    coordinates: Tuple[float, float, float]
    creation_time: datetime
    confidence: float
    data_sources: List[str]
    metadata: Dict[str, Any]
```

#### EntityRelationship
```python
@dataclass
class EntityRelationship:
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any]
    confidence: float
    created_at: datetime
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    data_sources: List[str]
    metadata: Dict[str, Any]
```

## Best Practices

### Data Quality
1. **Always set confidence levels** for entities and relationships
2. **Include data sources** for traceability
3. **Use standardized entity IDs** across systems
4. **Regularly validate data** using quality assessments
5. **Monitor for duplicates** and resolve conflicts

### Performance
1. **Limit graph size** for interactive visualization
2. **Use appropriate database** for your scale (NetworkX < 10K nodes, Neo4j > 10K nodes)
3. **Cache analytics results** for frequently accessed data
4. **Implement incremental updates** for large datasets
5. **Optimize queries** using database-specific features

### Security
1. **Secure database connections** with proper authentication
2. **Validate user inputs** in queries and parameters
3. **Implement access controls** for sensitive data
4. **Audit graph modifications** for compliance
5. **Encrypt sensitive data** in properties

### Visualization
1. **Choose appropriate layouts** for your network structure
2. **Use meaningful colors** and sizes for encoding
3. **Provide interactive controls** for exploration
4. **Include export options** for reporting
5. **Optimize for different screen sizes**

## Contributing

### Development Setup
```bash
git clone <repository>
cd business-intel-scraper
pip install -e .
python setup_graph_system.py --optional
```

### Adding New Features
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request

### Testing
```bash
# Run all tests
python -m pytest tests/test_advanced_entity_graph.py

# Run specific test
python -m pytest tests/test_analytics_engine.py::test_centrality_measures
```

## Roadmap

### Version 2.0 (Planned)
- [ ] Real-time graph streaming
- [ ] Advanced ML models (GCN, GraphSAGE)
- [ ] Multi-language support
- [ ] Advanced security features
- [ ] Cloud deployment options

### Version 2.1 (Future)
- [ ] Blockchain integration
- [ ] IoT device tracking
- [ ] Advanced temporal queries
- [ ] Graph diff and versioning
- [ ] Mobile app support

## Support

### Documentation
- System Architecture: `docs/architecture.md`
- API Reference: `docs/api_reference.md`
- Configuration Guide: `docs/configuration.md`

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share use cases
- Wiki: Community-contributed documentation

### Commercial Support
- Professional services available
- Custom development and integration
- Training and consulting
