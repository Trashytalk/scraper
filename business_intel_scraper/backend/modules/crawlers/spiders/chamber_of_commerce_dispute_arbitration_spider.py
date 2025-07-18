from __future__ import annotations

import scrapy


class ChamberOfCommerceDisputeArbitrationSpider(scrapy.Spider):
    """Chamber of Commerce dispute arbitration records."""

    name = "chamber_of_commerce_dispute_arbitration"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
