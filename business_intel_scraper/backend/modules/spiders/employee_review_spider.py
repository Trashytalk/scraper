"""Gather reviews/ratings from Glassdoor, Indeed, or regional equivalents for
culture and sentiment insights."""

from __future__ import annotations

import scrapy


class EmployeeReviewSpider(scrapy.Spider):
    """Gather reviews/ratings from Glassdoor, Indeed, or regional equivalents for
    culture and sentiment insights."""

    name = "employee_review_spider"
