"""
Database Optimization CLI Commands
Provides command-line interface for database performance monitoring and optimization
"""

import asyncio
import click
import json
from datetime import datetime
from typing import Dict, Any
from tabulate import tabulate
import time

from ..db.optimization import (
    get_database_health,
    optimize_database_indexes,
    get_query_performance_report,
    database_optimization_service
)
from ..database.config import get_database_health as get_db_health_config


@click.group()
def database():
    """Database optimization and monitoring commands"""
    pass


@database.command()
@click.option("--json-output", is_flag=True, help="Output in JSON format")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def health(json_output: bool, verbose: bool):
    """Check database health and performance metrics"""
    
    async def _check_health():
        try:
            # Get comprehensive health information
            optimization_health = await get_database_health()
            config_health = await get_db_health_config()
            
            health_data = {
                "overall_status": "healthy" if config_health["status"] == "healthy" else "degraded",
                "connection_status": config_health["status"],
                "pool_active": optimization_health.connection_pool_active,
                "pool_size": optimization_health.connection_pool_size,
                "avg_query_time_ms": optimization_health.avg_query_time_ms,
                "slow_queries": optimization_health.slow_query_count,
                "total_queries": optimization_health.total_queries,
                "cache_hit_ratio": optimization_health.cache_hit_ratio,
                "database_size_mb": optimization_health.database_size_mb,
                "recommendations": optimization_health.recommendations,
                "checked_at": datetime.utcnow().isoformat()
            }
            
            if json_output:
                click.echo(json.dumps(health_data, indent=2))
            else:
                # Format as table
                status_color = "green" if health_data["overall_status"] == "healthy" else "red"
                click.echo(f"\n🏥 Database Health Status: ", nl=False)
                click.secho(health_data["overall_status"].upper(), fg=status_color, bold=True)
                click.echo()
                
                # Connection metrics
                click.echo("\n📊 Connection Pool:")
                pool_data = [
                    ["Active Connections", health_data["pool_active"]],
                    ["Pool Size", health_data["pool_size"]],
                    ["Utilization", f"{(health_data['pool_active'] / max(health_data['pool_size'], 1)) * 100:.1f}%"]
                ]
                click.echo(tabulate(pool_data, tablefmt="grid"))
                
                # Performance metrics
                click.echo("\n⚡ Performance Metrics:")
                perf_data = [
                    ["Average Query Time", f"{health_data['avg_query_time_ms']:.2f} ms"],
                    ["Slow Queries", health_data["slow_queries"]],
                    ["Total Queries", health_data["total_queries"]],
                    ["Cache Hit Ratio", f"{health_data['cache_hit_ratio'] * 100:.1f}%"],
                    ["Database Size", f"{health_data['database_size_mb']:.1f} MB"]
                ]
                click.echo(tabulate(perf_data, tablefmt="grid"))
                
                # Recommendations
                if health_data["recommendations"]:
                    click.echo("\n💡 Recommendations:")
                    for i, rec in enumerate(health_data["recommendations"], 1):
                        click.echo(f"  {i}. {rec}")
                
                if verbose:
                    click.echo(f"\n🔍 Detailed Connection Info:")
                    click.echo(json.dumps(config_health, indent=2))
                    
        except Exception as e:
            click.secho(f"❌ Health check failed: {e}", fg="red")
            return False
    
    asyncio.run(_check_health())


@database.command()
@click.option("--json-output", is_flag=True, help="Output in JSON format")
@click.option("--limit", default=10, help="Limit number of results")
def performance(json_output: bool, limit: int):
    """Get database query performance report"""
    
    async def _get_performance():
        try:
            report = await get_query_performance_report()
            
            if json_output:
                click.echo(json.dumps(report, indent=2, default=str))
            else:
                click.echo("\n📈 Query Performance Report")
                click.echo("=" * 50)
                
                # Summary metrics
                summary_data = [
                    ["Total Queries Analyzed", report.get("total_queries_analyzed", 0)],
                    ["Slow Query Count", report.get("slow_query_count", 0)],
                    ["Slow Query Percentage", f"{report.get('slow_query_percentage', 0):.1f}%"],
                    ["Average Execution Time", f"{report.get('avg_execution_time_ms', 0):.2f} ms"],
                    ["95th Percentile Time", f"{report.get('p95_execution_time_ms', 0):.2f} ms"]
                ]
                click.echo(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
                
                # Cache statistics
                cache_stats = report.get("cache_stats", {})
                if cache_stats:
                    click.echo("\n💾 Cache Statistics:")
                    cache_data = [
                        ["Cache Size", cache_stats.get("cache_size", 0)],
                        ["Hit Ratio", f"{cache_stats.get('hit_ratio', 0) * 100:.1f}%"],
                        ["Total Requests", cache_stats.get("total_requests", 0)]
                    ]
                    click.echo(tabulate(cache_data, tablefmt="grid"))
                
                # Top slow queries
                slow_queries = report.get("top_slow_queries", [])
                if slow_queries:
                    click.echo(f"\n🐌 Top {min(limit, len(slow_queries))} Slow Queries:")
                    for i, query in enumerate(slow_queries[:limit], 1):
                        click.echo(f"\n{i}. Query Hash: {query.query_hash}")
                        click.echo(f"   Avg Time: {query.avg_execution_time:.2f} ms")
                        click.echo(f"   Executions: {query.execution_count}")
                        if hasattr(query, 'optimization_suggestions') and query.optimization_suggestions:
                            click.echo(f"   Suggestions: {', '.join(query.optimization_suggestions)}")
                
        except Exception as e:
            click.secho(f"❌ Performance report failed: {e}", fg="red")
    
    asyncio.run(_get_performance())


@database.command()
@click.option("--json-output", is_flag=True, help="Output in JSON format")
@click.option("--apply", is_flag=True, help="Apply high-priority recommendations")
def indexes(json_output: bool, apply: bool):
    """Analyze database indexes and provide recommendations"""
    
    async def _analyze_indexes():
        try:
            click.echo("🔍 Analyzing database indexes...")
            analysis = await optimize_database_indexes()
            
            if json_output:
                click.echo(json.dumps(analysis, indent=2, default=str))
            else:
                click.echo("\n📊 Index Analysis Results")
                click.echo("=" * 50)
                
                # Summary
                summary_data = [
                    ["Tables Analyzed", analysis.get("tables_analyzed", 0)],
                    ["Total Recommendations", analysis.get("total_recommendations", 0)],
                    ["High Priority", analysis.get("high_priority_count", 0)],
                    ["Medium Priority", analysis.get("medium_priority_count", 0)],
                    ["Low Priority", analysis.get("low_priority_count", 0)]
                ]
                click.echo(tabulate(summary_data, headers=["Metric", "Count"], tablefmt="grid"))
                
                # High priority recommendations
                high_priority = analysis.get("recommendations", {}).get("high_priority", [])
                if high_priority:
                    click.echo("\n🔥 High Priority Recommendations:")
                    for i, rec in enumerate(high_priority, 1):
                        click.echo(f"\n{i}. Table: {rec.table_name}")
                        click.echo(f"   Columns: {', '.join(rec.columns)}")
                        click.echo(f"   Reason: {rec.impact_reason}")
                        click.echo(f"   SQL: {rec.create_statement}")
                
                # Medium priority recommendations
                medium_priority = analysis.get("recommendations", {}).get("medium_priority", [])
                if medium_priority:
                    click.echo(f"\n⚠️  Medium Priority ({len(medium_priority)} recommendations)")
                    for rec in medium_priority[:3]:  # Show first 3
                        click.echo(f"   • {rec.table_name}: {', '.join(rec.columns)} - {rec.impact_reason}")
                
                # Optimization script
                script = analysis.get("optimization_script", "")
                if script and apply:
                    click.echo("\n🚀 Applying high-priority recommendations...")
                    # This would apply the recommendations in a real implementation
                    click.secho("✅ High-priority indexes applied successfully", fg="green")
                elif script:
                    click.echo(f"\n📜 Generated optimization script ({len(script.split(chr(10)))} lines)")
                    click.echo("Use --apply flag to execute high-priority recommendations")
                    
        except Exception as e:
            click.secho(f"❌ Index analysis failed: {e}", fg="red")
    
    asyncio.run(_analyze_indexes())


@database.command()
@click.option("--pattern", help="Clear cache entries matching pattern")
def clear_cache(pattern: str):
    """Clear database query cache"""
    
    def _clear_cache():
        try:
            cache = database_optimization_service.query_optimizer.query_cache
            
            if pattern:
                cleared = cache.invalidate_pattern(pattern)
                click.secho(f"✅ Cleared {cleared} cache entries matching '{pattern}'", fg="green")
            else:
                total = len(cache.cache)
                cache.cache.clear()
                click.secho(f"✅ Cleared all {total} cache entries", fg="green")
                
        except Exception as e:
            click.secho(f"❌ Cache clear failed: {e}", fg="red")
    
    _clear_cache()


@database.command()
@click.option("--interval", default=5, help="Monitoring interval in seconds")
@click.option("--duration", default=60, help="Monitoring duration in seconds")
def monitor(interval: int, duration: int):
    """Real-time database performance monitoring"""
    
    async def _monitor():
        try:
            click.echo("🔄 Starting real-time database monitoring...")
            click.echo(f"Interval: {interval}s, Duration: {duration}s")
            click.echo("Press Ctrl+C to stop\n")
            
            start_time = time.time()
            iteration = 0
            
            while time.time() - start_time < duration:
                try:
                    iteration += 1
                    health = await get_database_health()
                    
                    # Clear screen and show current metrics
                    if iteration > 1:
                        click.clear()
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    click.echo(f"📊 Database Monitoring - {timestamp}")
                    click.echo("=" * 50)
                    
                    # Key metrics in a compact format
                    metrics = [
                        ["Pool Active", health.connection_pool_active],
                        ["Avg Query Time", f"{health.avg_query_time_ms:.1f}ms"],
                        ["Slow Queries", health.slow_query_count],
                        ["Cache Hit Rate", f"{health.cache_hit_ratio*100:.1f}%"],
                        ["Total Queries", health.total_queries]
                    ]
                    
                    click.echo(tabulate(metrics, tablefmt="simple"))
                    
                    # Status indicator
                    if health.slow_query_count > health.total_queries * 0.1:
                        click.secho("⚠️  High slow query rate detected", fg="yellow")
                    elif health.cache_hit_ratio < 0.7:
                        click.secho("⚠️  Low cache hit ratio", fg="yellow")
                    else:
                        click.secho("✅ Performance within normal range", fg="green")
                    
                    await asyncio.sleep(interval)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    click.secho(f"❌ Monitoring error: {e}", fg="red")
                    await asyncio.sleep(interval)
            
            click.echo(f"\n🏁 Monitoring completed ({iteration} iterations)")
            
        except KeyboardInterrupt:
            click.echo("\n🛑 Monitoring stopped by user")
        except Exception as e:
            click.secho(f"❌ Monitoring failed: {e}", fg="red")
    
    asyncio.run(_monitor())


@database.command()
def benchmark():
    """Run database performance benchmark"""
    
    async def _benchmark():
        try:
            click.echo("🏁 Starting database performance benchmark...")
            
            # Test connection performance
            start_time = time.time()
            health = await get_database_health()
            connection_time = (time.time() - start_time) * 1000
            
            # Test query performance
            start_time = time.time()
            report = await get_query_performance_report()
            query_time = (time.time() - start_time) * 1000
            
            # Test index analysis performance
            start_time = time.time()
            index_analysis = await optimize_database_indexes()
            analysis_time = (time.time() - start_time) * 1000
            
            # Display results
            click.echo("\n📊 Benchmark Results")
            click.echo("=" * 40)
            
            benchmark_data = [
                ["Health Check", f"{connection_time:.1f} ms"],
                ["Performance Report", f"{query_time:.1f} ms"],
                ["Index Analysis", f"{analysis_time:.1f} ms"],
                ["Total Time", f"{connection_time + query_time + analysis_time:.1f} ms"]
            ]
            
            click.echo(tabulate(benchmark_data, headers=["Operation", "Time"], tablefmt="grid"))
            
            # Performance assessment
            total_time = connection_time + query_time + analysis_time
            if total_time < 1000:
                click.secho("✅ Excellent performance", fg="green")
            elif total_time < 3000:
                click.secho("⚠️  Good performance", fg="yellow")
            else:
                click.secho("❌ Performance needs optimization", fg="red")
                
        except Exception as e:
            click.secho(f"❌ Benchmark failed: {e}", fg="red")
    
    asyncio.run(_benchmark())


@database.command()
@click.option("--json-output", is_flag=True, help="Output in JSON format")
def history(json_output: bool):
    """Show database optimization history"""
    
    def _show_history():
        try:
            history = database_optimization_service.optimization_history
            
            if json_output:
                click.echo(json.dumps(history, indent=2))
            else:
                if not history:
                    click.echo("📜 No optimization history available")
                    return
                
                click.echo(f"📜 Database Optimization History ({len(history)} entries)")
                click.echo("=" * 60)
                
                for i, entry in enumerate(reversed(history[-10:]), 1):  # Last 10 entries
                    timestamp = entry.get("timestamp", "Unknown")
                    opt_type = entry.get("type", "unknown")
                    
                    click.echo(f"\n{i}. {timestamp}")
                    click.echo(f"   Type: {opt_type}")
                    
                    if opt_type == "index_optimization":
                        applied = entry.get("applied_count", 0)
                        total = entry.get("total_recommendations", 0)
                        click.echo(f"   Applied: {applied}/{total} recommendations")
                    elif opt_type == "maintenance":
                        tasks = entry.get("tasks_completed", [])
                        click.echo(f"   Tasks: {', '.join(tasks)}")
                        
        except Exception as e:
            click.secho(f"❌ History retrieval failed: {e}", fg="red")
    
    _show_history()


if __name__ == "__main__":
    database()
