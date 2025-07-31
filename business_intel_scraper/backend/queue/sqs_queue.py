"""
AWS SQS Queue Manager Implementation

Provides AWS SQS-based distributed queue system for cloud-native crawling:
- Standard and FIFO queue support
- Dead letter queues with automatic retry
- Delay queues for retry mechanisms
- CloudWatch integration for monitoring
"""

import asyncio
import json
import logging
import boto3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse

from .distributed_crawler import QueueManager, CrawlURL, ParseTask

try:
    import aioboto3
    SQS_AVAILABLE = True
except ImportError:
    SQS_AVAILABLE = False
    aioboto3 = None

logger = logging.getLogger(__name__)


class SQSQueueManager(QueueManager):
    """AWS SQS-based queue implementation for distributed crawling"""
    
    def __init__(
        self,
        region_name: str = "us-west-2",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        queue_prefix: str = "crawl-"
    ):
        if not SQS_AVAILABLE:
            raise ImportError("aioboto3 not available for SQS queue backend")
        
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.queue_prefix = queue_prefix
        
        # SQS client
        self.sqs_client = None
        self.session = None
        
        # Queue URLs (populated during connection)
        self.queue_urls = {}
        
        # Queue names
        self.queue_names = {
            "frontier": f"{queue_prefix}frontier",
            "frontier_priority": f"{queue_prefix}frontier-priority.fifo",
            "parsing": f"{queue_prefix}parsing",
            "parsing_priority": f"{queue_prefix}parsing-priority.fifo",
            "retry": f"{queue_prefix}retry",
            "dead": f"{queue_prefix}dead"
        }
        
        # Metrics
        self.metrics = {
            "urls_queued": 0,
            "urls_processed": 0,
            "parse_tasks_queued": 0,
            "parse_tasks_processed": 0,
            "urls_retried": 0,
            "urls_dead": 0,
            "sqs_errors": 0
        }
    
    async def connect(self):
        """Initialize SQS client and ensure queues exist"""
        try:
            # Create aioboto3 session
            self.session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Initialize SQS client
            self.sqs_client = self.session.client('sqs')
            
            # Ensure all queues exist
            await self._ensure_queues_exist()
            
            logger.info("SQS queue manager connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to SQS: {e}")
            await self.disconnect()
            raise
    
    async def disconnect(self):
        """Close SQS connections"""
        try:
            if self.sqs_client:
                await self.sqs_client.close()
            
            logger.info("SQS queue manager disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting from SQS: {e}")
    
    async def _ensure_queues_exist(self):
        """Create SQS queues if they don't exist"""
        async with self.sqs_client as sqs:
            for queue_type, queue_name in self.queue_names.items():
                try:
                    # Check if queue exists
                    try:
                        response = await sqs.get_queue_url(QueueName=queue_name)
                        self.queue_urls[queue_type] = response['QueueUrl']
                        logger.info(f"Found existing queue: {queue_name}")
                        continue
                    except sqs.exceptions.QueueDoesNotExist:
                        pass
                    
                    # Create queue with appropriate configuration
                    attributes = self._get_queue_attributes(queue_type, queue_name)
                    
                    if queue_name.endswith('.fifo'):
                        # FIFO queue
                        response = await sqs.create_queue(
                            QueueName=queue_name,
                            Attributes=attributes
                        )
                    else:
                        # Standard queue
                        response = await sqs.create_queue(
                            QueueName=queue_name,
                            Attributes=attributes
                        )
                    
                    self.queue_urls[queue_type] = response['QueueUrl']
                    logger.info(f"Created queue: {queue_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to create/access queue {queue_name}: {e}")
                    raise
    
    def _get_queue_attributes(self, queue_type: str, queue_name: str) -> Dict[str, str]:
        """Get queue attributes based on queue type"""
        base_attributes = {
            "MessageRetentionPeriod": "1209600",  # 14 days
            "VisibilityTimeoutSeconds": "300",    # 5 minutes
            "ReceiveMessageWaitTimeSeconds": "20" # Long polling
        }
        
        if queue_name.endswith('.fifo'):
            # FIFO queue attributes
            base_attributes.update({
                "FifoQueue": "true",
                "ContentBasedDeduplication": "true"
            })
        
        if queue_type == "retry":
            # Delay queue for retries
            base_attributes.update({
                "DelaySeconds": "60",  # 1 minute default delay
                "MaxReceiveCount": "3"
            })
        
        if queue_type == "dead":
            # Dead letter queue
            base_attributes.update({
                "MessageRetentionPeriod": "1209600"  # Longer retention for dead letters
            })
        
        # Configure dead letter queue for main queues
        if queue_type in ["frontier", "parsing"] and "dead" in self.queue_urls:
            base_attributes.update({
                "RedrivePolicy": json.dumps({
                    "deadLetterTargetArn": self._get_queue_arn("dead"),
                    "maxReceiveCount": 3
                })
            })
        
        return base_attributes
    
    def _get_queue_arn(self, queue_type: str) -> str:
        """Generate queue ARN from URL"""
        queue_url = self.queue_urls.get(queue_type, "")
        # Extract queue name from URL
        queue_name = queue_url.split('/')[-1] if queue_url else ""
        return f"arn:aws:sqs:{self.region_name}:*:{queue_name}"
    
    async def put_frontier_url(self, crawl_url: CrawlURL) -> bool:
        """Add URL to frontier queue with priority support"""
        try:
            queue_type = "frontier_priority" if crawl_url.priority >= 8 else "frontier"
            queue_url = self.queue_urls[queue_type]
            
            message_body = json.dumps(crawl_url.to_dict())
            
            async with self.sqs_client as sqs:
                if queue_type == "frontier_priority":
                    # FIFO queue requires MessageGroupId
                    await sqs.send_message(
                        QueueUrl=queue_url,
                        MessageBody=message_body,
                        MessageGroupId=crawl_url.domain or "default",
                        MessageDeduplicationId=f"{crawl_url.url}-{crawl_url.created_at.isoformat()}"
                    )
                else:
                    # Standard queue
                    await sqs.send_message(
                        QueueUrl=queue_url,
                        MessageBody=message_body,
                        MessageAttributes={
                            'Priority': {
                                'StringValue': str(crawl_url.priority),
                                'DataType': 'Number'
                            },
                            'Domain': {
                                'StringValue': crawl_url.domain or "unknown",
                                'DataType': 'String'
                            }
                        }
                    )
            
            self.metrics["urls_queued"] += 1
            return True
            
        except Exception as e:
            self.metrics["sqs_errors"] += 1
            logger.error(f"Failed to queue URL {crawl_url.url}: {e}")
            return False
    
    async def get_frontier_url(self) -> Optional[CrawlURL]:
        """Get next URL from frontier queue (priority first)"""
        try:
            # Check priority queue first
            for queue_type in ["frontier_priority", "frontier"]:
                queue_url = self.queue_urls[queue_type]
                
                async with self.sqs_client as sqs:
                    response = await sqs.receive_message(
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=1,
                        WaitTimeSeconds=1  # Short polling for responsiveness
                    )
                    
                    if 'Messages' in response:
                        message = response['Messages'][0]
                        
                        # Parse message
                        crawl_url = CrawlURL.from_dict(json.loads(message['Body']))
                        
                        # Delete message from queue
                        await sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        
                        self.metrics["urls_processed"] += 1
                        return crawl_url
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get frontier URL: {e}")
            return None
    
    async def put_parse_task(self, parse_task: ParseTask) -> bool:
        """Add task to parsing queue with priority support"""
        try:
            queue_type = "parsing_priority" if parse_task.priority >= 8 else "parsing"
            queue_url = self.queue_urls[queue_type]
            
            message_body = json.dumps(parse_task.to_dict())
            
            async with self.sqs_client as sqs:
                if queue_type == "parsing_priority":
                    # FIFO queue
                    domain = urlparse(parse_task.url).netloc
                    await sqs.send_message(
                        QueueUrl=queue_url,
                        MessageBody=message_body,
                        MessageGroupId=domain or "default",
                        MessageDeduplicationId=parse_task.task_id
                    )
                else:
                    # Standard queue
                    await sqs.send_message(
                        QueueUrl=queue_url,
                        MessageBody=message_body,
                        MessageAttributes={
                            'Priority': {
                                'StringValue': str(parse_task.priority),
                                'DataType': 'Number'
                            },
                            'RequiresOCR': {
                                'StringValue': str(parse_task.requires_ocr),
                                'DataType': 'String'
                            }
                        }
                    )
            
            self.metrics["parse_tasks_queued"] += 1
            return True
            
        except Exception as e:
            self.metrics["sqs_errors"] += 1
            logger.error(f"Failed to queue parse task {parse_task.task_id}: {e}")
            return False
    
    async def get_parse_task(self) -> Optional[ParseTask]:
        """Get next parsing task (priority first)"""
        try:
            # Check priority queue first
            for queue_type in ["parsing_priority", "parsing"]:
                queue_url = self.queue_urls[queue_type]
                
                async with self.sqs_client as sqs:
                    response = await sqs.receive_message(
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=1,
                        WaitTimeSeconds=1
                    )
                    
                    if 'Messages' in response:
                        message = response['Messages'][0]
                        
                        # Parse message
                        parse_task = ParseTask.from_dict(json.loads(message['Body']))
                        
                        # Delete message from queue
                        await sqs.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        
                        self.metrics["parse_tasks_processed"] += 1
                        return parse_task
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get parse task: {e}")
            return None
    
    async def put_retry_url(self, crawl_url: CrawlURL, delay_seconds: int) -> bool:
        """Add URL to retry queue with delay"""
        try:
            queue_url = self.queue_urls["retry"]
            
            retry_data = {
                **crawl_url.to_dict(),
                "retry_after": (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat(),
                "original_delay_seconds": delay_seconds
            }
            
            message_body = json.dumps(retry_data)
            
            async with self.sqs_client as sqs:
                await sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message_body,
                    DelaySeconds=min(delay_seconds, 900),  # SQS max delay is 15 minutes
                    MessageAttributes={
                        'RetryCount': {
                            'StringValue': str(crawl_url.retry_count),
                            'DataType': 'Number'
                        },
                        'Domain': {
                            'StringValue': crawl_url.domain or "unknown",
                            'DataType': 'String'
                        }
                    }
                )
            
            self.metrics["urls_retried"] += 1
            return True
            
        except Exception as e:
            self.metrics["sqs_errors"] += 1
            logger.error(f"Failed to queue retry URL {crawl_url.url}: {e}")
            return False
    
    async def put_dead_url(self, crawl_url: CrawlURL, reason: str) -> bool:
        """Add URL to dead letter queue"""
        try:
            queue_url = self.queue_urls["dead"]
            
            dead_record = {
                **crawl_url.to_dict(),
                "died_at": datetime.utcnow().isoformat(),
                "reason": reason
            }
            
            message_body = json.dumps(dead_record)
            
            async with self.sqs_client as sqs:
                await sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=message_body,
                    MessageAttributes={
                        'Reason': {
                            'StringValue': reason,
                            'DataType': 'String'
                        },
                        'Domain': {
                            'StringValue': crawl_url.domain or "unknown",
                            'DataType': 'String'
                        },
                        'FinalRetryCount': {
                            'StringValue': str(crawl_url.retry_count),
                            'DataType': 'Number'
                        }
                    }
                )
            
            self.metrics["urls_dead"] += 1
            return True
            
        except Exception as e:
            self.metrics["sqs_errors"] += 1
            logger.error(f"Failed to add dead URL {crawl_url.url}: {e}")
            return False
    
    async def get_queue_stats(self) -> Dict[str, int]:
        """Get queue statistics from SQS"""
        try:
            stats = self.metrics.copy()
            
            async with self.sqs_client as sqs:
                for queue_type, queue_url in self.queue_urls.items():
                    try:
                        response = await sqs.get_queue_attributes(
                            QueueUrl=queue_url,
                            AttributeNames=[
                                'ApproximateNumberOfMessages',
                                'ApproximateNumberOfMessagesNotVisible',
                                'ApproximateNumberOfMessagesDelayed'
                            ]
                        )
                        
                        attributes = response.get('Attributes', {})
                        queue_size = int(attributes.get('ApproximateNumberOfMessages', 0))
                        
                        if queue_type == "frontier":
                            stats["frontier_queue_size"] = queue_size
                        elif queue_type == "frontier_priority":
                            stats["frontier_priority_queue_size"] = queue_size
                        elif queue_type == "parsing":
                            stats["parse_queue_size"] = queue_size
                        elif queue_type == "parsing_priority":
                            stats["parse_priority_queue_size"] = queue_size
                        elif queue_type == "retry":
                            stats["retry_queue_size"] = queue_size
                        elif queue_type == "dead":
                            stats["dead_queue_size"] = queue_size
                            
                    except Exception as e:
                        logger.warning(f"Failed to get stats for queue {queue_type}: {e}")
            
            # Calculate totals
            stats["total_frontier_size"] = (
                stats.get("frontier_queue_size", 0) + 
                stats.get("frontier_priority_queue_size", 0)
            )
            stats["total_parse_size"] = (
                stats.get("parse_queue_size", 0) + 
                stats.get("parse_priority_queue_size", 0)
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return self.metrics.copy()
    
    async def process_retry_queue(self) -> int:
        """Process retry queue to requeue URLs ready for retry"""
        try:
            queue_url = self.queue_urls["retry"]
            processed = 0
            
            async with self.sqs_client as sqs:
                # Poll retry queue for ready messages
                while True:
                    response = await sqs.receive_message(
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=10,
                        WaitTimeSeconds=1
                    )
                    
                    if 'Messages' not in response:
                        break
                    
                    for message in response['Messages']:
                        try:
                            retry_data = json.loads(message['Body'])
                            
                            # Check if ready for retry
                            retry_after = datetime.fromisoformat(retry_data.get('retry_after', ''))
                            if datetime.utcnow() >= retry_after:
                                # Remove retry-specific fields
                                crawl_data = retry_data.copy()
                                crawl_data.pop('retry_after', None)
                                crawl_data.pop('original_delay_seconds', None)
                                
                                crawl_url = CrawlURL.from_dict(crawl_data)
                                
                                # Requeue for crawling
                                if await self.put_frontier_url(crawl_url):
                                    # Delete from retry queue
                                    await sqs.delete_message(
                                        QueueUrl=queue_url,
                                        ReceiptHandle=message['ReceiptHandle']
                                    )
                                    processed += 1
                                    
                        except Exception as e:
                            logger.error(f"Failed to process retry message: {e}")
                            # Delete malformed message
                            await sqs.delete_message(
                                QueueUrl=queue_url,
                                ReceiptHandle=message['ReceiptHandle']
                            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process retry queue: {e}")
            return 0


class SQSMonitor:
    """CloudWatch integration for SQS queue monitoring"""
    
    def __init__(
        self,
        sqs_queue_manager: SQSQueueManager,
        cloudwatch_namespace: str = "Crawling/SQS"
    ):
        self.sqs_queue_manager = sqs_queue_manager
        self.cloudwatch_namespace = cloudwatch_namespace
        self.cloudwatch_client = None
    
    async def connect(self):
        """Initialize CloudWatch client"""
        try:
            self.cloudwatch_client = self.sqs_queue_manager.session.client('cloudwatch')
            logger.info("CloudWatch monitoring connected")
        except Exception as e:
            logger.error(f"Failed to connect to CloudWatch: {e}")
    
    async def disconnect(self):
        """Close CloudWatch client"""
        if self.cloudwatch_client:
            await self.cloudwatch_client.close()
    
    async def publish_metrics(self):
        """Publish custom metrics to CloudWatch"""
        if not self.cloudwatch_client:
            return
        
        try:
            stats = await self.sqs_queue_manager.get_queue_stats()
            timestamp = datetime.utcnow()
            
            metrics = []
            
            # Queue size metrics
            for metric_name, value in stats.items():
                if isinstance(value, (int, float)):
                    metrics.append({
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': 'Count',
                        'Timestamp': timestamp
                    })
            
            # Batch publish metrics (CloudWatch accepts max 20 metrics per call)
            async with self.cloudwatch_client as cw:
                for i in range(0, len(metrics), 20):
                    batch = metrics[i:i+20]
                    await cw.put_metric_data(
                        Namespace=self.cloudwatch_namespace,
                        MetricData=batch
                    )
            
            logger.debug(f"Published {len(metrics)} metrics to CloudWatch")
            
        except Exception as e:
            logger.error(f"Failed to publish metrics to CloudWatch: {e}")
    
    async def create_alarms(self):
        """Create CloudWatch alarms for queue monitoring"""
        if not self.cloudwatch_client:
            return
        
        try:
            async with self.cloudwatch_client as cw:
                # High queue size alarm
                await cw.put_metric_alarm(
                    AlarmName='CrawlQueue-HighQueueSize',
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=2,
                    MetricName='total_frontier_size',
                    Namespace=self.cloudwatch_namespace,
                    Period=300,
                    Statistic='Average',
                    Threshold=10000.0,
                    ActionsEnabled=True,
                    AlarmActions=[
                        # Add SNS topic ARN here for notifications
                    ],
                    AlarmDescription='Alert when crawl queue size is high',
                    Unit='Count'
                )
                
                # High error rate alarm
                await cw.put_metric_alarm(
                    AlarmName='CrawlQueue-HighErrorRate',
                    ComparisonOperator='GreaterThanThreshold',
                    EvaluationPeriods=2,
                    MetricName='sqs_errors',
                    Namespace=self.cloudwatch_namespace,
                    Period=300,
                    Statistic='Sum',
                    Threshold=100.0,
                    ActionsEnabled=True,
                    AlarmActions=[
                        # Add SNS topic ARN here for notifications
                    ],
                    AlarmDescription='Alert when SQS error rate is high',
                    Unit='Count'
                )
            
            logger.info("CloudWatch alarms created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create CloudWatch alarms: {e}")


# Enhanced SQS Queue Manager with monitoring
class EnhancedSQSQueueManager(SQSQueueManager):
    """Extended SQS queue manager with CloudWatch monitoring"""
    
    def __init__(self, *args, enable_monitoring: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_monitoring = enable_monitoring
        self.monitor: Optional[SQSMonitor] = None
        self.metrics_task: Optional[asyncio.Task] = None
    
    async def connect(self):
        """Connect and start monitoring"""
        await super().connect()
        
        if self.enable_monitoring:
            self.monitor = SQSMonitor(self)
            await self.monitor.connect()
            
            # Start metrics publishing task
            self.metrics_task = asyncio.create_task(self._metrics_publisher())
    
    async def disconnect(self):
        """Disconnect and stop monitoring"""
        if self.metrics_task:
            self.metrics_task.cancel()
            try:
                await self.metrics_task
            except asyncio.CancelledError:
                pass
        
        if self.monitor:
            await self.monitor.disconnect()
        
        await super().disconnect()
    
    async def _metrics_publisher(self):
        """Periodic metrics publishing task"""
        try:
            while True:
                if self.monitor:
                    await self.monitor.publish_metrics()
                
                # Publish metrics every 5 minutes
                await asyncio.sleep(300)
                
        except asyncio.CancelledError:
            logger.info("Metrics publisher cancelled")
        except Exception as e:
            logger.error(f"Metrics publisher error: {e}")


# SQS Queue Configuration Helper
class SQSQueueSetup:
    """Helper class for setting up SQS queues with proper configurations"""
    
    def __init__(
        self,
        region_name: str = "us-west-2",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
    
    async def setup_crawl_infrastructure(self, queue_prefix: str = "crawl-") -> Dict[str, str]:
        """Set up complete SQS infrastructure for crawling"""
        try:
            session = aioboto3.Session(
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            async with session.client('sqs') as sqs:
                queue_configs = {
                    f"{queue_prefix}frontier": {
                        "MessageRetentionPeriod": "1209600",
                        "VisibilityTimeoutSeconds": "300",
                        "ReceiveMessageWaitTimeSeconds": "20"
                    },
                    f"{queue_prefix}frontier-priority.fifo": {
                        "MessageRetentionPeriod": "1209600",
                        "VisibilityTimeoutSeconds": "300",
                        "ReceiveMessageWaitTimeSeconds": "20",
                        "FifoQueue": "true",
                        "ContentBasedDeduplication": "true"
                    },
                    f"{queue_prefix}parsing": {
                        "MessageRetentionPeriod": "1209600",
                        "VisibilityTimeoutSeconds": "600",
                        "ReceiveMessageWaitTimeSeconds": "20"
                    },
                    f"{queue_prefix}parsing-priority.fifo": {
                        "MessageRetentionPeriod": "1209600",
                        "VisibilityTimeoutSeconds": "600",
                        "ReceiveMessageWaitTimeSeconds": "20",
                        "FifoQueue": "true",
                        "ContentBasedDeduplication": "true"
                    },
                    f"{queue_prefix}retry": {
                        "MessageRetentionPeriod": "1209600",
                        "VisibilityTimeoutSeconds": "300",
                        "DelaySeconds": "60"
                    },
                    f"{queue_prefix}dead": {
                        "MessageRetentionPeriod": "2419200"  # 28 days
                    }
                }
                
                created_queues = {}
                
                for queue_name, attributes in queue_configs.items():
                    try:
                        response = await sqs.create_queue(
                            QueueName=queue_name,
                            Attributes=attributes
                        )
                        created_queues[queue_name] = response['QueueUrl']
                        logger.info(f"Created queue: {queue_name}")
                        
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            # Queue already exists, get URL
                            response = await sqs.get_queue_url(QueueName=queue_name)
                            created_queues[queue_name] = response['QueueUrl']
                            logger.info(f"Found existing queue: {queue_name}")
                        else:
                            logger.error(f"Failed to create queue {queue_name}: {e}")
                
                return created_queues
                
        except Exception as e:
            logger.error(f"Failed to setup SQS infrastructure: {e}")
            return {}
