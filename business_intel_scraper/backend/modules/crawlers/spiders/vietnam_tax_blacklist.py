"""Scrape Vietnam's tax blacklist.

Collect companies banned from issuing invoices or listed as tax non-compliant.
"""

from __future__ import annotations

import scrapy


class VietnamTaxBlacklistSpider(scrapy.Spider):
    """Spider for Vietnam's tax blacklist."""

    name = "vietnamtaxblacklistspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
