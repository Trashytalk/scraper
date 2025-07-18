"""Fetch downloadable reports or whitepapers from industry associations or
research groups."""

from __future__ import annotations

import scrapy


class IndustryReportsSpider(scrapy.Spider):
    """Fetch downloadable reports or whitepapers from industry associations or
    research groups."""

    name = "industry_reports_spider"
