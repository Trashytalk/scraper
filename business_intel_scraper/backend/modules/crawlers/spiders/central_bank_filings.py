"""Harvest filings from GCC central banks."""

import scrapy


class CentralBankFilingsSpider(scrapy.Spider):
    """Harvest filings from GCC central banks."""

    name = "centralbankfilingsspider"
    allowed_domains = ["centralbank.ae"]
    start_urls = ["https://www.centralbank.ae"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
