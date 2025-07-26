"""Analytics CLI Commands.

Provides command-line interface for analytics and monitoring operations.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

import click


@click.group()
def analytics() -> None:
    """Analytics and monitoring commands."""
    click.echo("📊 Business Intelligence Analytics CLI")
    click.echo("Use 'analytics --help' to see available commands")


@analytics.command()
@click.option("--hours", default=24, help="Hours of data to show (default: 24)")
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def overview(hours: int, output_format: str) -> None:
    """Show analytics overview and key metrics."""
    from ..analytics.core import analytics_engine

    async def get_overview() -> Dict[str, Any]:
        # Get analytics summary
        summary = await analytics_engine.get_analytics_summary()
        return summary

    try:
        overview_data = asyncio.run(get_overview())

        if output_format == "json":
            click.echo(json.dumps(overview_data, indent=2, default=str))
        else:
            # Table format
            click.echo("🔍 Analytics Overview")
            click.echo("=" * 50)

            # Performance metrics
            perf = overview_data.get("performance", {})
            click.echo("📊 Performance Metrics:")
            click.echo(f"  Request Count: {perf.get('request_count', 0)}")
            click.echo(f"  Avg Response Time: {perf.get('avg_response_time', 0):.3f}s")
            click.echo(f"  Success Rate: {perf.get('success_rate', 0):.1%}")
            click.echo(f"  Error Rate: {perf.get('error_rate', 0):.1%}")
            click.echo(f"  Throughput: {perf.get('throughput', 0):.2f} req/s")

            # Data quality
            quality = overview_data.get("data_quality", {})
            if quality:
                click.echo("\n📈 Data Quality:")
                click.echo(f"  Overall Score: {quality.get('quality_score', 0):.1%}")
                click.echo(f"  Total Records: {quality.get('total_records', 0)}")
                click.echo(f"  Valid Records: {quality.get('valid_records', 0)}")
                click.echo(f"  Completeness: {quality.get('completeness_rate', 0):.1%}")

            # Trends
            trends = overview_data.get("trends", {})
            if trends:
                click.echo("\n📉 Trends:")
                click.echo(f"  Performance: {trends.get('performance', 'stable')}")
                click.echo(f"  Quality: {trends.get('quality', 'stable')}")

            # Alerts
            alerts = overview_data.get("alerts", [])
            if alerts:
                click.echo(f"\n🚨 Active Alerts ({len(alerts)}):")
                for alert in alerts[:5]:  # Show first 5 alerts
                    severity = alert.get("severity", "info")
                    icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(
                        severity, "⚪"
                    )
                    click.echo(f"  {icon} {alert.get('message', 'Unknown alert')}")

    except Exception as e:
        click.echo(f"Error getting overview: {e}")


@analytics.command()
@click.option("--metric", required=True, help="Metric name to query")
@click.option("--hours", default=24, help="Hours of historical data (default: 24)")
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "csv"]),
    help="Output format",
)
def historical(metric: str, hours: int, output_format: str) -> None:
    """Get historical data for a specific metric."""
    from ..analytics.core import analytics_engine

    async def get_historical_data() -> List[Dict[str, Any]]:
        return await analytics_engine.get_historical_data(metric, hours)

    try:
        data = asyncio.run(get_historical_data())

        if not data:
            click.echo(f"No historical data found for metric: {metric}")
            return

        if output_format == "json":
            click.echo(json.dumps(data, indent=2, default=str))
        elif output_format == "csv":
            click.echo("timestamp,value")
            for point in data:
                timestamp = point.get("timestamp", datetime.now().isoformat())
                value = point.get("value", 0)
                click.echo(f"{timestamp},{value}")
        else:
            # Table format
            click.echo(f"📊 Historical Data for {metric} (last {hours} hours)")
            click.echo("=" * 60)
            click.echo(f"{'Timestamp':<20} {'Value':<15} {'Tags'}")
            click.echo("-" * 60)

            for point in data[-20:]:  # Show last 20 points
                timestamp = point.get("timestamp", datetime.now().isoformat())
                if isinstance(timestamp, str):
                    timestamp = timestamp[:19]  # Truncate to seconds
                value = point.get("value", 0)
                tags = point.get("tags", {})
                tags_str = (
                    ", ".join([f"{k}={v}" for k, v in tags.items()]) if tags else ""
                )

                click.echo(f"{timestamp:<20} {value:<15.3f} {tags_str}")

    except Exception as e:
        click.echo(f"Error getting historical data: {e}")


@analytics.command()
def realtime() -> None:
    """Show real-time metrics dashboard."""
    from ..analytics.metrics import metrics_collector

    try:
        metrics = metrics_collector.get_metrics_summary()  # Use existing method

        click.echo("🔍 Real-time Metrics")
        click.echo("=" * 50)

        # System metrics
        system = metrics.get("system", {})
        if system:
            click.echo("🖥️  System Resources:")
            click.echo(f"  CPU: {system.get('cpu_percent', 0):.1f}%")
            click.echo(f"  Memory: {system.get('memory_percent', 0):.1f}%")
            click.echo(f"  Disk: {system.get('disk_percent', 0):.1f}%")

        # Response times
        response_times = metrics.get("response_times", {})
        if response_times:
            click.echo("\n⏱️  Response Times:")
            click.echo(f"  Average: {response_times.get('avg', 0):.3f}s")
            click.echo(f"  Min: {response_times.get('min', 0):.3f}s")
            click.echo(f"  Max: {response_times.get('max', 0):.3f}s")
            click.echo(f"  Count: {response_times.get('count', 0)}")

        # Jobs
        active_jobs = metrics.get("active_jobs", 0)
        total_jobs = metrics.get("total_jobs", 0)
        click.echo("\n🔧 Jobs:")
        click.echo(f"  Active: {active_jobs}")
        click.echo(f"  Total: {total_jobs}")

        # Error rates
        error_rates = metrics.get("error_rates", {})
        if error_rates:
            click.echo("\n🚨 Error Rates by Endpoint:")
            for endpoint, rate in error_rates.items():
                if rate > 0:
                    click.echo(f"  {endpoint}: {rate:.1%}")

    except Exception as e:
        click.echo(f"Error getting real-time metrics: {e}")


@analytics.command()
@click.option(
    "--format",
    "output_format",
    default="table",
    type=click.Choice(["table", "json"]),
    help="Output format",
)
def insights(output_format: str) -> None:
    """Generate AI insights and recommendations."""
    from ..analytics.insights import insights_generator

    async def get_insights() -> Dict[str, Any]:
        return await insights_generator.generate_comprehensive_report()

    try:
        insights_data = asyncio.run(get_insights())

        if output_format == "json":
            click.echo(json.dumps(insights_data, indent=2, default=str))
        else:
            # Table format
            click.echo("🤖 AI Insights & Recommendations")
            click.echo("=" * 50)

            health_score = insights_data.get("health_score", 0)
            click.echo(f"Overall Health Score: {health_score:.1f}/100")

            # Performance insights
            perf_insights = insights_data.get("insights", {}).get("performance", [])
            if perf_insights:
                click.echo("\n📊 Performance Insights:")
                for insight in perf_insights:
                    severity = insight.get("severity", "low")
                    icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(
                        severity, "⚪"
                    )
                    title = insight.get("title", "Unknown")
                    description = insight.get("description", "")
                    click.echo(f"  {icon} {title}")
                    if description:
                        click.echo(f"      {description}")

            # Anomalies
            anomalies = insights_data.get("insights", {}).get("anomalies", [])
            if anomalies:
                click.echo("\n🔍 Anomalies Detected:")
                for anomaly in anomalies:
                    title = anomaly.get("title", "Unknown anomaly")
                    description = anomaly.get("description", "")
                    click.echo(f"  ⚠️  {title}")
                    if description:
                        click.echo(f"      {description}")

            # Top recommendations
            recommendations = insights_data.get("recommendations", [])
            if recommendations:
                click.echo("\n💡 Top Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    title = rec.get("title", "Unknown recommendation")
                    recommendation = rec.get("recommendation", "")
                    click.echo(f"  {i}. {title}")
                    if recommendation:
                        click.echo(f"      → {recommendation}")

    except Exception as e:
        click.echo(f"Error generating insights: {e}")


@analytics.command()
@click.option("--days", default=30, help="Delete data older than this many days")
@click.confirmation_option(prompt="Are you sure you want to delete old analytics data?")
def cleanup(days: int) -> None:
    """Clean up old analytics data."""
    from ..analytics.core import analytics_engine

    async def cleanup_data() -> None:
        await analytics_engine.cleanup_old_data(days)

    try:
        asyncio.run(cleanup_data())
        click.echo(f"✅ Cleaned up analytics data older than {days} days")
    except Exception as e:
        click.echo(f"Error cleaning up data: {e}")


@analytics.command()
@click.option("--name", required=True, help="Metric name")
@click.option("--value", required=True, type=float, help="Metric value")
@click.option("--tags", help="Tags as key=value pairs, comma-separated")
def record(name: str, value: float, tags: Optional[str]) -> None:
    """Record a custom metric."""
    from ..analytics.core import analytics_engine

    # Parse tags
    tag_dict = {}
    if tags:
        for tag_pair in tags.split(","):
            if "=" in tag_pair:
                key, val = tag_pair.split("=", 1)
                tag_dict[key.strip()] = val.strip()

    async def record_metric() -> None:
        await analytics_engine.record_metric(name, value, tag_dict)

    try:
        asyncio.run(record_metric())
        click.echo(f"✅ Recorded metric: {name} = {value}")
        if tag_dict:
            click.echo(f"   Tags: {tag_dict}")
    except Exception as e:
        click.echo(f"Error recording metric: {e}")


@analytics.command()
def status() -> None:
    """Check analytics system status."""
    from ..analytics.core import analytics_engine
    from ..analytics.metrics import metrics_collector

    click.echo("🔍 Analytics System Status")
    click.echo("=" * 50)

    # Check analytics engine
    if analytics_engine.db_engine:
        click.echo("✅ Analytics Engine: Connected")
        click.echo(f"   Metrics buffer: {len(analytics_engine.metrics_buffer)} items")
    else:
        click.echo("❌ Analytics Engine: Database not connected")

    # Check metrics collector
    if (
        metrics_collector._collection_task
        and not metrics_collector._collection_task.done()
    ):
        click.echo("✅ Metrics Collector: Running")
    else:
        click.echo("❌ Metrics Collector: Not running")

    # Performance stats
    perf = analytics_engine.get_performance_metrics()
    click.echo("\n📊 Quick Stats:")
    click.echo(f"   Total requests: {perf.request_count}")
    click.echo(f"   Avg response time: {perf.avg_response_time:.3f}s")
    click.echo(f"   Success rate: {perf.success_rate:.1%}")

    # System resources
    try:
        import psutil  # type: ignore[import-untyped]

        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        click.echo("\n🖥️  System Resources:")
        click.echo(f"   CPU: {cpu:.1f}%")
        click.echo(f"   Memory: {memory:.1f}%")
    except ImportError:
        click.echo("\n🖥️  System Resources: psutil not available")


@analytics.command()
def flush() -> None:
    """Manually flush metrics buffer to storage."""
    from ..analytics.core import analytics_engine

    async def flush_metrics() -> None:
        await analytics_engine.flush_metrics()

    try:
        buffer_size = len(analytics_engine.metrics_buffer)
        asyncio.run(flush_metrics())
        click.echo(f"✅ Flushed {buffer_size} metrics to storage")
    except Exception as e:
        click.echo(f"Error flushing metrics: {e}")


if __name__ == "__main__":
    analytics()
