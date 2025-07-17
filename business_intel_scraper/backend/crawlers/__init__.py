"""Crawler module providing Scrapy spiders and browser-based crawlers."""

try:
    from .spider import ExampleSpider
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ExampleSpider = None  # type: ignore

from .browser import BrowserCrawler
from .playwright_utils import fetch_with_playwright

__all__ = ["BrowserCrawler", "fetch_with_playwright"]
if ExampleSpider is not None:
    __all__.insert(0, "ExampleSpider")


