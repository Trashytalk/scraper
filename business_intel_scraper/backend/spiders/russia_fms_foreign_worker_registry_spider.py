"""Placeholder spider for Russia FMS Foreign Worker Registry."""

import scrapy


class RussiaFmsForeignWorkerRegistrySpider(scrapy.Spider):
    name = "russia_fms_foreign_worker_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
