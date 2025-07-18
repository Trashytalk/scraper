"""Spider for Singapore Customs Import Export (placeholder)."""

import scrapy


class SingaporeCustomsImportExportSpider(scrapy.Spider):
    """Placeholder spider for Singapore Customs Import Export."""

    name = "singaporecustomsimportexport"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
