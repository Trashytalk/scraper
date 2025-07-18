from __future__ import annotations

import scrapy


class UAESCAInvestorAlertSpider(scrapy.Spider):
    """UAE Securities & Commodities Authority investor alerts."""

    name = "uae_sca_investor_alert"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
