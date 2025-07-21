"""
Core Storage & Indexing Layer Implementation

Advanced storage system supporting:
- Raw data lake with full provenance tracking
- Structured entity normalization and storage
- Complete data lineage and traceability
- Multi-backend storage (S3, PostgreSQL, Elasticsearch)
- Advanced indexing and search capabilities
"""

import asyncio
import hashlib
import json
import logging
import uuid
import time
import gzip
import pickle
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union, AsyncGenerator, Tuple
from urllib.parse import urlparse
import weakref

# Storage backends
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    Minio = None

try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    AsyncElasticsearch = None

# Database
try:
    from sqlalchemy import create_engine, text, and_, or_, func
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

# Data processing
try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from .models import (
    RawDataModel, StructuredEntityModel, RawToStructuredMappingModel,
    EntityRelationshipModel, DataQualityMetricsModel, DataLineageModel,
    StorageMetricsModel
)

logger = logging.getLogger(__name__)


@dataclass
class RawDataRecord:
    """Container for raw data with full provenance"""
    raw_id: str
    source_url: str
    content: str
    content_type: str
    fetched_at: datetime
    job_id: str
    
    # Optional fields with defaults
    referrer_url: Optional[str] = None
    http_status: int = 200
    content_encoding: str = 'utf-8'
    response_time_ms: int = 0
    
    # Headers and metadata
    request_headers: Dict[str, str] = field(default_factory=dict)
    response_headers: Dict[str, str] = field(default_factory=dict)
    
    # Storage configuration
    storage_backend: str = 's3'
    storage_bucket: str = "business-intelligence-raw"
    storage_key: Optional[str] = None
    
    # Content analysis
    language: Optional[str] = None
    charset: str = 'utf-8'
    page_title: Optional[str] = None
    content_quality_score: Optional[float] = None
    
    # Attachments and links
    attachments: List[Dict[str, str]] = field(default_factory=list)
    linked_resources: List[str] = field(default_factory=list)
    
    # Processing status
    processing_status: str = 'pending'
    spider_name: Optional[str] = None
    crawl_depth: int = 0
    
    # Custom metadata and tags
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass  
class StructuredEntity:
    """Structured entity with provenance and quality metrics"""
    entity_id: str
    entity_type: str
    canonical_name: str
    structured_data: Dict[str, Any]
    
    # Provenance
    raw_ids: List[str]
    source_urls: List[str] 
    extraction_method: str
    extractor_name: str
    extractor_version: str
    
    # Quality and confidence
    confidence_score: float
    data_quality_score: float
    completeness_score: float = 1.0
    
    # Temporal information
    extracted_at: datetime = field(default_factory=datetime.utcnow)
    first_seen_at: Optional[datetime] = None
    last_verified_at: Optional[datetime] = None
    
    # Classification and categorization
    category: Optional[str] = None
    subcategory: Optional[str] = None
    importance_score: float = 0.5
    
    # Business-specific data
    contact_info: Dict[str, Any] = field(default_factory=dict)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    industry_codes: List[str] = field(default_factory=list)
    business_identifiers: Dict[str, str] = field(default_factory=dict)
    financial_data: Dict[str, Any] = field(default_factory=dict)
    
    # Status and verification
    verification_status: str = 'unverified'
    verification_source: Optional[str] = None
    is_active: bool = True
    needs_review: bool = False
    
    # Metadata and tags
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class StorageConfig:
    """Configuration for storage backends"""
    # Database configuration
    database_url: str
    
    # S3/MinIO configuration
    s3_endpoint_url: Optional[str] = None
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "us-east-1"
    s3_bucket_prefix: str = "business-intel"
    
    # Elasticsearch configuration
    elasticsearch_url: Optional[str] = None
    elasticsearch_index_prefix: str = "business-intel"
    
    # Local storage fallback
    local_storage_path: str = "data/storage"
    
    # Performance settings
    connection_pool_size: int = 20
    max_overflow: int = 30
    pool_timeout: int = 30
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 10000


class AdvancedStorageManager:
    """Comprehensive storage manager for raw data, structured entities, and lineage"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Initialize storage backends
        self._init_object_storage()
        self._init_elasticsearch()
        
        # Initialize local storage fallback
        self.local_storage_path = Path(config.local_storage_path)
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Performance monitoring
        self.metrics = {
            'raw_data_stored': 0,
            'structured_entities_stored': 0,
            'storage_errors': 0,
            'retrieval_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # In-memory cache
        if config.enable_cache:
            self._cache: Dict[str, Tuple[Any, float]] = {}
            self._cache_access_times: Dict[str, float] = {}
            self._max_cache_size = config.max_cache_size
            self._cache_ttl = config.cache_ttl_seconds
        
        self.logger.info("Advanced Storage Manager initialized")
    
    def _init_database(self):
        """Initialize database connection and create tables"""
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy not available for database operations")
        
        self.engine = create_engine(
            self.config.database_url,
            poolclass=QueuePool,
            pool_size=self.config.connection_pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create tables
        from .models import RawDataModel
        RawDataModel.metadata.create_all(self.engine, checkfirst=True)
        
        self.Session = sessionmaker(bind=self.engine)
        self.logger.info("Database initialized successfully")
    
    def _init_object_storage(self):
        """Initialize S3/MinIO object storage"""
        self.s3_client = None
        
        if not self.config.s3_access_key or not self.config.s3_secret_key:
            self.logger.warning("S3 credentials not configured, using local storage only")
            return
        
        try:
            if S3_AVAILABLE:
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=self.config.s3_endpoint_url,
                    aws_access_key_id=self.config.s3_access_key,
                    aws_secret_access_key=self.config.s3_secret_key,
                    region_name=self.config.s3_region
                )
                self.logger.info("S3 client initialized")
            elif MINIO_AVAILABLE and self.config.s3_endpoint_url:
                # Parse endpoint for MinIO client
                from urllib.parse import urlparse
                parsed = urlparse(self.config.s3_endpoint_url)
                
                self.s3_client = Minio(
                    f"{parsed.hostname}:{parsed.port or 9000}",
                    access_key=self.config.s3_access_key,
                    secret_key=self.config.s3_secret_key,
                    secure=parsed.scheme == 'https'
                )
                self.logger.info("MinIO client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize object storage: {e}")
            self.s3_client = None
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch client"""
        self.es_client = None
        
        if not self.config.elasticsearch_url or not ELASTICSEARCH_AVAILABLE:
            self.logger.info("Elasticsearch not configured or not available")
            return
        
        try:
            self.es_client = AsyncElasticsearch([self.config.elasticsearch_url])
            self.logger.info("Elasticsearch client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Elasticsearch: {e}")
    
    async def store_raw_data(self, raw_record: RawDataRecord) -> str:
        """Store raw data with full provenance tracking"""
        try:
            # Generate storage key if not provided
            if not raw_record.storage_key:
                raw_record.storage_key = self._generate_storage_key(raw_record)
            
            # Calculate content hash for deduplication
            content_hash = self._calculate_content_hash(raw_record.content)
            
            # Check for duplicates
            existing_id = await self._check_duplicate_content(content_hash)
            if existing_id:
                self.logger.info(f"Duplicate content found, returning existing ID: {existing_id}")
                return existing_id
            
            # Store content in object storage
            storage_success = await self._store_raw_content(raw_record)
            if not storage_success:
                raise Exception("Failed to store content in object storage")
            
            # Store metadata in database
            await self._store_raw_metadata(raw_record, content_hash)
            
            # Index in Elasticsearch if available
            if self.es_client:
                await self._index_raw_data_elasticsearch(raw_record)
            
            # Update metrics
            self.metrics['raw_data_stored'] += 1
            
            self.logger.info(f"Raw data stored successfully: {raw_record.raw_id}")
            return raw_record.raw_id
            
        except Exception as e:
            self.metrics['storage_errors'] += 1
            self.logger.error(f"Failed to store raw data {raw_record.raw_id}: {e}")
            raise
    
    async def store_structured_entity(self, entity: StructuredEntity) -> str:
        """Store structured entity with full provenance linking"""
        try:
            session = self.Session()
            
            try:
                # Create entity record
                entity_model = StructuredEntityModel(
                    entity_id=entity.entity_id,
                    entity_type=entity.entity_type,
                    canonical_name=entity.canonical_name,
                    display_name=entity.structured_data.get('display_name', entity.canonical_name),
                    description=entity.structured_data.get('description'),
                    
                    category=entity.category,
                    subcategory=entity.subcategory,
                    confidence_score=entity.confidence_score,
                    importance_score=entity.importance_score,
                    
                    extracted_at=entity.extracted_at,
                    first_seen_at=entity.first_seen_at or entity.extracted_at,
                    last_verified_at=entity.last_verified_at,
                    
                    extractor_name=entity.extractor_name,
                    extractor_version=entity.extractor_version,
                    extraction_method=entity.extraction_method,
                    
                    structured_data=entity.structured_data,
                    contact_info=entity.contact_info,
                    locations=entity.locations,
                    industry_codes=entity.industry_codes,
                    business_identifiers=entity.business_identifiers,
                    financial_data=entity.financial_data,
                    
                    verification_status=entity.verification_status,
                    verification_source=entity.verification_source,
                    data_quality_score=entity.data_quality_score,
                    completeness_score=entity.completeness_score,
                    
                    primary_source_url=entity.source_urls[0] if entity.source_urls else None,
                    source_count=len(entity.source_urls),
                    
                    is_active=entity.is_active,
                    is_verified=entity.verification_status == 'verified',
                    needs_review=entity.needs_review,
                    
                    metadata=entity.metadata,
                    tags=entity.tags
                )
                
                session.merge(entity_model)  # Use merge to handle updates
                
                # Create mappings to raw data sources
                await self._create_entity_mappings(session, entity)
                
                # Create data lineage entries
                await self._create_lineage_entries(session, entity)
                
                session.commit()
                
                # Index in Elasticsearch
                if self.es_client:
                    await self._index_entity_elasticsearch(entity)
                
                # Update metrics
                self.metrics['structured_entities_stored'] += 1
                
                self.logger.info(f"Structured entity stored: {entity.entity_id}")
                return entity.entity_id
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            self.metrics['storage_errors'] += 1
            self.logger.error(f"Failed to store structured entity {entity.entity_id}: {e}")
            raise
    
    async def retrieve_raw_data(self, raw_id: str) -> Optional[RawDataRecord]:
        """Retrieve raw data by ID with full content reconstruction"""
        try:
            # Check cache first
            if hasattr(self, '_cache'):
                cached = self._get_from_cache(f"raw_data:{raw_id}")
                if cached:
                    self.metrics['cache_hits'] += 1
                    return cached
                self.metrics['cache_misses'] += 1
            
            session = self.Session()
            
            try:
                # Get metadata from database
                db_record = session.query(RawDataModel).filter_by(raw_id=raw_id).first()
                if not db_record:
                    return None
                
                # Retrieve content from storage
                content = await self._retrieve_raw_content(
                    db_record.storage_backend,
                    db_record.storage_bucket,
                    db_record.storage_key,
                    db_record.is_compressed
                )
                
                if content is None:
                    self.logger.error(f"Failed to retrieve content for {raw_id}")
                    return None
                
                # Reconstruct RawDataRecord
                raw_record = RawDataRecord(
                    raw_id=db_record.raw_id,
                    source_url=db_record.source_url,
                    content=content,
                    content_type=db_record.content_type or 'text/html',
                    fetched_at=db_record.fetched_at,
                    job_id=db_record.job_id,
                    
                    referrer_url=db_record.referrer_url,
                    http_status=db_record.http_status or 200,
                    content_encoding=db_record.content_encoding or 'utf-8',
                    response_time_ms=db_record.response_time_ms or 0,
                    
                    request_headers=db_record.request_headers or {},
                    response_headers=db_record.response_headers or {},
                    
                    storage_backend=db_record.storage_backend,
                    storage_bucket=db_record.storage_bucket,
                    storage_key=db_record.storage_key,
                    
                    language=db_record.language,
                    charset=db_record.charset or 'utf-8',
                    page_title=db_record.page_title,
                    content_quality_score=db_record.content_quality_score,
                    
                    attachments=db_record.attachments or [],
                    linked_resources=db_record.linked_resources or [],
                    
                    processing_status=db_record.processing_status,
                    spider_name=db_record.spider_name,
                    crawl_depth=db_record.crawl_depth or 0,
                    
                    metadata=db_record.metadata or {},
                    tags=db_record.tags or []
                )
                
                # Cache the result
                if hasattr(self, '_cache'):
                    self._add_to_cache(f"raw_data:{raw_id}", raw_record)
                
                self.metrics['retrieval_requests'] += 1
                return raw_record
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve raw data {raw_id}: {e}")
            return None
    
    async def get_entity_provenance(self, entity_id: str) -> Dict[str, Any]:
        """Get complete provenance chain for an entity"""
        session = self.Session()
        
        try:
            # Get entity details
            entity = session.query(StructuredEntityModel).filter_by(entity_id=entity_id).first()
            if not entity:
                return {}
            
            # Get all raw data mappings
            mappings = session.query(RawToStructuredMappingModel).filter_by(entity_id=entity_id).all()
            
            # Get raw data sources
            raw_sources = []
            for mapping in mappings:
                raw_data = session.query(RawDataModel).filter_by(raw_id=mapping.raw_id).first()
                if raw_data:
                    raw_sources.append({
                        'raw_id': raw_data.raw_id,
                        'source_url': raw_data.source_url,
                        'source_domain': raw_data.source_domain,
                        'fetched_at': raw_data.fetched_at.isoformat(),
                        'job_id': raw_data.job_id,
                        'spider_name': raw_data.spider_name,
                        'extraction_confidence': mapping.extraction_confidence,
                        'extraction_method': mapping.extraction_method,
                        'extractor_name': mapping.extractor_name,
                        'is_primary_source': mapping.is_primary_source,
                        'storage_location': f"{raw_data.storage_bucket}/{raw_data.storage_key}",
                        'content_quality_score': raw_data.content_quality_score,
                        'http_status': raw_data.http_status
                    })
            
            # Get data lineage
            lineage_entries = session.query(DataLineageModel).filter(
                or_(
                    DataLineageModel.source_id == entity_id,
                    DataLineageModel.target_id == entity_id
                )
            ).all()
            
            lineage_data = []
            for entry in lineage_entries:
                lineage_data.append({
                    'lineage_id': entry.lineage_id,
                    'source_type': entry.source_type,
                    'source_id': entry.source_id,
                    'target_type': entry.target_type,
                    'target_id': entry.target_id,
                    'transformation_type': entry.transformation_type,
                    'transformation_name': entry.transformation_name,
                    'path_length': entry.path_length,
                    'transformation_confidence': entry.transformation_confidence,
                    'created_at': entry.created_at.isoformat()
                })
            
            # Get relationships
            relationships_out = session.query(EntityRelationshipModel).filter_by(source_entity_id=entity_id).all()
            relationships_in = session.query(EntityRelationshipModel).filter_by(target_entity_id=entity_id).all()
            
            relationships = []
            for rel in relationships_out + relationships_in:
                relationships.append({
                    'relationship_id': rel.relationship_id,
                    'relationship_type': rel.relationship_type,
                    'source_entity_id': rel.source_entity_id,
                    'target_entity_id': rel.target_entity_id,
                    'strength': rel.strength,
                    'confidence': rel.confidence,
                    'is_directional': rel.is_directional,
                    'evidence_sources': rel.evidence_sources
                })
            
            return {
                'entity_id': entity.entity_id,
                'entity_type': entity.entity_type,
                'canonical_name': entity.canonical_name,
                'extracted_at': entity.extracted_at.isoformat(),
                'confidence_score': entity.confidence_score,
                'data_quality_score': entity.data_quality_score,
                'extractor_name': entity.extractor_name,
                'extractor_version': entity.extractor_version,
                'verification_status': entity.verification_status,
                'source_count': len(raw_sources),
                'raw_sources': raw_sources,
                'lineage_entries': lineage_data,
                'relationships': relationships,
                'total_sources': len(raw_sources),
                'total_lineage_entries': len(lineage_data),
                'total_relationships': len(relationships)
            }
            
        finally:
            session.close()
    
    async def search_entities(self, 
                            query: str, 
                            entity_type: Optional[str] = None,
                            category: Optional[str] = None,
                            min_confidence: Optional[float] = None,
                            limit: int = 50) -> List[Dict]:
        """Search entities using Elasticsearch or database fallback"""
        
        if self.es_client:
            return await self._elasticsearch_search_entities(query, entity_type, category, min_confidence, limit)
        else:
            return await self._database_search_entities(query, entity_type, category, min_confidence, limit)
    
    async def export_data_lineage(self, 
                                output_format: str = "parquet",
                                entity_types: Optional[List[str]] = None,
                                date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, str]:
        """Export complete data lineage for analysis"""
        
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas not available for data export")
        
        session = self.Session()
        
        try:
            # Build base queries with filters
            raw_query = session.query(RawDataModel)
            entities_query = session.query(StructuredEntityModel)
            mappings_query = session.query(RawToStructuredMappingModel)
            lineage_query = session.query(DataLineageModel)
            
            # Apply filters
            if date_range:
                start_date, end_date = date_range
                raw_query = raw_query.filter(RawDataModel.fetched_at.between(start_date, end_date))
                entities_query = entities_query.filter(StructuredEntityModel.extracted_at.between(start_date, end_date))
            
            if entity_types:
                entities_query = entities_query.filter(StructuredEntityModel.entity_type.in_(entity_types))
            
            # Execute queries and convert to DataFrames
            raw_data_df = pd.read_sql(raw_query.statement, self.engine)
            entities_df = pd.read_sql(entities_query.statement, self.engine)
            mappings_df = pd.read_sql(mappings_query.statement, self.engine)
            lineage_df = pd.read_sql(lineage_query.statement, self.engine)
            
            # Generate export directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = self.local_storage_path / "exports" / timestamp
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Export files
            file_paths = {}
            
            if output_format == "parquet":
                raw_path = export_dir / "raw_data.parquet"
                entities_path = export_dir / "structured_entities.parquet"
                mappings_path = export_dir / "data_mappings.parquet"
                lineage_path = export_dir / "data_lineage.parquet"
                
                raw_data_df.to_parquet(raw_path, index=False)
                entities_df.to_parquet(entities_path, index=False)
                mappings_df.to_parquet(mappings_path, index=False)
                lineage_df.to_parquet(lineage_path, index=False)
                
                file_paths = {
                    'raw_data': str(raw_path),
                    'entities': str(entities_path),
                    'mappings': str(mappings_path),
                    'lineage': str(lineage_path)
                }
                
            elif output_format == "csv":
                raw_path = export_dir / "raw_data.csv"
                entities_path = export_dir / "structured_entities.csv"
                mappings_path = export_dir / "data_mappings.csv"
                lineage_path = export_dir / "data_lineage.csv"
                
                raw_data_df.to_csv(raw_path, index=False)
                entities_df.to_csv(entities_path, index=False)
                mappings_df.to_csv(mappings_path, index=False)
                lineage_df.to_csv(lineage_path, index=False)
                
                file_paths = {
                    'raw_data': str(raw_path),
                    'entities': str(entities_path),
                    'mappings': str(mappings_path),
                    'lineage': str(lineage_path)
                }
            
            # Generate summary
            export_summary = {
                'export_directory': str(export_dir),
                'export_format': output_format,
                'timestamp': timestamp,
                'file_paths': file_paths,
                'record_counts': {
                    'raw_data_records': len(raw_data_df),
                    'structured_entities': len(entities_df),
                    'data_mappings': len(mappings_df),
                    'lineage_entries': len(lineage_df)
                },
                'date_range': [d.isoformat() if d else None for d in (date_range or [None, None])],
                'entity_types_filter': entity_types or [],
                'total_size_mb': sum(Path(p).stat().st_size for p in file_paths.values()) / 1024 / 1024
            }
            
            # Save summary
            summary_path = export_dir / "export_summary.json"
            with open(summary_path, 'w') as f:
                json.dump(export_summary, f, indent=2, default=str)
            
            return export_summary
            
        finally:
            session.close()
    
    # Helper methods
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _generate_storage_key(self, raw_record: RawDataRecord) -> str:
        """Generate hierarchical storage key"""
        parsed_url = urlparse(raw_record.source_url)
        domain = parsed_url.netloc.replace('.', '_').replace(':', '_')
        date_str = raw_record.fetched_at.strftime("%Y/%m/%d")
        hour_str = raw_record.fetched_at.strftime("%H")
        
        return f"raw/{domain}/{date_str}/{hour_str}/{raw_record.job_id}/{raw_record.raw_id}.html"
    
    async def _check_duplicate_content(self, content_hash: str) -> Optional[str]:
        """Check if content with this hash already exists"""
        session = self.Session()
        try:
            existing = session.query(RawDataModel.raw_id).filter_by(content_hash=content_hash).first()
            return existing.raw_id if existing else None
        finally:
            session.close()
    
    async def _store_raw_content(self, raw_record: RawDataRecord) -> bool:
        """Store raw content in object storage"""
        try:
            # Try object storage first
            if self.s3_client:
                return await self._store_s3_content(raw_record)
            
            # Fallback to local storage
            return await self._store_local_content(raw_record)
            
        except Exception as e:
            self.logger.error(f"Failed to store raw content: {e}")
            return False
    
    async def _store_s3_content(self, raw_record: RawDataRecord) -> bool:
        """Store content in S3/MinIO"""
        try:
            # Optionally compress large content
            content_bytes = raw_record.content.encode('utf-8')
            if len(content_bytes) > 10 * 1024:  # Compress if > 10KB
                content_bytes = gzip.compress(content_bytes)
                raw_record.metadata['compressed'] = True
            
            # Ensure bucket exists
            bucket_name = raw_record.storage_bucket
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
            except ClientError:
                self.s3_client.create_bucket(Bucket=bucket_name)
            
            # Store content
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=raw_record.storage_key,
                Body=content_bytes,
                ContentType=raw_record.content_type,
                Metadata={
                    'raw_id': raw_record.raw_id,
                    'source_url': raw_record.source_url[:1000],  # Truncate if too long
                    'job_id': raw_record.job_id,
                    'fetched_at': raw_record.fetched_at.isoformat(),
                    'compressed': str(raw_record.metadata.get('compressed', False))
                }
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"S3 storage failed: {e}")
            return False
    
    async def _store_local_content(self, raw_record: RawDataRecord) -> bool:
        """Store content locally as fallback"""
        try:
            # Create directory structure
            storage_path = self.local_storage_path / raw_record.storage_bucket / raw_record.storage_key
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Optionally compress
            content_bytes = raw_record.content.encode('utf-8')
            if len(content_bytes) > 10 * 1024:  # Compress if > 10KB
                content_bytes = gzip.compress(content_bytes)
                raw_record.metadata['compressed'] = True
                storage_path = storage_path.with_suffix('.gz')
            
            # Write content
            with open(storage_path, 'wb') as f:
                f.write(content_bytes)
            
            # Store metadata alongside
            metadata_path = storage_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump({
                    'raw_id': raw_record.raw_id,
                    'source_url': raw_record.source_url,
                    'job_id': raw_record.job_id,
                    'fetched_at': raw_record.fetched_at.isoformat(),
                    'content_type': raw_record.content_type,
                    'compressed': raw_record.metadata.get('compressed', False),
                    'metadata': raw_record.metadata
                }, f, indent=2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Local storage failed: {e}")
            return False
    
    async def _store_raw_metadata(self, raw_record: RawDataRecord, content_hash: str):
        """Store raw data metadata in database"""
        session = self.Session()
        
        try:
            # Extract domain from URL
            parsed_url = urlparse(raw_record.source_url)
            source_domain = parsed_url.netloc
            
            db_record = RawDataModel(
                raw_id=raw_record.raw_id,
                content_hash=content_hash,
                
                source_url=raw_record.source_url,
                referrer_url=raw_record.referrer_url,
                source_domain=source_domain,
                
                fetched_at=raw_record.fetched_at,
                page_last_modified=None,  # Could be extracted from headers
                
                job_id=raw_record.job_id,
                spider_name=raw_record.spider_name,
                crawl_depth=raw_record.crawl_depth,
                
                http_status=raw_record.http_status,
                content_type=raw_record.content_type,
                content_encoding=raw_record.content_encoding,
                response_time_ms=raw_record.response_time_ms,
                
                storage_backend=raw_record.storage_backend,
                storage_bucket=raw_record.storage_bucket,
                storage_key=raw_record.storage_key,
                content_size_bytes=len(raw_record.content.encode('utf-8')),
                is_compressed=raw_record.metadata.get('compressed', False),
                
                request_headers=raw_record.request_headers,
                response_headers=raw_record.response_headers,
                
                language=raw_record.language,
                charset=raw_record.charset,
                page_title=raw_record.page_title,
                
                processing_status=raw_record.processing_status,
                extraction_attempted=False,
                extraction_successful=False,
                
                content_quality_score=raw_record.content_quality_score,
                is_duplicate=False,
                similarity_hash=content_hash[:16],  # Truncated hash for similarity
                
                attachments=raw_record.attachments,
                linked_resources=raw_record.linked_resources,
                
                metadata=raw_record.metadata,
                tags=raw_record.tags
            )
            
            session.merge(db_record)
            session.commit()
            
        finally:
            session.close()
    
    async def get_storage_metrics(self) -> Dict[str, Any]:
        """Get comprehensive storage metrics and system health"""
        session = self.Session()
        
        try:
            # Database counts
            raw_count = session.query(RawDataModel).count()
            entity_count = session.query(StructuredEntityModel).count()
            mapping_count = session.query(RawToStructuredMappingModel).count()
            lineage_count = session.query(DataLineageModel).count()
            
            # Quality metrics
            quality_metrics = session.query(DataQualityMetricsModel).all()
            avg_quality_score = session.query(func.avg(StructuredEntityModel.data_quality_score)).scalar() or 0
            avg_confidence = session.query(func.avg(StructuredEntityModel.confidence_score)).scalar() or 0
            
            # Processing status
            processing_stats = session.query(
                RawDataModel.processing_status,
                func.count(RawDataModel.raw_id)
            ).group_by(RawDataModel.processing_status).all()
            
            # Entity types distribution
            entity_type_stats = session.query(
                StructuredEntityModel.entity_type,
                func.count(StructuredEntityModel.entity_id)
            ).group_by(StructuredEntityModel.entity_type).all()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_raw = session.query(RawDataModel).filter(RawDataModel.fetched_at >= yesterday).count()
            recent_entities = session.query(StructuredEntityModel).filter(StructuredEntityModel.extracted_at >= yesterday).count()
            
            # Storage size estimation
            total_content_size = session.query(func.sum(RawDataModel.content_size_bytes)).scalar() or 0
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'database_metrics': {
                    'raw_data_records': raw_count,
                    'structured_entities': entity_count,
                    'data_mappings': mapping_count,
                    'lineage_entries': lineage_count,
                    'quality_metrics': len(quality_metrics)
                },
                'quality_metrics': {
                    'average_data_quality_score': round(avg_quality_score, 3),
                    'average_confidence_score': round(avg_confidence, 3),
                    'total_quality_assessments': len(quality_metrics)
                },
                'processing_status': {
                    status: count for status, count in processing_stats
                },
                'entity_types': {
                    entity_type: count for entity_type, count in entity_type_stats
                },
                'recent_activity': {
                    'raw_data_last_24h': recent_raw,
                    'entities_last_24h': recent_entities
                },
                'storage_size': {
                    'total_content_bytes': total_content_size,
                    'total_content_mb': round(total_content_size / 1024 / 1024, 2),
                    'estimated_total_gb': round(total_content_size / 1024 / 1024 / 1024, 2)
                },
                'system_metrics': dict(self.metrics),
                'cache_metrics': {
                    'cache_enabled': hasattr(self, '_cache'),
                    'cache_size': len(self._cache) if hasattr(self, '_cache') else 0,
                    'cache_hit_rate': (
                        self.metrics['cache_hits'] / 
                        (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                        if self.metrics['cache_hits'] + self.metrics['cache_misses'] > 0 
                        else 0
                    )
                }
            }
            
        finally:
            session.close()
    
    # Cache management
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache if not expired"""
        if not hasattr(self, '_cache') or key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self._cache_ttl:
            del self._cache[key]
            if key in self._cache_access_times:
                del self._cache_access_times[key]
            return None
        
        self._cache_access_times[key] = time.time()
        return value
    
    def _add_to_cache(self, key: str, value: Any):
        """Add item to cache with LRU eviction"""
        if not hasattr(self, '_cache'):
            return
        
        # Evict if cache is full
        if len(self._cache) >= self._max_cache_size:
            # Remove least recently accessed item
            oldest_key = min(self._cache_access_times, key=self._cache_access_times.get)
            del self._cache[oldest_key]
            del self._cache_access_times[oldest_key]
        
        self._cache[key] = (value, time.time())
        self._cache_access_times[key] = time.time()


class DataLineageTracker:
    """Advanced data lineage tracking and visualization"""
    
    def __init__(self, storage_manager: AdvancedStorageManager):
        self.storage_manager = storage_manager
        self.logger = logging.getLogger(__name__)
    
    async def trace_entity_lineage(self, entity_id: str) -> Dict[str, Any]:
        """Trace complete lineage for an entity with graph visualization"""
        
        # Get basic provenance
        provenance = await self.storage_manager.get_entity_provenance(entity_id)
        if not provenance:
            return {}
        
        # Build comprehensive lineage graph
        lineage_graph = await self._build_lineage_graph(entity_id)
        
        # Calculate lineage metrics
        metrics = self._calculate_lineage_metrics(lineage_graph, provenance)
        
        # Generate lineage summary
        summary = self._generate_lineage_summary(provenance, metrics)
        
        return {
            'entity_id': entity_id,
            'provenance': provenance,
            'lineage_graph': lineage_graph,
            'metrics': metrics,
            'summary': summary,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _build_lineage_graph(self, entity_id: str) -> Dict[str, Any]:
        """Build comprehensive lineage graph"""
        session = self.storage_manager.Session()
        
        try:
            nodes = []
            edges = []
            visited = set()
            
            # Start with the target entity
            await self._add_entity_to_graph(session, entity_id, nodes, edges, visited)
            
            return {
                'nodes': nodes,
                'edges': edges,
                'node_count': len(nodes),
                'edge_count': len(edges)
            }
            
        finally:
            session.close()
    
    async def _add_entity_to_graph(self, session, entity_id: str, nodes: List, edges: List, visited: Set):
        """Recursively add entity and its dependencies to graph"""
        if entity_id in visited:
            return
        
        visited.add(entity_id)
        
        # Get entity details
        entity = session.query(StructuredEntityModel).filter_by(entity_id=entity_id).first()
        if not entity:
            return
        
        # Add entity node
        nodes.append({
            'id': entity_id,
            'type': 'entity',
            'label': entity.canonical_name,
            'entity_type': entity.entity_type,
            'confidence': entity.confidence_score,
            'quality': entity.data_quality_score,
            'created_at': entity.extracted_at.isoformat(),
            'verification_status': entity.verification_status
        })
        
        # Get raw data sources
        mappings = session.query(RawToStructuredMappingModel).filter_by(entity_id=entity_id).all()
        
        for mapping in mappings:
            raw_data = session.query(RawDataModel).filter_by(raw_id=mapping.raw_id).first()
            if raw_data:
                raw_node_id = f"raw_{mapping.raw_id}"
                
                if raw_node_id not in [n['id'] for n in nodes]:
                    # Add raw data node
                    nodes.append({
                        'id': raw_node_id,
                        'type': 'raw_data',
                        'label': raw_data.source_url,
                        'domain': raw_data.source_domain,
                        'fetched_at': raw_data.fetched_at.isoformat(),
                        'job_id': raw_data.job_id,
                        'http_status': raw_data.http_status,
                        'quality_score': raw_data.content_quality_score
                    })
                
                # Add edge from raw data to entity
                edges.append({
                    'source': raw_node_id,
                    'target': entity_id,
                    'type': 'extracted_from',
                    'method': mapping.extraction_method,
                    'confidence': mapping.extraction_confidence,
                    'extractor': mapping.extractor_name,
                    'created_at': mapping.extracted_at.isoformat()
                })
        
        # Get relationships to other entities
        relationships = session.query(EntityRelationshipModel).filter(
            or_(
                EntityRelationshipModel.source_entity_id == entity_id,
                EntityRelationshipModel.target_entity_id == entity_id
            )
        ).all()
        
        for rel in relationships:
            other_entity_id = rel.target_entity_id if rel.source_entity_id == entity_id else rel.source_entity_id
            
            # Recursively add related entity (with depth limit)
            if len(visited) < 50:  # Prevent infinite recursion
                await self._add_entity_to_graph(session, other_entity_id, nodes, edges, visited)
            
            # Add relationship edge
            edges.append({
                'source': rel.source_entity_id,
                'target': rel.target_entity_id,
                'type': 'relationship',
                'relationship_type': rel.relationship_type,
                'strength': rel.strength,
                'confidence': rel.confidence,
                'is_directional': rel.is_directional,
                'created_at': rel.extracted_at.isoformat()
            })
    
    def _calculate_lineage_metrics(self, lineage_graph: Dict, provenance: Dict) -> Dict[str, Any]:
        """Calculate comprehensive lineage metrics"""
        
        nodes = lineage_graph['nodes']
        edges = lineage_graph['edges']
        
        # Node type distribution
        node_types = defaultdict(int)
        for node in nodes:
            node_types[node['type']] += 1
        
        # Edge type distribution
        edge_types = defaultdict(int)
        for edge in edges:
            edge_types[edge['type']] += 1
        
        # Quality metrics
        entity_nodes = [n for n in nodes if n['type'] == 'entity']
        raw_nodes = [n for n in nodes if n['type'] == 'raw_data']
        
        avg_entity_confidence = sum(n.get('confidence', 0) for n in entity_nodes) / len(entity_nodes) if entity_nodes else 0
        avg_entity_quality = sum(n.get('quality', 0) for n in entity_nodes) / len(entity_nodes) if entity_nodes else 0
        avg_raw_quality = sum(n.get('quality_score', 0) or 0 for n in raw_nodes) / len(raw_nodes) if raw_nodes else 0
        
        # Source diversity
        domains = set(n.get('domain', '') for n in raw_nodes if n.get('domain'))
        job_ids = set(n.get('job_id', '') for n in raw_nodes if n.get('job_id'))
        
        return {
            'graph_size': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'entity_nodes': len(entity_nodes),
                'raw_data_nodes': len(raw_nodes)
            },
            'node_types': dict(node_types),
            'edge_types': dict(edge_types),
            'quality_metrics': {
                'avg_entity_confidence': round(avg_entity_confidence, 3),
                'avg_entity_quality': round(avg_entity_quality, 3),
                'avg_raw_quality': round(avg_raw_quality, 3)
            },
            'source_diversity': {
                'unique_domains': len(domains),
                'unique_jobs': len(job_ids),
                'domains': list(domains),
                'job_ids': list(job_ids)
            }
        }
    
    def _generate_lineage_summary(self, provenance: Dict, metrics: Dict) -> Dict[str, Any]:
        """Generate human-readable lineage summary"""
        
        total_sources = provenance.get('total_sources', 0)
        total_relationships = provenance.get('total_relationships', 0)
        
        summary = {
            'overview': f"Entity traced through {total_sources} raw sources and {total_relationships} relationships",
            'data_quality': 'Good' if metrics['quality_metrics']['avg_entity_quality'] > 0.7 else 'Fair' if metrics['quality_metrics']['avg_entity_quality'] > 0.5 else 'Poor',
            'source_diversity': 'High' if metrics['source_diversity']['unique_domains'] > 5 else 'Medium' if metrics['source_diversity']['unique_domains'] > 2 else 'Low',
            'confidence_level': 'High' if metrics['quality_metrics']['avg_entity_confidence'] > 0.8 else 'Medium' if metrics['quality_metrics']['avg_entity_confidence'] > 0.6 else 'Low',
            'complexity': 'Complex' if metrics['graph_size']['total_nodes'] > 20 else 'Moderate' if metrics['graph_size']['total_nodes'] > 10 else 'Simple'
        }
        
        return summary
