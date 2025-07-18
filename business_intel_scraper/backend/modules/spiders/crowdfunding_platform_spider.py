"""Monitor Kickstarter, Indiegogo, or regional platforms for startup signals and
emerging ventures."""

from __future__ import annotations

import scrapy


class CrowdfundingPlatformSpider(scrapy.Spider):
    """Monitor Kickstarter, Indiegogo, or regional platforms for startup signals and
    emerging ventures."""

    name = "crowdfunding_platform_spider"
