from __future__ import annotations

"""Scrapy middleware for proxy rotation and user-agent spoofing."""

import random
import time
from typing import Iterable

from scrapy import Request
from scrapy.crawler import Spider

from ..proxy.manager import ProxyManager


class ProxyMiddleware:
    """Middleware that sets proxy for each request."""

    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager

    @classmethod
    def from_crawler(cls, crawler):  # type: ignore[no-untyped-def]
        provider = getattr(crawler.settings, "PROXY_PROVIDER", None)
        if provider is None:
            raise RuntimeError("PROXY_PROVIDER setting not configured")
        return cls(proxy_manager=ProxyManager(provider))

    def process_request(self, request: Request, spider: Spider) -> None:
        request.meta["proxy"] = self.proxy_manager.get_proxy()

    def process_exception(self, request: Request, exception: Exception, spider: Spider) -> None:
        # rotate proxy on failure
        self.proxy_manager.rotate_proxy()



class RandomUserAgentMiddleware:
    """Set a random ``User-Agent`` header for each request."""

    def __init__(self, user_agents: Iterable[str]) -> None:
        self.user_agents = list(user_agents)

    @classmethod
    def from_crawler(cls, crawler):  # type: ignore[no-untyped-def]
        settings_agents = crawler.settings.getlist(
            "USER_AGENTS",
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/118.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            ],
        )
        return cls(settings_agents)

    def process_request(self, request, spider):  # type: ignore[no-untyped-def]
        request.headers.setdefault("User-Agent", random.choice(self.user_agents))


class RandomDelayMiddleware:
    """Introduce a random delay between requests."""

    def __init__(self, min_delay: float = 0.5, max_delay: float = 2.0) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay

    @classmethod
    def from_crawler(cls, crawler):  # type: ignore[no-untyped-def]
        return cls(
            crawler.settings.getfloat("MIN_DELAY", 0.5),
            crawler.settings.getfloat("MAX_DELAY", 2.0),
        )

    def process_request(self, request, spider):  # type: ignore[no-untyped-def]
        time.sleep(random.uniform(self.min_delay, self.max_delay))
