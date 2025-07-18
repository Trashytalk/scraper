"""Monitor bankruptcy or insolvency announcements."""

from __future__ import annotations

import scrapy


class BankruptcyFilingsSpider(scrapy.Spider):
    """Monitor bankruptcy or insolvency announcements."""

    name = "bankruptcy_filings_spider"
