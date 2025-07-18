from __future__ import annotations

import scrapy


class CambodiaEnvironmentComplianceSpider(scrapy.Spider):
    """Cambodia Ministry of Environment compliance."""

    name = "cambodia_environment_compliance"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
