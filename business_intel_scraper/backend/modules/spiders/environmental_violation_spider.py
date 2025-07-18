"""Harvest environmental violation or compliance records from EPA, regional, or
global sources."""

from __future__ import annotations

import scrapy


class EnvironmentalViolationSpider(scrapy.Spider):
    """Harvest environmental violation or compliance records from EPA, regional, or
    global sources."""

    name = "environmental_violation_spider"
