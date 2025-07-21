import argparse
import json
from typing import Optional, Any
import click

from business_intel_scraper.backend.workers.tasks import run_spider_task
from business_intel_scraper.backend.modules.scrapers.integrations import (
    run_spiderfoot,
    run_theharvester,
    run_shodan,
    run_nmap,
)

# Import marketplace CLI  
try:
    from ..marketplace.cli import marketplace
except ImportError:
    marketplace: Optional[click.Group] = None

# Import analytics CLI
try:
    from ..analytics.cli import analytics
    analytics_cli: Optional[click.Group] = analytics
except ImportError:
    analytics_cli: Optional[click.Group] = None

# Import discovery CLI
try:
    from .discovery import setup_discovery_parser
except ImportError:
    setup_discovery_parser = None


def main() -> None:
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="Run scraping tasks or OSINT queries manually",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scrape_parser = subparsers.add_parser(
        "scrape", help="Run a scraping spider synchronously"
    )
    scrape_parser.add_argument(
        "--spider",
        default="example",
        help="Name of the spider to run (default: %(default)s)",
    )
    scrape_parser.add_argument(
        "--html", help="Optional HTML content to parse instead of fetching"
    )

    sf_parser = subparsers.add_parser("spiderfoot", help="Run SpiderFoot OSINT scan")
    sf_parser.add_argument("domain", help="Domain to scan")

    th_parser = subparsers.add_parser(
        "theharvester", help="Run TheHarvester OSINT scan"
    )
    th_parser.add_argument("domain", help="Domain to scan")

    shodan_parser = subparsers.add_parser("shodan", help="Run Shodan search")
    shodan_parser.add_argument("target", help="IP or query string")

    # Add marketplace command if available
    if marketplace:
        marketplace_parser = subparsers.add_parser("marketplace", help="Spider marketplace commands")
        marketplace_parser.set_defaults(func=lambda args: marketplace.main(standalone_mode=False))

    # Add analytics command if available
    if analytics_cli:
        analytics_parser = subparsers.add_parser("analytics", help="Analytics dashboard commands")
        analytics_parser.set_defaults(func=lambda args: analytics_cli.main(standalone_mode=False))

    # Add discovery command if available
    if setup_discovery_parser:
        setup_discovery_parser(subparsers)

    nmap_parser = subparsers.add_parser("nmap", help="Run Nmap scan")
    nmap_parser.add_argument("target", help="Target host")

    args = parser.parse_args()

    if args.command == "scrape":
        items = run_spider_task(args.spider, html=args.html)
        print(json.dumps(items, indent=2))
    elif args.command == "marketplace" and marketplace:
        # Handle marketplace commands through Click
        import sys
        marketplace.main(sys.argv[2:], standalone_mode=False)
    elif args.command == "analytics" and analytics_cli:
        # Handle analytics commands through Click
        import sys
        analytics_cli.main(sys.argv[2:], standalone_mode=False)
    elif args.command == "discovery" and setup_discovery_parser:
        # Handle discovery commands
        from .discovery import main as discovery_main
        import sys
        original_argv = sys.argv
        try:
            # Set up argv for discovery command
            sys.argv = ['discovery'] + sys.argv[2:]  # Remove main script name and 'discovery'
            discovery_main()
        finally:
            sys.argv = original_argv
    elif args.command == "spiderfoot":
        result = run_spiderfoot(args.domain)
        print(json.dumps(result, indent=2))
    elif args.command == "theharvester":
        result = run_theharvester(args.domain)
        print(json.dumps(result, indent=2))
    elif args.command == "shodan":
        result = run_shodan(args.target)
        print(json.dumps(result, indent=2))
    elif args.command == "nmap":
        result = run_nmap(args.target)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
