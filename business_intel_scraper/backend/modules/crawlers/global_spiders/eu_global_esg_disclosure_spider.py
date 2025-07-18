"""EU/Global ESG Disclosure Spider implementation."""

import scrapy


class EuGlobalEsgDisclosureSpider(scrapy.Spider):
    """Spider for EU/Global ESG Disclosure."""

    name = "eu_global_esg_disclosure_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
