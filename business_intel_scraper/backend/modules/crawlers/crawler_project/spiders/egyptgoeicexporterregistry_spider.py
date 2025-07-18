"""Spider for Egypt GOEIC Exporter Registry (placeholder)."""

import scrapy


class EgyptGoeicExporterRegistrySpider(scrapy.Spider):
    """Placeholder spider for Egypt GOEIC Exporter Registry."""

    name = "egyptgoeicexporterregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
