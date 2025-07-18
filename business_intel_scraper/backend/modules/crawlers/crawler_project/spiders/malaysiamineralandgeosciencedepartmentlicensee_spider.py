"""Spider for Malaysia Mineral and Geoscience Department Licensee (placeholder)."""

import scrapy


class MalaysiaMineralAndGeoscienceDepartmentLicenseeSpider(scrapy.Spider):
    """Placeholder spider for Malaysia Mineral and Geoscience Department Licensee."""

    name = "malaysiamineralandgeosciencedepartmentlicensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
