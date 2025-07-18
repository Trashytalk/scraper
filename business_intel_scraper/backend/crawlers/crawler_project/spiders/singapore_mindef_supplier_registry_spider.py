from __future__ import annotations

import scrapy


class SingaporeMindefSupplierRegistrySpider(scrapy.Spider):
    """Placeholder for the Singapore MINDEF Supplier Registry."""

    name = "singapore_mindef_supplier_registry_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
