from __future__ import annotations

import scrapy


class SingaporeRegisteredFilingAgentSpider(scrapy.Spider):
    """Placeholder for the Singapore Registered Filing Agent."""

    name = "singapore_registered_filing_agent_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
