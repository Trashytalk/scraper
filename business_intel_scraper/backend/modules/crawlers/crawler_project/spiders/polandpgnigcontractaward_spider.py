"""Spider for Poland PGNiG Contract Award (placeholder)."""

import scrapy


class PolandPgnigContractAwardSpider(scrapy.Spider):
    """Placeholder spider for Poland PGNiG Contract Award."""

    name = "polandpgnigcontractaward"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
