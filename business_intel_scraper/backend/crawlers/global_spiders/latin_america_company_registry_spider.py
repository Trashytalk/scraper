"""Latin America Company Registry Spider implementation."""

import scrapy


class LatinAmericaCompanyRegistrySpider(scrapy.Spider):
    """Spider for Latin America Company Registry."""

    name = "latin_america_company_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
