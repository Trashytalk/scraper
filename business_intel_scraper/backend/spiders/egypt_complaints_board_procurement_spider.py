"""Placeholder spider for Egypt Complaints Board Procurement."""

import scrapy


class EgyptComplaintsBoardProcurementSpider(scrapy.Spider):
    name = "egypt_complaints_board_procurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
