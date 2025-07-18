from __future__ import annotations

import scrapy


class MajorBankSuspiciousAccountClosureSpider(scrapy.Spider):
    """Major bank suspicious account closures."""

    name = "major_bank_suspicious_account_closure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
