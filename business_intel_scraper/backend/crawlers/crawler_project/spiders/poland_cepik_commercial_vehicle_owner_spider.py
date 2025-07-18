from __future__ import annotations

import scrapy


class PolandCepikCommercialVehicleOwnerSpider(scrapy.Spider):
    """Placeholder for the Poland CEPIK Commercial Vehicle Owner."""

    name = "poland_cepik_commercial_vehicle_owner_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
