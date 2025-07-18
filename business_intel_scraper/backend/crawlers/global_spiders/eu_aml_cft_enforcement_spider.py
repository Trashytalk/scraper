"""EU AML/CFT Enforcement Spider implementation."""

import scrapy


class EuAmlCftEnforcementSpider(scrapy.Spider):
    """Spider for EU AML/CFT Enforcement."""

    name = "eu_aml_cft_enforcement_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
