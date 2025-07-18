"""Spider collecting business association memberships."""

from __future__ import annotations

import scrapy


class BusinessAssociationSpider(scrapy.Spider):
    """Gather rosters from chambers of commerce and trade groups."""

    name = "business_association"

    def parse(self, response: scrapy.http.Response):
        yield {}
