"""Global Labor/Workplace Violation Spider implementation."""

import scrapy


class GlobalLaborWorkplaceViolationSpider(scrapy.Spider):
    """Spider for Global Labor/Workplace Violation."""

    name = "global_labor_workplace_violation_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
