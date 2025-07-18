"""Spider for Shopee Power Seller (placeholder)."""

import scrapy


class ShopeePowerSellerSpider(scrapy.Spider):
    """Placeholder spider for Shopee Power Seller."""

    name = "shopeepowerseller"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
