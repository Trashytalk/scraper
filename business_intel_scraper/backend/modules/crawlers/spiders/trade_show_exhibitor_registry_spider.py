from __future__ import annotations

import scrapy


class TradeShowExhibitorRegistrySpider(scrapy.Spider):
    """Trade show exhibitor registries."""

    name = "trade_show_exhibitor_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
