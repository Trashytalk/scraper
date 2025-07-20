"""
Performance optimization CLI commands.
"""

import asyncio
import click
import json
import time
from typing import Dict, Any

try:
    from ..performance.optimizer import get_performance_optimizer, OptimizationConfig
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False


@click.group()
def performance() -> None:
    """Performance optimization commands."""
    if not PERFORMANCE_AVAILABLE:
        click.echo("❌ Performance optimization not available - install required dependencies")
        return


@performance.command()
def status() -> None:
    """Show performance optimization status."""
    if not PERFORMANCE_AVAILABLE:
        return
    
    click.echo("⚡ Performance Optimization Status")
    click.echo("=" * 40)
    
    try:
        optimizer = get_performance_optimizer()
        
        # Run synchronous analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analysis = loop.run_until_complete(optimizer.run_performance_analysis())
        
        # Display status
        click.echo(f"✅ Optimization System: Active")
        click.echo(f"⏱️  Analysis Time: {analysis['timestamp']}")
        
        # Cache stats
        cache_stats = analysis.get('cache_performance', {})
        if cache_stats:
            click.echo(f"\n📋 Cache Performance:")
            click.echo(f"   Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")
            click.echo(f"   Total Requests: {cache_stats.get('total_requests', 0)}")
            click.echo(f"   Redis Connected: {'Yes' if cache_stats.get('redis_connected', False) else 'No'}")
        
        # Task stats
        task_stats = analysis.get('task_performance', {})
        if task_stats:
            click.echo(f"\n🔧 Task Processing:")
            click.echo(f"   Total Tasks: {task_stats.get('total_tasks', 0)}")
            click.echo(f"   Active Tasks: {task_stats.get('active_tasks', 0)}")
            click.echo(f"   Error Rate: {task_stats.get('error_rate', 0):.1%}")
        
        # Memory stats
        memory_stats = analysis.get('memory_performance', {})
        if memory_stats and 'current_memory_percent' in memory_stats:
            click.echo(f"\n💾 Memory Usage:")
            click.echo(f"   Current: {memory_stats['current_memory_percent']:.1f}%")
            click.echo(f"   Peak: {memory_stats.get('peak_memory_percent', 0):.1f}%")
            click.echo(f"   GC Collections: {memory_stats.get('gc_collections', 0)}")
        
        # System stats
        system_stats = analysis.get('system_performance', {})
        if system_stats and 'cpu_percent' in system_stats:
            click.echo(f"\n🖥️  System Resources:")
            click.echo(f"   CPU: {system_stats['cpu_percent']:.1f}%")
            click.echo(f"   Memory: {system_stats['memory_percent']:.1f}%")
            click.echo(f"   Disk: {system_stats['disk_percent']:.1f}%")
        
    except Exception as e:
        click.echo(f"❌ Failed to get performance status: {e}")


@performance.command()
@click.option('--format', default='table', help='Output format: table, json')
def metrics(format: str) -> None:
    """Show detailed performance metrics."""
    if not PERFORMANCE_AVAILABLE:
        return
    
    try:
        optimizer = get_performance_optimizer()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        analysis = loop.run_until_complete(optimizer.run_performance_analysis())
        
        if format == 'json':
            click.echo(json.dumps(analysis, indent=2, default=str))
        else:
            click.echo("📊 Performance Metrics")
            click.echo("=" * 40)
            
            for category, stats in analysis.items():
                if category == 'timestamp':
                    continue
                    
                click.echo(f"\n{category.replace('_', ' ').title()}:")
                if isinstance(stats, dict):
                    for key, value in stats.items():
                        if isinstance(value, float):
                            click.echo(f"   {key}: {value:.3f}")
                        else:
                            click.echo(f"   {key}: {value}")
    
    except Exception as e:
        click.echo(f"❌ Failed to get metrics: {e}")


@performance.command()
@click.argument('profile', type=click.Choice(['memory_focused', 'performance_focused', 'balanced']))
def optimize(profile: str) -> None:
    """Apply optimization profile."""
    if not PERFORMANCE_AVAILABLE:
        return
    
    click.echo(f"⚡ Applying {profile} optimization profile...")
    
    try:
        optimizer = get_performance_optimizer()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(optimizer.apply_optimizations(profile))
        
        click.echo("✅ Optimization applied successfully!")
        click.echo(f"Profile: {result['profile_applied']}")
        
        if result['changes']:
            click.echo("\nChanges made:")
            for change in result['changes']:
                click.echo(f"  • {change}")
    
    except Exception as e:
        click.echo(f"❌ Failed to apply optimization: {e}")


@performance.command()
@click.option('--pattern', help='Clear specific cache pattern')
def clear_cache(pattern: str) -> None:
    """Clear performance cache."""
    if not PERFORMANCE_AVAILABLE:
        return
    
    click.echo("🧹 Clearing performance cache...")
    
    try:
        optimizer = get_performance_optimizer()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if pattern:
            cleared_count = loop.run_until_complete(optimizer.cache.clear_pattern(pattern))
            click.echo(f"✅ Cleared {cleared_count} entries matching '{pattern}'")
        else:
            # Clear common patterns
            patterns = ["dashboard", "analytics", "metrics", "insights"]
            total_cleared = 0
            for p in patterns:
                cleared = loop.run_until_complete(optimizer.cache.clear_pattern(p))
                total_cleared += cleared
            
            click.echo(f"✅ Cleared {total_cleared} cache entries")
    
    except Exception as e:
        click.echo(f"❌ Failed to clear cache: {e}")


@performance.command()
def benchmark() -> None:
    """Run performance benchmark."""
    if not PERFORMANCE_AVAILABLE:
        return
    
    click.echo("⏱️  Running performance benchmark...")
    
    try:
        optimizer = get_performance_optimizer()
        
        # Test cache performance
        click.echo("Testing cache operations...")
        start_time = time.time()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def cache_benchmark() -> Dict[str, Any]:
            # Test cache set/get operations
            for i in range(100):
                await optimizer.cache.set(f"benchmark_key_{i}", f"value_{i}")
            
            hits = 0
            for i in range(100):
                result = await optimizer.cache.get(f"benchmark_key_{i}")
                if result is not None:
                    hits += 1
            
            return {'hits': hits, 'total': 100}
        
        result = loop.run_until_complete(cache_benchmark())
        cache_time = time.time() - start_time
        
        click.echo(f"✅ Cache benchmark: {result['hits']}/{result['total']} hits in {cache_time:.3f}s")
        
        # Test task processing
        click.echo("Testing task processing...")
        start_time = time.time()
        
        async def task_benchmark() -> None:
            tasks = []
            for i in range(10):
                task = optimizer.task_optimizer.submit_task(
                    lambda x=i: time.sleep(0.01),  # 10ms task
                    task_name=f"benchmark_{i}"
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        loop.run_until_complete(task_benchmark())
        task_time = time.time() - start_time
        
        click.echo(f"✅ Task benchmark: 10 tasks in {task_time:.3f}s")
        
        click.echo(f"\n🎯 Overall Performance Score: {((100/cache_time) + (10/task_time))/2:.1f}")
    
    except Exception as e:
        click.echo(f"❌ Benchmark failed: {e}")


@performance.command()
def recommendations() -> None:
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
        
        recommendations = []
        
        # Analyze cache performance
        cache_stats = analysis.get("cache_performance", {})
        if cache_stats.get("hit_rate", 1.0) < 0.7:
            recommendations.append({
                "priority": "HIGH",
                "category": "Cache",
                "issue": f"Low cache hit rate: {cache_stats.get('hit_rate', 0):.1%}",
                "recommendation": "Increase cache TTL or review caching strategy"
            })
        
        # Analyze memory usage
        memory_stats = analysis.get("memory_performance", {})
        if memory_stats.get("current_memory_percent", 0) > 80:
            recommendations.append({
                "priority": "HIGH", 
                "category": "Memory",
                "issue": f"High memory usage: {memory_stats.get('current_memory_percent', 0):.1f}%",
                "recommendation": "Consider memory optimization or scaling"
            })
        
        # Analyze task performance
        task_stats = analysis.get("task_performance", {})
        if task_stats.get("error_rate", 0) > 0.1:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Tasks",
                "issue": f"High task error rate: {task_stats.get('error_rate', 0):.1%}",
                "recommendation": "Review task implementations and error handling"
            })
        
        if not recommendations:
            click.echo("✅ No performance issues detected! System is running optimally.")
        else:
            for i, rec in enumerate(recommendations, 1):
                click.echo(f"\n{i}. [{rec['priority']}] {rec['category']}")
                click.echo(f"   Issue: {rec['issue']}")
                click.echo(f"   Action: {rec['recommendation']}")
    
    except Exception as e:
        click.echo(f"❌ Failed to get recommendations: {e}")


if __name__ == "__main__":
    performance()
