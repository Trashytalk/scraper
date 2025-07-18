"""Scrape PEP and sanctions lists across ASEAN."""

import scrapy


class AseanPEPSanctionsSpider(scrapy.Spider):
    """Scrape PEP and sanctions lists across ASEAN."""

    name = "aseanpepsanctionsspider"
    allowed_domains = ["asean.org"]
    start_urls = ["https://asean.org"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
