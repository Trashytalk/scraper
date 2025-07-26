"""
Data Integration Bridge

Connects the Data Quality & Provenance Intelligence system with the
Advanced Entity Graph System for comprehensive business intelligence analysis.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    from sqlalchemy.orm import Session
    from sqlalchemy import and_, or_, desc

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Import our systems
try:
    from .advanced_entity_graph import (
        AdvancedEntityGraphSystem,
        NodeType,
        RelationshipType,
        EntityNode,
        EntityRelationship,
        advanced_entity_graph,
    )
    from .data_quality_engine import DataQualityEngine, data_quality_engine
    from business_intel_scraper.backend.db.quality_models import (
        EntityRecord,
        ProvenanceRecord,
        DataSource,
        QualityAssessment,
    )
    from business_intel_scraper.backend.db.models import Company, Location, User
except ImportError:
    # Handle import errors gracefully
    pass

logger = logging.getLogger(__name__)


@dataclass
class IntegrationMapping:
    """Mapping between database entities and graph nodes"""

    db_table: str
    db_id_field: str
    graph_node_type: NodeType
    property_mappings: Dict[str, str]  # db_field -> graph_property
    confidence_field: Optional[str] = None
    data_source_field: Optional[str] = None


class DataIntegrationBridge:
    """Bridge between data quality system and entity graph system"""

    def __init__(self):
        self.graph_system = advanced_entity_graph
        self.quality_engine = data_quality_engine
        self.entity_mappings = self._create_entity_mappings()
        self.sync_enabled = True
        self.auto_sync_interval = 300  # 5 minutes
        self._sync_timer = None

    def _create_entity_mappings(self) -> Dict[str, IntegrationMapping]:
        """Create mappings between database entities and graph nodes"""
        return {
            "company": IntegrationMapping(
                db_table="companies",
                db_id_field="id",
                graph_node_type=NodeType.COMPANY,
                property_mappings={
                    "name": "name",
                    "registration_number": "registration_number",
                    "status": "status",
                    "industry": "industry",
                    "website": "website",
                    "incorporation_date": "incorporation_date",
                    "description": "description",
                },
                confidence_field="data_confidence",
                data_source_field="data_source",
            ),
            "location": IntegrationMapping(
                db_table="locations",
                db_id_field="id",
                graph_node_type=NodeType.ADDRESS,
                property_mappings={
                    "address": "address",
                    "city": "city",
                    "state": "state",
                    "country": "country",
                    "postal_code": "postal_code",
                    "latitude": "latitude",
                    "longitude": "longitude",
                },
            ),
            "user": IntegrationMapping(
                db_table="users",
                db_id_field="id",
                graph_node_type=NodeType.PERSON,
                property_mappings={
                    "username": "username",
                    "email": "email",
                    "role": "role",
                    "first_name": "first_name",
                    "last_name": "last_name",
                },
            ),
        }

    async def initialize_integration(self) -> bool:
        """Initialize the integration bridge"""
        try:
            # Ensure both systems are initialized
            if not self.graph_system.connector:
                graph_init = await self.graph_system.initialize()
                if not graph_init:
                    logger.error("Failed to initialize graph system")
                    return False

            # Start auto-sync if enabled
            if self.sync_enabled:
                self.start_auto_sync()

            logger.info("Data integration bridge initialized")
            return True

        except Exception as e:
            logger.error(f"Error initializing integration bridge: {e}")
            return False

    async def sync_entities_to_graph(
        self, entity_types: List[str] = None
    ) -> Dict[str, int]:
        """Sync database entities to the graph system"""
        if not SQLALCHEMY_AVAILABLE:
            logger.warning("SQLAlchemy not available for entity sync")
            return {}

        sync_results = {}
        entity_types = entity_types or list(self.entity_mappings.keys())

        try:
            from business_intel_scraper.backend.db.utils import get_db_session

            with get_db_session() as session:
                for entity_type in entity_types:
                    if entity_type not in self.entity_mappings:
                        continue

                    mapping = self.entity_mappings[entity_type]
                    synced_count = await self._sync_entity_type(
                        session, entity_type, mapping
                    )
                    sync_results[entity_type] = synced_count

                    logger.info(
                        f"Synced {synced_count} {entity_type} entities to graph"
                    )

            # Sync relationships
            relationship_count = await self._sync_relationships(session)
            sync_results["relationships"] = relationship_count

            return sync_results

        except Exception as e:
            logger.error(f"Error syncing entities to graph: {e}")
            return {}

    async def _sync_entity_type(
        self, session: Session, entity_type: str, mapping: IntegrationMapping
    ) -> int:
        """Sync a specific entity type to the graph"""
        synced_count = 0

        try:
            # Get the appropriate model class
            model_class = self._get_model_class(entity_type)
            if not model_class:
                return 0

            # Query entities
            query = session.query(model_class)
            entities = query.all()

            for entity in entities:
                entity_id = f"{entity_type}_{getattr(entity, mapping.db_id_field)}"

                # Build properties from mapping
                properties = {}
                for db_field, graph_property in mapping.property_mappings.items():
                    value = getattr(entity, db_field, None)
                    if value is not None:
                        # Convert datetime objects to ISO strings
                        if isinstance(value, datetime):
                            value = value.isoformat()
                        properties[graph_property] = value

                # Get confidence level
                confidence = 1.0
                if mapping.confidence_field and hasattr(
                    entity, mapping.confidence_field
                ):
                    confidence = getattr(entity, mapping.confidence_field, 1.0)

                # Get data sources
                data_sources = []
                if mapping.data_source_field and hasattr(
                    entity, mapping.data_source_field
                ):
                    source = getattr(entity, mapping.data_source_field)
                    if source:
                        data_sources.append(source)

                # Add to graph
                success = await self.graph_system.add_entity(
                    entity_id=entity_id,
                    node_type=mapping.graph_node_type,
                    properties=properties,
                    confidence=confidence,
                    data_sources=data_sources,
                )

                if success:
                    synced_count += 1

            return synced_count

        except Exception as e:
            logger.error(f"Error syncing {entity_type} entities: {e}")
            return 0

    async def _sync_relationships(self, session: Session) -> int:
        """Sync relationships between entities"""
        relationship_count = 0

        try:
            # Get companies and their related entities
            from business_intel_scraper.backend.db.models import Company

            companies = session.query(Company).all()

            for company in companies:
                company_id = f"company_{company.id}"

                # Company -> Location relationships (if exists)
                if hasattr(company, "location_id") and company.location_id:
                    location_id = f"location_{company.location_id}"

                    success = await self.graph_system.add_relationship(
                        source_id=company_id,
                        target_id=location_id,
                        relationship_type=RelationshipType.REGISTERED_AT,
                        properties={"relationship_source": "database_sync"},
                        confidence=0.9,
                    )

                    if success:
                        relationship_count += 1

                # Add more relationship types as needed
                # Company -> User (officers, directors, etc.)
                # Company -> Company (subsidiaries, partnerships, etc.)

            return relationship_count

        except Exception as e:
            logger.error(f"Error syncing relationships: {e}")
            return 0

    def _get_model_class(self, entity_type: str):
        """Get the SQLAlchemy model class for an entity type"""
        try:
            if entity_type == "company":
                from business_intel_scraper.backend.db.models import Company

                return Company
            elif entity_type == "location":
                from business_intel_scraper.backend.db.models import Location

                return Location
            elif entity_type == "user":
                from business_intel_scraper.backend.db.models import User

                return User
            else:
                return None
        except ImportError:
            return None

    async def sync_quality_assessments_to_graph(self) -> int:
        """Sync data quality assessments to graph node properties"""
        if not SQLALCHEMY_AVAILABLE:
            return 0

        try:
            from business_intel_scraper.backend.db.utils import get_db_session
            from business_intel_scraper.backend.db.quality_models import (
                QualityAssessment,
            )

            with get_db_session() as session:
                assessments = session.query(QualityAssessment).all()
                updated_count = 0

                for assessment in assessments:
                    # Map assessment to graph entity
                    entity_id = f"{assessment.entity_type}_{assessment.entity_id}"

                    # Update graph node with quality information
                    if hasattr(self.graph_system.connector, "nodes_data"):
                        nodes_data = self.graph_system.connector.nodes_data
                        if entity_id in nodes_data:
                            node = nodes_data[entity_id]

                            # Add quality metadata
                            node.metadata.update(
                                {
                                    "quality_score": assessment.quality_score,
                                    "completeness_score": assessment.completeness_score,
                                    "accuracy_score": assessment.accuracy_score,
                                    "consistency_score": assessment.consistency_score,
                                    "timeliness_score": assessment.timeliness_score,
                                    "last_quality_check": assessment.assessment_date.isoformat(),
                                    "quality_issues": assessment.issues or [],
                                }
                            )

                            updated_count += 1

                logger.info(
                    f"Updated {updated_count} graph nodes with quality assessments"
                )
                return updated_count

        except Exception as e:
            logger.error(f"Error syncing quality assessments: {e}")
            return 0

    async def sync_provenance_to_graph(self) -> int:
        """Sync provenance information to graph relationships"""
        if not SQLALCHEMY_AVAILABLE:
            return 0

        try:
            from business_intel_scraper.backend.db.utils import get_db_session
            from business_intel_scraper.backend.db.quality_models import (
                ProvenanceRecord,
            )

            with get_db_session() as session:
                provenance_records = session.query(ProvenanceRecord).all()
                updated_count = 0

                for record in provenance_records:
                    # Create provenance relationships
                    entity_id = f"{record.entity_type}_{record.entity_id}"
                    source_id = f"source_{record.source_id}"

                    # Add source entity if not exists
                    await self.graph_system.add_entity(
                        entity_id=source_id,
                        node_type=NodeType.DOCUMENT,
                        properties={
                            "source_type": record.source_type,
                            "source_identifier": record.source_identifier,
                            "collection_method": record.collection_method,
                        },
                        confidence=0.8,
                        data_sources=["provenance_sync"],
                    )

                    # Add provenance relationship
                    success = await self.graph_system.add_relationship(
                        source_id=source_id,
                        target_id=entity_id,
                        relationship_type=RelationshipType.LINKED_TO,
                        properties={
                            "provenance_type": "data_source",
                            "transformation_applied": record.transformation_applied,
                            "lineage_path": record.lineage_path,
                        },
                        confidence=0.9,
                        valid_from=record.created_at,
                        data_sources=["provenance_tracking"],
                    )

                    if success:
                        updated_count += 1

                logger.info(f"Created {updated_count} provenance relationships")
                return updated_count

        except Exception as e:
            logger.error(f"Error syncing provenance information: {e}")
            return 0

    async def identify_entity_duplicates(self) -> List[Dict[str, Any]]:
        """Use graph analytics to identify potential duplicate entities"""
        if not self.graph_system.analytics_engine:
            return []

        try:
            # Run analytics to find similar entities
            analytics = await self.graph_system.perform_analytics()

            duplicates = []

            # Analyze nodes for similar properties
            if hasattr(self.graph_system.connector, "nodes_data"):
                nodes_data = self.graph_system.connector.nodes_data

                # Group nodes by type
                nodes_by_type = {}
                for node_id, node in nodes_data.items():
                    node_type = node.node_type.value
                    if node_type not in nodes_by_type:
                        nodes_by_type[node_type] = []
                    nodes_by_type[node_type].append(node)

                # Find potential duplicates within each type
                for node_type, nodes in nodes_by_type.items():
                    for i, node1 in enumerate(nodes):
                        for j, node2 in enumerate(nodes[i + 1 :], i + 1):
                            similarity_score = self._calculate_entity_similarity(
                                node1, node2
                            )

                            if similarity_score > 0.8:  # High similarity threshold
                                duplicates.append(
                                    {
                                        "entity1_id": node1.entity_id,
                                        "entity2_id": node2.entity_id,
                                        "entity_type": node_type,
                                        "similarity_score": similarity_score,
                                        "matching_properties": self._get_matching_properties(
                                            node1, node2
                                        ),
                                        "recommended_action": (
                                            "merge"
                                            if similarity_score > 0.9
                                            else "review"
                                        ),
                                    }
                                )

            logger.info(f"Identified {len(duplicates)} potential duplicate entities")
            return duplicates

        except Exception as e:
            logger.error(f"Error identifying entity duplicates: {e}")
            return []

    def _calculate_entity_similarity(
        self, node1: EntityNode, node2: EntityNode
    ) -> float:
        """Calculate similarity score between two entities"""
        if node1.node_type != node2.node_type:
            return 0.0

        # Compare properties
        props1 = node1.properties
        props2 = node2.properties

        if not props1 or not props2:
            return 0.0

        common_props = set(props1.keys()) & set(props2.keys())
        if not common_props:
            return 0.0

        matches = 0
        for prop in common_props:
            val1 = str(props1[prop]).lower().strip()
            val2 = str(props2[prop]).lower().strip()

            if val1 == val2:
                matches += 1
            elif self._strings_similar(val1, val2):
                matches += 0.5

        return matches / len(common_props)

    def _strings_similar(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Check if two strings are similar using simple comparison"""
        if not str1 or not str2:
            return False

        # Simple similarity check - could be enhanced with fuzzy matching
        shorter = min(len(str1), len(str2))
        longer = max(len(str1), len(str2))

        if longer == 0:
            return True

        # Check if one string is contained in the other
        if str1 in str2 or str2 in str1:
            return True

        # Check character overlap
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        overlap = len(set1 & set2) / len(set1 | set2)

        return overlap >= threshold

    def _get_matching_properties(
        self, node1: EntityNode, node2: EntityNode
    ) -> List[str]:
        """Get list of matching properties between two nodes"""
        props1 = node1.properties
        props2 = node2.properties

        matching = []
        common_props = set(props1.keys()) & set(props2.keys())

        for prop in common_props:
            val1 = str(props1[prop]).lower().strip()
            val2 = str(props2[prop]).lower().strip()

            if val1 == val2 or self._strings_similar(val1, val2):
                matching.append(prop)

        return matching

    async def create_quality_based_relationships(self) -> int:
        """Create relationships based on data quality patterns"""
        relationship_count = 0

        try:
            # Find entities with similar data sources
            if hasattr(self.graph_system.connector, "nodes_data"):
                nodes_data = self.graph_system.connector.nodes_data

                # Group by data sources
                source_groups = {}
                for node_id, node in nodes_data.items():
                    for source in node.data_sources:
                        if source not in source_groups:
                            source_groups[source] = []
                        source_groups[source].append(node_id)

                # Create relationships between entities from same source
                for source, entity_ids in source_groups.items():
                    if len(entity_ids) > 1:
                        for i, entity1 in enumerate(entity_ids):
                            for entity2 in entity_ids[i + 1 :]:
                                success = await self.graph_system.add_relationship(
                                    source_id=entity1,
                                    target_id=entity2,
                                    relationship_type=RelationshipType.RELATED_TO,
                                    properties={
                                        "relationship_basis": "common_data_source",
                                        "common_source": source,
                                    },
                                    confidence=0.6,
                                )

                                if success:
                                    relationship_count += 1

            logger.info(f"Created {relationship_count} quality-based relationships")
            return relationship_count

        except Exception as e:
            logger.error(f"Error creating quality-based relationships: {e}")
            return 0

    def start_auto_sync(self):
        """Start automatic synchronization"""
        if self._sync_timer:
            self._sync_timer.cancel()

        self._sync_timer = asyncio.create_task(self._auto_sync_loop())
        logger.info("Started auto-sync for data integration")

    def stop_auto_sync(self):
        """Stop automatic synchronization"""
        if self._sync_timer:
            self._sync_timer.cancel()
            self._sync_timer = None

        logger.info("Stopped auto-sync for data integration")

    async def _auto_sync_loop(self):
        """Auto-sync loop"""
        while self.sync_enabled:
            try:
                await asyncio.sleep(self.auto_sync_interval)

                # Perform incremental sync
                sync_results = await self.sync_entities_to_graph()
                await self.sync_quality_assessments_to_graph()
                await self.sync_provenance_to_graph()

                logger.info(f"Auto-sync completed: {sync_results}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-sync loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        status = {
            "graph_system_connected": bool(
                self.graph_system.connector and self.graph_system.connector.connected
            ),
            "auto_sync_enabled": self.sync_enabled,
            "auto_sync_interval": self.auto_sync_interval,
            "entity_mappings": list(self.entity_mappings.keys()),
            "last_sync_time": None,  # Could be tracked
            "sync_statistics": {},
        }

        # Get graph statistics
        if hasattr(self.graph_system.connector, "nodes_data"):
            nodes_data = self.graph_system.connector.nodes_data
            relationships_data = getattr(
                self.graph_system.connector, "relationships_data", {}
            )

            status["sync_statistics"] = {
                "total_nodes": len(nodes_data),
                "total_relationships": len(relationships_data),
                "nodes_by_type": {},
            }

            # Count nodes by type
            for node in nodes_data.values():
                node_type = node.node_type.value
                status["sync_statistics"]["nodes_by_type"][node_type] = (
                    status["sync_statistics"]["nodes_by_type"].get(node_type, 0) + 1
                )

        return status


# Global integration bridge instance
data_integration_bridge = DataIntegrationBridge()
