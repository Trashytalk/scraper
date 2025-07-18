"""Spider for Singapore Law Society Licensed Firms (placeholder)."""

import scrapy


class SingaporeLawSocietyLicensedFirmsSpider(scrapy.Spider):
    """Placeholder spider for Singapore Law Society Licensed Firms."""

    name = "singaporelawsocietylicensedfirms"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
