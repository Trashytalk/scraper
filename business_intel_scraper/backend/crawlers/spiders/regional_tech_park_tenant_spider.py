from __future__ import annotations

import scrapy


class RegionalTechParkTenantSpider(scrapy.Spider):
    """Regional technology park and incubator tenants."""

    name = "regional_tech_park_tenant"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
