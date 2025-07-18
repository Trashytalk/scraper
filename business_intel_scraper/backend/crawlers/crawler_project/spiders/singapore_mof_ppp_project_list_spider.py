from __future__ import annotations

import scrapy


class SingaporeMofPppProjectListSpider(scrapy.Spider):
    """Placeholder for the Singapore MOF PPP Project List."""

    name = "singapore_mof_ppp_project_list_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
