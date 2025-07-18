from __future__ import annotations

import scrapy


class PhilippinesBSPBankOwnershipPenaltySpider(scrapy.Spider):
    """Philippines BSP bank ownership and penalties."""

    name = "philippines_bsp_bank_ownership_penalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
