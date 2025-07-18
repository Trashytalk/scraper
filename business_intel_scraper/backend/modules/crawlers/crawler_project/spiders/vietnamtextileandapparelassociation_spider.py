"""Spider for Vietnam Textile and Apparel Association (placeholder)."""

import scrapy


class VietnamTextileAndApparelAssociationSpider(scrapy.Spider):
    """Placeholder spider for Vietnam Textile and Apparel Association."""

    name = "vietnamtextileandapparelassociation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
