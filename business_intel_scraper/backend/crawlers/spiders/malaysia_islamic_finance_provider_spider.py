from __future__ import annotations

import scrapy


class MalaysiaIslamicFinanceProviderSpider(scrapy.Spider):
    """Malaysia Islamic Finance provider registry."""

    name = "malaysia_islamic_finance_provider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
