"""Placeholder spider for Saudi GOSI Expat Worker License."""

import scrapy


class SaudiGosiExpatWorkerLicenseSpider(scrapy.Spider):
    name = "saudi_gosi_expat_worker_license"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
