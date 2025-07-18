"""Spider for Polish KNF Public Warning (placeholder)."""

import scrapy


class PolishKnfPublicWarningSpider(scrapy.Spider):
    """Placeholder spider for Polish KNF Public Warning."""

    name = "polishknfpublicwarning"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
