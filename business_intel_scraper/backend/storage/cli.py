"""Storage Layer CLI Commands"""

import asyncio
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import json

from .core import AdvancedStorageManager, DataLineageTracker
from .config import storage_config
from .models import RawDataModel, StructuredEntityModel


console = Console()


@click.group(name="storage")
def storage_cli():
    """Storage layer management commands."""
    pass


@storage_cli.command("init")
@click.option("--create-indexes", is_flag=True, help="Create search indexes")
@click.option("--create-buckets", is_flag=True, help="Create storage buckets")
@click.option("--test-connections", is_flag=True, help="Test all connections")
def init_storage(create_indexes: bool, create_buckets: bool, test_connections: bool):
    """Initialize the storage layer."""
    console.print("[bold blue]Initializing Storage Layer...[/bold blue]")
    
    async def _init():
        storage_manager = AdvancedStorageManager()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            if test_connections:
                task = progress.add_task("Testing connections...", total=None)
                try:
                    # Test database connection
                    await storage_manager._ensure_db_session()
                    console.print("✓ Database connection successful")
                    
                    # Test storage backend
                    await storage_manager._ensure_storage_client()
                    console.print("✓ Storage backend connection successful")
                    
                    # Test Elasticsearch
                    await storage_manager._ensure_elasticsearch_client()
                    console.print("✓ Elasticsearch connection successful")
                    
                except Exception as e:
                    console.print(f"❌ Connection test failed: {e}")
                    return
                finally:
                    progress.remove_task(task)
            
            if create_buckets:
                task = progress.add_task("Creating storage buckets...", total=None)
                try:
                    await storage_manager._ensure_bucket_exists()
                    console.print("✓ Storage bucket ready")
                except Exception as e:
                    console.print(f"❌ Failed to create bucket: {e}")
                finally:
                    progress.remove_task(task)
            
            if create_indexes:
                task = progress.add_task("Creating search indexes...", total=None)
                try:
                    await storage_manager._ensure_indexes_exist()
                    console.print("✓ Search indexes ready")
                except Exception as e:
                    console.print(f"❌ Failed to create indexes: {e}")
                finally:
                    progress.remove_task(task)
        
        console.print("[green]Storage layer initialized successfully![/green]")
    
    asyncio.run(_init())


@storage_cli.command("status")
def storage_status():
    """Show storage layer status and metrics."""
    
    async def _status():
        storage_manager = AdvancedStorageManager()
        
        # Get storage stats
        try:
            session = await storage_manager._ensure_db_session()
            
            # Raw data stats
            raw_data_count = await session.execute(
                "SELECT COUNT(*) FROM raw_data"
            )
            raw_data_count = raw_data_count.scalar()
            
            # Entity stats
            entity_count = await session.execute(
                "SELECT COUNT(*) FROM structured_entities"
            )
            entity_count = entity_count.scalar()
            
            # Relationship stats
            relationship_count = await session.execute(
                "SELECT COUNT(*) FROM entity_relationships"
            )
            relationship_count = relationship_count.scalar()
            
            # Quality metrics stats
            quality_metrics_count = await session.execute(
                "SELECT COUNT(*) FROM data_quality_metrics"
            )
            quality_metrics_count = quality_metrics_count.scalar()
            
            # Recent activity
            recent_raw_data = await session.execute(
                "SELECT COUNT(*) FROM raw_data WHERE created_at >= NOW() - INTERVAL '24 hours'"
            )
            recent_raw_data = recent_raw_data.scalar()
            
            recent_entities = await session.execute(
                "SELECT COUNT(*) FROM structured_entities WHERE extracted_at >= NOW() - INTERVAL '24 hours'"
            )
            recent_entities = recent_entities.scalar()
            
        except Exception as e:
            console.print(f"❌ Failed to get database stats: {e}")
            return
        
        # Create status table
        table = Table(title="Storage Layer Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("24h Activity", justify="right", style="green")
        
        table.add_row("Raw Data Records", str(raw_data_count), str(recent_raw_data))
        table.add_row("Structured Entities", str(entity_count), str(recent_entities))
        table.add_row("Entity Relationships", str(relationship_count), "-")
        table.add_row("Quality Metrics", str(quality_metrics_count), "-")
        
        console.print(table)
        
        # Show configuration
        config_panel = Panel(
            f"""[bold]Configuration:[/bold]
• Database: {storage_config.database_backend.value}
• Raw Storage: {storage_config.raw_storage_backend.value}
• Search Engine: {storage_config.indexing_engine.value}
• Caching: {'Enabled' if storage_config.enable_caching else 'Disabled'}
• Data Quality: {'Enabled' if storage_config.enable_data_quality_checks else 'Disabled'}
• Lineage Tracking: {'Enabled' if storage_config.enable_lineage_tracking else 'Disabled'}""",
            title="Storage Configuration"
        )
        console.print(config_panel)
    
    asyncio.run(_status())


@storage_cli.command("cleanup")
@click.option("--older-than-days", type=int, default=30, help="Delete records older than N days")
@click.option("--dry-run", is_flag=True, help="Show what would be deleted without deleting")
@click.confirmation_option(prompt="Are you sure you want to cleanup old data?")
def cleanup_storage(older_than_days: int, dry_run: bool):
    """Clean up old storage data."""
    
    async def _cleanup():
        storage_manager = AdvancedStorageManager()
        
        console.print(f"[yellow]Cleaning up data older than {older_than_days} days...[/yellow]")
        
        try:
            session = await storage_manager._ensure_db_session()
            
            # Find old records
            old_raw_data = await session.execute(
                f"SELECT COUNT(*) FROM raw_data WHERE created_at < NOW() - INTERVAL '{older_than_days} days'"
            )
            old_raw_data_count = old_raw_data.scalar()
            
            old_quality_metrics = await session.execute(
                f"SELECT COUNT(*) FROM data_quality_metrics WHERE measurement_date < NOW() - INTERVAL '{older_than_days} days'"
            )
            old_quality_metrics_count = old_quality_metrics.scalar()
            
            if dry_run:
                console.print(f"Would delete {old_raw_data_count} raw data records")
                console.print(f"Would delete {old_quality_metrics_count} quality metrics")
                return
            
            # Delete old records
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                if old_raw_data_count > 0:
                    task = progress.add_task("Deleting old raw data...", total=None)
                    await session.execute(
                        f"DELETE FROM raw_data WHERE created_at < NOW() - INTERVAL '{older_than_days} days'"
                    )
                    progress.remove_task(task)
                    console.print(f"✓ Deleted {old_raw_data_count} raw data records")
                
                if old_quality_metrics_count > 0:
                    task = progress.add_task("Deleting old quality metrics...", total=None)
                    await session.execute(
                        f"DELETE FROM data_quality_metrics WHERE measurement_date < NOW() - INTERVAL '{older_than_days} days'"
                    )
                    progress.remove_task(task)
                    console.print(f"✓ Deleted {old_quality_metrics_count} quality metrics")
                
                await session.commit()
            
            console.print("[green]Cleanup completed successfully![/green]")
            
        except Exception as e:
            console.print(f"❌ Cleanup failed: {e}")
    
    asyncio.run(_cleanup())


@storage_cli.command("reindex")
@click.option("--entity-type", help="Reindex specific entity type only")
@click.option("--force", is_flag=True, help="Force reindex even if up to date")
def reindex_search(entity_type: Optional[str], force: bool):
    """Reindex data in search engine."""
    
    async def _reindex():
        storage_manager = AdvancedStorageManager()
        
        console.print("[yellow]Reindexing search data...[/yellow]")
        
        try:
            session = await storage_manager._ensure_db_session()
            es_client = await storage_manager._ensure_elasticsearch_client()
            
            # Get entities to reindex
            if entity_type:
                query = f"SELECT * FROM structured_entities WHERE entity_type = '{entity_type}'"
            else:
                query = "SELECT * FROM structured_entities"
            
            entities = await session.execute(query)
            entities = entities.fetchall()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                task = progress.add_task(f"Reindexing {len(entities)} entities...", total=len(entities))
                
                for entity in entities:
                    # Index entity in Elasticsearch
                    doc_id = entity.entity_id
                    doc_body = {
                        "entity_id": entity.entity_id,
                        "entity_type": entity.entity_type,
                        "canonical_name": entity.canonical_name,
                        "display_name": entity.display_name,
                        "description": entity.description,
                        "category": entity.category,
                        "subcategory": entity.subcategory,
                        "confidence_score": entity.confidence_score,
                        "structured_data": entity.structured_data,
                        "contact_info": entity.contact_info,
                        "locations": entity.locations,
                        "extracted_at": entity.extracted_at.isoformat() if entity.extracted_at else None,
                        "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
                    }
                    
                    await es_client.index(
                        index=storage_config.entities_index_name,
                        id=doc_id,
                        body=doc_body
                    )
                    
                    progress.advance(task)
                
                progress.remove_task(task)
            
            console.print(f"[green]Successfully reindexed {len(entities)} entities![/green]")
            
        except Exception as e:
            console.print(f"❌ Reindexing failed: {e}")
    
    asyncio.run(_reindex())


@storage_cli.command("lineage")
@click.argument("entity_id")
@click.option("--max-depth", type=int, default=3, help="Maximum lineage depth to show")
@click.option("--direction", type=click.Choice(["upstream", "downstream", "both"]), default="both")
def show_lineage(entity_id: str, max_depth: int, direction: str):
    """Show data lineage for an entity."""
    
    async def _show_lineage():
        storage_manager = AdvancedStorageManager()
        lineage_tracker = DataLineageTracker(storage_manager)
        
        try:
            if direction in ["upstream", "both"]:
                upstream = await lineage_tracker.get_upstream_lineage(
                    target_type="entity",
                    target_id=entity_id,
                    max_depth=max_depth
                )
                
                if upstream:
                    console.print("[bold blue]Upstream Lineage:[/bold blue]")
                    for item in upstream:
                        console.print(f"  {item['source_type']}:{item['source_id']} -> {item['transformation_type']}")
                else:
                    console.print("[yellow]No upstream lineage found[/yellow]")
            
            if direction in ["downstream", "both"]:
                downstream = await lineage_tracker.get_downstream_lineage(
                    source_type="entity",
                    source_id=entity_id,
                    max_depth=max_depth
                )
                
                if downstream:
                    console.print("[bold blue]Downstream Lineage:[/bold blue]")
                    for item in downstream:
                        console.print(f"  {item['transformation_type']} -> {item['target_type']}:{item['target_id']}")
                else:
                    console.print("[yellow]No downstream lineage found[/yellow]")
        
        except Exception as e:
            console.print(f"❌ Failed to get lineage: {e}")
    
    asyncio.run(_show_lineage())


@storage_cli.command("quality-report")
@click.option("--entity-type", help="Generate report for specific entity type")
@click.option("--format", type=click.Choice(["table", "json"]), default="table")
def quality_report(entity_type: Optional[str], format: str):
    """Generate data quality report."""
    
    async def _quality_report():
        storage_manager = AdvancedStorageManager()
        
        try:
            session = await storage_manager._ensure_db_session()
            
            # Get quality metrics
            if entity_type:
                query = """
                    SELECT 
                        dqm.metric_name,
                        AVG(dqm.metric_value) as avg_value,
                        MIN(dqm.metric_value) as min_value,
                        MAX(dqm.metric_value) as max_value,
                        COUNT(*) as measurement_count
                    FROM data_quality_metrics dqm
                    JOIN structured_entities se ON dqm.entity_id = se.entity_id
                    WHERE se.entity_type = :entity_type
                    GROUP BY dqm.metric_name
                """
                params = {"entity_type": entity_type}
            else:
                query = """
                    SELECT 
                        metric_name,
                        AVG(metric_value) as avg_value,
                        MIN(metric_value) as min_value,
                        MAX(metric_value) as max_value,
                        COUNT(*) as measurement_count
                    FROM data_quality_metrics
                    GROUP BY metric_name
                """
                params = {}
            
            result = await session.execute(query, params)
            metrics = result.fetchall()
            
            if format == "json":
                quality_data = []
                for metric in metrics:
                    quality_data.append({
                        "metric_name": metric.metric_name,
                        "avg_value": float(metric.avg_value) if metric.avg_value else 0,
                        "min_value": float(metric.min_value) if metric.min_value else 0,
                        "max_value": float(metric.max_value) if metric.max_value else 0,
                        "measurement_count": metric.measurement_count,
                    })
                
                console.print(json.dumps(quality_data, indent=2))
            
            else:
                table = Table(title=f"Data Quality Report{f' - {entity_type}' if entity_type else ''}")
                table.add_column("Metric", style="cyan")
                table.add_column("Avg", justify="right", style="green")
                table.add_column("Min", justify="right", style="red")
                table.add_column("Max", justify="right", style="blue")
                table.add_column("Count", justify="right", style="magenta")
                
                for metric in metrics:
                    table.add_row(
                        metric.metric_name,
                        f"{metric.avg_value:.3f}" if metric.avg_value else "0.000",
                        f"{metric.min_value:.3f}" if metric.min_value else "0.000",
                        f"{metric.max_value:.3f}" if metric.max_value else "0.000",
                        str(metric.measurement_count),
                    )
                
                console.print(table)
        
        except Exception as e:
            console.print(f"❌ Failed to generate quality report: {e}")
    
    asyncio.run(_quality_report())


if __name__ == "__main__":
    storage_cli()
