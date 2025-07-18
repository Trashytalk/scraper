"""Spider for India Medical Council Doctor Registry (placeholder)."""

import scrapy


class IndiaMedicalCouncilDoctorRegistrySpider(scrapy.Spider):
    """Placeholder spider for India Medical Council Doctor Registry."""

    name = "indiamedicalcouncildoctorregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
