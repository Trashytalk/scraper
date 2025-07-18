"""Placeholder spider for Vietnam Logistics Business Association Members."""

import scrapy


class VietnamLogisticsBusinessAssociationMembersSpider(scrapy.Spider):
    name = "vietnam_logistics_business_association_members"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
