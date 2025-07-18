from __future__ import annotations

import scrapy


class CzechNationalBankBlacklistSpider(scrapy.Spider):
    """Czech National Bank enforcement blacklist."""

    name = "czech_national_bank_blacklist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
