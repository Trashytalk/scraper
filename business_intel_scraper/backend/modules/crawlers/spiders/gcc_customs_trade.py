"""Gather GCC customs and trade data."""

import scrapy


class GCCCustomsTradeSpider(scrapy.Spider):
    """Gather GCC customs and trade data."""

    name = "gcccustomstradespider"
    allowed_domains = ["gcc-sg.org"]
    start_urls = ["https://gcc-sg.org"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
