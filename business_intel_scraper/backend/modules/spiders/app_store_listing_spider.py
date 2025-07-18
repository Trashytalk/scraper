"""Harvest company or product listings from Google Play, Apple App Store, or
regional alternatives."""

from __future__ import annotations

import scrapy


class AppStoreListingSpider(scrapy.Spider):
    """Harvest company or product listings from Google Play, Apple App Store, or
    regional alternatives."""

    name = "app_store_listing_spider"
