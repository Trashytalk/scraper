"""Spider for TED EU Tenders Electronic Daily Award (placeholder)."""

import scrapy


class TedEuTendersElectronicDailyAwardSpider(scrapy.Spider):
    """Placeholder spider for TED EU Tenders Electronic Daily Award."""

    name = "tedeutenderselectronicdailyaward"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
