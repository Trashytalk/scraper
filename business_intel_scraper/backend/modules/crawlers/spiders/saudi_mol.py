"""Collect data from the Saudi Ministry of Labor."""

import scrapy


class SaudiMOLSpider(scrapy.Spider):
    """Collect data from the Saudi Ministry of Labor."""

    name = "saudimolspider"
    allowed_domains = ["mol.gov.sa"]
    start_urls = ["https://mol.gov.sa"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
