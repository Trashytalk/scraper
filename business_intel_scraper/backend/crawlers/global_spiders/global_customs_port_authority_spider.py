"""Global Customs & Port Authority Spider implementation."""

import scrapy


class GlobalCustomsPortAuthoritySpider(scrapy.Spider):
    """Spider for Global Customs & Port Authority."""

    name = "global_customs_port_authority_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
