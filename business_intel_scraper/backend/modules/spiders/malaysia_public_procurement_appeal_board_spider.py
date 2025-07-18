"""Placeholder spider for Malaysia Public Procurement Appeal Board."""

import scrapy


class MalaysiaPublicProcurementAppealBoardSpider(scrapy.Spider):
    name = "malaysia_public_procurement_appeal_board"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
