"""Scrapy project settings.

This configuration identifies the bot, limits concurrency, and enables the
default item pipeline.
"""

from __future__ import annotations

# Identify the bot with a custom User-Agent string.
USER_AGENT = "BusinessIntelBot/1.0 (+https://example.com)"

# Limit the number of concurrent requests.
CONCURRENT_REQUESTS = 16

# Enable item pipelines.
ITEM_PIPELINES = {
    "business_intel_scraper.backend.modules.crawlers.pipelines.ExamplePipeline": 300,
}
