"""Spider harvesting franchise directory listings."""

from __future__ import annotations

import scrapy


class FranchiseDirectorySpider(scrapy.Spider):
    """Profile franchise expansion and local presence."""

    name = "franchise_directory"

    def parse(self, response: scrapy.http.Response):
        yield {}
