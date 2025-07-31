"""
Distributed Queue Management System

This module provides a comprehensive distributed crawling and parsing queue system
with support for multiple queue backends (Redis, Kafka, SQS) and advanced features
like fault tolerance, retry mechanisms, and OCR integration.

Key Components:
- DistributedCrawlSystem: Main coordinator for the crawling system
- QueueManager: Abstract base for queue implementations
- CrawlWorker: Distributed workers for fetching web pages
- ParseWorker: Distributed workers for extracting URLs and content
- OCR integration for image and PDF processing
- Exponential backoff retry mechanisms
- Dead letter queues for failed URLs

Supported Queue Backends:
- Redis: High-performance in-memory queuing
- Kafka: High-throughput distributed streaming
- AWS SQS: Cloud-native managed queuing
- Memory: In-memory queuing for development

Usage:
    from business_intel_scraper.backend.queue import DistributedCrawlSystem, QueueBackend
    
    # Initialize system
    crawl_system = DistributedCrawlSystem(
        queue_backend=QueueBackend.REDIS,
        redis_url="redis://localhost:6379/0",
        num_crawl_workers=5,
        num_parse_workers=3
    )
    
    # Start the system
    await crawl_system.start()
    
    # Add seed URLs
    await crawl_system.add_seed_urls([
        "https://example.com",
        "https://business-directory.com"
    ], job_id="business-discovery")
    
    # Get statistics
    stats = await crawl_system.get_system_stats()
"""

from .distributed_crawler import (
    DistributedCrawlSystem,
    QueueManager,
    CrawlWorker,
    ParseWorker,
    CrawlURL,
    ParseTask,
    QueueBackend,
    URLStatus
)

from .api import router as queue_router

# Queue backend implementations
try:
    from .kafka_queue import KafkaQueueManager, EnhancedKafkaQueueManager, KafkaTopicManager
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    KafkaQueueManager = None
    EnhancedKafkaQueueManager = None
    KafkaTopicManager = None

try:
    from .sqs_queue import SQSQueueManager, EnhancedSQSQueueManager, SQSQueueSetup
    SQS_AVAILABLE = True
except ImportError:
    SQS_AVAILABLE = False
    SQSQueueManager = None
    EnhancedSQSQueueManager = None
    SQSQueueSetup = None

__all__ = [
    # Core components
    "DistributedCrawlSystem",
    "QueueManager", 
    "CrawlWorker",
    "ParseWorker",
    "CrawlURL",
    "ParseTask",
    "QueueBackend",
    "URLStatus",
    
    # API
    "queue_router",
    
    # Queue implementations
    "KafkaQueueManager",
    "EnhancedKafkaQueueManager", 
    "KafkaTopicManager",
    "SQSQueueManager",
    "EnhancedSQSQueueManager",
    "SQSQueueSetup",
    
    # Availability flags
    "KAFKA_AVAILABLE",
    "SQS_AVAILABLE"
]


def create_queue_manager(backend: QueueBackend, **kwargs) -> QueueManager:
    """Factory function to create queue manager based on backend type"""
    if backend == QueueBackend.REDIS:
        from .distributed_crawler import RedisQueueManager
        return RedisQueueManager(kwargs.get('redis_url', 'redis://localhost:6379/0'))
    
    elif backend == QueueBackend.KAFKA:
        if not KAFKA_AVAILABLE:
            raise ImportError("Kafka backend not available. Install aiokafka: pip install aiokafka")
        return EnhancedKafkaQueueManager(
            bootstrap_servers=kwargs.get('bootstrap_servers', 'localhost:9092'),
            consumer_group_id=kwargs.get('consumer_group_id', 'crawl-workers')
        )
    
    elif backend == QueueBackend.SQS:
        if not SQS_AVAILABLE:
            raise ImportError("SQS backend not available. Install aioboto3: pip install aioboto3")
        return EnhancedSQSQueueManager(
            region_name=kwargs.get('region_name', 'us-west-2'),
            aws_access_key_id=kwargs.get('aws_access_key_id'),
            aws_secret_access_key=kwargs.get('aws_secret_access_key'),
            queue_prefix=kwargs.get('queue_prefix', 'crawl-')
        )
    
    elif backend == QueueBackend.MEMORY:
        from .distributed_crawler import MemoryQueueManager
        return MemoryQueueManager()
    
    else:
        raise ValueError(f"Unsupported queue backend: {backend}")


def get_queue_recommendations() -> dict:
    """Get recommendations for queue backend selection"""
    return {
        "development": {
            "backend": QueueBackend.MEMORY,
            "description": "In-memory queuing for development and testing",
            "pros": ["No external dependencies", "Fast setup", "Good for testing"],
            "cons": ["Not persistent", "Single process only", "No fault tolerance"]
        },
        "small_scale": {
            "backend": QueueBackend.REDIS,
            "description": "Redis-based queuing for small to medium scale deployments",
            "pros": ["High performance", "Simple setup", "Good ecosystem", "Persistent"],
            "cons": ["Single point of failure", "Memory constraints", "Limited scaling"]
        },
        "high_throughput": {
            "backend": QueueBackend.KAFKA,
            "description": "Kafka-based queuing for high-throughput distributed systems",
            "pros": ["High throughput", "Horizontal scaling", "Fault tolerant", "Replay capability"],
            "cons": ["Complex setup", "Resource intensive", "Learning curve"]
        },
        "cloud_native": {
            "backend": QueueBackend.SQS,
            "description": "AWS SQS for cloud-native managed queuing",
            "pros": ["Fully managed", "Auto-scaling", "High availability", "Pay per use"],
            "cons": ["AWS vendor lock-in", "Potential costs", "Network latency"]
        }
    }


def get_system_requirements() -> dict:
    """Get system requirements for different queue backends"""
    return {
        "memory": {
            "external_services": [],
            "python_packages": [],
            "description": "No external dependencies required"
        },
        "redis": {
            "external_services": ["Redis Server"],
            "python_packages": ["redis[hiredis]", "aioredis"],
            "description": "Requires Redis server installation and Python Redis client"
        },
        "kafka": {
            "external_services": ["Apache Kafka", "Apache Zookeeper"],
            "python_packages": ["aiokafka", "kafka-python"],
            "description": "Requires Kafka cluster setup and Python Kafka client"
        },
        "sqs": {
            "external_services": ["AWS Account", "SQS Service"],
            "python_packages": ["aioboto3", "boto3"],
            "description": "Requires AWS account and proper IAM permissions for SQS"
        }
    }
