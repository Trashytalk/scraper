from __future__ import annotations

import scrapy


class KuwaitCMAViolatorSpider(scrapy.Spider):
    """Kuwait Capital Markets Authority violator registry."""

    name = "kuwait_cma_violator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
