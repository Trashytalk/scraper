"""VAT & Taxpayer Registry Spider implementation."""

import scrapy


class VatTaxpayerRegistrySpider(scrapy.Spider):
    """Spider for VAT & Taxpayer Registry."""

    name = "vat_taxpayer_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
