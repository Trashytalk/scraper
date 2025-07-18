from __future__ import annotations

import scrapy


class DubaiExpoExhibitorListSpider(scrapy.Spider):
    """Placeholder for the Dubai Expo Exhibitor List."""

    name = "dubai_expo_exhibitor_list_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
