"""Scrape Thai company registrations from DBD."""

import scrapy


class ThailandDBDCompanyRegistrySpider(scrapy.Spider):
    """Scrape Thai company registrations from DBD."""

    name = "thailanddbdcompanyregistryspider"
    allowed_domains = ["dbd.go.th"]
    start_urls = ["https://www.dbd.go.th"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
