"""Collect business/industry awards, 'top company' lists, or innovation
rankings."""

from __future__ import annotations

import scrapy


class AwardsRankingsSpider(scrapy.Spider):
    """Collect business/industry awards, 'top company' lists, or innovation
    rankings."""

    name = "awards_and_rankings_spider"
