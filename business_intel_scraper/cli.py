"""Simple command line client for the BI scraper API."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx


DEFAULT_URL = os.getenv("BI_SCRAPER_URL", "http://localhost:8000")
DEFAULT_TOKEN = os.getenv("BI_SCRAPER_TOKEN", "")


def _headers(token: str) -> dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def start_scrape(url: str, token: str) -> None:
    resp = httpx.post(f"{url}/scrape", headers=_headers(token))
    resp.raise_for_status()
    print(resp.json()["task_id"])


def check_status(url: str, token: str, task_id: str) -> None:
    resp = httpx.get(f"{url}/tasks/{task_id}", headers=_headers(token))
    resp.raise_for_status()
    print(resp.json()["status"])


def download_data(url: str, token: str, output: str | None) -> None:
    resp = httpx.get(f"{url}/data", headers=_headers(token))
    resp.raise_for_status()
    data = resp.json()
    if output:
        Path(output).write_text(json.dumps(data, indent=2))
    else:
        print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interact with the Business Intelligence Scraper API"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="API base URL")
    parser.add_argument("--token", default=DEFAULT_TOKEN, help="Bearer token")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("scrape", help="Launch a scraping job")

    stat = sub.add_parser("status", help="Check job status")
    stat.add_argument("task_id")

    dl = sub.add_parser("download", help="Download scraped data")
    dl.add_argument("-o", "--output")

    args = parser.parse_args()

    if args.cmd == "scrape":
        start_scrape(args.url, args.token)
    elif args.cmd == "status":
        check_status(args.url, args.token, args.task_id)
    elif args.cmd == "download":
        download_data(args.url, args.token, args.output)


if __name__ == "__main__":
    main()
