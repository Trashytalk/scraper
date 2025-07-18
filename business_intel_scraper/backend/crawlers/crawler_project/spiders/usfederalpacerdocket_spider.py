"""Spider for US Federal PACER Docket (placeholder)."""

import scrapy


class UsFederalPacerDocketSpider(scrapy.Spider):
    """Placeholder spider for US Federal PACER Docket."""

    name = "usfederalpacerdocket"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
