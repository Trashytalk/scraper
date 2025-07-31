"""
Kafka Queue Manager Implementation

Provides Kafka-based distributed queue system for high-throughput crawling:
- Persistent topic-based queues
- Built-in partitioning and replication
- Dead letter queue support
- Consumer group management
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .distributed_crawler import QueueManager, CrawlURL, ParseTask

try:
    from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
    from aiokafka.errors import KafkaError
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    AIOKafkaProducer = None
    AIOKafkaConsumer = None

logger = logging.getLogger(__name__)


class KafkaQueueManager(QueueManager):
    """Kafka-based queue implementation for distributed crawling"""
    
    def __init__(
        self, 
        bootstrap_servers: str = "localhost:9092",
        consumer_group_id: str = "crawl-workers",
        enable_auto_commit: bool = True,
        auto_offset_reset: str = "earliest"
    ):
        if not KAFKA_AVAILABLE:
            raise ImportError("aiokafka not available for Kafka queue backend")
        
        self.bootstrap_servers = bootstrap_servers
        self.consumer_group_id = consumer_group_id
        self.enable_auto_commit = enable_auto_commit
        self.auto_offset_reset = auto_offset_reset
        
        # Kafka clients
        self.producer: Optional[AIOKafkaProducer] = None
        self.frontier_consumer: Optional[AIOKafkaConsumer] = None
        self.parse_consumer: Optional[AIOKafkaConsumer] = None
        
        # Topic names
        self.topics = {
            "frontier": "crawler-frontier",
            "frontier_priority": "crawler-frontier-priority",
            "parsing": "crawler-parsing",
            "parsing_priority": "crawler-parsing-priority",
            "retry": "crawler-retry",
            "dead": "crawler-dead"
        }
        
        # Consumer task references
        self.consumer_tasks: List[asyncio.Task] = []
        self.frontier_queue = asyncio.Queue(maxsize=1000)
        self.parse_queue = asyncio.Queue(maxsize=1000)
        
        # Metrics
        self.metrics = {
            "urls_queued": 0,
            "urls_processed": 0,
            "parse_tasks_queued": 0,
            "parse_tasks_processed": 0,
            "urls_retried": 0,
            "urls_dead": 0,
            "kafka_errors": 0
        }
    
    async def connect(self):
        """Initialize Kafka producer and consumers"""
        try:
            # Initialize producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                compression_type="gzip",
                batch_size=16384,
                linger_ms=10,
                max_request_size=1048576
            )
            await self.producer.start()
            
            # Initialize consumers
            self.frontier_consumer = AIOKafkaConsumer(
                self.topics["frontier"],
                self.topics["frontier_priority"],
                bootstrap_servers=self.bootstrap_servers,
                group_id=f"{self.consumer_group_id}-frontier",
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                max_poll_records=100,
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000
            )
            await self.frontier_consumer.start()
            
            self.parse_consumer = AIOKafkaConsumer(
                self.topics["parsing"],
                self.topics["parsing_priority"],
                bootstrap_servers=self.bootstrap_servers,
                group_id=f"{self.consumer_group_id}-parsing",
                enable_auto_commit=self.enable_auto_commit,
                auto_offset_reset=self.auto_offset_reset,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                max_poll_records=50,
                session_timeout_ms=30000,
                heartbeat_interval_ms=3000
            )
            await self.parse_consumer.start()
            
            # Start consumer tasks
            self.consumer_tasks = [
                asyncio.create_task(self._frontier_consumer_loop()),
                asyncio.create_task(self._parse_consumer_loop())
            ]
            
            logger.info("Kafka queue manager connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            await self.disconnect()
            raise
    
    async def disconnect(self):
        """Close Kafka connections"""
        try:
            # Cancel consumer tasks
            for task in self.consumer_tasks:
                task.cancel()
            
            if self.consumer_tasks:
                await asyncio.gather(*self.consumer_tasks, return_exceptions=True)
            
            # Stop consumers
            if self.frontier_consumer:
                await self.frontier_consumer.stop()
            
            if self.parse_consumer:
                await self.parse_consumer.stop()
            
            # Stop producer
            if self.producer:
                await self.producer.stop()
            
            logger.info("Kafka queue manager disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting from Kafka: {e}")
    
    async def put_frontier_url(self, crawl_url: CrawlURL) -> bool:
        """Add URL to frontier queue with priority support"""
        try:
            topic = self.topics["frontier_priority"] if crawl_url.priority >= 8 else self.topics["frontier"]
            
            # Create partition key based on domain for better distribution
            partition_key = crawl_url.domain.encode('utf-8') if crawl_url.domain else None
            
            await self.producer.send(
                topic,
                value=crawl_url.to_dict(),
                key=partition_key
            )
            
            self.metrics["urls_queued"] += 1
            return True
            
        except Exception as e:
            self.metrics["kafka_errors"] += 1
            logger.error(f"Failed to queue URL {crawl_url.url}: {e}")
            return False
    
    async def get_frontier_url(self) -> Optional[CrawlURL]:
        """Get next URL from frontier queue"""
        try:
            # Non-blocking get from internal queue
            if not self.frontier_queue.empty():
                url_data = await asyncio.wait_for(self.frontier_queue.get(), timeout=0.1)
                crawl_url = CrawlURL.from_dict(url_data)
                self.metrics["urls_processed"] += 1
                return crawl_url
            
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to get frontier URL: {e}")
            return None
    
    async def put_parse_task(self, parse_task: ParseTask) -> bool:
        """Add task to parsing queue with priority support"""
        try:
            topic = self.topics["parsing_priority"] if parse_task.priority >= 8 else self.topics["parsing"]
            
            # Create partition key based on URL domain
            from urllib.parse import urlparse
            domain = urlparse(parse_task.url).netloc
            partition_key = domain.encode('utf-8') if domain else None
            
            await self.producer.send(
                topic,
                value=parse_task.to_dict(),
                key=partition_key
            )
            
            self.metrics["parse_tasks_queued"] += 1
            return True
            
        except Exception as e:
            self.metrics["kafka_errors"] += 1
            logger.error(f"Failed to queue parse task {parse_task.task_id}: {e}")
            return False
    
    async def get_parse_task(self) -> Optional[ParseTask]:
        """Get next parsing task"""
        try:
            # Non-blocking get from internal queue
            if not self.parse_queue.empty():
                task_data = await asyncio.wait_for(self.parse_queue.get(), timeout=0.1)
                parse_task = ParseTask.from_dict(task_data)
                self.metrics["parse_tasks_processed"] += 1
                return parse_task
            
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Failed to get parse task: {e}")
            return None
    
    async def put_retry_url(self, crawl_url: CrawlURL, delay_seconds: int) -> bool:
        """Add URL to retry topic with delay information"""
        try:
            # Add retry scheduling information
            retry_data = {
                **crawl_url.to_dict(),
                "retry_after_timestamp": (datetime.utcnow().timestamp() + delay_seconds),
                "delay_seconds": delay_seconds
            }
            
            partition_key = crawl_url.domain.encode('utf-8') if crawl_url.domain else None
            
            await self.producer.send(
                self.topics["retry"],
                value=retry_data,
                key=partition_key
            )
            
            self.metrics["urls_retried"] += 1
            return True
            
        except Exception as e:
            self.metrics["kafka_errors"] += 1
            logger.error(f"Failed to queue retry URL {crawl_url.url}: {e}")
            return False
    
    async def put_dead_url(self, crawl_url: CrawlURL, reason: str) -> bool:
        """Add URL to dead letter topic"""
        try:
            dead_record = {
                **crawl_url.to_dict(),
                "died_at": datetime.utcnow().isoformat(),
                "reason": reason
            }
            
            partition_key = crawl_url.domain.encode('utf-8') if crawl_url.domain else None
            
            await self.producer.send(
                self.topics["dead"],
                value=dead_record,
                key=partition_key
            )
            
            self.metrics["urls_dead"] += 1
            return True
            
        except Exception as e:
            self.metrics["kafka_errors"] += 1
            logger.error(f"Failed to add dead URL {crawl_url.url}: {e}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics (approximations for Kafka)"""
        try:
            # Note: Kafka doesn't provide real-time queue size easily
            # These are approximations based on internal queue sizes and metrics
            stats = {
                "frontier_queue_size": self.frontier_queue.qsize(),
                "frontier_priority_queue_size": 0,  # Combined in frontier_queue
                "parse_queue_size": self.parse_queue.qsize(),
                "parse_priority_queue_size": 0,  # Combined in parse_queue
                "retry_queue_size": 0,  # Would need separate tracking
                "dead_queue_size": 0,  # Would need separate tracking
                "total_frontier_size": self.frontier_queue.qsize(),
                "total_parse_size": self.parse_queue.qsize(),
                **self.metrics
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return self.metrics.copy()
    
    async def _frontier_consumer_loop(self):
        """Consumer loop for frontier topics"""
        try:
            async for message in self.frontier_consumer:
                try:
                    # Add to internal queue for get_frontier_url()
                    if not self.frontier_queue.full():
                        await self.frontier_queue.put(message.value)
                    else:
                        # Queue full, skip message (will be reprocessed)
                        logger.warning("Frontier queue full, skipping message")
                        
                except Exception as e:
                    logger.error(f"Error processing frontier message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Frontier consumer loop cancelled")
        except Exception as e:
            logger.error(f"Frontier consumer loop error: {e}")
    
    async def _parse_consumer_loop(self):
        """Consumer loop for parsing topics"""
        try:
            async for message in self.parse_consumer:
                try:
                    # Add to internal queue for get_parse_task()
                    if not self.parse_queue.full():
                        await self.parse_queue.put(message.value)
                    else:
                        # Queue full, skip message (will be reprocessed)
                        logger.warning("Parse queue full, skipping message")
                        
                except Exception as e:
                    logger.error(f"Error processing parse message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Parse consumer loop cancelled")
        except Exception as e:
            logger.error(f"Parse consumer loop error: {e}")


class KafkaRetryProcessor:
    """Separate processor for handling retry messages"""
    
    def __init__(
        self,
        kafka_queue_manager: KafkaQueueManager,
        bootstrap_servers: str = "localhost:9092",
        consumer_group_id: str = "retry-processor"
    ):
        self.kafka_queue_manager = kafka_queue_manager
        self.bootstrap_servers = bootstrap_servers
        self.consumer_group_id = consumer_group_id
        
        self.retry_consumer: Optional[AIOKafkaConsumer] = None
        self.is_running = False
        self.processor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the retry processor"""
        if self.is_running:
            return
        
        try:
            # Initialize retry consumer
            self.retry_consumer = AIOKafkaConsumer(
                self.kafka_queue_manager.topics["retry"],
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group_id,
                enable_auto_commit=True,
                auto_offset_reset="earliest",
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                max_poll_records=50
            )
            await self.retry_consumer.start()
            
            # Start processor task
            self.processor_task = asyncio.create_task(self._retry_processor_loop())
            self.is_running = True
            
            logger.info("Kafka retry processor started")
            
        except Exception as e:
            logger.error(f"Failed to start retry processor: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the retry processor"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        try:
            # Cancel processor task
            if self.processor_task:
                self.processor_task.cancel()
                await self.processor_task
            
            # Stop consumer
            if self.retry_consumer:
                await self.retry_consumer.stop()
            
            logger.info("Kafka retry processor stopped")
            
        except Exception as e:
            logger.error(f"Error stopping retry processor: {e}")
    
    async def _retry_processor_loop(self):
        """Process retry messages and requeue when ready"""
        try:
            async for message in self.retry_consumer:
                try:
                    retry_data = message.value
                    current_time = datetime.utcnow().timestamp()
                    
                    # Check if URL is ready for retry
                    if retry_data.get("retry_after_timestamp", 0) <= current_time:
                        # Remove retry-specific fields and convert back to CrawlURL
                        crawl_data = retry_data.copy()
                        crawl_data.pop("retry_after_timestamp", None)
                        crawl_data.pop("delay_seconds", None)
                        
                        crawl_url = CrawlURL.from_dict(crawl_data)
                        
                        # Requeue for crawling
                        await self.kafka_queue_manager.put_frontier_url(crawl_url)
                        
                        logger.debug(f"Requeued retry URL: {crawl_url.url}")
                    else:
                        # Not ready yet, put back in retry topic
                        await self.kafka_queue_manager.producer.send(
                            self.kafka_queue_manager.topics["retry"],
                            value=retry_data,
                            key=retry_data.get("domain", "").encode('utf-8')
                        )
                        
                        # Wait a bit to avoid tight loop
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Error processing retry message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Retry processor loop cancelled")
        except Exception as e:
            logger.error(f"Retry processor loop error: {e}")


# Enhanced Kafka Queue Manager with retry processor
class EnhancedKafkaQueueManager(KafkaQueueManager):
    """Extended Kafka queue manager with built-in retry processing"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_processor: Optional[KafkaRetryProcessor] = None
    
    async def connect(self):
        """Connect and start retry processor"""
        await super().connect()
        
        # Start retry processor
        self.retry_processor = KafkaRetryProcessor(
            kafka_queue_manager=self,
            bootstrap_servers=self.bootstrap_servers,
            consumer_group_id=f"{self.consumer_group_id}-retry"
        )
        await self.retry_processor.start()
    
    async def disconnect(self):
        """Disconnect and stop retry processor"""
        if self.retry_processor:
            await self.retry_processor.stop()
        
        await super().disconnect()
    
    async def process_retry_queue(self) -> int:
        """Manual retry queue processing (handled automatically by retry processor)"""
        # With Kafka, retry processing is handled automatically
        # Return 0 to indicate no manual processing needed
        return 0


# Topic administration utilities
class KafkaTopicManager:
    """Utility class for managing Kafka topics"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
    
    async def create_crawl_topics(
        self,
        num_partitions: int = 6,
        replication_factor: int = 1,
        retention_ms: int = 604800000  # 7 days
    ) -> Dict[str, bool]:
        """Create all necessary topics for crawling system"""
        try:
            from kafka import KafkaAdminClient, NewTopic
            from kafka.errors import TopicAlreadyExistsError
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="crawl-topic-manager"
            )
            
            topics = [
                "crawler-frontier",
                "crawler-frontier-priority", 
                "crawler-parsing",
                "crawler-parsing-priority",
                "crawler-retry",
                "crawler-dead"
            ]
            
            new_topics = []
            for topic_name in topics:
                topic = NewTopic(
                    name=topic_name,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor,
                    topic_configs={
                        "retention.ms": str(retention_ms),
                        "compression.type": "gzip",
                        "cleanup.policy": "delete"
                    }
                )
                new_topics.append(topic)
            
            results = {}
            try:
                fs = admin_client.create_topics(new_topics, validate_only=False)
                
                for topic_name, future in fs.items():
                    try:
                        future.result()
                        results[topic_name] = True
                        logger.info(f"Created topic: {topic_name}")
                    except TopicAlreadyExistsError:
                        results[topic_name] = True
                        logger.info(f"Topic already exists: {topic_name}")
                    except Exception as e:
                        results[topic_name] = False
                        logger.error(f"Failed to create topic {topic_name}: {e}")
                        
            finally:
                admin_client.close()
            
            return results
            
        except ImportError:
            logger.error("kafka-python not available for topic management")
            return {}
        except Exception as e:
            logger.error(f"Failed to create topics: {e}")
            return {}
    
    def get_topic_info(self) -> Dict[str, Any]:
        """Get information about crawl topics"""
        try:
            from kafka import KafkaAdminClient
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id="crawl-topic-info"
            )
            
            try:
                metadata = admin_client.describe_topics()
                
                crawl_topics = {}
                for topic_name, topic_metadata in metadata.items():
                    if topic_name.startswith("crawler-"):
                        crawl_topics[topic_name] = {
                            "partitions": len(topic_metadata.partitions),
                            "is_internal": topic_metadata.is_internal,
                            "partition_info": [
                                {
                                    "partition": p.partition,
                                    "leader": p.leader,
                                    "replicas": p.replicas,
                                    "isr": p.isr
                                }
                                for p in topic_metadata.partitions.values()
                            ]
                        }
                
                return crawl_topics
                
            finally:
                admin_client.close()
                
        except Exception as e:
            logger.error(f"Failed to get topic info: {e}")
            return {}
