"""Spider monitoring asset auctions and liquidations."""

from __future__ import annotations

import scrapy


class AssetAuctionSpider(scrapy.Spider):
    """Track sales of repossessed or distressed assets."""

    name = "asset_auction"

    def parse(self, response: scrapy.http.Response):
        yield {}
