"""
Data Provenance & Lineage Tracking System

Comprehensive system for tracking the origin, transformation, and lineage
of all data throughout the business intelligence pipeline.
"""

import logging
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass
from uuid import uuid4
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, text, func
from sqlalchemy.orm import selectinload

from .quality_models import (
    DataSource, RawDataRecord, EntityRecord, ProvenanceRecord,
    DataChangeLog, ChangeType
)

logger = logging.getLogger(__name__)


@dataclass
class LineageNode:
    """Node in data lineage tree"""
    id: str
    type: str  # source, raw_record, entity, field
    name: str
    timestamp: datetime
    metadata: Dict[str, Any]
    children: List['LineageNode']
    parents: List['LineageNode']


@dataclass
class ProvenanceInfo:
    """Complete provenance information for a data field"""
    field_name: str
    field_value: Any
    entity_id: str
    
    # Source information
    source_name: str
    source_url: str
    source_type: str
    
    # Extraction details
    raw_record_id: str
    extracted_at: datetime
    extraction_method: str
    extractor_version: str
    extraction_confidence: float
    
    # Processing details
    processed_at: datetime
    processor_version: str
    transformations: List[str]
    
    # Verification
    verification_hash: str
    signature: Optional[str]


class ProvenanceTracker:
    """Main provenance tracking system"""
    
    def __init__(self):
        self.signature_key = None  # For cryptographic signatures
        self.enable_signatures = False
    
    async def record_data_source(self, source_config: Dict[str, Any], session: AsyncSession) -> DataSource:
        """Register a new data source"""
        source_id = source_config.get('source_id') or str(uuid4())
        
        # Check if source already exists
        existing_query = select(DataSource).where(DataSource.source_id == source_id)
        existing_source = (await session.execute(existing_query)).scalar_one_or_none()
        
        if existing_source:
            # Update existing source
            existing_source.name = source_config.get('name', existing_source.name)
            existing_source.description = source_config.get('description', existing_source.description)
            existing_source.updated_at = datetime.now(timezone.utc)
            return existing_source
        
        # Create new source
        source = DataSource(
            source_id=source_id,
            name=source_config['name'],
            source_type=source_config['source_type'],
            base_url=source_config.get('base_url'),
            description=source_config.get('description'),
            update_frequency_hours=source_config.get('update_frequency_hours', 24),
            quality_checks=source_config.get('quality_checks', {})
        )
        
        session.add(source)
        await session.commit()
        
        logger.info(f"Registered data source: {source.name} ({source.source_id})")
        return source
    
    async def record_raw_extraction(self, extraction_data: Dict[str, Any], 
                                   session: AsyncSession) -> RawDataRecord:
        """Record raw data extraction with full provenance"""
        source_id = extraction_data['source_id']
        raw_content = extraction_data['raw_content']
        source_url = extraction_data['source_url']
        
        # Get or create data source
        source_query = select(DataSource).where(DataSource.source_id == source_id)
        source = (await session.execute(source_query)).scalar_one_or_none()
        
        if not source:
            raise ValueError(f"Data source {source_id} not found")
        
        # Generate content hash
        content_hash = hashlib.sha256(raw_content.encode()).hexdigest()
        
        # Check for duplicate content
        duplicate_query = select(RawDataRecord).where(
            and_(
                RawDataRecord.content_hash == content_hash,
                RawDataRecord.source_url == source_url
            )
        )
        duplicate = (await session.execute(duplicate_query)).scalar_one_or_none()
        
        if duplicate:
            logger.info(f"Duplicate content detected for {source_url}, using existing record")
            return duplicate
        
        # Create raw data record
        raw_record = RawDataRecord(
            raw_id=str(uuid4()),
            source_id=source.id,
            source_url=source_url,
            extraction_job_id=extraction_data.get('job_id'),
            extractor_version=extraction_data.get('extractor_version'),
            raw_content=raw_content,
            content_hash=content_hash,
            content_type=extraction_data.get('content_type'),
            extracted_at=extraction_data.get('extracted_at', datetime.now(timezone.utc)),
            source_timestamp=extraction_data.get('source_timestamp'),
            extraction_confidence=extraction_data.get('confidence', 0.8),
            validation_errors=extraction_data.get('validation_errors', [])
        )
        
        session.add(raw_record)
        
        # Update source statistics
        source.total_requests += 1
        if not raw_record.validation_errors:
            source.successful_requests += 1
            source.last_successful_access = datetime.now(timezone.utc)
        
        # Update reliability score
        if source.total_requests > 0:
            source.reliability_score = source.successful_requests / source.total_requests
        
        await session.commit()
        
        logger.info(f"Recorded raw extraction: {raw_record.raw_id} from {source_url}")
        return raw_record
    
    async def record_field_provenance(self, field_data: Dict[str, Any], 
                                     entity: EntityRecord, raw_record: RawDataRecord,
                                     session: AsyncSession) -> ProvenanceRecord:
        """Record detailed provenance for a specific field"""
        field_name = field_data['field_name']
        field_value = field_data.get('field_value')
        
        # Create provenance record
        provenance = ProvenanceRecord(
            entity_id=entity.id,
            field_name=field_name,
            field_value=str(field_value) if field_value is not None else None,
            raw_record_id=raw_record.id,
            source_url=raw_record.source_url,
            extraction_method=field_data.get('extraction_method'),
            extracted_at=raw_record.extracted_at,
            processor_version=field_data.get('processor_version'),
            extraction_confidence=field_data.get('confidence', 0.5),
            transformation_applied=field_data.get('transformations')
        )
        
        # Generate cryptographic signature if enabled
        if self.enable_signatures:
            provenance.signature = self._generate_signature(provenance)
        
        session.add(provenance)
        await session.commit()
        
        logger.debug(f"Recorded provenance for field {field_name} of entity {entity.entity_id}")
        return provenance
    
    async def record_entity_change(self, change_data: Dict[str, Any], 
                                  entity: EntityRecord, session: AsyncSession) -> DataChangeLog:
        """Record a change to an entity with full audit trail"""
        change_log = DataChangeLog(
            entity_id=entity.id,
            change_type=ChangeType(change_data['change_type']),
            field_name=change_data.get('field_name'),
            old_value=change_data.get('old_value'),
            new_value=change_data.get('new_value'),
            changed_by=change_data.get('changed_by'),
            change_reason=change_data.get('reason'),
            change_source=change_data.get('source'),
            metadata=change_data.get('metadata', {})
        )
        
        session.add(change_log)
        
        # Update entity timestamp
        entity.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        
        logger.info(f"Recorded change {change_log.change_type.value} for entity {entity.entity_id}")
        return change_log
    
    async def get_field_lineage(self, entity_id: str, field_name: str, 
                               session: AsyncSession) -> Optional[ProvenanceInfo]:
        """Get complete lineage for a specific field"""
        # Get entity
        entity_query = select(EntityRecord).where(EntityRecord.entity_id == entity_id)
        entity = (await session.execute(entity_query)).scalar_one_or_none()
        
        if not entity:
            return None
        
        # Get provenance record
        prov_query = (
            select(ProvenanceRecord)
            .where(
                and_(
                    ProvenanceRecord.entity_id == entity.id,
                    ProvenanceRecord.field_name == field_name
                )
            )
            .options(
                selectinload(ProvenanceRecord.raw_record).selectinload(RawDataRecord.source)
            )
            .order_by(ProvenanceRecord.extracted_at.desc())
        )
        
        provenance = (await session.execute(prov_query)).scalar_one_or_none()
        
        if not provenance:
            return None
        
        # Build complete provenance info
        raw_record = provenance.raw_record
        source = raw_record.source
        
        return ProvenanceInfo(
            field_name=field_name,
            field_value=provenance.field_value,
            entity_id=entity_id,
            source_name=source.name,
            source_url=provenance.source_url,
            source_type=source.source_type,
            raw_record_id=raw_record.raw_id,
            extracted_at=provenance.extracted_at,
            extraction_method=provenance.extraction_method or 'unknown',
            extractor_version=raw_record.extractor_version or 'unknown',
            extraction_confidence=provenance.extraction_confidence,
            processed_at=provenance.processed_at,
            processor_version=provenance.processor_version or 'unknown',
            transformations=provenance.transformation_applied.split(',') if provenance.transformation_applied else [],
            verification_hash=provenance.provenance_hash,
            signature=provenance.signature
        )
    
    async def get_entity_lineage_tree(self, entity_id: str, 
                                     session: AsyncSession) -> Optional[LineageNode]:
        """Build complete lineage tree for an entity"""
        # Get entity with all provenance
        entity_query = (
            select(EntityRecord)
            .where(EntityRecord.entity_id == entity_id)
            .options(
                selectinload(EntityRecord.provenance_records).selectinload(ProvenanceRecord.raw_record).selectinload(RawDataRecord.source)
            )
        )
        
        entity = (await session.execute(entity_query)).scalar_one_or_none()
        
        if not entity:
            return None
        
        # Build entity node
        entity_node = LineageNode(
            id=entity.entity_id,
            type='entity',
            name=f"{entity.entity_type}:{entity.entity_id}",
            timestamp=entity.created_at,
            metadata={
                'entity_type': entity.entity_type,
                'quality_score': entity.overall_quality_score,
                'has_issues': entity.has_issues
            },
            children=[],
            parents=[]
        )
        
        # Group provenance by raw record
        raw_records = {}
        for prov in entity.provenance_records:
            raw_record = prov.raw_record
            if raw_record.raw_id not in raw_records:
                raw_records[raw_record.raw_id] = {
                    'record': raw_record,
                    'fields': []
                }
            raw_records[raw_record.raw_id]['fields'].append(prov)
        
        # Build raw record nodes
        for raw_id, raw_data in raw_records.items():
            raw_record = raw_data['record']
            source = raw_record.source
            
            # Raw record node
            raw_node = LineageNode(
                id=raw_record.raw_id,
                type='raw_record',
                name=f"Raw:{raw_record.raw_id[:8]}",
                timestamp=raw_record.extracted_at,
                metadata={
                    'source_url': raw_record.source_url,
                    'extraction_confidence': raw_record.extraction_confidence,
                    'content_hash': raw_record.content_hash[:16],
                    'field_count': len(raw_data['fields'])
                },
                children=[entity_node],
                parents=[]
            )
            
            # Source node
            source_node = LineageNode(
                id=source.source_id,
                type='source',
                name=source.name,
                timestamp=source.created_at,
                metadata={
                    'source_type': source.source_type,
                    'base_url': source.base_url,
                    'reliability_score': source.reliability_score,
                    'success_rate': source.success_rate
                },
                children=[raw_node],
                parents=[]
            )
            
            # Link nodes
            raw_node.parents.append(source_node)
            entity_node.parents.append(raw_node)
        
        return entity_node
    
    async def trace_data_lineage(self, entity_id: str, field_name: Optional[str] = None,
                                session: AsyncSession) -> List[Dict[str, Any]]:
        """Trace complete data lineage path"""
        lineage_path = []
        
        # Get entity
        entity_query = select(EntityRecord).where(EntityRecord.entity_id == entity_id)
        entity = (await session.execute(entity_query)).scalar_one_or_none()
        
        if not entity:
            return lineage_path
        
        # Add entity to path
        lineage_path.append({
            'step': 'entity',
            'id': entity.entity_id,
            'name': f"{entity.entity_type}:{entity.entity_id}",
            'timestamp': entity.created_at.isoformat(),
            'metadata': {
                'quality_score': entity.overall_quality_score,
                'confidence_level': entity.confidence_level.value if entity.confidence_level else 'unknown'
            }
        })
        
        # Get provenance records
        prov_query = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.entity_id == entity.id)
            .options(
                selectinload(ProvenanceRecord.raw_record).selectinload(RawDataRecord.source)
            )
        )
        
        if field_name:
            prov_query = prov_query.where(ProvenanceRecord.field_name == field_name)
        
        provenance_records = (await session.execute(prov_query)).scalars().all()
        
        # Add processing steps
        for prov in provenance_records:
            raw_record = prov.raw_record
            source = raw_record.source
            
            # Add processing step
            lineage_path.append({
                'step': 'processing',
                'id': prov.provenance_id,
                'name': f"Process field: {prov.field_name}",
                'timestamp': prov.processed_at.isoformat(),
                'metadata': {
                    'field_name': prov.field_name,
                    'extraction_method': prov.extraction_method,
                    'confidence': prov.extraction_confidence,
                    'transformations': prov.transformation_applied
                }
            })
            
            # Add extraction step
            lineage_path.append({
                'step': 'extraction',
                'id': raw_record.raw_id,
                'name': f"Extract from: {source.name}",
                'timestamp': raw_record.extracted_at.isoformat(),
                'metadata': {
                    'source_url': raw_record.source_url,
                    'extractor_version': raw_record.extractor_version,
                    'content_hash': raw_record.content_hash[:16]
                }
            })
            
            # Add source step
            lineage_path.append({
                'step': 'source',
                'id': source.source_id,
                'name': source.name,
                'timestamp': source.created_at.isoformat(),
                'metadata': {
                    'source_type': source.source_type,
                    'base_url': source.base_url,
                    'reliability_score': source.reliability_score
                }
            })
        
        # Sort by timestamp (newest first)
        lineage_path.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return lineage_path
    
    async def get_entity_change_history(self, entity_id: str, 
                                       session: AsyncSession) -> List[Dict[str, Any]]:
        """Get complete change history for an entity"""
        # Get entity
        entity_query = select(EntityRecord).where(EntityRecord.entity_id == entity_id)
        entity = (await session.execute(entity_query)).scalar_one_or_none()
        
        if not entity:
            return []
        
        # Get change history
        changes_query = (
            select(DataChangeLog)
            .where(DataChangeLog.entity_id == entity.id)
            .order_by(DataChangeLog.changed_at.desc())
        )
        
        changes = (await session.execute(changes_query)).scalars().all()
        
        change_history = []
        for change in changes:
            change_history.append({
                'change_id': change.change_id,
                'type': change.change_type.value,
                'field': change.field_name,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'timestamp': change.changed_at.isoformat(),
                'changed_by': change.changed_by,
                'reason': change.change_reason,
                'source': change.change_source,
                'verified': change.is_verified,
                'rollback': change.is_rollback,
                'metadata': change.metadata
            })
        
        return change_history
    
    async def verify_data_integrity(self, entity_id: str, 
                                   session: AsyncSession) -> Dict[str, Any]:
        """Verify data integrity using cryptographic hashes"""
        integrity_report = {
            'entity_id': entity_id,
            'verified': True,
            'issues': [],
            'provenance_verified': 0,
            'provenance_total': 0,
            'hash_mismatches': []
        }
        
        # Get entity
        entity_query = select(EntityRecord).where(EntityRecord.entity_id == entity_id)
        entity = (await session.execute(entity_query)).scalar_one_or_none()
        
        if not entity:
            integrity_report['verified'] = False
            integrity_report['issues'].append('Entity not found')
            return integrity_report
        
        # Verify entity data hash
        current_data_str = json.dumps(entity.data, sort_keys=True)
        current_hash = hashlib.sha256(current_data_str.encode()).hexdigest()
        
        if current_hash != entity.data_hash:
            integrity_report['verified'] = False
            integrity_report['issues'].append('Entity data hash mismatch')
            integrity_report['hash_mismatches'].append({
                'type': 'entity_data',
                'expected': entity.data_hash,
                'actual': current_hash
            })
        
        # Verify provenance records
        prov_query = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.entity_id == entity.id)
        )
        
        provenance_records = (await session.execute(prov_query)).scalars().all()
        integrity_report['provenance_total'] = len(provenance_records)
        
        for prov in provenance_records:
            # Regenerate provenance hash
            hash_data = f"{prov.entity_id}:{prov.field_name}:{prov.field_value}:{prov.source_url}:{prov.extracted_at}"
            expected_hash = hashlib.sha256(hash_data.encode()).hexdigest()
            
            if expected_hash == prov.provenance_hash:
                integrity_report['provenance_verified'] += 1
            else:
                integrity_report['verified'] = False
                integrity_report['issues'].append(f'Provenance hash mismatch for field {prov.field_name}')
                integrity_report['hash_mismatches'].append({
                    'type': 'provenance',
                    'field': prov.field_name,
                    'expected': prov.provenance_hash,
                    'actual': expected_hash
                })
        
        return integrity_report
    
    async def export_lineage_data(self, entity_ids: List[str], 
                                 session: AsyncSession) -> Dict[str, Any]:
        """Export complete lineage data for audit purposes"""
        export_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'entities': [],
            'sources': [],
            'raw_records': [],
            'provenance': [],
            'changes': []
        }
        
        for entity_id in entity_ids:
            # Get entity with full relations
            entity_query = (
                select(EntityRecord)
                .where(EntityRecord.entity_id == entity_id)
                .options(
                    selectinload(EntityRecord.provenance_records).selectinload(ProvenanceRecord.raw_record).selectinload(RawDataRecord.source),
                    selectinload(EntityRecord.change_log)
                )
            )
            
            entity = (await session.execute(entity_query)).scalar_one_or_none()
            
            if not entity:
                continue
            
            # Export entity
            export_data['entities'].append({
                'entity_id': entity.entity_id,
                'entity_type': entity.entity_type,
                'data': entity.data,
                'data_hash': entity.data_hash,
                'quality_scores': {
                    'overall': entity.overall_quality_score,
                    'completeness': entity.completeness_score,
                    'consistency': entity.consistency_score,
                    'freshness': entity.freshness_score,
                    'confidence': entity.confidence_score
                },
                'created_at': entity.created_at.isoformat(),
                'updated_at': entity.updated_at.isoformat()
            })
            
            # Export provenance and sources
            for prov in entity.provenance_records:
                raw_record = prov.raw_record
                source = raw_record.source
                
                # Export source (deduplicated)
                source_data = {
                    'source_id': source.source_id,
                    'name': source.name,
                    'source_type': source.source_type,
                    'base_url': source.base_url,
                    'reliability_score': source.reliability_score,
                    'created_at': source.created_at.isoformat()
                }
                
                if source_data not in export_data['sources']:
                    export_data['sources'].append(source_data)
                
                # Export raw record
                raw_data = {
                    'raw_id': raw_record.raw_id,
                    'source_id': source.source_id,
                    'source_url': raw_record.source_url,
                    'content_hash': raw_record.content_hash,
                    'extracted_at': raw_record.extracted_at.isoformat(),
                    'extractor_version': raw_record.extractor_version
                }
                
                if raw_data not in export_data['raw_records']:
                    export_data['raw_records'].append(raw_data)
                
                # Export provenance
                export_data['provenance'].append({
                    'provenance_id': prov.provenance_id,
                    'entity_id': entity.entity_id,
                    'field_name': prov.field_name,
                    'field_value': prov.field_value,
                    'raw_record_id': raw_record.raw_id,
                    'source_url': prov.source_url,
                    'extracted_at': prov.extracted_at.isoformat(),
                    'processed_at': prov.processed_at.isoformat(),
                    'extraction_confidence': prov.extraction_confidence,
                    'provenance_hash': prov.provenance_hash,
                    'signature': prov.signature
                })
            
            # Export change history
            for change in entity.change_log:
                export_data['changes'].append({
                    'change_id': change.change_id,
                    'entity_id': entity.entity_id,
                    'change_type': change.change_type.value,
                    'field_name': change.field_name,
                    'old_value': change.old_value,
                    'new_value': change.new_value,
                    'changed_at': change.changed_at.isoformat(),
                    'changed_by': change.changed_by,
                    'change_reason': change.change_reason,
                    'verified': change.is_verified
                })
        
        return export_data
    
    def _generate_signature(self, provenance: ProvenanceRecord) -> str:
        """Generate cryptographic signature for provenance record"""
        # This is a placeholder - implement actual digital signing
        # with your preferred cryptographic library (e.g., cryptography, pycryptodome)
        data = f"{provenance.provenance_hash}:{provenance.extracted_at}"
        return hashlib.sha256(data.encode()).hexdigest()


# Global provenance tracker instance
provenance_tracker = ProvenanceTracker()
