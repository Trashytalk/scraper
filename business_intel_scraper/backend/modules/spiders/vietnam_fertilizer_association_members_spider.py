"""Placeholder spider for Vietnam Fertilizer Association Members."""

import scrapy


class VietnamFertilizerAssociationMembersSpider(scrapy.Spider):
    name = "vietnam_fertilizer_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
