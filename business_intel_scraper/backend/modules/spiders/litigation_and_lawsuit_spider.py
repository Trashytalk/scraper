"""Scrape court dockets or litigation trackers for cases involving target
companies."""

from __future__ import annotations

import scrapy


class LitigationLawsuitSpider(scrapy.Spider):
    """Scrape court dockets or litigation trackers for cases involving target
    companies."""

    name = "litigation_and_lawsuit_spider"
