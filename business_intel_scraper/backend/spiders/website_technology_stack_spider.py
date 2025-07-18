"""Scrape for usage of web technologies (Wappalyzer, BuiltWith) to assess
technical sophistication."""

from __future__ import annotations

import scrapy


class WebsiteTechnologyStackSpider(scrapy.Spider):
    """Scrape for usage of web technologies (Wappalyzer, BuiltWith) to assess
    technical sophistication."""

    name = "website_technology_stack_spider"
