from __future__ import annotations

import scrapy


class IsraelInnovationAuthorityGrantSpider(scrapy.Spider):
    """Placeholder for the Israel Innovation Authority Grant."""

    name = "israel_innovation_authority_grant_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
