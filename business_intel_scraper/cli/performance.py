"""Performance CLI commands for the BI Scraper."""

import click
import asyncio
import json
import time
from typing import Optional

try:
    from ..backend.performance.optimizer import get_performance_optimizer

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False


@click.group()
def performance():
    """Performance optimization and monitoring commands."""
    if not PERFORMANCE_AVAILABLE:
        click.echo(
            "❌ Performance module not available. Install optional dependencies."
        )
        return


@performance.command()
def status():
    """Show current performance status."""
    if not PERFORMANCE_AVAILABLE:
        return

    click.echo("⚡ Performance Status Dashboard")
    click.echo("=" * 50)

    try:
        optimizer = get_performance_optimizer()

        # Get performance analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(optimizer.run_performance_analysis())

        # System overview
        click.echo(f"🕐 Timestamp: {analysis.get('timestamp', 'N/A')}")

        # Cache performance
        cache_stats = analysis.get("cache_performance", {})
        if cache_stats:
            click.echo("\n📊 Cache Performance:")
            click.echo(f"   Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")
            click.echo(f"   Total Requests: {cache_stats.get('total_requests', 0)}")
            click.echo(f"   Cache Size: {cache_stats.get('cache_size', 0)} entries")
            click.echo(
                f"   Redis: {'✅ Connected' if cache_stats.get('redis_connected') else '❌ Disconnected'}"
            )

        # System performance
        system_stats = analysis.get("system_performance", {})
        if system_stats:
            click.echo("\n🖥️  System Resources:")
            click.echo(f"   CPU Usage: {system_stats.get('cpu_percent', 0):.1f}%")
            click.echo(f"   Memory Usage: {system_stats.get('memory_percent', 0):.1f}%")
            click.echo(f"   Disk Usage: {system_stats.get('disk_percent', 0):.1f}%")

        # Memory optimization
        memory_stats = analysis.get("memory_performance", {})
        if memory_stats:
            click.echo("\n💾 Memory Management:")
            click.echo(
                f"   Current Usage: {memory_stats.get('current_memory_percent', 0):.1f}%"
            )
            click.echo(f"   GC Collections: {memory_stats.get('gc_collections', 0)}")
            click.echo(f"   Objects Created: {memory_stats.get('objects_created', 0)}")

        # Task processing
        task_stats = analysis.get("task_performance", {})
        if task_stats:
            click.echo("\n🔄 Task Processing:")
            click.echo(f"   Total Tasks: {task_stats.get('total_tasks', 0)}")
            click.echo(f"   Active Tasks: {task_stats.get('active_tasks', 0)}")
            click.echo(f"   Success Rate: {(1 - task_stats.get('error_rate', 0)):.1%}")

        loop.close()

    except Exception as e:
        click.echo(f"❌ Error getting performance status: {e}")


@performance.command()
@click.option("--json-output", is_flag=True, help="Output as JSON")
def metrics(json_output):
    """Get detailed performance metrics."""
    if not PERFORMANCE_AVAILABLE:
        return

    try:
        optimizer = get_performance_optimizer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(optimizer.run_performance_analysis())
        loop.close()

        if json_output:
            click.echo(json.dumps(analysis, indent=2, default=str))
        else:
            click.echo("📈 Detailed Performance Metrics")
            click.echo("=" * 40)

            for category, data in analysis.items():
                if category == "timestamp":
                    continue

                click.echo(f"\n{category.replace('_', ' ').title()}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, float):
                            click.echo(f"   {key}: {value:.3f}")
                        else:
                            click.echo(f"   {key}: {value}")
                else:
                    click.echo(f"   {data}")

    except Exception as e:
        click.echo(f"❌ Error getting metrics: {e}")


@performance.command()
@click.argument(
    "profile", type=click.Choice(["balanced", "memory_focused", "performance_focused"])
)
def optimize(profile):
    """Apply performance optimization profile."""
    if not PERFORMANCE_AVAILABLE:
        return

    click.echo(f"⚙️ Applying {profile} optimization profile...")

    try:
        optimizer = get_performance_optimizer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(optimizer.apply_optimizations(profile))
        loop.close()

        click.echo(
            f"✅ Successfully applied {result.get('profile_applied', profile)} profile"
        )

        changes = result.get("changes", [])
        if changes:
            click.echo("\nOptimization changes made:")
            for change in changes:
                click.echo(f"  • {change}")
        else:
            click.echo("No changes needed - system already optimized")

    except Exception as e:
        click.echo(f"❌ Error applying optimization: {e}")


@performance.command()
@click.option(
    "--pattern", help='Clear specific cache pattern (e.g. "dashboard", "analytics")'
)
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def clear_cache(pattern: Optional[str], confirm: bool):
    """Clear performance cache."""
    if not PERFORMANCE_AVAILABLE:
        return

    if not confirm:
        if pattern:
            if not click.confirm(f"Clear cache entries matching '{pattern}'?"):
                return
        else:
            if not click.confirm("Clear all performance cache?"):
                return

    try:
        optimizer = get_performance_optimizer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if pattern:
            cleared = loop.run_until_complete(optimizer.cache.clear_pattern(pattern))
            click.echo(f"✅ Cleared {cleared} cache entries matching '{pattern}'")
        else:
            # Clear common patterns
            common_patterns = [
                "dashboard",
                "analytics",
                "metrics",
                "insights",
                "reports",
            ]
            total_cleared = 0

            for p in common_patterns:
                cleared = loop.run_until_complete(optimizer.cache.clear_pattern(p))
                total_cleared += cleared
                if cleared > 0:
                    click.echo(f"   Cleared {cleared} entries for pattern '{p}'")

            click.echo(f"✅ Total cleared: {total_cleared} cache entries")

        loop.close()

    except Exception as e:
        click.echo(f"❌ Error clearing cache: {e}")


@performance.command()
@click.option("--iterations", default=50, help="Number of benchmark iterations")
def benchmark(iterations: int):
    """Run performance benchmark tests."""
    if not PERFORMANCE_AVAILABLE:
        return

    click.echo(f"🏃 Running performance benchmark ({iterations} iterations)...")
    click.echo("=" * 50)

    try:
        optimizer = get_performance_optimizer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Cache benchmark
        click.echo("1️⃣  Testing cache performance...")
        cache_start = time.time()

        async def cache_benchmark():
            # Write test
            write_times = []
            for i in range(iterations):
                start = time.time()
                await optimizer.cache.set(f"bench_key_{i}", f"test_value_{i}", ttl=60)
                write_times.append(time.time() - start)

            # Read test
            read_times = []
            cache_hits = 0
            for i in range(iterations):
                start = time.time()
                result = await optimizer.cache.get(f"bench_key_{i}")
                read_times.append(time.time() - start)
                if result is not None:
                    cache_hits += 1

            return {
                "write_avg": sum(write_times) / len(write_times),
                "read_avg": sum(read_times) / len(read_times),
                "hit_rate": cache_hits / iterations,
                "total_time": time.time() - cache_start,
            }

        cache_results = loop.run_until_complete(cache_benchmark())

        click.echo(f"   ✅ Cache write: {cache_results['write_avg']*1000:.2f}ms avg")
        click.echo(f"   ✅ Cache read: {cache_results['read_avg']*1000:.2f}ms avg")
        click.echo(f"   ✅ Hit rate: {cache_results['hit_rate']:.1%}")
        click.echo(f"   ⏱️  Total time: {cache_results['total_time']:.2f}s")

        # Task processing benchmark
        click.echo("\n2️⃣  Testing task processing...")
        task_start = time.time()

        async def task_benchmark():
            tasks = []
            for i in range(min(20, iterations)):  # Limit concurrent tasks
                task = optimizer.task_optimizer.submit_task(
                    lambda: time.sleep(0.01),  # 10ms work
                    task_name=f"benchmark_task_{i}",
                )
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)
            return time.time() - task_start

        task_time = loop.run_until_complete(task_benchmark())
        click.echo(f"   ✅ Processed {min(20, iterations)} tasks in {task_time:.2f}s")
        click.echo(
            f"   ✅ Average task time: {(task_time/min(20, iterations))*1000:.2f}ms"
        )

        # Memory benchmark
        click.echo("\n3️⃣  Testing memory management...")
        memory_start = time.time()

        # Create and cleanup test objects
        test_objects = []
        for i in range(iterations):
            test_objects.append([i] * 1000)  # Small memory allocation

        optimizer.memory_optimizer.cleanup()
        memory_time = time.time() - memory_start

        click.echo(f"   ✅ Memory test completed in {memory_time:.2f}s")

        # Overall score
        cache_score = 1000 / (cache_results["read_avg"] * 1000)  # Higher is better
        task_score = min(20, iterations) / task_time  # Tasks per second
        overall_score = (cache_score + task_score) / 2

        click.echo(f"\n🎯 Performance Score: {overall_score:.1f} (higher is better)")

        loop.close()

    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}")


@performance.command()
def recommendations():
    """Get performance optimization recommendations."""
    if not PERFORMANCE_AVAILABLE:
        return

    click.echo("💡 Performance Recommendations")
    click.echo("=" * 40)

    try:
        optimizer = get_performance_optimizer()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(optimizer.run_performance_analysis())
        loop.close()

        recommendations = []

        # Cache analysis
        cache_stats = analysis.get("cache_performance", {})
        hit_rate = cache_stats.get("hit_rate", 1.0)
        if hit_rate < 0.6:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Cache",
                    "issue": f"Low cache hit rate: {hit_rate:.1%}",
                    "action": "Review caching strategy, increase TTL, or add more cacheable operations",
                }
            )
        elif hit_rate < 0.8:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Cache",
                    "issue": f"Moderate cache hit rate: {hit_rate:.1%}",
                    "action": "Fine-tune cache keys and TTL values",
                }
            )

        # Memory analysis
        memory_stats = analysis.get("memory_performance", {})
        memory_percent = memory_stats.get("current_memory_percent", 0)
        if memory_percent > 85:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Memory",
                    "issue": f"High memory usage: {memory_percent:.1f}%",
                    "action": "Enable memory optimization profile or increase available memory",
                }
            )
        elif memory_percent > 70:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "category": "Memory",
                    "issue": f"Elevated memory usage: {memory_percent:.1f}%",
                    "action": "Monitor memory usage and consider optimization",
                }
            )

        # System analysis
        system_stats = analysis.get("system_performance", {})
        cpu_percent = system_stats.get("cpu_percent", 0)
        if cpu_percent > 80:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "CPU",
                    "issue": f"High CPU usage: {cpu_percent:.1f}%",
                    "action": "Scale horizontally or optimize CPU-intensive operations",
                }
            )

        # Task analysis
        task_stats = analysis.get("task_performance", {})
        error_rate = task_stats.get("error_rate", 0)
        if error_rate > 0.05:  # 5% error rate
            recommendations.append(
                {
                    "priority": "HIGH",
                    "category": "Tasks",
                    "issue": f"High task error rate: {error_rate:.1%}",
                    "action": "Review task implementations and improve error handling",
                }
            )

        if not recommendations:
            click.echo("✅ System is performing well! No recommendations at this time.")
            click.echo("\n💡 General tips:")
            click.echo("  • Monitor performance regularly")
            click.echo("  • Consider Redis for better cache performance")
            click.echo("  • Use appropriate optimization profiles for your workload")
        else:
            for i, rec in enumerate(recommendations, 1):
                priority_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}
                priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}

                click.echo(
                    f"\n{i}. {priority_emoji[rec['priority']]} [{rec['priority']}] {rec['category']}"
                )
                click.echo(f"   Issue: {rec['issue']}")
                click.echo(f"   Action: {rec['action']}")

    except Exception as e:
        click.echo(f"❌ Error generating recommendations: {e}")


@performance.command()
def monitor():
    """Start real-time performance monitoring."""
    if not PERFORMANCE_AVAILABLE:
        return

    click.echo("📊 Starting real-time performance monitor...")
    click.echo("Press Ctrl+C to stop")
    click.echo("=" * 50)

    try:
        optimizer = get_performance_optimizer()

        while True:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(optimizer.run_performance_analysis())
            loop.close()

            # Clear screen and show current stats
            click.clear()
            click.echo("📊 Real-time Performance Monitor")
            click.echo("=" * 50)
            click.echo(f"Timestamp: {analysis.get('timestamp', 'N/A')}")

            # Key metrics
            cache_stats = analysis.get("cache_performance", {})
            if cache_stats:
                click.echo(f"Cache Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")

            system_stats = analysis.get("system_performance", {})
            if system_stats:
                click.echo(
                    f"CPU: {system_stats.get('cpu_percent', 0):.1f}% | Memory: {system_stats.get('memory_percent', 0):.1f}%"
                )

            task_stats = analysis.get("task_performance", {})
            if task_stats:
                click.echo(
                    f"Active Tasks: {task_stats.get('active_tasks', 0)} | Success Rate: {(1-task_stats.get('error_rate', 0)):.1%}"
                )

            click.echo("\nPress Ctrl+C to stop monitoring...")

            # Wait 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        click.echo("\n👋 Monitoring stopped")
    except Exception as e:
        click.echo(f"❌ Monitoring error: {e}")


if __name__ == "__main__":
    performance()
