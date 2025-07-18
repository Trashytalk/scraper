"""Spider for Lazada Seller Directory (placeholder)."""

import scrapy


class LazadaSellerDirectorySpider(scrapy.Spider):
    """Placeholder spider for Lazada Seller Directory."""

    name = "lazadasellerdirectory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
