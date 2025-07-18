"""Spider for Kumon Learning Center Franchisee (placeholder)."""

import scrapy


class KumonLearningCenterFranchiseeSpider(scrapy.Spider):
    """Placeholder spider for Kumon Learning Center Franchisee."""

    name = "kumonlearningcenterfranchisee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
