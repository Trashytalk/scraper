"""Placeholder spider for UAE Federal Procurement Complaint."""

import scrapy


class UaeFederalProcurementComplaintSpider(scrapy.Spider):
    name = "uae_federal_procurement_complaint"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
