"""Collect import/export records from ASEAN customs."""

import scrapy


class AseanCustomsTradeSpider(scrapy.Spider):
    """Collect import/export records from ASEAN customs."""

    name = "aseancustomstradespider"
    allowed_domains = ["customs.gov.sg"]
    start_urls = ["https://www.customs.gov.sg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
