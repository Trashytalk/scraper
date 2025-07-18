"""Spider for UN Comtrade Import Export (placeholder)."""

import scrapy


class UnComtradeImportExportSpider(scrapy.Spider):
    """Placeholder spider for UN Comtrade Import Export."""

    name = "uncomtradeimportexport"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
