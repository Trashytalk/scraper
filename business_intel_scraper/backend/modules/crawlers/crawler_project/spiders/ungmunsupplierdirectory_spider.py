"""Spider for UNGM UN Supplier Directory (placeholder)."""

import scrapy


class UngmUnSupplierDirectorySpider(scrapy.Spider):
    """Placeholder spider for UNGM UN Supplier Directory."""

    name = "ungmunsupplierdirectory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
