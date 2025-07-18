"""Spider harvesting PE/VC portfolio company data."""

from __future__ import annotations

import scrapy


class PEVCPortfolioSpider(scrapy.Spider):
    """Collect current and former portfolio rosters."""

    name = "pe_vc_portfolio"

    def parse(self, response: scrapy.http.Response):
        yield {}
