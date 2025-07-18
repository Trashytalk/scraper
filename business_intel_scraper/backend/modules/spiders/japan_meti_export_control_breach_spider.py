"""Placeholder spider for Japan METI Export Control Breach."""

import scrapy


class JapanMetiExportControlBreachSpider(scrapy.Spider):
    name = "japan_meti_export_control_breach"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
