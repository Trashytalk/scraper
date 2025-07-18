"""Scrape international sanctions, blacklists, and watchlists (OFAC, UN, EU,
etc.) for due diligence."""

from __future__ import annotations

import scrapy


class SanctionsWatchlistSpider(scrapy.Spider):
    """Scrape international sanctions, blacklists, and watchlists (OFAC, UN, EU,
    etc.) for due diligence."""

    name = "sanctions_and_watchlist_spider"
