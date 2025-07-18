"""Scrape manufacturing plant, warehouse, or R&D location data from multiple
sources."""

from __future__ import annotations

import scrapy


class FacilityPlantLocationSpider(scrapy.Spider):
    """Scrape manufacturing plant, warehouse, or R&D location data from multiple
    sources."""

    name = "facility_plant_location_spider"
