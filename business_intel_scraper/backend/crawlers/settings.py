"""Scrapy project settings."""

from __future__ import annotations

# Identify the bot with a custom User-Agent string.
USER_AGENT = "BusinessIntelBot/1.0 (+https://example.com)"

# Limit the number of concurrent requests.
CONCURRENT_REQUESTS = 16

# Enable item pipelines.
ITEM_PIPELINES = {
    "business_intel_scraper.backend.crawlers.pipelines.ExamplePipeline": 300,
}
