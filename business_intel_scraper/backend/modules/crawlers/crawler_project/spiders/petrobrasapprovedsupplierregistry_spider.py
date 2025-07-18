"""Spider for Petrobras Approved Supplier Registry (placeholder)."""

import scrapy


class PetrobrasApprovedSupplierRegistrySpider(scrapy.Spider):
    """Placeholder spider for Petrobras Approved Supplier Registry."""

    name = "petrobrasapprovedsupplierregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
