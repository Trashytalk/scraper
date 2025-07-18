"""Global UBO Registry Spider implementation."""

import scrapy


class GlobalUboRegistrySpider(scrapy.Spider):
    """Spider for Global UBO Registry."""

    name = "global_ubo_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
