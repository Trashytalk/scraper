"""Storage Layer Configuration"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
from enum import Enum


class StorageBackend(str, Enum):
    """Supported storage backends."""
    S3 = "s3"
    MINIO = "minio"
    LOCAL = "local"
    GCS = "gcs"
    AZURE = "azure"


class IndexingEngine(str, Enum):
    """Supported indexing/search engines."""
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    SOLR = "solr"
    WHOOSH = "whoosh"


class DatabaseBackend(str, Enum):
    """Supported database backends."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class StorageConfig(BaseSettings):
    """Configuration for the Storage/Indexing Layer."""
    
    # Raw Data Storage Configuration
    raw_storage_backend: StorageBackend = Field(
        default=StorageBackend.S3,
        env="STORAGE_RAW_BACKEND",
        description="Backend for raw data storage"
    )
    
    raw_storage_bucket: str = Field(
        default="business-intel-raw-data",
        env="STORAGE_RAW_BUCKET",
        description="Bucket/container name for raw data"
    )
    
    raw_storage_endpoint: Optional[str] = Field(
        default=None,
        env="STORAGE_RAW_ENDPOINT",
        description="Storage endpoint URL (for MinIO, custom S3)"
    )
    
    raw_storage_access_key: Optional[str] = Field(
        default=None,
        env="STORAGE_RAW_ACCESS_KEY",
        description="Storage access key"
    )
    
    raw_storage_secret_key: Optional[str] = Field(
        default=None,
        env="STORAGE_RAW_SECRET_KEY",
        description="Storage secret key"
    )
    
    raw_storage_region: str = Field(
        default="us-east-1",
        env="STORAGE_RAW_REGION",
        description="Storage region"
    )
    
    raw_storage_prefix: str = Field(
        default="raw-data",
        env="STORAGE_RAW_PREFIX",
        description="Prefix for raw data keys"
    )
    
    # Structured Database Configuration
    database_backend: DatabaseBackend = Field(
        default=DatabaseBackend.POSTGRESQL,
        env="STORAGE_DB_BACKEND",
        description="Database backend for structured data"
    )
    
    database_url: Optional[str] = Field(
        default=None,
        env="DATABASE_URL",
        description="Database connection URL"
    )
    
    database_host: str = Field(
        default="localhost",
        env="STORAGE_DB_HOST",
        description="Database host"
    )
    
    database_port: int = Field(
        default=5432,
        env="STORAGE_DB_PORT",
        description="Database port"
    )
    
    database_name: str = Field(
        default="business_intel",
        env="STORAGE_DB_NAME",
        description="Database name"
    )
    
    database_user: str = Field(
        default="postgres",
        env="STORAGE_DB_USER",
        description="Database user"
    )
    
    database_password: Optional[str] = Field(
        default=None,
        env="STORAGE_DB_PASSWORD",
        description="Database password"
    )
    
    database_pool_size: int = Field(
        default=10,
        env="STORAGE_DB_POOL_SIZE",
        description="Database connection pool size"
    )
    
    database_pool_overflow: int = Field(
        default=20,
        env="STORAGE_DB_POOL_OVERFLOW",
        description="Database connection pool overflow"
    )
    
    # Search/Indexing Configuration
    indexing_engine: IndexingEngine = Field(
        default=IndexingEngine.ELASTICSEARCH,
        env="STORAGE_INDEX_ENGINE",
        description="Search/indexing engine"
    )
    
    elasticsearch_url: str = Field(
        default="http://localhost:9200",
        env="ELASTICSEARCH_URL",
        description="Elasticsearch cluster URL"
    )
    
    elasticsearch_username: Optional[str] = Field(
        default=None,
        env="ELASTICSEARCH_USERNAME",
        description="Elasticsearch username"
    )
    
    elasticsearch_password: Optional[str] = Field(
        default=None,
        env="ELASTICSEARCH_PASSWORD",
        description="Elasticsearch password"
    )
    
    elasticsearch_timeout: int = Field(
        default=30,
        env="ELASTICSEARCH_TIMEOUT",
        description="Elasticsearch request timeout (seconds)"
    )
    
    elasticsearch_max_retries: int = Field(
        default=3,
        env="ELASTICSEARCH_MAX_RETRIES",
        description="Elasticsearch max retry attempts"
    )
    
    # Index Configuration
    raw_data_index_name: str = Field(
        default="business-intel-raw-data",
        env="STORAGE_RAW_INDEX",
        description="Elasticsearch index name for raw data"
    )
    
    entities_index_name: str = Field(
        default="business-intel-entities",
        env="STORAGE_ENTITIES_INDEX",
        description="Elasticsearch index name for entities"
    )
    
    relationships_index_name: str = Field(
        default="business-intel-relationships",
        env="STORAGE_RELATIONSHIPS_INDEX",
        description="Elasticsearch index name for relationships"
    )
    
    # Caching Configuration
    enable_caching: bool = Field(
        default=True,
        env="STORAGE_ENABLE_CACHING",
        description="Enable caching layer"
    )
    
    cache_backend: str = Field(
        default="redis",
        env="STORAGE_CACHE_BACKEND",
        description="Cache backend (redis, memory, memcached)"
    )
    
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    cache_ttl_seconds: int = Field(
        default=3600,
        env="STORAGE_CACHE_TTL",
        description="Default cache TTL in seconds"
    )
    
    # Data Quality Configuration
    enable_data_quality_checks: bool = Field(
        default=True,
        env="STORAGE_ENABLE_QUALITY_CHECKS",
        description="Enable data quality monitoring"
    )
    
    quality_check_interval_minutes: int = Field(
        default=60,
        env="STORAGE_QUALITY_CHECK_INTERVAL",
        description="Data quality check interval (minutes)"
    )
    
    min_quality_score_threshold: float = Field(
        default=0.7,
        env="STORAGE_MIN_QUALITY_SCORE",
        description="Minimum acceptable data quality score"
    )
    
    # Lineage Tracking Configuration
    enable_lineage_tracking: bool = Field(
        default=True,
        env="STORAGE_ENABLE_LINEAGE",
        description="Enable data lineage tracking"
    )
    
    lineage_max_depth: int = Field(
        default=10,
        env="STORAGE_LINEAGE_MAX_DEPTH",
        description="Maximum lineage tracking depth"
    )
    
    lineage_retention_days: int = Field(
        default=365,
        env="STORAGE_LINEAGE_RETENTION_DAYS",
        description="Lineage data retention period (days)"
    )
    
    # Storage Optimization Configuration
    enable_compression: bool = Field(
        default=True,
        env="STORAGE_ENABLE_COMPRESSION",
        description="Enable data compression"
    )
    
    compression_algorithm: str = Field(
        default="gzip",
        env="STORAGE_COMPRESSION_ALGORITHM",
        description="Compression algorithm (gzip, bzip2, lz4)"
    )
    
    enable_deduplication: bool = Field(
        default=True,
        env="STORAGE_ENABLE_DEDUPLICATION",
        description="Enable content deduplication"
    )
    
    deduplication_threshold: float = Field(
        default=0.95,
        env="STORAGE_DEDUPLICATION_THRESHOLD",
        description="Content similarity threshold for deduplication"
    )
    
    # Performance Configuration
    max_concurrent_operations: int = Field(
        default=10,
        env="STORAGE_MAX_CONCURRENT_OPS",
        description="Maximum concurrent storage operations"
    )
    
    batch_size: int = Field(
        default=100,
        env="STORAGE_BATCH_SIZE",
        description="Default batch size for bulk operations"
    )
    
    request_timeout_seconds: int = Field(
        default=60,
        env="STORAGE_REQUEST_TIMEOUT",
        description="Storage request timeout (seconds)"
    )
    
    # Monitoring Configuration
    enable_metrics: bool = Field(
        default=True,
        env="STORAGE_ENABLE_METRICS",
        description="Enable storage metrics collection"
    )
    
    metrics_collection_interval_seconds: int = Field(
        default=60,
        env="STORAGE_METRICS_INTERVAL",
        description="Metrics collection interval (seconds)"
    )
    
    enable_alerts: bool = Field(
        default=True,
        env="STORAGE_ENABLE_ALERTS",
        description="Enable storage alerting"
    )
    
    # Backup Configuration
    enable_backup: bool = Field(
        default=False,
        env="STORAGE_ENABLE_BACKUP",
        description="Enable automatic backup"
    )
    
    backup_schedule: str = Field(
        default="0 2 * * *",  # Daily at 2 AM
        env="STORAGE_BACKUP_SCHEDULE",
        description="Backup schedule (cron format)"
    )
    
    backup_retention_days: int = Field(
        default=30,
        env="STORAGE_BACKUP_RETENTION_DAYS",
        description="Backup retention period (days)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def database_connection_url(self) -> str:
        """Get the complete database connection URL."""
        if self.database_url:
            return self.database_url
        
        if self.database_backend == DatabaseBackend.POSTGRESQL:
            return (
                f"postgresql://{self.database_user}:{self.database_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
            )
        elif self.database_backend == DatabaseBackend.MYSQL:
            return (
                f"mysql://{self.database_user}:{self.database_password}"
                f"@{self.database_host}:{self.database_port}/{self.database_name}"
            )
        elif self.database_backend == DatabaseBackend.SQLITE:
            return f"sqlite:///./{self.database_name}.db"
        else:
            raise ValueError(f"Unsupported database backend: {self.database_backend}")
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage backend configuration."""
        config = {
            "backend": self.raw_storage_backend.value,
            "bucket": self.raw_storage_bucket,
            "prefix": self.raw_storage_prefix,
            "region": self.raw_storage_region,
        }
        
        if self.raw_storage_endpoint:
            config["endpoint"] = self.raw_storage_endpoint
        
        if self.raw_storage_access_key:
            config["access_key"] = self.raw_storage_access_key
        
        if self.raw_storage_secret_key:
            config["secret_key"] = self.raw_storage_secret_key
        
        return config
    
    def get_elasticsearch_config(self) -> Dict[str, Any]:
        """Get Elasticsearch configuration."""
        config = {
            "hosts": [self.elasticsearch_url],
            "timeout": self.elasticsearch_timeout,
            "max_retries": self.elasticsearch_max_retries,
        }
        
        if self.elasticsearch_username and self.elasticsearch_password:
            config["http_auth"] = (self.elasticsearch_username, self.elasticsearch_password)
        
        return config


# Global configuration instance
storage_config = StorageConfig()
