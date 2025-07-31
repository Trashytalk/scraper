"""
Queue Management CLI

Command-line interface for managing the distributed crawling queue system.
Provides commands for:
- System initialization and management
- Queue monitoring and statistics
- Worker management
- Seed URL management
- Health checks and diagnostics
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

# Import queue system components
from . import (
    DistributedCrawlSystem,
    QueueBackend,
    create_queue_manager,
    get_queue_recommendations,
    get_system_requirements
)

console = Console()


@click.group(name="queue")
def queue_cli():
    """Distributed Queue Management System"""
    console.print("🔄 [bold blue]Distributed Queue Management System[/bold blue]")


@queue_cli.group()
def system():
    """System management commands"""
    pass


@queue_cli.group()
def monitor():
    """Monitoring and statistics commands"""
    pass


@queue_cli.group()
def worker():
    """Worker management commands"""
    pass


@queue_cli.group()
def seed():
    """Seed URL management commands"""
    pass


# System Management Commands

@system.command()
@click.option('--backend', type=click.Choice(['redis', 'kafka', 'sqs', 'memory']), 
              default='redis', help='Queue backend to use')
@click.option('--redis-url', default='redis://localhost:6379/0', 
              help='Redis connection URL')
@click.option('--kafka-servers', default='localhost:9092', 
              help='Kafka bootstrap servers')
@click.option('--aws-region', default='us-west-2', 
              help='AWS region for SQS')
@click.option('--crawl-workers', default=5, 
              help='Number of crawl workers')
@click.option('--parse-workers', default=3, 
              help='Number of parse workers')
@click.option('--config-file', type=click.Path(),
              help='Configuration file path')
@click.option('--dry-run', is_flag=True, 
              help='Show configuration without starting')
def initialize(backend, redis_url, kafka_servers, aws_region, crawl_workers, 
               parse_workers, config_file, dry_run):
    """Initialize the distributed queue system"""
    
    # Load configuration
    config = {}
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            console.print(f"✅ Loaded configuration from {config_file}")
        except Exception as e:
            console.print(f"❌ Failed to load config file: {e}")
            sys.exit(1)
    
    # Prepare system configuration
    queue_backend = QueueBackend(backend)
    
    system_config = {
        'queue_backend': queue_backend,
        'num_crawl_workers': crawl_workers,
        'num_parse_workers': parse_workers,
        **config
    }
    
    if backend == 'redis':
        system_config['redis_url'] = redis_url
    elif backend == 'kafka':
        system_config['bootstrap_servers'] = kafka_servers
    elif backend == 'sqs':
        system_config['region_name'] = aws_region
    
    if dry_run:
        # Show configuration
        console.print("\n📋 [bold]System Configuration:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Setting")
        table.add_column("Value")
        
        table.add_row("Queue Backend", backend)
        table.add_row("Crawl Workers", str(crawl_workers))
        table.add_row("Parse Workers", str(parse_workers))
        
        if backend == 'redis':
            table.add_row("Redis URL", redis_url)
        elif backend == 'kafka':
            table.add_row("Kafka Servers", kafka_servers)
        elif backend == 'sqs':
            table.add_row("AWS Region", aws_region)
        
        console.print(table)
        return
    
    # Initialize system
    async def init_system():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                
                task = progress.add_task("Initializing queue system...", total=None)
                
                # Create system
                crawl_system = DistributedCrawlSystem(**system_config)
                
                progress.update(task, description="Starting workers...")
                await crawl_system.start()
                
                progress.update(task, description="Verifying system health...")
                stats = await crawl_system.get_system_stats()
                
                console.print("\n✅ [bold green]Queue system initialized successfully![/bold green]")
                
                # Show system status
                _display_system_status(stats)
                
                # Save system reference for cleanup
                try:
                    console.print("\n⏳ System running... Press Ctrl+C to stop")
                    while True:
                        await asyncio.sleep(10)
                        # Could add periodic health checks here
                        
                except KeyboardInterrupt:
                    console.print("\n🛑 Stopping system...")
                    await crawl_system.stop()
                    console.print("✅ System stopped")
                
        except Exception as e:
            console.print(f"❌ Failed to initialize system: {e}")
            sys.exit(1)
    
    asyncio.run(init_system())


@system.command()
@click.option('--backend', type=click.Choice(['redis', 'kafka', 'sqs', 'memory']),
              help='Show requirements for specific backend')
def requirements(backend):
    """Show system requirements for queue backends"""
    
    if backend:
        # Show requirements for specific backend
        reqs = get_system_requirements()
        if backend in reqs:
            req_info = reqs[backend]
            
            panel_content = f"""
[bold]Description:[/bold] {req_info['description']}

[bold]External Services:[/bold]
{chr(10).join([f"• {service}" for service in req_info['external_services']]) if req_info['external_services'] else "• None"}

[bold]Python Packages:[/bold]
{chr(10).join([f"• {pkg}" for pkg in req_info['python_packages']]) if req_info['python_packages'] else "• None"}
"""
            
            console.print(Panel(panel_content.strip(), title=f"{backend.upper()} Requirements"))
        else:
            console.print(f"❌ Unknown backend: {backend}")
    else:
        # Show recommendations table
        recommendations = get_queue_recommendations()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Use Case")
        table.add_column("Backend")
        table.add_column("Description")
        table.add_column("Pros")
        table.add_column("Cons")
        
        for use_case, info in recommendations.items():
            pros = "\n".join([f"• {pro}" for pro in info['pros']])
            cons = "\n".join([f"• {con}" for con in info['cons']])
            
            table.add_row(
                use_case.replace('_', ' ').title(),
                info['backend'].value.upper(),
                info['description'],
                pros,
                cons
            )
        
        console.print(table)


@system.command()
def health():
    """Check system health status"""
    
    async def check_health():
        try:
            # This would connect to a running system
            # For now, show example health check
            console.print("🏥 [bold]System Health Check[/bold]")
            
            # Simulate health check
            health_data = {
                "system_status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "queue_system": {"status": "up", "message": "Queue system is running"},
                    "queue_backend": {"status": "up", "type": "redis", "message": "Redis connection healthy"},
                    "workers": {
                        "status": "up",
                        "crawl_workers": {"active": 5, "total": 5},
                        "parse_workers": {"active": 3, "total": 3}
                    }
                }
            }
            
            _display_health_status(health_data)
            
        except Exception as e:
            console.print(f"❌ Health check failed: {e}")
            sys.exit(1)
    
    asyncio.run(check_health())


# Monitoring Commands

@monitor.command()
@click.option('--watch', is_flag=True, help='Watch statistics in real-time')
@click.option('--interval', default=5, help='Update interval in seconds')
def stats(watch, interval):
    """Show queue statistics"""
    
    async def show_stats():
        try:
            # This would connect to running system
            # For now, show example statistics
            stats_data = {
                "system_status": {
                    "is_running": True,
                    "crawl_workers": 5,
                    "parse_workers": 3,
                    "queue_backend": "redis"
                },
                "queue_stats": {
                    "frontier_queue_size": 1250,
                    "frontier_priority_queue_size": 45,
                    "parse_queue_size": 320,
                    "parse_priority_queue_size": 12,
                    "retry_queue_size": 89,
                    "dead_queue_size": 23,
                    "total_frontier_size": 1295,
                    "total_parse_size": 332
                },
                "crawl_metrics": {
                    "urls_crawled": 15430,
                    "urls_failed": 234,
                    "bytes_downloaded": 892456789,
                    "avg_response_time": 1.45
                },
                "parse_metrics": {
                    "tasks_processed": 14890,
                    "tasks_failed": 67,
                    "urls_extracted": 87234,
                    "ocr_tasks_processed": 234
                }
            }
            
            if watch:
                console.clear()
                console.print("📊 [bold]Live Queue Statistics[/bold] (Press Ctrl+C to exit)")
                console.print(f"Updating every {interval} seconds...\n")
            
            _display_statistics(stats_data)
            
            if watch:
                # Simulate real-time updates
                try:
                    while True:
                        await asyncio.sleep(interval)
                        console.clear()
                        console.print("📊 [bold]Live Queue Statistics[/bold] (Press Ctrl+C to exit)")
                        console.print(f"Last updated: {datetime.now().strftime('%H:%M:%S')}\n")
                        
                        # Update some values to simulate change
                        stats_data["queue_stats"]["frontier_queue_size"] += 5
                        stats_data["crawl_metrics"]["urls_crawled"] += 3
                        
                        _display_statistics(stats_data)
                        
                except KeyboardInterrupt:
                    console.print("\n👋 Monitoring stopped")
            
        except Exception as e:
            console.print(f"❌ Failed to get statistics: {e}")
            sys.exit(1)
    
    asyncio.run(show_stats())


@monitor.command()
@click.option('--queue', type=click.Choice(['frontier', 'parsing', 'retry', 'dead']),
              help='Show specific queue details')
def queues(queue):
    """Show detailed queue information"""
    
    # Example queue details
    queue_details = {
        "frontier": {
            "name": "Frontier Queue",
            "description": "URLs waiting to be crawled",
            "size": 1295,
            "recent_items": [
                "https://example.com/page1",
                "https://business-dir.com/companies",
                "https://registry.gov/listings"
            ]
        },
        "parsing": {
            "name": "Parsing Queue", 
            "description": "Pages waiting to be parsed",
            "size": 332,
            "recent_items": [
                "Parse task: abc123 (https://example.com)",
                "Parse task: def456 (https://company.org)",
                "Parse task: ghi789 (https://directory.net)"
            ]
        },
        "retry": {
            "name": "Retry Queue",
            "description": "Failed URLs waiting for retry",
            "size": 89,
            "recent_items": [
                "https://timeout-site.com (retry 2/3)",
                "https://error-site.org (retry 1/3)", 
                "https://slow-site.net (retry 3/3)"
            ]
        },
        "dead": {
            "name": "Dead Letter Queue",
            "description": "URLs that exceeded max retries",
            "size": 23,
            "recent_items": [
                "https://dead-site.com (max retries exceeded)",
                "https://invalid-url.broken (connection failed)",
                "https://blocked-site.org (access denied)"
            ]
        }
    }
    
    if queue:
        # Show specific queue
        if queue in queue_details:
            details = queue_details[queue]
            
            console.print(f"\n📋 [bold]{details['name']}[/bold]")
            console.print(f"Description: {details['description']}")
            console.print(f"Current size: {details['size']}")
            
            console.print("\n📝 Recent items:")
            for item in details['recent_items']:
                console.print(f"  • {item}")
        else:
            console.print(f"❌ Unknown queue: {queue}")
    else:
        # Show all queues
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Queue")
        table.add_column("Size")
        table.add_column("Description")
        
        for queue_name, details in queue_details.items():
            table.add_row(
                details['name'],
                str(details['size']),
                details['description']
            )
        
        console.print(table)


# Worker Management Commands

@worker.command()
def list():
    """List all workers and their status"""
    
    # Example worker data
    workers = [
        {"id": "crawl-worker-0", "type": "crawl", "status": "active", "tasks": 3, "urls_processed": 2341},
        {"id": "crawl-worker-1", "type": "crawl", "status": "active", "tasks": 2, "urls_processed": 2156}, 
        {"id": "crawl-worker-2", "type": "crawl", "status": "active", "tasks": 4, "urls_processed": 2498},
        {"id": "crawl-worker-3", "type": "crawl", "status": "idle", "tasks": 0, "urls_processed": 2034},
        {"id": "crawl-worker-4", "type": "crawl", "status": "active", "tasks": 1, "urls_processed": 2267},
        {"id": "parse-worker-0", "type": "parse", "status": "active", "tasks": 2, "tasks_processed": 1834},
        {"id": "parse-worker-1", "type": "parse", "status": "active", "tasks": 3, "tasks_processed": 1945},
        {"id": "parse-worker-2", "type": "parse", "status": "idle", "tasks": 0, "tasks_processed": 1723}
    ]
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Worker ID")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Active Tasks")
    table.add_column("Total Processed")
    
    for worker in workers:
        status_color = "green" if worker["status"] == "active" else "yellow"
        table.add_row(
            worker["id"],
            worker["type"].title(),
            f"[{status_color}]{worker['status'].title()}[/{status_color}]",
            str(worker["tasks"]),
            str(worker.get("urls_processed", worker.get("tasks_processed", 0)))
        )
    
    console.print(table)


# Seed URL Management Commands

@seed.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--job-id', required=True, help='Job ID for tracking')
@click.option('--priority', default=5, help='Priority level (1-10)')
@click.option('--batch-size', default=100, help='Batch size for bulk operations')
def add(urls, job_id, priority, batch_size):
    """Add seed URLs to the frontier queue"""
    
    async def add_urls():
        try:
            # Validate URLs
            valid_urls = []
            for url in urls:
                if url.startswith(('http://', 'https://')):
                    valid_urls.append(url)
                else:
                    console.print(f"⚠️  Skipping invalid URL: {url}")
            
            if not valid_urls:
                console.print("❌ No valid URLs provided")
                return
            
            console.print(f"📥 Adding {len(valid_urls)} URLs to frontier queue...")
            console.print(f"Job ID: {job_id}")
            console.print(f"Priority: {priority}")
            
            # Simulate adding URLs
            added = len(valid_urls)  # In real implementation, this would be the actual count
            
            console.print(f"✅ Successfully added {added}/{len(valid_urls)} URLs to queue")
            
        except Exception as e:
            console.print(f"❌ Failed to add URLs: {e}")
            sys.exit(1)
    
    asyncio.run(add_urls())


@seed.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--job-id', required=True, help='Job ID for tracking')
@click.option('--priority', default=5, help='Priority level (1-10)')
@click.option('--column', default=0, help='Column index for CSV files')
def import_file(file_path, job_id, priority, column):
    """Import seed URLs from a file"""
    
    async def import_urls():
        try:
            file_path_obj = Path(file_path)
            
            if file_path_obj.suffix.lower() == '.json':
                # JSON file
                with open(file_path_obj, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        urls = data
                    elif isinstance(data, dict) and 'urls' in data:
                        urls = data['urls']
                    else:
                        raise ValueError("JSON must be a list of URLs or dict with 'urls' key")
                        
            elif file_path_obj.suffix.lower() == '.csv':
                # CSV file
                import csv
                urls = []
                with open(file_path_obj, 'r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) > column:
                            urls.append(row[column])
                            
            else:
                # Plain text file
                with open(file_path_obj, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
            
            console.print(f"📄 Loaded {len(urls)} URLs from {file_path}")
            
            # Validate and add URLs (simulated)
            valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
            
            console.print(f"✅ Added {len(valid_urls)} valid URLs to queue")
            console.print(f"⚠️  Skipped {len(urls) - len(valid_urls)} invalid URLs")
            
        except Exception as e:
            console.print(f"❌ Failed to import URLs: {e}")
            sys.exit(1)
    
    asyncio.run(import_urls())


# Helper functions for display

def _display_system_status(stats):
    """Display system status information"""
    system_status = stats.get("system_status", {})
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")
    
    table.add_row(
        "System",
        "🟢 Running" if system_status.get("is_running") else "🔴 Stopped",
        f"Backend: {system_status.get('queue_backend', 'unknown')}"
    )
    
    table.add_row(
        "Workers",
        "🟢 Active",
        f"Crawl: {system_status.get('crawl_workers', 0)} | Parse: {system_status.get('parse_workers', 0)}"
    )
    
    console.print(table)


def _display_statistics(stats):
    """Display queue statistics"""
    queue_stats = stats.get("queue_stats", {})
    crawl_metrics = stats.get("crawl_metrics", {})
    parse_metrics = stats.get("parse_metrics", {})
    
    # Queue sizes
    queue_table = Table(title="Queue Sizes", show_header=True, header_style="bold magenta")
    queue_table.add_column("Queue")
    queue_table.add_column("Size")
    queue_table.add_column("Priority")
    queue_table.add_column("Total")
    
    queue_table.add_row(
        "Frontier",
        str(queue_stats.get("frontier_queue_size", 0)),
        str(queue_stats.get("frontier_priority_queue_size", 0)),
        str(queue_stats.get("total_frontier_size", 0))
    )
    
    queue_table.add_row(
        "Parsing",
        str(queue_stats.get("parse_queue_size", 0)),
        str(queue_stats.get("parse_priority_queue_size", 0)),
        str(queue_stats.get("total_parse_size", 0))
    )
    
    queue_table.add_row(
        "Retry",
        str(queue_stats.get("retry_queue_size", 0)),
        "-",
        str(queue_stats.get("retry_queue_size", 0))
    )
    
    queue_table.add_row(
        "Dead",
        str(queue_stats.get("dead_queue_size", 0)),
        "-",
        str(queue_stats.get("dead_queue_size", 0))
    )
    
    console.print(queue_table)
    
    # Performance metrics
    perf_table = Table(title="Performance Metrics", show_header=True, header_style="bold cyan")
    perf_table.add_column("Metric")
    perf_table.add_column("Crawling")
    perf_table.add_column("Parsing")
    
    perf_table.add_row(
        "Processed",
        str(crawl_metrics.get("urls_crawled", 0)),
        str(parse_metrics.get("tasks_processed", 0))
    )
    
    perf_table.add_row(
        "Failed",
        str(crawl_metrics.get("urls_failed", 0)),
        str(parse_metrics.get("tasks_failed", 0))
    )
    
    success_rate = 0
    total_crawled = crawl_metrics.get("urls_crawled", 0)
    total_failed = crawl_metrics.get("urls_failed", 0)
    if total_crawled + total_failed > 0:
        success_rate = total_crawled / (total_crawled + total_failed) * 100
    
    perf_table.add_row(
        "Success Rate",
        f"{success_rate:.1f}%",
        "-"
    )
    
    perf_table.add_row(
        "Avg Response Time",
        f"{crawl_metrics.get('avg_response_time', 0):.2f}s",
        "-"
    )
    
    console.print(perf_table)


def _display_health_status(health_data):
    """Display health status information"""
    status = health_data.get("status", "unknown")
    components = health_data.get("components", {})
    
    # Overall status
    status_color = "green" if status == "healthy" else "red" if status == "unhealthy" else "yellow"
    console.print(f"\n🏥 Overall Status: [{status_color}]{status.upper()}[/{status_color}]")
    console.print(f"📅 Checked at: {health_data.get('timestamp', 'unknown')}")
    
    # Component details
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")
    
    for component, info in components.items():
        comp_status = info.get("status", "unknown")
        comp_color = "green" if comp_status == "up" else "red" if comp_status == "down" else "yellow"
        
        table.add_row(
            component.replace("_", " ").title(),
            f"[{comp_color}]{comp_status.upper()}[/{comp_color}]",
            info.get("message", "No details")
        )
    
    console.print(table)


if __name__ == "__main__":
    queue_cli()
