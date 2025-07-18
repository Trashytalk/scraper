"""Harvest Saudi Commercial Registration data."""

import scrapy


class SaudiCRCompanyRegistrySpider(scrapy.Spider):
    """Harvest Saudi Commercial Registration data."""

    name = "saudicrcompanyregistryspider"
    allowed_domains = ["mc.gov.sa"]
    start_urls = ["https://mc.gov.sa"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
