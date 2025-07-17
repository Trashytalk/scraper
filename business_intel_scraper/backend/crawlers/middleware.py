from __future__ import annotations

"""Scrapy middleware for proxy rotation."""

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
