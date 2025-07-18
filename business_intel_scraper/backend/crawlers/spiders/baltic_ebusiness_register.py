"""Collect filings, digital signatures, and cross-border company links."""

from __future__ import annotations

import scrapy


class BalticEBusinessRegisterSpider(scrapy.Spider):
    """Collect filings, digital signatures, and cross-border company links."""

    name = "balticebusinessregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
