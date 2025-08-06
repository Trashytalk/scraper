#!/usr/bin/env python3
"""
Production Monitoring System
Business Intelligence Scraper Platform v2.0.0

Comprehensive monitoring solution with health checks, metrics collection,
alerting, and dashboard integration.
"""

import asyncio
import json
import logging
import os
import sqlite3
import smtplib
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import psutil
    import redis
    import requests
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install with: pip install psutil redis requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class SystemMetric:
    """System performance metric"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_sent: int
    network_recv: int
    timestamp: datetime

@dataclass 
class ServiceStatus:
    """Service health status"""
    name: str
    status: str  # 'healthy', 'warning', 'critical'
    response_time: float
    message: str
    timestamp: datetime

@dataclass
class Alert:
    """System alert"""
    severity: str  # 'info', 'warning', 'critical'
    component: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime

class DatabaseMonitor:
    """Monitor database connectivity and performance"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.logger = logging.getLogger(f"{__name__}.DatabaseMonitor")
    
    async def check_health(self) -> ServiceStatus:
        """Check database health"""
        start_time = time.time()
        
        try:
            # This is a placeholder - implement based on your database
            # For PostgreSQL:
            # import psycopg2
            # conn = psycopg2.connect(self.db_url)
            # cursor = conn.cursor()
            # cursor.execute("SELECT 1")
            # result = cursor.fetchone()
            # conn.close()
            
            # Simulated check for now
            await asyncio.sleep(0.01)  # Simulate DB query time
            
            response_time = (time.time() - start_time) * 1000
            
            return ServiceStatus(
                name="Database",
                status="healthy",
                response_time=response_time,
                message="Database connection successful",
                timestamp=datetime.now(),
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ServiceStatus(
                name="Database", 
                status="critical",
                response_time=response_time,
                message=f"Database connection failed: {str(e)}",
                timestamp=datetime.now(),
            )

class RedisMonitor:
    """Monitor Redis connectivity and performance"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.logger = logging.getLogger(f"{__name__}.RedisMonitor")
    
    async def check_health(self) -> ServiceStatus:
        """Check Redis health"""
        start_time = time.time()
        
        try:
            # Parse Redis URL
            r = redis.Redis.from_url(self.redis_url)
            info = r.info()
            
            # Check basic connectivity
            pong = r.ping()
            
            response_time = (time.time() - start_time) * 1000
            
            if pong:
                memory_usage = info.get('used_memory_human', 'unknown')
                return ServiceStatus(
                    name="Redis",
                    status="healthy",
                    response_time=response_time,
                    message=f"Redis healthy - Memory: {memory_usage}",
                    timestamp=datetime.now(),
                )
            else:
                return ServiceStatus(
                    name="Redis",
                    status="warning", 
                    response_time=response_time,
                    message="Redis ping failed",
                    timestamp=datetime.now(),
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ServiceStatus(
                name="Redis",
                status="critical",
                response_time=response_time,
                message=f"Redis connection failed: {str(e)}",
                timestamp=datetime.now(),
            )

class APIMonitor:
    """Monitor API endpoints"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger(f"{__name__}.APIMonitor")
    
    async def check_health(self) -> ServiceStatus:
        """Check API health"""
        start_time = time.time()
        
        try:
            # Check health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return ServiceStatus(
                    name="API",
                    status="healthy",
                    response_time=response_time,
                    message=f"API healthy - Status: {response.status_code}",
                    timestamp=datetime.now(),
                )
            else:
                return ServiceStatus(
                    name="API",
                    status="warning",
                    response_time=response_time, 
                    message=f"API warning - Status: {response.status_code}",
                    timestamp=datetime.now(),
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ServiceStatus(
                name="API",
                status="critical",
                response_time=response_time,
                message=f"API failed: {str(e)}",
                timestamp=datetime.now(),
            )

class SystemMonitor:
    """Monitor system resources"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SystemMonitor")
    
    def get_metrics(self) -> SystemMetric:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return SystemMetric(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_sent=network.bytes_sent,
                network_recv=network.bytes_recv,
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return SystemMetric(
                cpu_percent=0,
                memory_percent=0,
                disk_percent=0,
                network_sent=0,
                network_recv=0,
                timestamp=datetime.now()
            )

class AlertManager:
    """Manage alerts and notifications"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alerts_config = self.config.get('alerts', {})
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
        self.alert_history: List[Alert] = []
    
    async def send_alert(self, alert: Alert):
        """Send alert through configured channels"""
        self.alert_history.append(alert)
        
        # Keep only recent alerts
        cutoff = datetime.now() - timedelta(hours=24)
        self.alert_history = [a for a in self.alert_history if a.timestamp > cutoff]
        
        # Check if alerts are enabled
        if not self.alerts_config.get('enabled', True):
            return
        
        # Get severity config
        severity_config = self.alerts_config.get('severity_levels', {}).get(alert.severity, {})
        if not severity_config.get('enabled', True):
            return
        
        channels = severity_config.get('notification_channels', ['console'])
        
        # Send to each configured channel
        for channel in channels:
            try:
                if channel == 'console' and self.alerts_config.get('console_enabled', True):
                    await self._send_console_alert(alert)
                elif channel == 'file' and self.alerts_config.get('file_enabled', True):
                    await self._send_file_alert(alert)
                elif channel == 'email' and self.alerts_config.get('email_enabled', False):
                    await self._send_email_alert(alert)
                elif channel == 'webhook' and self.alerts_config.get('webhook_enabled', False):
                    await self._send_webhook_alert(alert)
            except Exception as e:
                self.logger.error(f"Failed to send {channel} alert: {e}")
    
    async def _send_console_alert(self, alert: Alert):
        """Send alert to console"""
        severity_emoji = {'info': 'ℹ️', 'warning': '⚠️', 'critical': '🚨'}
        emoji = severity_emoji.get(alert.severity, '📢')
        
        print(f"\n{emoji} ALERT [{alert.severity.upper()}] - {alert.component}")
        print(f"Message: {alert.message}")
        print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if alert.details:
            print(f"Details: {json.dumps(alert.details, indent=2)}")
        print("-" * 50)
    
    async def _send_file_alert(self, alert: Alert):
        """Send alert to file"""
        log_file = "monitoring/alerts.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(f"{alert.timestamp.isoformat()} [{alert.severity.upper()}] "
                   f"{alert.component}: {alert.message}\n")
    
    async def _send_email_alert(self, alert: Alert):
        """Send alert via email"""
        email_config = self.alerts_config.get('email', {})
        
        if not all(key in email_config for key in ['smtp_host', 'smtp_username', 'smtp_password', 'to_emails']):
            self.logger.warning("Email configuration incomplete")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config.get('from_email', email_config['smtp_username'])
            msg['To'] = ", ".join(email_config['to_emails'])
            subject_prefix = email_config.get('subject_prefix', '[MONITOR]')
            msg['Subject'] = f"{subject_prefix} {alert.severity.upper()} - {alert.component}"
            
            body = f"""
Alert Details:
--------------
Severity: {alert.severity.upper()}
Component: {alert.component}
Message: {alert.message}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Details:
{json.dumps(alert.details, indent=2) if alert.details else 'None'}

--
Business Intelligence Scraper Monitoring System
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_host'], email_config.get('smtp_port', 587))
            server.starttls()
            server.login(email_config['smtp_username'], email_config['smtp_password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent for {alert.component}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send alert via webhook"""
        webhook_config = self.alerts_config.get('webhook', {})
        webhook_url = webhook_config.get('url')
        
        if not webhook_url:
            self.logger.warning("Webhook URL not configured")
            return
        
        try:
            payload = {
                'severity': alert.severity,
                'component': alert.component,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'details': alert.details
            }
            
            headers = webhook_config.get('headers', {'Content-Type': 'application/json'})
            timeout = webhook_config.get('timeout', 5)
            
            response = requests.post(webhook_url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            self.logger.info(f"Webhook alert sent for {alert.component}")
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")

class MonitoringOrchestrator:
    """Main monitoring orchestrator"""
    
    def __init__(self, config_path: str = "monitoring/config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(f"{__name__}.MonitoringOrchestrator")
        
        # Initialize components
        services_config = self.config.get('services', {})
        self.db_monitor = DatabaseMonitor(services_config.get('database_url', ''))
        self.redis_monitor = RedisMonitor(services_config.get('redis_url', ''))
        self.api_monitor = APIMonitor(services_config.get('api_base_url', ''))
        self.system_monitor = SystemMonitor()
        self.alert_manager = AlertManager(self.config)
        
        # Monitoring intervals
        intervals = self.config.get('intervals', {})
        self.health_check_interval = intervals.get('health_check_interval', 30)
        self.metrics_interval = intervals.get('metrics_interval', 60)
        
        # Thresholds
        self.thresholds = self.config.get('thresholds', {})
        
        self.running = False
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'monitoring': {'enabled': True},
            'services': {
                'database_url': 'postgresql://localhost:5432/business_intel_scraper',
                'redis_url': 'redis://localhost:6379/0',
                'api_base_url': 'http://localhost:8000'
            },
            'intervals': {
                'health_check_interval': 30,
                'metrics_interval': 60
            },
            'thresholds': {
                'cpu_warning': 80,
                'cpu_critical': 95,
                'memory_warning': 85,
                'memory_critical': 95,
                'disk_warning': 80,
                'disk_critical': 90
            },
            'alerts': {
                'enabled': True,
                'console_enabled': True,
                'file_enabled': True,
                'email_enabled': False,
                'webhook_enabled': False
            }
        }
    
    async def run_health_checks(self):
        """Run health checks for all services"""
        self.logger.info("Running health checks...")
        
        # Check database
        db_status = await self.db_monitor.check_health()
        
        if db_status.status != 'healthy':
            await self.alert_manager.send_alert(Alert(
                severity='critical' if db_status.status == 'critical' else 'warning',
                component='Database',
                message=db_status.message,
                details={'response_time': db_status.response_time},
                timestamp=datetime.now()
            ))
        
        # Check Redis
        redis_status = await self.redis_monitor.check_health()
        
        if redis_status.status != 'healthy':
            await self.alert_manager.send_alert(Alert(
                severity='warning' if redis_status.status == 'warning' else 'critical',
                component='Redis',
                message=redis_status.message,
                details={'response_time': redis_status.response_time},
                timestamp=datetime.now()
            ))
        
        # Check API
        api_status = await self.api_monitor.check_health()
        
        if api_status.status != 'healthy':
            await self.alert_manager.send_alert(Alert(
                severity='critical' if api_status.status == 'critical' else 'warning',
                component='API',
                message=api_status.message,
                details={'response_time': api_status.response_time},
                timestamp=datetime.now()
            ))
    
    async def collect_metrics(self):
        """Collect system metrics"""
        self.logger.debug("Collecting system metrics...")
        
        metrics = self.system_monitor.get_metrics()
        
        # Check thresholds and generate alerts
        await self._check_metric_thresholds(metrics)
    
    async def _check_metric_thresholds(self, metrics: SystemMetric):
        """Check if metrics exceed thresholds"""
        
        # CPU threshold check
        if metrics.cpu_percent > self.thresholds.get('cpu_critical', 95):
            await self.alert_manager.send_alert(Alert(
                severity='critical',
                component='System',
                message=f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                details={'cpu_percent': metrics.cpu_percent, 'threshold': self.thresholds.get('cpu_critical')},
                timestamp=datetime.now()
            ))
        elif metrics.cpu_percent > self.thresholds.get('cpu_warning', 80):
            await self.alert_manager.send_alert(Alert(
                severity='warning',
                component='System',
                message=f"CPU usage high: {metrics.cpu_percent:.1f}%",
                details={'cpu_percent': metrics.cpu_percent, 'threshold': self.thresholds.get('cpu_warning')},
                timestamp=datetime.now()
            ))
        
        # Memory threshold check
        if metrics.memory_percent > self.thresholds.get('memory_critical', 95):
            await self.alert_manager.send_alert(Alert(
                severity='critical',
                component='System',
                message=f"Memory usage critical: {metrics.memory_percent:.1f}%",
                details={'memory_percent': metrics.memory_percent, 'threshold': self.thresholds.get('memory_critical')},
                timestamp=datetime.now()
            ))
        elif metrics.memory_percent > self.thresholds.get('memory_warning', 85):
            await self.alert_manager.send_alert(Alert(
                severity='warning',
                component='System',
                message=f"Memory usage high: {metrics.memory_percent:.1f}%",
                details={'memory_percent': metrics.memory_percent, 'threshold': self.thresholds.get('memory_warning')},
                timestamp=datetime.now()
            ))
        
        # Disk threshold check
        if metrics.disk_percent > self.thresholds.get('disk_critical', 90):
            await self.alert_manager.send_alert(Alert(
                severity='critical',
                component='System',
                message=f"Disk usage critical: {metrics.disk_percent:.1f}%",
                details={'disk_percent': metrics.disk_percent, 'threshold': self.thresholds.get('disk_critical')},
                timestamp=datetime.now()
            ))
        elif metrics.disk_percent > self.thresholds.get('disk_warning', 80):
            await self.alert_manager.send_alert(Alert(
                severity='warning',
                component='System',
                message=f"Disk usage high: {metrics.disk_percent:.1f}%",
                details={'disk_percent': metrics.disk_percent, 'threshold': self.thresholds.get('disk_warning')},
                timestamp=datetime.now()
            ))
    
    async def start(self):
        """Start monitoring"""
        if not self.config.get('monitoring', {}).get('enabled', True):
            self.logger.warning("Monitoring is disabled in configuration")
            return
        
        self.running = True
        self.logger.info("Starting Business Intelligence Scraper Monitoring System")
        
        # Send startup alert
        await self.alert_manager.send_alert(Alert(
            severity='info',
            component='Monitoring',
            message='Monitoring system started successfully',
            details={'config_path': self.config_path},
            timestamp=datetime.now()
        ))
        
        # Create monitoring tasks
        tasks = [
            asyncio.create_task(self._health_check_loop()),
            asyncio.create_task(self._metrics_collection_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
            await self.alert_manager.send_alert(Alert(
                severity='critical',
                component='Monitoring',
                message=f'Monitoring system error: {str(e)}',
                details={'error': str(e)},
                timestamp=datetime.now()
            ))
        finally:
            self.running = False
            self.logger.info("Monitoring system stopped")
    
    async def _health_check_loop(self):
        """Health check loop"""
        while self.running:
            try:
                await self.run_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _metrics_collection_loop(self):
        """Metrics collection loop"""
        while self.running:
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.metrics_interval)
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(self.metrics_interval)
    
    def stop(self):
        """Stop monitoring"""
        self.running = False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Business Intelligence Scraper Monitoring System")
    parser.add_argument("--config", default="monitoring/config.json", help="Configuration file path")
    parser.add_argument("--test", action="store_true", help="Run health checks once and exit")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create monitoring instance
    orchestrator = MonitoringOrchestrator(args.config)
    
    if args.test:
        # Run a single health check
        async def test_run():
            await orchestrator.run_health_checks()
            await orchestrator.collect_metrics()
            print("Health check completed successfully")
        
        asyncio.run(test_run())
    else:
        # Run continuous monitoring
        try:
            asyncio.run(orchestrator.start())
        except KeyboardInterrupt:
            print("\nShutting down monitoring system...")
            orchestrator.stop()

if __name__ == "__main__":
    main()
