"""
Enhanced Monitoring CLI Commands
Provides comprehensive monitoring, alerting, and observability management via CLI
"""

import click
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from tabulate import tabulate

from ..services.monitoring_service import monitoring_service
from ..db.centralized_data import SystemMetrics, AlertRecord, PerformanceBaseline
from ..dependencies import get_db


@click.group()
def monitoring():
    """Advanced monitoring and observability commands"""
    pass


@monitoring.command()
@click.option("--interval", "-i", default=30, help="Collection interval in seconds")
@click.option("--duration", "-d", default=0, help="Duration to run (0 = infinite)")
@click.option("--output", "-o", type=click.Choice(["table", "json", "csv"]), default="table")
def collect(interval: int, duration: int, output: str):
    """Start metrics collection with real-time display"""
    click.echo(f"🔍 Starting metrics collection (interval: {interval}s)")
    click.echo("Press Ctrl+C to stop")
    click.echo("=" * 80)
    
    start_time = time.time()
    collection_count = 0
    
    try:
        while True:
            # Check duration limit
            if duration > 0 and (time.time() - start_time) >= duration:
                break
                
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                metrics = loop.run_until_complete(
                    monitoring_service.collect_system_metrics(source="cli_collect")
                )
                collection_count += 1
                
                if output == "table":
                    _display_metrics_table(metrics, collection_count)
                elif output == "json":
                    _display_metrics_json(metrics)
                elif output == "csv":
                    _display_metrics_csv(metrics, collection_count == 1)
                    
            finally:
                loop.close()
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        click.echo(f"\n\n✅ Collection stopped. Total collections: {collection_count}")
    except Exception as e:
        click.echo(f"\n❌ Error during collection: {e}")


@monitoring.command()
@click.option("--hours", "-h", default=24, help="Hours of history to display")
@click.option("--metric", "-m", multiple=True, help="Specific metrics to display")
@click.option("--format", "-f", type=click.Choice(["table", "json", "chart"]), default="table")
def history(hours: int, metric: tuple, format: str):
    """Display metrics history"""
    click.echo(f"📈 Metrics History (Last {hours} hours)")
    click.echo("=" * 60)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        metrics_history = loop.run_until_complete(
            monitoring_service.get_metrics_history(hours=hours)
        )
        
        if not metrics_history:
            click.echo("No metrics data available")
            return
        
        if format == "table":
            _display_history_table(metrics_history, metric)
        elif format == "json":
            click.echo(json.dumps(metrics_history, indent=2))
        elif format == "chart":
            _display_history_chart(metrics_history, metric)
            
    except Exception as e:
        click.echo(f"❌ Error retrieving history: {e}")
    finally:
        loop.close()


@monitoring.command()
@click.option("--severity", "-s", type=click.Choice(["low", "medium", "high", "critical"]))
@click.option("--status", "-t", type=click.Choice(["active", "acknowledged", "resolved"]))
@click.option("--hours", "-h", default=24, help="Hours to look back")
@click.option("--limit", "-l", default=50, help="Maximum alerts to display")
def alerts(severity: str, status: str, hours: int, limit: int):
    """Display and manage alerts"""
    click.echo(f"🚨 System Alerts (Last {hours} hours)")
    click.echo("=" * 70)
    
    try:
        db = next(get_db())
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        # Build query
        query = db.query(AlertRecord).filter(AlertRecord.triggered_at >= cutoff)
        
        if severity:
            query = query.filter(AlertRecord.severity == severity)
        if status:
            query = query.filter(AlertRecord.status == status)
            
        alerts = query.order_by(AlertRecord.triggered_at.desc()).limit(limit).all()
        
        if not alerts:
            click.echo("No alerts found matching criteria")
            return
        
        # Display alerts table
        headers = ["UUID", "Severity", "Category", "Title", "Status", "Triggered", "Component"]
        rows = []
        
        for alert in alerts:
            rows.append([
                alert.alert_uuid[:8] + "...",
                _colorize_severity(alert.severity),
                alert.category,
                alert.title[:40] + "..." if len(alert.title) > 40 else alert.title,
                _colorize_status(alert.status),
                alert.triggered_at.strftime("%m/%d %H:%M"),
                alert.source_component
            ])
        
        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        
        # Display summary
        summary = _get_alerts_summary(alerts)
        click.echo(f"\n📊 Summary: {summary}")
        
    except Exception as e:
        click.echo(f"❌ Error retrieving alerts: {e}")
    finally:
        if db:
            db.close()


@monitoring.command()
@click.option("--alert-uuid", "-u", required=True, help="Alert UUID to acknowledge")
@click.option("--user", "-user", default="cli-user", help="User acknowledging the alert")
@click.option("--notes", "-n", help="Acknowledgment notes")
def acknowledge(alert_uuid: str, user: str, notes: str):
    """Acknowledge an alert"""
    try:
        db = next(get_db())
        
        alert = db.query(AlertRecord).filter(AlertRecord.alert_uuid == alert_uuid).first()
        
        if not alert:
            click.echo(f"❌ Alert {alert_uuid} not found")
            return
            
        if alert.status != "active":
            click.echo(f"⚠️  Alert {alert_uuid} is not in active status (current: {alert.status})")
            return
        
        # Update alert
        alert.status = "acknowledged"
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = user
        if notes:
            alert.resolution_notes = notes
            
        db.commit()
        
        click.echo(f"✅ Alert {alert_uuid} acknowledged by {user}")
        if notes:
            click.echo(f"   Notes: {notes}")
            
    except Exception as e:
        click.echo(f"❌ Error acknowledging alert: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()


@monitoring.command()
@click.option("--metric", "-m", help="Specific metric to show baseline for")
@click.option("--component", "-c", default="system", help="Component to filter by")
def baselines(metric: str, component: str):
    """Display performance baselines"""
    click.echo(f"📊 Performance Baselines")
    click.echo("=" * 60)
    
    try:
        db = next(get_db())
        
        query = db.query(PerformanceBaseline).filter(
            PerformanceBaseline.is_active == True,
            PerformanceBaseline.component == component
        )
        
        if metric:
            query = query.filter(PerformanceBaseline.metric_name == metric)
            
        baselines = query.order_by(PerformanceBaseline.metric_name).all()
        
        if not baselines:
            click.echo("No active baselines found")
            return
        
        # Display baselines table
        headers = ["Metric", "Mean", "Std Dev", "Warning", "Critical", "Confidence", "Samples"]
        rows = []
        
        for baseline in baselines:
            rows.append([
                baseline.metric_name,
                f"{baseline.baseline_mean:.2f}" if baseline.baseline_mean else "N/A",
                f"{baseline.baseline_std_dev:.2f}" if baseline.baseline_std_dev else "N/A",
                f"{baseline.warning_threshold:.2f}" if baseline.warning_threshold else "N/A",
                f"{baseline.critical_threshold:.2f}" if baseline.critical_threshold else "N/A",
                f"{baseline.confidence_score:.2f}" if baseline.confidence_score else "N/A",
                baseline.sample_count or 0
            ])
        
        click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
        
    except Exception as e:
        click.echo(f"❌ Error retrieving baselines: {e}")
    finally:
        if db:
            db.close()


@monitoring.command()
@click.option("--metric", "-m", help="Specific metric to recalculate")
def recalculate_baselines(metric: str):
    """Recalculate performance baselines"""
    click.echo("🔄 Recalculating performance baselines...")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if metric:
            loop.run_until_complete(monitoring_service._calculate_metric_baseline(metric))
            click.echo(f"✅ Baseline recalculated for: {metric}")
        else:
            loop.run_until_complete(monitoring_service.update_performance_baselines())
            click.echo("✅ All baselines recalculated")
            
    except Exception as e:
        click.echo(f"❌ Error recalculating baselines: {e}")
    finally:
        loop.close()


@monitoring.command()
def health():
    """Comprehensive system health check"""
    click.echo("🏥 System Health Check")
    click.echo("=" * 50)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        health_summary = loop.run_until_complete(
            monitoring_service.get_system_health_summary()
        )
        
        # Overall status
        status = health_summary.get("overall_status", "unknown")
        status_color = _colorize_health_status(status)
        click.echo(f"Overall Status: {status_color}")
        click.echo(f"Timestamp: {health_summary.get('timestamp', 'N/A')}")
        click.echo()
        
        # System resources
        if "system_resources" in health_summary:
            resources = health_summary["system_resources"]
            click.echo("💻 System Resources:")
            click.echo(f"  CPU: {resources.get('cpu_percent', 0):.1f}%")
            click.echo(f"  Memory: {resources.get('memory_percent', 0):.1f}%")
            click.echo(f"  Disk: {resources.get('disk_usage_percent', 0):.1f}%")
            click.echo()
        
        # Performance metrics
        if "performance" in health_summary:
            perf = health_summary["performance"]
            click.echo("⚡ Performance:")
            click.echo(f"  Requests/min: {perf.get('requests_per_minute', 0):.1f}")
            click.echo(f"  Avg response: {perf.get('avg_response_time_ms', 0):.1f}ms")
            click.echo(f"  Error rate: {perf.get('error_rate_percent', 0):.1f}%")
            click.echo()
        
        # Jobs status
        if "jobs" in health_summary:
            jobs = health_summary["jobs"]
            click.echo("🔧 Jobs:")
            click.echo(f"  Active: {jobs.get('active', 0)}")
            click.echo(f"  Completed (1h): {jobs.get('completed_last_hour', 0)}")
            click.echo(f"  Failed (1h): {jobs.get('failed_last_hour', 0)}")
            click.echo()
        
        # Alerts summary
        if "alerts" in health_summary:
            alerts = health_summary["alerts"]
            click.echo("🚨 Alerts:")
            click.echo(f"  Critical: {alerts.get('critical', 0)}")
            click.echo(f"  Warning: {alerts.get('warning', 0)}")
            click.echo(f"  Total Active: {alerts.get('total_active', 0)}")
            click.echo()
        
        # Anomaly score
        anomaly_score = health_summary.get("anomaly_score", 0)
        click.echo(f"🔍 Anomaly Score: {anomaly_score:.3f} (0.0=normal, 1.0=highly anomalous)")
        
    except Exception as e:
        click.echo(f"❌ Error checking system health: {e}")
    finally:
        loop.close()


@monitoring.command()
@click.option("--duration", "-d", default=300, help="Duration to monitor in seconds")
@click.option("--refresh", "-r", default=10, help="Refresh interval in seconds")
def realtime(duration: int, refresh: int):
    """Real-time monitoring dashboard"""
    click.echo("📊 Real-time Monitoring Dashboard")
    click.echo("Press Ctrl+C to stop")
    click.echo("=" * 80)
    
    start_time = time.time()
    
    try:
        while True:
            # Check duration
            if (time.time() - start_time) >= duration:
                break
            
            # Clear screen
            click.clear()
            
            # Display current time
            click.echo(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo("=" * 80)
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Get current metrics
                current_metrics = loop.run_until_complete(
                    monitoring_service.collect_system_metrics(source="cli_realtime")
                )
                
                # Display key metrics
                click.echo(f"💻 System: CPU {current_metrics.cpu_percent:.1f}% | "
                          f"Memory {current_metrics.memory_percent:.1f}% | "
                          f"Disk {current_metrics.disk_usage_percent:.1f}%")
                
                click.echo(f"⚡ Performance: {current_metrics.requests_per_minute:.1f} req/min | "
                          f"{current_metrics.avg_response_time_ms:.1f}ms avg | "
                          f"{current_metrics.error_rate_percent:.1f}% errors")
                
                click.echo(f"🔧 Jobs: {current_metrics.active_scraping_jobs} active | "
                          f"{current_metrics.completed_jobs_last_hour} completed/h | "
                          f"{current_metrics.failed_jobs_last_hour} failed/h")
                
                click.echo(f"🏥 Health: {current_metrics.health_status.upper()} | "
                          f"Alerts: {current_metrics.alert_count} | "
                          f"Anomaly: {current_metrics.anomaly_score:.3f}")
                
                # Display recent alerts if any
                if current_metrics.alert_count > 0:
                    click.echo("\n🚨 Recent Alerts:")
                    # This would fetch and display recent alerts
                    
            except Exception as e:
                click.echo(f"❌ Error updating display: {e}")
            finally:
                loop.close()
            
            time.sleep(refresh)
            
    except KeyboardInterrupt:
        click.echo("\n\n✅ Real-time monitoring stopped")


@monitoring.command()
def start_service():
    """Start the monitoring service"""
    click.echo("🚀 Starting monitoring service...")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(monitoring_service.start_monitoring())
        
    except KeyboardInterrupt:
        click.echo("\n⏹️  Monitoring service stopped by user")
    except Exception as e:
        click.echo(f"❌ Error starting monitoring service: {e}")
    finally:
        loop.close()


@monitoring.command()
def stop_service():
    """Stop the monitoring service"""
    click.echo("⏹️  Stopping monitoring service...")
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(monitoring_service.stop_monitoring())
        click.echo("✅ Monitoring service stopped")
        
    except Exception as e:
        click.echo(f"❌ Error stopping monitoring service: {e}")
    finally:
        loop.close()


# Helper functions for display formatting

def _display_metrics_table(metrics: SystemMetrics, count: int):
    """Display metrics in table format"""
    click.echo(f"\n📊 Collection #{count} - {metrics.collected_at.strftime('%H:%M:%S')}")
    
    data = [
        ["CPU", f"{metrics.cpu_percent:.1f}%"],
        ["Memory", f"{metrics.memory_percent:.1f}%"],
        ["Disk", f"{metrics.disk_usage_percent:.1f}%"],
        ["Requests/min", f"{metrics.requests_per_minute:.1f}"],
        ["Avg Response", f"{metrics.avg_response_time_ms:.1f}ms"],
        ["Error Rate", f"{metrics.error_rate_percent:.1f}%"],
        ["Active Jobs", str(metrics.active_scraping_jobs)],
        ["Health", metrics.health_status.upper()]
    ]
    
    click.echo(tabulate(data, headers=["Metric", "Value"], tablefmt="simple"))


def _display_metrics_json(metrics: SystemMetrics):
    """Display metrics in JSON format"""
    data = {
        "timestamp": metrics.collected_at.isoformat(),
        "cpu_percent": metrics.cpu_percent,
        "memory_percent": metrics.memory_percent,
        "disk_usage_percent": metrics.disk_usage_percent,
        "requests_per_minute": metrics.requests_per_minute,
        "avg_response_time_ms": metrics.avg_response_time_ms,
        "error_rate_percent": metrics.error_rate_percent,
        "active_scraping_jobs": metrics.active_scraping_jobs,
        "health_status": metrics.health_status
    }
    click.echo(json.dumps(data, indent=2))


def _display_metrics_csv(metrics: SystemMetrics, include_header: bool):
    """Display metrics in CSV format"""
    if include_header:
        click.echo("timestamp,cpu_percent,memory_percent,disk_usage_percent,requests_per_minute,avg_response_time_ms,error_rate_percent,active_jobs,health_status")
    
    click.echo(f"{metrics.collected_at.isoformat()},{metrics.cpu_percent},{metrics.memory_percent},{metrics.disk_usage_percent},{metrics.requests_per_minute},{metrics.avg_response_time_ms},{metrics.error_rate_percent},{metrics.active_scraping_jobs},{metrics.health_status}")


def _display_history_table(history: List[Dict[str, Any]], metrics: tuple):
    """Display metrics history in table format"""
    if not history:
        return
    
    # Determine which metrics to show
    if metrics:
        metric_names = metrics
    else:
        metric_names = ["cpu_percent", "memory_percent", "error_rate_percent"]
    
    headers = ["Timestamp"] + [m.replace("_", " ").title() for m in metric_names]
    rows = []
    
    for entry in history[-20:]:  # Show last 20 entries
        row = [datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")]
        for metric in metric_names:
            value = entry.get(metric, 0)
            if isinstance(value, float):
                row.append(f"{value:.1f}")
            else:
                row.append(str(value))
        rows.append(row)
    
    click.echo(tabulate(rows, headers=headers, tablefmt="grid"))


def _display_history_chart(history: List[Dict[str, Any]], metrics: tuple):
    """Display ASCII chart of metrics history"""
    # Simple ASCII chart implementation
    if not history:
        return
    
    metric_name = metrics[0] if metrics else "cpu_percent"
    values = [entry.get(metric_name, 0) for entry in history[-50:]]
    
    if not values:
        return
    
    # Normalize values to chart height
    max_val = max(values)
    min_val = min(values)
    chart_height = 10
    
    click.echo(f"\n📈 {metric_name.replace('_', ' ').title()} Trend (Last {len(values)} points)")
    click.echo("=" * 60)
    
    for i in range(chart_height, 0, -1):
        line = ""
        threshold = min_val + (max_val - min_val) * (i / chart_height)
        
        for value in values:
            if value >= threshold:
                line += "█"
            else:
                line += " "
        
        click.echo(f"{threshold:6.1f} |{line}")
    
    click.echo(f"{'':>7}+{'-' * len(values)}")
    click.echo(f"Min: {min_val:.1f}, Max: {max_val:.1f}, Avg: {sum(values)/len(values):.1f}")


def _colorize_severity(severity: str) -> str:
    """Colorize severity levels"""
    colors = {
        "critical": click.style(severity.upper(), fg="red", bold=True),
        "high": click.style(severity.upper(), fg="red"),
        "medium": click.style(severity.upper(), fg="yellow"),
        "low": click.style(severity.upper(), fg="green")
    }
    return colors.get(severity, severity.upper())


def _colorize_status(status: str) -> str:
    """Colorize status levels"""
    colors = {
        "active": click.style(status.upper(), fg="red"),
        "acknowledged": click.style(status.upper(), fg="yellow"),
        "resolved": click.style(status.upper(), fg="green")
    }
    return colors.get(status, status.upper())


def _colorize_health_status(status: str) -> str:
    """Colorize health status"""
    colors = {
        "healthy": click.style(status.upper(), fg="green", bold=True),
        "warning": click.style(status.upper(), fg="yellow", bold=True),
        "critical": click.style(status.upper(), fg="red", bold=True)
    }
    return colors.get(status, status.upper())


def _get_alerts_summary(alerts: List[AlertRecord]) -> str:
    """Generate alerts summary"""
    if not alerts:
        return "No alerts"
    
    severity_counts = {}
    status_counts = {}
    
    for alert in alerts:
        severity_counts[alert.severity] = severity_counts.get(alert.severity, 0) + 1
        status_counts[alert.status] = status_counts.get(alert.status, 0) + 1
    
    severity_str = ", ".join([f"{k}: {v}" for k, v in severity_counts.items()])
    status_str = ", ".join([f"{k}: {v}" for k, v in status_counts.items()])
    
    return f"Severity [{severity_str}] | Status [{status_str}]"


if __name__ == "__main__":
    monitoring()
