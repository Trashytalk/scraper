"""
Queue System Configuration

Centralized configuration management for the distributed crawling queue system.
Supports multiple backends and deployment environments.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class QueueBackend(str, Enum):
    """Supported queue backend types"""
    REDIS = "redis"
    KAFKA = "kafka"
    SQS = "sqs"
    MEMORY = "memory"


class OCREngine(str, Enum):
    """Supported OCR engines"""
    TESSERACT = "tesseract"
    AWS_TEXTRACT = "aws_textract"
    GOOGLE_VISION = "google_vision"


@dataclass
class RedisConfig:
    """Redis-specific configuration"""
    url: str = "redis://localhost:6379/0"
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_timeout: float = 30.0
    socket_connect_timeout: float = 30.0
    health_check_interval: int = 30


@dataclass
class KafkaConfig:
    """Kafka-specific configuration"""
    bootstrap_servers: str = "localhost:9092"
    client_id: str = "queue-system"
    group_id: str = "queue-workers"
    auto_offset_reset: str = "latest"
    enable_auto_commit: bool = True
    session_timeout_ms: int = 30000
    heartbeat_interval_ms: int = 3000
    max_poll_records: int = 500
    max_poll_interval_ms: int = 300000
    topic_config: Dict[str, Any] = field(default_factory=lambda: {
        'num_partitions': 6,
        'replication_factor': 1,
        'retention_ms': 604800000,  # 7 days
        'cleanup_policy': 'delete'
    })


@dataclass
class SQSConfig:
    """AWS SQS-specific configuration"""
    region_name: str = "us-west-2"
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    queue_prefix: str = "queue-system"
    visibility_timeout: int = 300
    message_retention_period: int = 1209600  # 14 days
    receive_message_wait_time: int = 20  # Long polling
    max_receive_count: int = 3
    enable_fifo: bool = False
    content_based_deduplication: bool = False


@dataclass
class WorkerConfig:
    """Worker configuration"""
    max_workers: int = 10
    worker_timeout: float = 300.0
    heartbeat_interval: float = 30.0
    task_timeout: float = 180.0
    graceful_shutdown_timeout: float = 60.0
    max_tasks_per_worker: int = 1000
    restart_on_failure: bool = True


@dataclass
class CrawlConfig:
    """Crawling configuration"""
    num_crawl_workers: int = 5
    crawl_delay: float = 1.0
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay_base: float = 2.0
    retry_delay_max: float = 300.0
    max_depth: int = 3
    max_pages_per_domain: int = 1000
    respect_robots_txt: bool = True
    user_agent: str = "BusinessIntelScraper/1.0"
    max_concurrent_requests: int = 10
    max_content_size: int = 10 * 1024 * 1024  # 10MB


@dataclass
class ParseConfig:
    """Parsing configuration"""
    num_parse_workers: int = 3
    parse_timeout: float = 60.0
    max_extracted_urls: int = 500
    enable_ocr: bool = True
    ocr_engines: List[OCREngine] = field(default_factory=lambda: [OCREngine.TESSERACT])
    image_max_size: int = 5 * 1024 * 1024  # 5MB
    pdf_max_pages: int = 50
    text_extraction_timeout: float = 120.0


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = "postgresql://user:password@localhost:5432/business_intel"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class StorageConfig:
    """Storage configuration"""
    type: str = "s3"  # s3, minio, local
    endpoint: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bucket: str = "business-intel-storage"
    region: str = "us-west-2"
    prefix: str = "queue-system"
    local_path: str = "./storage"


@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    enable_metrics: bool = True
    metrics_port: int = 8080
    log_level: str = "INFO"
    log_format: str = "json"
    enable_health_checks: bool = True
    health_check_interval: float = 30.0
    enable_performance_monitoring: bool = True
    slow_query_threshold: float = 5.0


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_auth: bool = False
    api_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    jwt_expiry: int = 3600
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600


@dataclass
class QueueSystemConfig:
    """Main queue system configuration"""
    # Core settings
    queue_backend: QueueBackend = QueueBackend.REDIS
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    # Backend-specific configs
    redis: RedisConfig = field(default_factory=RedisConfig)
    kafka: KafkaConfig = field(default_factory=KafkaConfig)
    sqs: SQSConfig = field(default_factory=SQSConfig)
    
    # Component configs
    worker: WorkerConfig = field(default_factory=WorkerConfig)
    crawl: CrawlConfig = field(default_factory=CrawlConfig)
    parse: ParseConfig = field(default_factory=ParseConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    @classmethod
    def from_env(cls) -> 'QueueSystemConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Core settings
        config.queue_backend = QueueBackend(os.getenv("QUEUE_BACKEND", "redis"))
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Redis config
        if redis_url := os.getenv("REDIS_URL"):
            config.redis.url = redis_url
        config.redis.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
        
        # Kafka config
        if kafka_servers := os.getenv("KAFKA_BOOTSTRAP_SERVERS"):
            config.kafka.bootstrap_servers = kafka_servers
        config.kafka.group_id = os.getenv("KAFKA_GROUP_ID", "queue-workers")
        
        # SQS config
        if aws_region := os.getenv("AWS_REGION"):
            config.sqs.region_name = aws_region
        if aws_access_key := os.getenv("AWS_ACCESS_KEY_ID"):
            config.sqs.access_key_id = aws_access_key
        if aws_secret_key := os.getenv("AWS_SECRET_ACCESS_KEY"):
            config.sqs.secret_access_key = aws_secret_key
        
        # Worker config
        config.crawl.num_crawl_workers = int(os.getenv("NUM_CRAWL_WORKERS", "5"))
        config.parse.num_parse_workers = int(os.getenv("NUM_PARSE_WORKERS", "3"))
        
        # Database config
        if db_url := os.getenv("DATABASE_URL"):
            config.database.url = db_url
        
        # Storage config
        config.storage.type = os.getenv("STORAGE_TYPE", "s3")
        if s3_endpoint := os.getenv("S3_ENDPOINT"):
            config.storage.endpoint = s3_endpoint
        if s3_access_key := os.getenv("S3_ACCESS_KEY"):
            config.storage.access_key = s3_access_key
        if s3_secret_key := os.getenv("S3_SECRET_KEY"):
            config.storage.secret_key = s3_secret_key
        if s3_bucket := os.getenv("S3_BUCKET"):
            config.storage.bucket = s3_bucket
        
        # Security config
        config.security.enable_auth = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        if api_key := os.getenv("API_KEY"):
            config.security.api_key = api_key
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'QueueSystemConfig':
        """Load configuration from file (JSON or YAML)"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            if config_file.suffix.lower() in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueSystemConfig':
        """Create configuration from dictionary"""
        config = cls()
        
        # Core settings
        if "queue_backend" in data:
            config.queue_backend = QueueBackend(data["queue_backend"])
        if "environment" in data:
            config.environment = data["environment"]
        if "debug" in data:
            config.debug = data["debug"]
        
        # Backend configs
        if "redis" in data:
            config.redis = RedisConfig(**data["redis"])
        if "kafka" in data:
            config.kafka = KafkaConfig(**data["kafka"])
        if "sqs" in data:
            config.sqs = SQSConfig(**data["sqs"])
        
        # Component configs
        if "worker" in data:
            config.worker = WorkerConfig(**data["worker"])
        if "crawl" in data:
            config.crawl = CrawlConfig(**data["crawl"])
        if "parse" in data:
            # Handle OCR engines enum conversion
            parse_data = data["parse"].copy()
            if "ocr_engines" in parse_data:
                parse_data["ocr_engines"] = [OCREngine(engine) for engine in parse_data["ocr_engines"]]
            config.parse = ParseConfig(**parse_data)
        if "database" in data:
            config.database = DatabaseConfig(**data["database"])
        if "storage" in data:
            config.storage = StorageConfig(**data["storage"])
        if "monitoring" in data:
            config.monitoring = MonitoringConfig(**data["monitoring"])
        if "security" in data:
            config.security = SecurityConfig(**data["security"])
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "queue_backend": self.queue_backend.value,
            "environment": self.environment,
            "debug": self.debug,
            "redis": {
                "url": self.redis.url,
                "max_connections": self.redis.max_connections,
                "retry_on_timeout": self.redis.retry_on_timeout,
                "socket_timeout": self.redis.socket_timeout,
                "socket_connect_timeout": self.redis.socket_connect_timeout,
                "health_check_interval": self.redis.health_check_interval
            },
            "kafka": {
                "bootstrap_servers": self.kafka.bootstrap_servers,
                "client_id": self.kafka.client_id,
                "group_id": self.kafka.group_id,
                "auto_offset_reset": self.kafka.auto_offset_reset,
                "enable_auto_commit": self.kafka.enable_auto_commit,
                "session_timeout_ms": self.kafka.session_timeout_ms,
                "heartbeat_interval_ms": self.kafka.heartbeat_interval_ms,
                "max_poll_records": self.kafka.max_poll_records,
                "max_poll_interval_ms": self.kafka.max_poll_interval_ms,
                "topic_config": self.kafka.topic_config
            },
            "sqs": {
                "region_name": self.sqs.region_name,
                "access_key_id": self.sqs.access_key_id,
                "secret_access_key": self.sqs.secret_access_key,
                "endpoint_url": self.sqs.endpoint_url,
                "queue_prefix": self.sqs.queue_prefix,
                "visibility_timeout": self.sqs.visibility_timeout,
                "message_retention_period": self.sqs.message_retention_period,
                "receive_message_wait_time": self.sqs.receive_message_wait_time,
                "max_receive_count": self.sqs.max_receive_count,
                "enable_fifo": self.sqs.enable_fifo,
                "content_based_deduplication": self.sqs.content_based_deduplication
            },
            "worker": {
                "max_workers": self.worker.max_workers,
                "worker_timeout": self.worker.worker_timeout,
                "heartbeat_interval": self.worker.heartbeat_interval,
                "task_timeout": self.worker.task_timeout,
                "graceful_shutdown_timeout": self.worker.graceful_shutdown_timeout,
                "max_tasks_per_worker": self.worker.max_tasks_per_worker,
                "restart_on_failure": self.worker.restart_on_failure
            },
            "crawl": {
                "num_crawl_workers": self.crawl.num_crawl_workers,
                "crawl_delay": self.crawl.crawl_delay,
                "timeout": self.crawl.timeout,
                "max_retries": self.crawl.max_retries,
                "retry_delay_base": self.crawl.retry_delay_base,
                "retry_delay_max": self.crawl.retry_delay_max,
                "max_depth": self.crawl.max_depth,
                "max_pages_per_domain": self.crawl.max_pages_per_domain,
                "respect_robots_txt": self.crawl.respect_robots_txt,
                "user_agent": self.crawl.user_agent,
                "max_concurrent_requests": self.crawl.max_concurrent_requests,
                "max_content_size": self.crawl.max_content_size
            },
            "parse": {
                "num_parse_workers": self.parse.num_parse_workers,
                "parse_timeout": self.parse.parse_timeout,
                "max_extracted_urls": self.parse.max_extracted_urls,
                "enable_ocr": self.parse.enable_ocr,
                "ocr_engines": [engine.value for engine in self.parse.ocr_engines],
                "image_max_size": self.parse.image_max_size,
                "pdf_max_pages": self.parse.pdf_max_pages,
                "text_extraction_timeout": self.parse.text_extraction_timeout
            },
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow,
                "pool_timeout": self.database.pool_timeout,
                "pool_recycle": self.database.pool_recycle,
                "echo": self.database.echo
            },
            "storage": {
                "type": self.storage.type,
                "endpoint": self.storage.endpoint,
                "access_key": self.storage.access_key,
                "secret_key": self.storage.secret_key,
                "bucket": self.storage.bucket,
                "region": self.storage.region,
                "prefix": self.storage.prefix,
                "local_path": self.storage.local_path
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "metrics_port": self.monitoring.metrics_port,
                "log_level": self.monitoring.log_level,
                "log_format": self.monitoring.log_format,
                "enable_health_checks": self.monitoring.enable_health_checks,
                "health_check_interval": self.monitoring.health_check_interval,
                "enable_performance_monitoring": self.monitoring.enable_performance_monitoring,
                "slow_query_threshold": self.monitoring.slow_query_threshold
            },
            "security": {
                "enable_auth": self.security.enable_auth,
                "api_key": self.security.api_key,
                "jwt_secret": self.security.jwt_secret,
                "jwt_expiry": self.security.jwt_expiry,
                "allowed_origins": self.security.allowed_origins,
                "rate_limit_enabled": self.security.rate_limit_enabled,
                "rate_limit_requests": self.security.rate_limit_requests,
                "rate_limit_window": self.security.rate_limit_window
            }
        }
    
    def save_to_file(self, config_path: str, format: str = "yaml"):
        """Save configuration to file"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        with open(config_file, 'w') as f:
            if format.lower() == "yaml":
                yaml.safe_dump(data, f, default_flow_style=False, indent=2)
            else:
                json.dump(data, f, indent=2)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        
        # Validate queue backend requirements
        if self.queue_backend == QueueBackend.REDIS:
            if not self.redis.url:
                errors.append("Redis URL is required when using Redis backend")
        elif self.queue_backend == QueueBackend.KAFKA:
            if not self.kafka.bootstrap_servers:
                errors.append("Kafka bootstrap servers are required when using Kafka backend")
        elif self.queue_backend == QueueBackend.SQS:
            if not self.sqs.region_name:
                errors.append("AWS region is required when using SQS backend")
        
        # Validate worker counts
        if self.crawl.num_crawl_workers <= 0:
            errors.append("Number of crawl workers must be positive")
        if self.parse.num_parse_workers <= 0:
            errors.append("Number of parse workers must be positive")
        
        # Validate database URL
        if not self.database.url:
            errors.append("Database URL is required")
        
        # Validate storage configuration
        if self.storage.type == "s3" and not self.storage.bucket:
            errors.append("S3 bucket name is required when using S3 storage")
        
        return errors


# Predefined configuration templates

def get_development_config() -> QueueSystemConfig:
    """Get configuration optimized for development"""
    config = QueueSystemConfig()
    config.environment = "development"
    config.debug = True
    config.queue_backend = QueueBackend.MEMORY
    config.crawl.num_crawl_workers = 2
    config.parse.num_parse_workers = 1
    config.crawl.crawl_delay = 0.5
    config.monitoring.log_level = "DEBUG"
    return config


def get_testing_config() -> QueueSystemConfig:
    """Get configuration optimized for testing"""
    config = QueueSystemConfig()
    config.environment = "testing"
    config.debug = True
    config.queue_backend = QueueBackend.MEMORY
    config.crawl.num_crawl_workers = 1
    config.parse.num_parse_workers = 1
    config.crawl.max_retries = 1
    config.crawl.timeout = 10.0
    config.database.url = "postgresql://test:test@localhost:5432/test_business_intel"
    return config


def get_production_config() -> QueueSystemConfig:
    """Get configuration optimized for production"""
    config = QueueSystemConfig()
    config.environment = "production"
    config.debug = False
    config.queue_backend = QueueBackend.REDIS
    config.crawl.num_crawl_workers = 10
    config.parse.num_parse_workers = 5
    config.crawl.crawl_delay = 1.0
    config.monitoring.log_level = "INFO"
    config.monitoring.enable_metrics = True
    config.security.enable_auth = True
    config.security.rate_limit_enabled = True
    return config


def get_high_throughput_config() -> QueueSystemConfig:
    """Get configuration optimized for high-throughput scenarios"""
    config = QueueSystemConfig()
    config.environment = "production"
    config.debug = False
    config.queue_backend = QueueBackend.KAFKA
    config.crawl.num_crawl_workers = 20
    config.parse.num_parse_workers = 10
    config.crawl.crawl_delay = 0.5
    config.crawl.max_concurrent_requests = 50
    config.kafka.topic_config['num_partitions'] = 12
    config.monitoring.enable_performance_monitoring = True
    return config


# Configuration factory
def create_config(
    template: str = "development",
    config_file: Optional[str] = None,
    env_override: bool = True
) -> QueueSystemConfig:
    """
    Create configuration using template, file, and environment variables
    
    Args:
        template: Configuration template ('development', 'testing', 'production', 'high_throughput')
        config_file: Path to configuration file (optional)
        env_override: Whether to override with environment variables
    
    Returns:
        Configured QueueSystemConfig instance
    """
    # Start with template
    if template == "development":
        config = get_development_config()
    elif template == "testing":
        config = get_testing_config()
    elif template == "production":
        config = get_production_config()
    elif template == "high_throughput":
        config = get_high_throughput_config()
    else:
        config = QueueSystemConfig()
    
    # Override with file if provided
    if config_file and Path(config_file).exists():
        file_config = QueueSystemConfig.from_file(config_file)
        # Merge file config with template
        # This is a simplified merge - in practice, you might want more sophisticated merging
        config = file_config
    
    # Override with environment variables if requested
    if env_override:
        env_config = QueueSystemConfig.from_env()
        # Apply environment overrides
        # This is simplified - you might want to merge more selectively
        if os.getenv("QUEUE_BACKEND"):
            config.queue_backend = env_config.queue_backend
        if os.getenv("DATABASE_URL"):
            config.database = env_config.database
        if os.getenv("REDIS_URL"):
            config.redis = env_config.redis
        # Add more specific overrides as needed
    
    return config
