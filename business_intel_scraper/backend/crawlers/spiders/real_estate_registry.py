"""Scrape regional land and property ownership records."""

import scrapy


class RealEstateRegistrySpider(scrapy.Spider):
    """Scrape regional land and property ownership records."""

    name = "realestateregistryspider"
    allowed_domains = ["dld.gov.ae"]
    start_urls = ["https://www.dld.gov.ae"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
