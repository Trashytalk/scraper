"""Gather company data, insolvency, and enforcement notices."""

from __future__ import annotations

import scrapy


class CzechJusticeMinistryBusinessRegisterSpider(scrapy.Spider):
    """Gather company data, insolvency, and enforcement notices."""

    name = "czechjusticeministrybusinessregisterspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
