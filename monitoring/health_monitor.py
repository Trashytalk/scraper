#!/usr/bin/env python3
"""
Advanced System Health Monitor
Comprehensive health checks, performance monitoring, and alerting
"""

import asyncio
import json
import time
import psutil
import requests
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

@dataclass
class HealthStatus:
    """Health check status"""
    service: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    details: Dict[str, Any]
    timestamp: datetime
    
@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_connections: int
    running_processes: int
    timestamp: datetime

class HealthMonitor:
    """Comprehensive health monitoring system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.alert_history = {}
        self.thresholds = config.get('thresholds', {
            'cpu_warning': 70,
            'cpu_critical': 90,
            'memory_warning': 80,
            'memory_critical': 95,
            'disk_warning': 80,
            'disk_critical': 90,
            'response_time_warning': 2000,
            'response_time_critical': 5000
        })
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger('health_monitor')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def check_api_health(self, endpoint: str) -> HealthStatus:
        """Check API endpoint health"""
        start_time = time.time()
        
        try:
            response = requests.get(
                endpoint,
                timeout=10,
                headers={'User-Agent': 'HealthMonitor/1.0'}
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status = 'healthy'
                if response_time > self.thresholds['response_time_warning']:
                    status = 'degraded'
            else:
                status = 'unhealthy'
            
            return HealthStatus(
                service='api',
                status=status,
                response_time=response_time,
                details={
                    'status_code': response.status_code,
                    'endpoint': endpoint,
                    'content_length': len(response.content)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return HealthStatus(
                service='api',
                status='unhealthy',
                response_time=(time.time() - start_time) * 1000,
                details={'error': str(e), 'endpoint': endpoint},
                timestamp=datetime.now()
            )
    
    def check_database_health(self, db_url: str) -> HealthStatus:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            # Import database connection here to avoid dependency issues
            import sqlite3
            
            if 'sqlite' in db_url:
                conn = sqlite3.connect(db_url.replace('sqlite:///', ''))
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
                conn.close()
                
                response_time = (time.time() - start_time) * 1000
                
                return HealthStatus(
                    service='database',
                    status='healthy' if result else 'unhealthy',
                    response_time=response_time,
                    details={'type': 'sqlite', 'result': result},
                    timestamp=datetime.now()
                )
            else:
                # For PostgreSQL or other databases
                return HealthStatus(
                    service='database',
                    status='unknown',
                    response_time=0,
                    details={'type': 'unsupported_for_health_check'},
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return HealthStatus(
                service='database',
                status='unhealthy',
                response_time=(time.time() - start_time) * 1000,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def check_redis_health(self, redis_url: str) -> HealthStatus:
        """Check Redis connectivity"""
        start_time = time.time()
        
        try:
            import redis
            
            r = redis.from_url(redis_url)
            r.ping()
            
            response_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = r.info()
            
            return HealthStatus(
                service='redis',
                status='healthy',
                response_time=response_time,
                details={
                    'version': info.get('redis_version'),
                    'connected_clients': info.get('connected_clients'),
                    'used_memory_human': info.get('used_memory_human')
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return HealthStatus(
                service='redis',
                status='unhealthy',
                response_time=(time.time() - start_time) * 1000,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_percent=psutil.disk_usage('/').percent,
            network_connections=len(psutil.net_connections()),
            running_processes=len(psutil.pids()),
            timestamp=datetime.now()
        )
    
    def check_disk_space(self) -> HealthStatus:
        """Check available disk space"""
        start_time = time.time()
        
        try:
            disk_usage = psutil.disk_usage('/')
            free_percent = (disk_usage.free / disk_usage.total) * 100
            used_percent = 100 - free_percent
            
            if used_percent < self.thresholds['disk_warning']:
                status = 'healthy'
            elif used_percent < self.thresholds['disk_critical']:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service='disk',
                status=status,
                response_time=response_time,
                details={
                    'total_gb': round(disk_usage.total / (1024**3), 2),
                    'used_gb': round(disk_usage.used / (1024**3), 2),
                    'free_gb': round(disk_usage.free / (1024**3), 2),
                    'used_percent': round(used_percent, 2)
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return HealthStatus(
                service='disk',
                status='unhealthy',
                response_time=0,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    async def run_comprehensive_health_check(self) -> Dict[str, HealthStatus]:
        """Run all health checks"""
        results = {}
        
        # API Health Check
        api_url = self.config.get('api_url', 'http://localhost:8000/api/health')
        results['api'] = await self.check_api_health(api_url)
        
        # Database Health Check
        db_url = self.config.get('database_url', 'data.db')
        results['database'] = self.check_database_health(db_url)
        
        # Redis Health Check (if configured)
        redis_url = self.config.get('redis_url')
        if redis_url:
            results['redis'] = self.check_redis_health(redis_url)
        
        # Disk Space Check
        results['disk'] = self.check_disk_space()
        
        return results
    
    def generate_health_report(self, health_results: Dict[str, HealthStatus], 
                             system_metrics: SystemMetrics) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        overall_status = 'healthy'
        
        # Determine overall status
        for health in health_results.values():
            if health.status == 'unhealthy':
                overall_status = 'unhealthy'
                break
            elif health.status == 'degraded':
                overall_status = 'degraded'
        
        # System status assessment
        if (system_metrics.cpu_percent > self.thresholds['cpu_critical'] or 
            system_metrics.memory_percent > self.thresholds['memory_critical']):
            overall_status = 'unhealthy'
        elif (system_metrics.cpu_percent > self.thresholds['cpu_warning'] or 
              system_metrics.memory_percent > self.thresholds['memory_warning']):
            if overall_status == 'healthy':
                overall_status = 'degraded'
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'services': {name: asdict(health) for name, health in health_results.items()},
            'system_metrics': asdict(system_metrics),
            'thresholds': self.thresholds
        }
    
    def send_alert(self, report: Dict[str, Any]):
        """Send alert if critical issues detected"""
        if report['overall_status'] != 'unhealthy':
            return
        
        # Check if we've already sent an alert recently
        last_alert = self.alert_history.get('critical')
        if last_alert and (datetime.now() - last_alert) < timedelta(minutes=15):
            return  # Don't spam alerts
        
        try:
            smtp_config = self.config.get('smtp', {})
            if not smtp_config.get('enabled'):
                return
            
            # Create email
            msg = MimeMultipart()
            msg['From'] = smtp_config.get('from_email')
            msg['To'] = smtp_config.get('alert_email')
            msg['Subject'] = f"CRITICAL: Business Intelligence Scraper Health Alert"
            
            # Email body
            body = f"""
            CRITICAL HEALTH ALERT
            =====================
            
            Overall Status: {report['overall_status'].upper()}
            Timestamp: {report['timestamp']}
            
            Service Status:
            """
            
            for service, details in report['services'].items():
                body += f"- {service}: {details['status'].upper()}\n"
            
            body += f"""
            
            System Metrics:
            - CPU: {report['system_metrics']['cpu_percent']:.1f}%
            - Memory: {report['system_metrics']['memory_percent']:.1f}%
            - Disk: {report['system_metrics']['disk_percent']:.1f}%
            
            Please investigate immediately.
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            if smtp_config.get('tls'):
                server.starttls()
            if smtp_config.get('username'):
                server.login(smtp_config['username'], smtp_config['password'])
            
            server.send_message(msg)
            server.quit()
            
            self.alert_history['critical'] = datetime.now()
            self.logger.info("Critical health alert sent successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to send health alert: {e}")
    
    async def monitor_continuously(self, interval_seconds: int = 60):
        """Run continuous health monitoring"""
        self.logger.info(f"Starting continuous health monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Run health checks
                health_results = await self.run_comprehensive_health_check()
                system_metrics = self.get_system_metrics()
                
                # Generate report
                report = self.generate_health_report(health_results, system_metrics)
                
                # Log status
                self.logger.info(f"Health check complete - Status: {report['overall_status']}")
                
                # Send alerts if needed
                self.send_alert(report)
                
                # Save report to file
                report_file = f"health_reports/health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                os.makedirs('health_reports', exist_ok=True)
                with open(report_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                # Wait for next check
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)  # Shorter wait on error

# Example usage and configuration
if __name__ == "__main__":
    import os
    
    # Configuration
    config = {
        'api_url': os.getenv('API_URL', 'http://localhost:8000/api/health'),
        'database_url': os.getenv('DATABASE_URL', 'data.db'),
        'redis_url': os.getenv('REDIS_URL'),
        'thresholds': {
            'cpu_warning': 70,
            'cpu_critical': 90,
            'memory_warning': 80,
            'memory_critical': 95,
            'disk_warning': 80,
            'disk_critical': 90,
            'response_time_warning': 2000,
            'response_time_critical': 5000
        },
        'smtp': {
            'enabled': os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
            'host': os.getenv('SMTP_HOST'),
            'port': int(os.getenv('SMTP_PORT', 587)),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD'),
            'tls': os.getenv('SMTP_TLS', 'true').lower() == 'true',
            'from_email': os.getenv('SMTP_FROM_EMAIL'),
            'alert_email': os.getenv('ALERT_EMAIL')
        }
    }
    
    # Run health monitor
    monitor = HealthMonitor(config)
    
    print("🏥 Advanced Health Monitor Starting...")
    print("=" * 50)
    
    # Run single health check
    async def run_single_check():
        health_results = await monitor.run_comprehensive_health_check()
        system_metrics = monitor.get_system_metrics()
        report = monitor.generate_health_report(health_results, system_metrics)
        
        print(f"Overall Status: {report['overall_status'].upper()}")
        print(f"Timestamp: {report['timestamp']}")
        print("\nService Health:")
        for service, details in report['services'].items():
            print(f"  {service}: {details['status']} ({details['response_time']:.0f}ms)")
        
        print(f"\nSystem Metrics:")
        print(f"  CPU: {system_metrics.cpu_percent:.1f}%")
        print(f"  Memory: {system_metrics.memory_percent:.1f}%")
        print(f"  Disk: {system_metrics.disk_percent:.1f}%")
        print(f"  Processes: {system_metrics.running_processes}")
        
        return report
    
    # Check if continuous monitoring is requested
    if len(os.sys.argv) > 1 and os.sys.argv[1] == 'monitor':
        asyncio.run(monitor.monitor_continuously())
    else:
        report = asyncio.run(run_single_check())
        
        if report['overall_status'] == 'unhealthy':
            exit(1)
        elif report['overall_status'] == 'degraded':
            exit(2)
        else:
            exit(0)
