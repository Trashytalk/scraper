"""Background task worker using Celery."""

from __future__ import annotations

from business_intel_scraper.backend.osint.integrations import run_spiderfoot

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional dependency

    class Celery:  # type: ignore
        """Fallback Celery replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def task(self, func):  # type: ignore[no-untyped-def]
            return func


celery_app = Celery("tasks")


try:
    from scrapy.crawler import CrawlerProcess
    from scrapy.http import TextResponse
except ModuleNotFoundError:  # pragma: no cover - optional dependency

    class CrawlerProcess:  # type: ignore
        """Fallback when Scrapy is not installed."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            raise RuntimeError("Scrapy is required to run this task")

    class TextResponse:  # type: ignore[no-redef]
        def __init__(self, *args: object, **kwargs: object) -> None:  # pragma: no cover - simple stub
            pass


@celery_app.task
def example_task(x: int, y: int) -> int:
    """Add two numbers together.

    Parameters
    ----------
    x : int
        First number.
    y : int
        Second number.

    Returns
    -------
    int
        Sum of ``x`` and ``y``.
    """
    return x + y


@celery_app.task
def run_spider_task(spider: str = "example", html: str | None = None) -> list[dict[str, str]]:
    """Run a Scrapy spider.

    Parameters
    ----------
    spider : str, optional
        Name of the spider to run. Only ``"example"`` is supported.
    html : str, optional
        Optional HTML body to parse instead of fetching from the network.

    Returns
    -------
    list[dict[str, str]]
        Items scraped by the spider.
    """
    from importlib import import_module

    if spider != "example":
        raise ValueError(f"Unknown spider '{spider}'")

    try:
        module = import_module("business_intel_scraper.backend.crawlers.spider")
        spider_cls = getattr(module, "ExampleSpider")
    except Exception:  # pragma: no cover - unexpected import failure
        return []

    if html is not None:
        spider_instance = spider_cls()
        response = TextResponse(url="https://example.com", body=html.encode("utf-8"))
        item = spider_instance.parse(response)
        return [dict(item)]

    items: list[dict[str, str]] = []
    process = CrawlerProcess(settings={"LOG_ENABLED": False})

    def _collect(item):
        items.append(dict(item))

    process.crawl(spider_cls)
    for crawler in process.crawlers:
        crawler.signals.connect(_collect, signal="item_scraped")
    process.start(stop_after_crawl=True)

    return items

def spiderfoot_scan(domain: str) -> dict[str, str]:
    """Run SpiderFoot OSINT scan.

    Parameters
    ----------
    domain : str
        Domain to investigate.

    Returns
    -------
    dict[str, str]
        Results from :func:`run_spiderfoot`.
    """

    return run_spiderfoot(domain)
