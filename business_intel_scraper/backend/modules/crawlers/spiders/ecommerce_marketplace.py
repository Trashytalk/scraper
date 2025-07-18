"""Scrape SEA e-commerce seller profiles."""

import scrapy


class SEAEcommerceMarketplaceSpider(scrapy.Spider):
    """Scrape SEA e-commerce seller profiles."""

    name = "seaecommercemarketplacespider"
    allowed_domains = ["shopee.sg"]
    start_urls = ["https://shopee.sg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
