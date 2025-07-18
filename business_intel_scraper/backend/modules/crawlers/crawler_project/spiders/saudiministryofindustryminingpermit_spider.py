"""Spider for Saudi Ministry of Industry Mining Permit (placeholder)."""

import scrapy


class SaudiMinistryOfIndustryMiningPermitSpider(scrapy.Spider):
    """Placeholder spider for Saudi Ministry of Industry Mining Permit."""

    name = "saudiministryofindustryminingpermit"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
