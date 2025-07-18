"""Map QFC and free zone business registries."""

from __future__ import annotations

import scrapy


class QatarFinancialCenterCompanySpider(scrapy.Spider):
    """Map QFC and free zone business registries."""

    name = "qatarfinancialcentercompanyspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
