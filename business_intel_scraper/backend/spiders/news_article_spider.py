"""Scrape targeted news sites for articles mentioning selected businesses or
keywords."""

from __future__ import annotations

import scrapy


class NewsArticleSpider(scrapy.Spider):
    """Scrape targeted news sites for articles mentioning selected businesses or
    keywords."""

    name = "news_article_spider"
