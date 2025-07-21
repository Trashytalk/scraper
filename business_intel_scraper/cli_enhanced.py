"""Enhanced CLI for Business Intelligence Scraper with performance optimization."""

import click
import json
import os
import httpx
from pathlib import Path

from .cli.performance import performance
from .backend.storage.cli import storage_cli

DEFAULT_URL = os.getenv("BI_SCRAPER_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("BI_SCRAPER_TOKEN", "")


def _headers(token: str) -> dict[str, str]:
    """Get authorization headers."""
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@click.group()
@click.option('--url', default=DEFAULT_URL, help='API base URL')
@click.option('--token', default=DEFAULT_TOKEN, help='Bearer token')
@click.pass_context
def cli(ctx, url, token):
    """Business Intelligence Scraper CLI with performance optimization."""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url
    ctx.obj['token'] = token


@cli.command()
@click.pass_context
def scrape(ctx):
    """Launch a scraping job."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    try:
        resp = httpx.post(f"{url}/scrape", headers=_headers(token))
        resp.raise_for_status()
        result = resp.json()
        click.echo(f"✅ Scraping job started: {result['task_id']}")
    except httpx.HTTPError as e:
        click.echo(f"❌ Error starting scrape: {e}")


@cli.command()
@click.argument('task_id')
@click.pass_context
def status(ctx, task_id):
    """Check job status."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    try:
        resp = httpx.get(f"{url}/tasks/{task_id}", headers=_headers(token))
        resp.raise_for_status()
        result = resp.json()
        
        status_emoji = {
            'pending': '⏳',
            'running': '🔄',
            'completed': '✅',
            'failed': '❌'
        }
        
        current_status = result.get('status', 'unknown')
        emoji = status_emoji.get(current_status, '❓')
        
        click.echo(f"{emoji} Task {task_id}: {current_status}")
        
        if 'progress' in result:
            click.echo(f"   Progress: {result['progress']}%")
        if 'message' in result:
            click.echo(f"   Message: {result['message']}")
            
    except httpx.HTTPError as e:
        click.echo(f"❌ Error checking status: {e}")


@cli.command()
@click.option('-o', '--output', help='Output file path')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'pretty']),
              help='Output format')
@click.pass_context
def download(ctx, output, output_format):
    """Download scraped data."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    try:
        resp = httpx.get(f"{url}/data", headers=_headers(token))
        resp.raise_for_status()
        data = resp.json()
        
        if output_format == 'pretty':
            formatted_data = json.dumps(data, indent=2, sort_keys=True)
        else:
            formatted_data = json.dumps(data)
        
        if output:
            Path(output).write_text(formatted_data)
            click.echo(f"✅ Data saved to {output}")
        else:
            click.echo(formatted_data)
            
    except httpx.HTTPError as e:
        click.echo(f"❌ Error downloading data: {e}")


@cli.command()
@click.option('--format', 'export_format', default='jsonl', 
              type=click.Choice(['csv', 'jsonl', 's3']), help='Export format')
@click.option('--bucket', help='S3 bucket name (for S3 export)')
@click.option('--key', help='S3 key/path (for S3 export)')
@click.option('-o', '--output', help='Output file path')
@click.pass_context
def export(ctx, export_format, bucket, key, output):
    """Export data in various formats."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    params = {"format": export_format}
    if bucket:
        params["bucket"] = bucket
    if key:
        params["key"] = key
    
    try:
        resp = httpx.get(f"{url}/export", params=params, headers=_headers(token))
        resp.raise_for_status()
        
        if export_format == "s3":
            result = resp.json()
            location = result.get("location", "")
            click.echo(f"✅ Data exported to S3: {location}")
        else:
            content = resp.text
            if output:
                Path(output).write_text(content)
                click.echo(f"✅ Data exported to {output}")
            else:
                click.echo(content)
                
    except httpx.HTTPError as e:
        click.echo(f"❌ Error exporting data: {e}")


@cli.group()
def analytics():
    """Analytics and dashboard commands."""
    pass


@analytics.command()
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json']), help='Output format')
@click.pass_context
def dashboard(ctx, output_format):
    """View analytics dashboard."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    try:
        resp = httpx.get(f"{url}/analytics/dashboard", headers=_headers(token))
        resp.raise_for_status()
        data = resp.json()
        
        if output_format == 'json':
            click.echo(json.dumps(data, indent=2))
        else:
            click.echo("📊 Analytics Dashboard")
            click.echo("=" * 30)
            
            # Display key metrics
            metrics = data.get('metrics', {})
            for key, value in metrics.items():
                click.echo(f"{key}: {value}")
            
            # Display insights
            insights = data.get('insights', [])
            if insights:
                click.echo("\n💡 Key Insights:")
                for insight in insights:
                    click.echo(f"  • {insight}")
                    
    except httpx.HTTPError as e:
        click.echo(f"❌ Error getting dashboard: {e}")


@analytics.command()
@click.option('--metric', help='Specific metric to retrieve')
@click.pass_context
def metrics(ctx, metric):
    """Get analytics metrics."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    endpoint = f"{url}/analytics/metrics"
    params = {}
    if metric:
        params['metric'] = metric
    
    try:
        resp = httpx.get(endpoint, params=params, headers=_headers(token))
        resp.raise_for_status()
        data = resp.json()
        
        click.echo("📈 Analytics Metrics")
        click.echo("=" * 25)
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    click.echo(f"{key}: {value}")
                else:
                    click.echo(f"{key}: {json.dumps(value)}")
        else:
            click.echo(json.dumps(data, indent=2))
            
    except httpx.HTTPError as e:
        click.echo(f"❌ Error getting metrics: {e}")


@cli.command()
@click.option('--check', help='Specific health check to run')
@click.pass_context
def health(ctx, check):
    """Check system health."""
    url = ctx.obj['url']
    token = ctx.obj['token']
    
    endpoint = f"{url}/health"
    params = {}
    if check:
        params['check'] = check
    
    try:
        resp = httpx.get(endpoint, params=params, headers=_headers(token))
        resp.raise_for_status()
        data = resp.json()
        
        overall_status = data.get('status', 'unknown')
        status_emoji = {'healthy': '✅', 'unhealthy': '❌', 'degraded': '⚠️'}
        emoji = status_emoji.get(overall_status, '❓')
        
        click.echo(f"{emoji} System Status: {overall_status}")
        
        # Show component status
        components = data.get('components', {})
        if components:
            click.echo("\nComponent Status:")
            for component, status in components.items():
                comp_emoji = status_emoji.get(status, '❓')
                click.echo(f"  {comp_emoji} {component}: {status}")
        
        # Show any messages
        messages = data.get('messages', [])
        if messages:
            click.echo("\nMessages:")
            for message in messages:
                click.echo(f"  • {message}")
                
    except httpx.HTTPError as e:
        click.echo(f"❌ Error checking health: {e}")


# Add command groups
cli.add_command(performance)
cli.add_command(storage_cli)

if __name__ == "__main__":
    cli()
