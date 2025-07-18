"""Spider for MercadoLibre Top Seller (placeholder)."""

import scrapy


class MercadolibreTopSellerSpider(scrapy.Spider):
    """Placeholder spider for MercadoLibre Top Seller."""

    name = "mercadolibretopseller"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
