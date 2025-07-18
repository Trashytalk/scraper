from __future__ import annotations

import scrapy


class JapanCabinetOfficeBcpFilingSpider(scrapy.Spider):
    """Placeholder for the Japan Cabinet Office BCP Filing."""

    name = "japan_cabinet_office_bcp_filing_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
