from __future__ import annotations

import scrapy


class QatarStockExchangeCGViolationSpider(scrapy.Spider):
    """Qatar Stock Exchange corporate governance violations."""

    name = "qatar_stock_exchange_cg_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
