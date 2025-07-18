"""Scrape GitHub, GitLab, etc. for company-affiliated OSS activity and project
contributions."""

from __future__ import annotations

import scrapy


class OpenSourceContributionsSpider(scrapy.Spider):
    """Scrape GitHub, GitLab, etc. for company-affiliated OSS activity and project
    contributions."""

    name = "open_source_contributions_spider"
