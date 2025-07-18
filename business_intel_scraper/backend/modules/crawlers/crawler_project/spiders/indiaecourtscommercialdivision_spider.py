"""Spider for India eCourts Commercial Division (placeholder)."""

import scrapy


class IndiaEcourtsCommercialDivisionSpider(scrapy.Spider):
    """Placeholder spider for India eCourts Commercial Division."""

    name = "indiaecourtscommercialdivision"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
