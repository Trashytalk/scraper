"""Scrape FDI approvals, renewals, and project permits."""

from __future__ import annotations

import scrapy


class SaudiSagiaInvestmentLicenseSpider(scrapy.Spider):
    """Scrape FDI approvals, renewals, and project permits."""

    name = "saudisagiainvestmentlicensespider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
