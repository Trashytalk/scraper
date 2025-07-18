"""Placeholder spider for Germany BAFA Export Violation."""

import scrapy


class GermanyBafaExportViolationSpider(scrapy.Spider):
    name = "germany_bafa_export_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
