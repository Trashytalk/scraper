"""Placeholder spider for China MOFCOM Technology Export Violation."""

import scrapy


class ChinaMofcomTechnologyExportViolationSpider(scrapy.Spider):
    name = "china_mofcom_technology_export_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
