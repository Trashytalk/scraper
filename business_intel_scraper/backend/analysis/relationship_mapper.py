"""
Advanced Relationship Mapping and Graph Construction

Builds comprehensive graphs linking entities through various relationship types:
- Officer/director relationships
- Shared addresses and locations  
- Corporate structure (parent/subsidiary)
- Shared domains, emails, phone numbers
- Contract relationships
- Network analysis and community detection
"""

import asyncio
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any, Union
import networkx as nx
import numpy as np
from sklearn.cluster import DBSCAN
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

@dataclass
class EntityRelationship:
    """Container for entity relationships"""
    relationship_id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    relationship_subtype: Optional[str]
    relationship_data: Dict[str, Any]
    confidence_score: float
    evidence_sources: List[str]
    strength: float = 1.0
    is_directional: bool = True
    semantic_role: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class EntityRelationshipMapper:
    """Advanced relationship mapping and graph construction"""
    
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
        # Graph for relationship analysis
        self.relationship_graph = nx.MultiDiGraph()
        
        # Relationship extraction patterns
        self.relationship_patterns = self._load_relationship_patterns()
        
        # Relationship type weights for importance scoring
        self.relationship_weights = self._load_relationship_weights()
        
        # Performance metrics
        self.mapping_metrics = defaultdict(int)
    
    def _load_relationship_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting relationships"""
        return {
            'officer_patterns': [
                r'director', r'ceo', r'president', r'secretary', r'treasurer',
                r'chairman', r'managing director', r'chief executive', r'cfo',
                r'coo', r'cto', r'founder', r'partner', r'manager', r'vice president',
                r'board member', r'executive', r'officer'
            ],
            'ownership_patterns': [
                r'owns', r'subsidiary', r'parent company', r'holding company',
                r'joint venture', r'partnership', r'affiliate', r'division',
                r'branch', r'unit', r'controlled by', r'acquired by'
            ],
            'address_patterns': [
                r'registered office', r'business address', r'mailing address',
                r'corporate office', r'headquarters', r'principal place',
                r'registered address', r'business location'
            ],
            'contract_patterns': [
                r'vendor', r'supplier', r'contractor', r'client', r'customer',
                r'service provider', r'consultant', r'partner', r'distributor'
            ],
            'family_patterns': [
                r'spouse', r'married to', r'child of', r'parent of', r'sibling',
                r'family member', r'relative', r'heir', r'beneficiary'
            ]
        }
    
    def _load_relationship_weights(self) -> Dict[str, float]:
        """Load importance weights for different relationship types"""
        return {
            'IS_OFFICER_OF': 0.9,
            'IS_DIRECTOR_OF': 0.95,
            'IS_CEO_OF': 1.0,
            'IS_OWNER_OF': 1.0,
            'IS_SUBSIDIARY_OF': 0.95,
            'IS_PARENT_OF': 0.95,
            'SHARES_ADDRESS': 0.7,
            'SHARES_PHONE': 0.6,
            'SHARES_EMAIL_DOMAIN': 0.5,
            'SHARES_WEBSITE_DOMAIN': 0.8,
            'HAS_CONTRACT_WITH': 0.4,
            'IS_COMPETITOR_OF': 0.3,
            'IS_FAMILY_MEMBER_OF': 0.6,
            'IS_ASSOCIATED_WITH': 0.3
        }
    
    async def map_relationships(self, entities: List[Dict], 
                              raw_data_sources: List[Dict]) -> List[EntityRelationship]:
        """Extract and map relationships between entities"""
        relationships = []
        
        logger.info(f"Starting relationship mapping for {len(entities)} entities")
        
        # Extract different types of relationships
        officer_rels = await self._extract_officer_relationships(entities, raw_data_sources)
        relationships.extend(officer_rels)
        logger.info(f"Extracted {len(officer_rels)} officer relationships")
        
        ownership_rels = await self._extract_ownership_relationships(entities, raw_data_sources)
        relationships.extend(ownership_rels)
        logger.info(f"Extracted {len(ownership_rels)} ownership relationships")
        
        address_rels = await self._extract_address_relationships(entities)
        relationships.extend(address_rels)
        logger.info(f"Extracted {len(address_rels)} address relationships")
        
        contact_rels = await self._extract_contact_relationships(entities)
        relationships.extend(contact_rels)
        logger.info(f"Extracted {len(contact_rels)} contact relationships")
        
        domain_rels = await self._extract_domain_relationships(entities)
        relationships.extend(domain_rels)
        logger.info(f"Extracted {len(domain_rels)} domain relationships")
        
        contract_rels = await self._extract_contract_relationships(entities, raw_data_sources)
        relationships.extend(contract_rels)
        logger.info(f"Extracted {len(contract_rels)} contract relationships")
        
        # Store relationships
        await self._store_relationships(relationships)
        
        # Update relationship graph
        self._update_relationship_graph(relationships)
        
        logger.info(f"Total relationships mapped: {len(relationships)}")
        self.mapping_metrics['total_relationships'] += len(relationships)
        
        return relationships
    
    async def _extract_officer_relationships(self, entities: List[Dict], 
                                           raw_data_sources: List[Dict]) -> List[EntityRelationship]:
        """Extract officer/director relationships"""
        relationships = []
        
        for entity in entities:
            if entity.get('type') == 'company' and 'officers' in entity:
                for officer in entity['officers']:
                    # Determine relationship type based on role
                    role = officer.get('role', '').lower()
                    relationship_type = self._classify_officer_role(role)
                    
                    relationship = EntityRelationship(
                        relationship_id=f"officer_{entity['entity_id']}_{officer.get('person_id', 'unknown')}_{hash(role)}",
                        source_entity_id=officer.get('person_id', f"person_{officer.get('name', 'unknown')}"),
                        target_entity_id=entity['entity_id'],
                        relationship_type=relationship_type,
                        relationship_subtype=officer.get('role'),
                        relationship_data={
                            'role': officer.get('role', 'Unknown'),
                            'appointed_date': officer.get('appointed_date'),
                            'resigned_date': officer.get('resigned_date'),
                            'status': officer.get('status', 'active'),
                            'nationality': officer.get('nationality'),
                            'occupation': officer.get('occupation')
                        },
                        confidence_score=self._calculate_officer_confidence(officer),
                        evidence_sources=[entity.get('source_url', '')],
                        strength=self.relationship_weights.get(relationship_type, 0.8),
                        valid_from=self._parse_date(officer.get('appointed_date')),
                        valid_to=self._parse_date(officer.get('resigned_date'))
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _classify_officer_role(self, role: str) -> str:
        """Classify officer role into standard relationship type"""
        role = role.lower()
        
        if any(word in role for word in ['ceo', 'chief executive']):
            return 'IS_CEO_OF'
        elif any(word in role for word in ['cfo', 'chief financial']):
            return 'IS_CFO_OF'
        elif any(word in role for word in ['cto', 'chief technology', 'chief technical']):
            return 'IS_CTO_OF'
        elif any(word in role for word in ['coo', 'chief operating']):
            return 'IS_COO_OF'
        elif any(word in role for word in ['director', 'board']):
            return 'IS_DIRECTOR_OF'
        elif any(word in role for word in ['president']):
            return 'IS_PRESIDENT_OF'
        elif any(word in role for word in ['chairman', 'chair']):
            return 'IS_CHAIRMAN_OF'
        elif any(word in role for word in ['secretary']):
            return 'IS_SECRETARY_OF'
        elif any(word in role for word in ['treasurer']):
            return 'IS_TREASURER_OF'
        elif any(word in role for word in ['founder']):
            return 'IS_FOUNDER_OF'
        else:
            return 'IS_OFFICER_OF'
    
    def _calculate_officer_confidence(self, officer: Dict) -> float:
        """Calculate confidence score for officer relationship"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on available data
        if officer.get('appointed_date'):
            confidence += 0.2
        if officer.get('role') and len(officer['role']) > 5:
            confidence += 0.2
        if officer.get('nationality'):
            confidence += 0.1
        if officer.get('status') == 'active':
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _extract_ownership_relationships(self, entities: List[Dict], 
                                             raw_data_sources: List[Dict]) -> List[EntityRelationship]:
        """Extract ownership and corporate structure relationships"""
        relationships = []
        
        for entity in entities:
            # Parent company relationships
            if 'parent_company' in entity and entity['parent_company']:
                relationship = EntityRelationship(
                    relationship_id=f"subsidiary_{entity['entity_id']}_{entity['parent_company']}",
                    source_entity_id=entity['parent_company'],
                    target_entity_id=entity['entity_id'],
                    relationship_type='IS_PARENT_OF',
                    relationship_subtype='subsidiary',
                    relationship_data={
                        'ownership_type': 'subsidiary',
                        'ownership_percentage': entity.get('ownership_percentage'),
                        'control_type': entity.get('control_type', 'direct')
                    },
                    confidence_score=0.9,
                    evidence_sources=[entity.get('source_url', '')],
                    strength=0.95
                )
                relationships.append(relationship)
            
            # Subsidiary relationships
            if 'subsidiaries' in entity:
                for subsidiary in entity['subsidiaries']:
                    relationship = EntityRelationship(
                        relationship_id=f"parent_{entity['entity_id']}_{subsidiary.get('entity_id')}",
                        source_entity_id=entity['entity_id'],
                        target_entity_id=subsidiary.get('entity_id'),
                        relationship_type='IS_PARENT_OF',
                        relationship_subtype='subsidiary',
                        relationship_data={
                            'ownership_percentage': subsidiary.get('ownership_percentage'),
                            'acquisition_date': subsidiary.get('acquisition_date'),
                            'control_type': subsidiary.get('control_type', 'direct')
                        },
                        confidence_score=0.9,
                        evidence_sources=[entity.get('source_url', '')],
                        strength=0.95,
                        valid_from=self._parse_date(subsidiary.get('acquisition_date'))
                    )
                    relationships.append(relationship)
            
            # Shareholder relationships
            if 'shareholders' in entity:
                for shareholder in entity['shareholders']:
                    ownership_pct = shareholder.get('percentage', 0)
                    relationship_type = 'IS_MAJOR_SHAREHOLDER_OF' if ownership_pct >= 10 else 'IS_SHAREHOLDER_OF'
                    
                    relationship = EntityRelationship(
                        relationship_id=f"shareholder_{shareholder.get('entity_id')}_{entity['entity_id']}",
                        source_entity_id=shareholder.get('entity_id'),
                        target_entity_id=entity['entity_id'],
                        relationship_type=relationship_type,
                        relationship_data={
                            'ownership_percentage': ownership_pct,
                            'share_class': shareholder.get('share_class'),
                            'voting_rights': shareholder.get('voting_rights')
                        },
                        confidence_score=0.85,
                        evidence_sources=[entity.get('source_url', '')],
                        strength=min(ownership_pct / 100.0 + 0.3, 1.0)  # Scale by ownership percentage
                    )
                    relationships.append(relationship)
        
        return relationships
    
    async def _extract_address_relationships(self, entities: List[Dict]) -> List[EntityRelationship]:
        """Extract shared address relationships"""
        relationships = []
        
        # Group entities by normalized address
        address_groups = defaultdict(list)
        for entity in entities:
            if 'normalized_address' in entity and entity['normalized_address']:
                address_groups[entity['normalized_address']].append(entity)
        
        # Create relationships for entities sharing addresses
        for address, entity_group in address_groups.items():
            if len(entity_group) > 1:
                for i in range(len(entity_group)):
                    for j in range(i + 1, len(entity_group)):
                        entity1, entity2 = entity_group[i], entity_group[j]
                        
                        # Calculate relationship strength based on address specificity
                        strength = self._calculate_address_strength(address, entity1, entity2)
                        
                        relationship = EntityRelationship(
                            relationship_id=f"shared_address_{entity1['entity_id']}_{entity2['entity_id']}",
                            source_entity_id=entity1['entity_id'],
                            target_entity_id=entity2['entity_id'],
                            relationship_type='SHARES_ADDRESS',
                            relationship_data={
                                'address': address,
                                'address_type': self._classify_address_type(address),
                                'full_address_match': entity1.get('address') == entity2.get('address')
                            },
                            confidence_score=strength,
                            evidence_sources=[],
                            strength=strength,
                            is_directional=False
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _calculate_address_strength(self, address: str, entity1: Dict, entity2: Dict) -> float:
        """Calculate strength of address relationship"""
        base_strength = 0.7
        
        # Boost for specific addresses (more tokens = more specific)
        tokens = len(address.split())
        if tokens >= 5:
            base_strength += 0.2
        elif tokens >= 3:
            base_strength += 0.1
        
        # Reduce strength for very common addresses or PO boxes
        if 'po box' in address.lower() or 'p.o. box' in address.lower():
            base_strength -= 0.3
        
        # Consider entity types - same type sharing address is more significant
        if entity1.get('type') == entity2.get('type'):
            base_strength += 0.1
        
        return min(max(base_strength, 0.1), 1.0)
    
    def _classify_address_type(self, address: str) -> str:
        """Classify address type"""
        address_lower = address.lower()
        
        if 'po box' in address_lower or 'p.o. box' in address_lower:
            return 'po_box'
        elif any(word in address_lower for word in ['suite', 'floor', 'unit', 'apt']):
            return 'office'
        elif any(word in address_lower for word in ['registered', 'corporate']):
            return 'registered'
        else:
            return 'business'
    
    async def _extract_contact_relationships(self, entities: List[Dict]) -> List[EntityRelationship]:
        """Extract shared contact information relationships"""
        relationships = []
        
        # Phone number relationships
        phone_groups = defaultdict(list)
        for entity in entities:
            if 'normalized_phone' in entity and entity['normalized_phone']:
                phone_groups[entity['normalized_phone']].append(entity)
        
        for phone, entity_group in phone_groups.items():
            if len(entity_group) > 1:
                for i in range(len(entity_group)):
                    for j in range(i + 1, len(entity_group)):
                        entity1, entity2 = entity_group[i], entity_group[j]
                        
                        relationship = EntityRelationship(
                            relationship_id=f"shared_phone_{entity1['entity_id']}_{entity2['entity_id']}",
                            source_entity_id=entity1['entity_id'],
                            target_entity_id=entity2['entity_id'],
                            relationship_type='SHARES_PHONE',
                            relationship_data={
                                'phone_number': phone,
                                'phone_type': 'business'  # Could be enhanced to detect type
                            },
                            confidence_score=0.8,
                            evidence_sources=[],
                            strength=0.6,
                            is_directional=False
                        )
                        relationships.append(relationship)
        
        return relationships
    
    async def _extract_domain_relationships(self, entities: List[Dict]) -> List[EntityRelationship]:
        """Extract domain and website relationships"""
        relationships = []
        
        # Email domain relationships
        email_domain_groups = defaultdict(list)
        for entity in entities:
            if 'email_domain' in entity and entity['email_domain']:
                email_domain_groups[entity['email_domain']].append(entity)
        
        for domain, entity_group in email_domain_groups.items():
            if len(entity_group) > 1:
                for i in range(len(entity_group)):
                    for j in range(i + 1, len(entity_group)):
                        entity1, entity2 = entity_group[i], entity_group[j]
                        
                        relationship = EntityRelationship(
                            relationship_id=f"shared_email_domain_{entity1['entity_id']}_{entity2['entity_id']}",
                            source_entity_id=entity1['entity_id'],
                            target_entity_id=entity2['entity_id'],
                            relationship_type='SHARES_EMAIL_DOMAIN',
                            relationship_data={
                                'domain': domain,
                                'domain_type': 'email'
                            },
                            confidence_score=0.6,
                            evidence_sources=[],
                            strength=0.5,
                            is_directional=False
                        )
                        relationships.append(relationship)
        
        # Website domain relationships
        website_domain_groups = defaultdict(list)
        for entity in entities:
            if 'website_domain' in entity and entity['website_domain']:
                website_domain_groups[entity['website_domain']].append(entity)
        
        for domain, entity_group in website_domain_groups.items():
            if len(entity_group) > 1:
                for i in range(len(entity_group)):
                    for j in range(i + 1, len(entity_group)):
                        entity1, entity2 = entity_group[i], entity_group[j]
                        
                        relationship = EntityRelationship(
                            relationship_id=f"shared_website_domain_{entity1['entity_id']}_{entity2['entity_id']}",
                            source_entity_id=entity1['entity_id'],
                            target_entity_id=entity2['entity_id'],
                            relationship_type='SHARES_WEBSITE_DOMAIN',
                            relationship_data={
                                'domain': domain,
                                'domain_type': 'website'
                            },
                            confidence_score=0.9,
                            evidence_sources=[],
                            strength=0.8,
                            is_directional=False
                        )
                        relationships.append(relationship)
        
        return relationships
    
    async def _extract_contract_relationships(self, entities: List[Dict], 
                                            raw_data_sources: List[Dict]) -> List[EntityRelationship]:
        """Extract contract and business relationships from raw data"""
        relationships = []
        
        # This would analyze raw data sources for contract relationships
        # For now, we'll extract from entity data if available
        
        for entity in entities:
            # Vendor/supplier relationships
            if 'vendors' in entity:
                for vendor in entity['vendors']:
                    relationship = EntityRelationship(
                        relationship_id=f"vendor_{vendor.get('entity_id')}_{entity['entity_id']}",
                        source_entity_id=vendor.get('entity_id'),
                        target_entity_id=entity['entity_id'],
                        relationship_type='IS_VENDOR_OF',
                        relationship_data={
                            'contract_value': vendor.get('contract_value'),
                            'contract_start': vendor.get('contract_start'),
                            'contract_end': vendor.get('contract_end'),
                            'service_type': vendor.get('service_type')
                        },
                        confidence_score=0.7,
                        evidence_sources=[entity.get('source_url', '')],
                        strength=0.4,
                        valid_from=self._parse_date(vendor.get('contract_start')),
                        valid_to=self._parse_date(vendor.get('contract_end'))
                    )
                    relationships.append(relationship)
            
            # Customer relationships
            if 'customers' in entity:
                for customer in entity['customers']:
                    relationship = EntityRelationship(
                        relationship_id=f"customer_{entity['entity_id']}_{customer.get('entity_id')}",
                        source_entity_id=entity['entity_id'],
                        target_entity_id=customer.get('entity_id'),
                        relationship_type='HAS_CUSTOMER',
                        relationship_data={
                            'contract_value': customer.get('contract_value'),
                            'relationship_start': customer.get('relationship_start'),
                            'customer_type': customer.get('customer_type')
                        },
                        confidence_score=0.7,
                        evidence_sources=[entity.get('source_url', '')],
                        strength=0.4
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _update_relationship_graph(self, relationships: List[EntityRelationship]):
        """Update the NetworkX graph with new relationships"""
        for rel in relationships:
            edge_data = {
                'relationship_type': rel.relationship_type,
                'relationship_subtype': rel.relationship_subtype,
                'relationship_data': rel.relationship_data,
                'confidence': rel.confidence_score,
                'strength': rel.strength,
                'is_directional': rel.is_directional,
                'created_at': rel.created_at,
                'evidence_sources': rel.evidence_sources
            }
            
            if rel.is_directional:
                self.relationship_graph.add_edge(
                    rel.source_entity_id,
                    rel.target_entity_id,
                    key=rel.relationship_type,
                    **edge_data
                )
            else:
                # Add both directions for non-directional relationships
                self.relationship_graph.add_edge(
                    rel.source_entity_id,
                    rel.target_entity_id,
                    key=rel.relationship_type,
                    **edge_data
                )
                self.relationship_graph.add_edge(
                    rel.target_entity_id,
                    rel.source_entity_id,
                    key=rel.relationship_type,
                    **edge_data
                )
    
    async def _store_relationships(self, relationships: List[EntityRelationship]):
        """Store relationships to database"""
        from ..storage.models import EntityRelationshipModel
        
        session = self.Session()
        
        try:
            for rel in relationships:
                db_rel = EntityRelationshipModel(
                    relationship_id=rel.relationship_id,
                    source_entity_id=rel.source_entity_id,
                    target_entity_id=rel.target_entity_id,
                    relationship_type=rel.relationship_type,
                    relationship_subtype=rel.relationship_subtype,
                    relationship_data=rel.relationship_data,
                    confidence=rel.confidence_score,
                    strength=rel.strength,
                    is_directional=rel.is_directional,
                    semantic_role=rel.semantic_role,
                    evidence_sources=rel.evidence_sources,
                    relationship_start_date=rel.valid_from,
                    relationship_end_date=rel.valid_to,
                    extractor_name='relationship_mapper',
                    extractor_version='1.0.0'
                )
                session.merge(db_rel)
            
            session.commit()
            logger.info(f"Stored {len(relationships)} relationships")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store relationships: {e}")
            raise
        finally:
            session.close()
    
    def analyze_entity_network(self, entity_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Analyze network around a specific entity"""
        if entity_id not in self.relationship_graph:
            return {'entity_id': entity_id, 'network': 'not_found'}
        
        # Get subgraph within specified depth
        subgraph_nodes = set([entity_id])
        current_depth = 0
        
        while current_depth < max_depth:
            current_nodes = list(subgraph_nodes)
            for node in current_nodes:
                if node in self.relationship_graph:
                    # Add neighbors
                    neighbors = list(self.relationship_graph.neighbors(node))
                    subgraph_nodes.update(neighbors)
                    
                    # Add predecessors (incoming edges)
                    predecessors = list(self.relationship_graph.predecessors(node))
                    subgraph_nodes.update(predecessors)
            
            current_depth += 1
        
        subgraph = self.relationship_graph.subgraph(subgraph_nodes)
        
        # Calculate network metrics
        metrics = self._calculate_network_metrics(subgraph, entity_id)
        
        # Get relationship types and their counts
        relationship_types = defaultdict(int)
        relationship_strengths = defaultdict(list)
        
        for _, _, edge_data in subgraph.edges(data=True):
            rel_type = edge_data.get('relationship_type', 'unknown')
            relationship_types[rel_type] += 1
            relationship_strengths[rel_type].append(edge_data.get('strength', 0))
        
        # Calculate average strengths
        avg_strengths = {
            rel_type: np.mean(strengths) 
            for rel_type, strengths in relationship_strengths.items()
        }
        
        # Identify key relationships (high strength/confidence)
        key_relationships = []
        for source, target, edge_data in subgraph.edges(data=True):
            if edge_data.get('strength', 0) > 0.7 and edge_data.get('confidence', 0) > 0.7:
                key_relationships.append({
                    'source': source,
                    'target': target,
                    'type': edge_data.get('relationship_type'),
                    'strength': edge_data.get('strength'),
                    'confidence': edge_data.get('confidence')
                })
        
        return {
            'entity_id': entity_id,
            'network_metrics': metrics,
            'relationship_types': dict(relationship_types),
            'average_relationship_strengths': avg_strengths,
            'key_relationships': key_relationships,
            'connected_entities': list(subgraph_nodes),
            'total_connections': len(subgraph.edges()),
            'network_density': nx.density(subgraph.to_undirected()) if subgraph_nodes else 0,
            'subgraph_data': {
                'nodes': list(subgraph.nodes(data=True)),
                'edges': [(u, v, d) for u, v, d in subgraph.edges(data=True)]
            }
        }
    
    def _calculate_network_metrics(self, subgraph: nx.MultiDiGraph, entity_id: str) -> Dict[str, Any]:
        """Calculate comprehensive network metrics"""
        metrics = {
            'total_nodes': len(subgraph.nodes),
            'total_edges': len(subgraph.edges),
        }
        
        if entity_id in subgraph:
            metrics.update({
                'entity_degree': subgraph.degree(entity_id),
                'entity_in_degree': subgraph.in_degree(entity_id),
                'entity_out_degree': subgraph.out_degree(entity_id)
            })
            
            # Centrality measures
            if len(subgraph.nodes) > 1:
                undirected_graph = subgraph.to_undirected()
                
                # Degree centrality
                degree_centrality = nx.degree_centrality(undirected_graph)
                metrics['degree_centrality'] = degree_centrality.get(entity_id, 0)
                
                # Betweenness centrality
                if len(subgraph.nodes) > 2:
                    betweenness_centrality = nx.betweenness_centrality(undirected_graph)
                    metrics['betweenness_centrality'] = betweenness_centrality.get(entity_id, 0)
                
                # Closeness centrality
                if nx.is_connected(undirected_graph):
                    closeness_centrality = nx.closeness_centrality(undirected_graph)
                    metrics['closeness_centrality'] = closeness_centrality.get(entity_id, 0)
        
        return metrics
    
    def detect_communities(self, min_community_size: int = 3) -> List[List[str]]:
        """Detect communities/clusters in the relationship network"""
        try:
            # Convert to undirected for community detection
            undirected_graph = self.relationship_graph.to_undirected()
            
            # Use Louvain community detection
            import community as community_louvain
            partition = community_louvain.best_partition(undirected_graph)
            
            # Group entities by community
            communities = defaultdict(list)
            for entity_id, community_id in partition.items():
                communities[community_id].append(entity_id)
            
            # Filter by minimum size
            filtered_communities = [
                community for community in communities.values() 
                if len(community) >= min_community_size
            ]
            
            return filtered_communities
            
        except ImportError:
            logger.warning("python-louvain not installed. Using simple connected components.")
            # Fallback to connected components
            undirected_graph = self.relationship_graph.to_undirected()
            components = list(nx.connected_components(undirected_graph))
            return [list(component) for component in components if len(component) >= min_community_size]
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None
    
    def get_mapping_metrics(self) -> Dict[str, Any]:
        """Get relationship mapping performance metrics"""
        return dict(self.mapping_metrics)
