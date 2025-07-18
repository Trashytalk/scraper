"""Gather public information from company or executive profiles on platforms
like LinkedIn or Twitter."""

from __future__ import annotations

import scrapy


class SocialMediaProfileSpider(scrapy.Spider):
    """Gather public information from company or executive profiles on platforms
    like LinkedIn or Twitter."""

    name = "social_media_profile_spider"
