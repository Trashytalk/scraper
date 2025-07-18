"""European Procurement/Tender Spider implementation."""

import scrapy


class EuropeanProcurementTenderSpider(scrapy.Spider):
    """Spider for European Procurement/Tender."""

    name = "european_procurement_tender_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
