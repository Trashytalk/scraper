"""Global Trade Registry Spider implementation."""

import scrapy


class GlobalTradeRegistrySpider(scrapy.Spider):
    """Spider for Global Trade Registry."""

    name = "global_trade_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
