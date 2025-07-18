"""Global OpenCorporates Integration Spider implementation."""

import scrapy


class GlobalOpencorporatesIntegrationSpider(scrapy.Spider):
    """Spider for Global OpenCorporates Integration."""

    name = "global_opencorporates_integration_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
