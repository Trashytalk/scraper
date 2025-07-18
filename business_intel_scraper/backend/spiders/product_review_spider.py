"""Gather reviews from e-commerce sites to analyze sentiment about specific
products or brands."""

from __future__ import annotations

import scrapy


class ProductReviewSpider(scrapy.Spider):
    """Gather reviews from e-commerce sites to analyze sentiment about specific
    products or brands."""

    name = "product_review_spider"
