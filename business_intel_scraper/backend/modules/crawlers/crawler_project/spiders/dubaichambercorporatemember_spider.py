"""Spider for Dubai Chamber Corporate Member (placeholder)."""

import scrapy


class DubaiChamberCorporateMemberSpider(scrapy.Spider):
    """Placeholder spider for Dubai Chamber Corporate Member."""

    name = "dubaichambercorporatemember"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
