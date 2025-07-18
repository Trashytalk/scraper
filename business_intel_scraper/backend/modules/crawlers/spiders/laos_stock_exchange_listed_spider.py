from __future__ import annotations

import scrapy


class LaosStockExchangeListedSpider(scrapy.Spider):
    """Laos Stock Exchange listed companies."""

    name = "laos_stock_exchange_listed"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
