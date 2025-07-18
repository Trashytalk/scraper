import argparse
import json

from business_intel_scraper.backend.workers.tasks import run_spider_task
from business_intel_scraper.backend.utils import export
from business_intel_scraper.backend.osint.integrations import (
    run_spiderfoot,
    run_theharvester,
)


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

    export_parser = subparsers.add_parser("export", help="Run spider and export data")
    export_parser.add_argument(
        "--format", choices=["csv", "jsonl"], default="csv", help="Output format"
    )
    export_parser.add_argument("--output", required=True, help="Output file path")
    export_parser.add_argument(
        "--spider",
        default="example",
        help="Name of the spider to run (default: %(default)s)",
    )

    args = parser.parse_args()

    if args.command == "scrape":
        items = run_spider_task(args.spider, html=args.html)
        print(json.dumps(items, indent=2))
    elif args.command == "spiderfoot":
        result = run_spiderfoot(args.domain)
        print(json.dumps(result, indent=2))
    elif args.command == "theharvester":
        result = run_theharvester(args.domain)
        print(json.dumps(result, indent=2))
    elif args.command == "export":
        items = run_spider_task(args.spider)
        if args.format == "csv":
            data = export.to_csv(items)
        else:
            data = export.to_jsonl(items)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(data)
        print(f"Exported {len(items)} items to {args.output}")


if __name__ == "__main__":
    main()
