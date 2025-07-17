"""Tests for crawler middleware."""

from __future__ import annotations

import time
from unittest import mock

import scrapy
from scrapy.http import Request

from business_intel_scraper.backend.crawlers.middleware import (
    RandomDelayMiddleware,
    RandomUserAgentMiddleware,
)


class DummySpider(scrapy.Spider):
    name = "dummy"


def test_random_user_agent_sets_header() -> None:
    middleware = RandomUserAgentMiddleware(["agent1", "agent2"])
    request = Request(url="http://example.com")
    middleware.process_request(request, DummySpider())
    assert request.headers.get("User-Agent") in [b"agent1", b"agent2"]


def test_random_delay_calls_sleep() -> None:
    middleware = RandomDelayMiddleware(min_delay=0.1, max_delay=0.2)
    request = Request(url="http://example.com")
    with mock.patch.object(time, "sleep") as mocked_sleep:
        middleware.process_request(request, DummySpider())
        assert mocked_sleep.call_count == 1
        args = mocked_sleep.call_args[0]
        assert 0.1 <= args[0] <= 0.2
