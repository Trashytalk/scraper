"""Spider for Poland Law Society Licensed Firm (placeholder)."""

import scrapy


class PolandLawSocietyLicensedFirmSpider(scrapy.Spider):
    """Placeholder spider for Poland Law Society Licensed Firm."""

    name = "polandlawsocietylicensedfirm"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
