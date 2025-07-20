"""
Spider Marketplace CLI Commands
Command-line interface for managing spiders
"""

import click
import json
import yaml
from pathlib import Path
from typing import Dict, Any
from . import SpiderMarketplace


@click.group()
def marketplace() -> None:
    """Spider Marketplace commands"""
    pass


@marketplace.command()
@click.option('--query', '-q', default='', help='Search query')
@click.option('--category', '-c', default='', help='Filter by category')
@click.option('--tags', '-t', default='', help='Comma-separated tags')
@click.option('--limit', '-l', default=20, help='Maximum results')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def search(query: str, category: str, tags: str, limit: int, format: str) -> None:
    """Search for spiders in the marketplace"""
    mp = SpiderMarketplace()
    
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    spiders = mp.search_spiders(query=query, category=category, tags=tag_list, limit=limit)
    
    if format == 'json':
        click.echo(json.dumps(spiders, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(spiders, default_flow_style=False))
    else:
        # Table format
        if not spiders:
            click.echo("No spiders found.")
            return
        
        click.echo(f"{'Name':<30} {'Version':<10} {'Category':<20} {'Author':<20} {'Rating':<8} {'Downloads':<10}")
        click.echo("-" * 110)
        
        for spider in spiders:
            name = spider['name'][:29]
            version = spider['version'][:9]
            category = spider['category'][:19]
            author = spider['author'][:19]
            rating = f"{spider.get('rating', 0):.1f}"
            downloads = str(spider.get('downloads', 0))
            installed = "✓" if spider.get('installed', False) else ""
            
            click.echo(f"{name:<30} {version:<10} {category:<20} {author:<20} {rating:<8} {downloads:<10} {installed}")


@marketplace.command()
@click.argument('spider_name')
@click.option('--version', '-v', default='latest', help='Spider version')
def install(spider_name: str, version: str) -> None:
    """Install a spider from the marketplace"""
    mp = SpiderMarketplace()
    
    click.echo(f"Installing {spider_name} v{version}...")
    
    result = mp.install_spider(spider_name, version)
    
    if result['success']:
        click.echo(f"✅ {result['message']}")
    else:
        click.echo(f"❌ {result['error']}")


@marketplace.command()
@click.argument('spider_name')
def uninstall(spider_name: str) -> None:
    """Uninstall a spider"""
    mp = SpiderMarketplace()
    
    if click.confirm(f"Are you sure you want to uninstall {spider_name}?"):
        result = mp.uninstall_spider(spider_name)
        
        if result['success']:
            click.echo(f"✅ {result['message']}")
        else:
            click.echo(f"❌ {result['error']}")


@marketplace.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def list_installed(format: str) -> None:
    """List installed spiders"""
    mp = SpiderMarketplace()
    
    spiders = mp.list_installed_spiders()
    
    if format == 'json':
        click.echo(json.dumps(spiders, indent=2))
    elif format == 'yaml':
        click.echo(yaml.dump(spiders, default_flow_style=False))
    else:
        if not spiders:
            click.echo("No spiders installed.")
            return
        
        click.echo(f"{'Name':<30} {'Version':<10} {'Category':<20} {'Author':<20}")
        click.echo("-" * 90)
        
        for spider in spiders:
            name = spider['name'][:29]
            version = spider['version'][:9]
            category = spider['category'][:19]
            author = spider['author'][:19]
            
            click.echo(f"{name:<30} {version:<10} {category:<20} {author:<20}")


@marketplace.command()
@click.argument('spider_name')
def info(spider_name: str) -> None:
    """Get detailed information about a spider"""
    mp = SpiderMarketplace()
    
    spider_info = mp.get_spider_info(spider_name)
    
    if not spider_info:
        click.echo(f"❌ Spider {spider_name} not found")
        return
    
    click.echo(f"📦 {spider_info['name']} v{spider_info['version']}")
    click.echo(f"👤 Author: {spider_info['author']}")
    click.echo(f"📝 Description: {spider_info['description']}")
    click.echo(f"🏷️  Category: {spider_info['category']}")
    click.echo(f"🔖 Tags: {', '.join(spider_info.get('tags', []))}")
    click.echo(f"📄 License: {spider_info['license']}")
    
    if spider_info.get('rating'):
        click.echo(f"⭐ Rating: {spider_info['rating']:.1f}/5.0 ({spider_info.get('rating_count', 0)} reviews)")
    
    if spider_info.get('downloads'):
        click.echo(f"📥 Downloads: {spider_info['downloads']:,}")
    
    if spider_info.get('verified'):
        click.echo("✅ Verified spider")
    
    if spider_info.get('installed'):
        click.echo("💾 Installed locally")
    
    if spider_info.get('requirements'):
        click.echo(f"📋 Requirements: {', '.join(spider_info['requirements'])}")


@marketplace.command()
@click.argument('spider_path', type=click.Path(exists=True))
def validate(spider_path: str) -> None:
    """Validate a spider package"""
    mp = SpiderMarketplace()
    
    click.echo(f"Validating spider at {spider_path}...")
    
    result = mp.validate_spider(spider_path)
    
    if result['valid']:
        click.echo(f"✅ Spider is valid (score: {result['score']:.1%})")
    else:
        click.echo(f"❌ Spider validation failed (score: {result['score']:.1%})")
        
        if 'issues' in result:
            click.echo("Issues found:")
            for issue in result['issues']:
                click.echo(f"  - {issue}")


@marketplace.command()
@click.argument('spider_path', type=click.Path(exists=True))
@click.option('--name', '-n', required=True, help='Spider name')
@click.option('--version', '-v', required=True, help='Spider version')
@click.option('--author', '-a', required=True, help='Author name')
@click.option('--description', '-d', required=True, help='Spider description')
@click.option('--category', '-c', required=True, help='Spider category')
@click.option('--license', '-l', default='MIT', help='License')
@click.option('--tags', '-t', default='', help='Comma-separated tags')
@click.option('--requirements', '-r', default='', help='Comma-separated requirements')
@click.option('--entry-point', '-e', required=True, help='Entry point (module.ClassName)')
def publish(spider_path: str, name: str, version: str, author: str, description: str, 
           category: str, license: str, tags: str, requirements: str, entry_point: str) -> None:
    """Publish a spider to the marketplace"""
    mp = SpiderMarketplace()
    
    # Prepare metadata
    metadata = {
        'name': name,
        'version': version,
        'author': author,
        'description': description,
        'category': category,
        'license': license,
        'entry_point': entry_point,
        'tags': [tag.strip() for tag in tags.split(",")] if tags else [],
        'requirements': [req.strip() for req in requirements.split(",")] if requirements else []
    }
    
    click.echo(f"Publishing {name} v{version}...")
    
    result = mp.publish_spider(spider_path, metadata)
    
    if result['success']:
        click.echo(f"✅ {result['message']}")
    else:
        click.echo(f"❌ {result['error']}")


@marketplace.command()
def categories() -> None:
    """List available categories"""
    mp = SpiderMarketplace()
    
    cats = mp.get_categories()
    
    click.echo("Available categories:")
    for category in cats:
        click.echo(f"  - {category}")


@marketplace.command()
def stats() -> None:
    """Show marketplace statistics"""
    mp = SpiderMarketplace()
    
    stats = mp.get_marketplace_stats()
    
    click.echo("📊 Marketplace Statistics")
    click.echo("=" * 30)
    click.echo(f"Total spiders: {stats['total_spiders']}")
    click.echo(f"Installed spiders: {stats['installed_spiders']}")
    click.echo(f"Categories: {stats['categories']}")
    click.echo(f"Verified spiders: {stats['verified_spiders']}")
    click.echo(f"Total downloads: {stats['total_downloads']:,}")


@marketplace.command()
@click.argument('spider_name')
@click.argument('template_path', type=click.Path())
def create_template(spider_name: str, template_path: str) -> None:
    """Create a spider template"""
    template_dir = Path(template_path)
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # Create spider.yaml
    spider_metadata = {
        'name': spider_name,
        'version': '1.0.0',
        'author': 'Your Name',
        'description': f'A spider for {spider_name}',
        'category': 'business-intelligence',
        'tags': ['template'],
        'requirements': ['scrapy', 'requests'],
        'entry_point': f'{spider_name.replace("-", "_")}.{spider_name.replace("-", "_").title()}Spider',
        'license': 'MIT'
    }
    
    with open(template_dir / 'spider.yaml', 'w') as f:
        yaml.dump(spider_metadata, f, default_flow_style=False)
    
    # Create main spider file
    spider_code = f'''"""
{spider_name.title()} Spider Template

This is a template spider for {spider_name}. Customize it for your specific needs.
"""

import scrapy
from typing import Dict, Any, Generator


class {spider_name.replace("-", "_").title()}Spider(scrapy.Spider):
    """
    Spider for scraping {spider_name} data
    """
    
    name = "{spider_name}"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]
    
    custom_settings = {{
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'BusinessIntelScraper/1.0 (+https://your-site.com)'
    }}
    
    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse the main page and extract data
        """
        # Example data extraction
        yield {{
            'url': response.url,
            'title': response.css('title::text').get(),
            'scraped_at': response.meta.get('download_time')
        }}
        
        # Follow pagination or additional URLs
        for link in response.css('a::attr(href)').getall():
            if link:
                yield response.follow(link, self.parse_detail)
    
    def parse_detail(self, response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse detail pages
        """
        yield {{
            'detail_url': response.url,
            'content': response.css('body::text').get(),
            'scraped_at': response.meta.get('download_time')
        }}
'''
    
    with open(template_dir / f'{spider_name.replace("-", "_")}.py', 'w') as f:
        f.write(spider_code)
    
    # Create requirements.txt
    with open(template_dir / 'requirements.txt', 'w') as f:
        f.write("scrapy\\nrequests\\nbeautifulsoup4\\n")
    
    # Create README.md
    readme_content = f'''# {spider_name.title()} Spider

A spider template for scraping {spider_name} data.

## Installation

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the spider settings in `spider.yaml`

3. Run the spider:
   ```bash
   scrapy crawl {spider_name}
   ```

## Customization

Edit `{spider_name.replace("-", "_")}.py` to customize the scraping logic for your specific needs.

## Configuration

- Update `allowed_domains` with the target domains
- Modify `start_urls` with the starting URLs
- Adjust `custom_settings` for rate limiting and other preferences
'''
    
    with open(template_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    click.echo(f"✅ Spider template created at {template_path}")
    click.echo(f"📝 Edit the files to customize your spider")
    click.echo(f"🚀 Test with: cd {template_path} && scrapy crawl {spider_name}")


if __name__ == '__main__':
    marketplace()
