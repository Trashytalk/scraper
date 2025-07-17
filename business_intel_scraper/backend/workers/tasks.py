"""Background task worker using Celery."""

from __future__ import annotations

import uuid
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict
import time

try:
    from gevent.pool import Pool
    from gevent import sleep as async_sleep
    GEVENT_AVAILABLE = True
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    Pool = None  # type: ignore
    async_sleep = time.sleep  # type: ignore
    GEVENT_AVAILABLE = False
from business_intel_scraper.backend.osint.integrations import run_spiderfoot
from business_intel_scraper.backend.db.utils import (
    Base,
    ENGINE,
    SessionLocal,
    init_db,
    save_companies,
)
from business_intel_scraper.backend.db.models import Company

from . import celery_app


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

# In the test environment Celery may not be installed. To provide basic
# asynchronous behaviour without requiring external services we also manage
# an executor and in-memory task registry. If ``gevent`` is available we use a
# greenlet pool for lightweight concurrency, otherwise a ``ThreadPoolExecutor``
# is used. Each launched task is tracked by a UUID so the API can query its
# status.

if GEVENT_AVAILABLE:
    _executor = Pool()
    _tasks: Dict[str, object] = {}
else:  # pragma: no cover - fallback when gevent is missing
    _executor = ThreadPoolExecutor()
    _tasks: Dict[str, Future] = {}

def _submit(func, *args, **kwargs):  # type: ignore[no-untyped-def]
    """Submit a callable to the underlying executor."""

    if GEVENT_AVAILABLE:
        return _executor.spawn(func, *args, **kwargs)
    return _executor.submit(func, *args, **kwargs)


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


def _run_example_spider() -> str:
    """Run the example Scrapy spider and persist results."""

    try:
        from business_intel_scraper.backend.db.utils import init_db, save_companies
    except Exception:  # pragma: no cover - database optional
        init_db = save_companies = None  # type: ignore

    items = run_spider_task("example")

    if init_db and save_companies:
        try:
            init_db()
            save_companies(item.get("url", "") for item in items)
        except Exception:  # pragma: no cover - database failure
            pass

    return "scraping complete"


def launch_scraping_task() -> str:
    """Launch a background scraping task.

    Returns
    -------
    str
        Identifier of the launched task.
    """

    task_id = str(uuid.uuid4())
    future = _submit(_run_example_spider)
    _tasks[task_id] = future
    return task_id


def get_task_status(task_id: str) -> str:
    """Return the current status of a task."""

    future = _tasks.get(task_id)
    if future is None:
        return "not_found"
    if GEVENT_AVAILABLE:
        if future.ready():
            return "completed"
    else:
        if isinstance(future, Future) and future.done():
            return "completed"
    return "running"

@celery_app.task
def run_spider_task(spider_name: str = "example", **kwargs: object) -> list[dict[str, str]]:
    """Run a Scrapy spider.

    Parameters
    ----------
    spider_name : str, optional
        Name of the spider to run. Only ``"example"`` is supported.
    **kwargs : object
        Additional arguments passed to the spider. Currently only ``html`` is
        recognised and used when provided.

    Returns
    -------
    list[dict[str, str]]
        Items scraped by the spider.
    """
    from importlib import import_module

    if spider_name != "example":
        raise ValueError(f"Unknown spider '{spider_name}'")

    try:
        module = import_module("business_intel_scraper.backend.crawlers.spider")
        spider_cls = getattr(module, "ExampleSpider")
    except Exception:  # pragma: no cover - unexpected import failure
        return []

    html = kwargs.get("html")

    if html is not None:
        spider_instance = spider_cls()
        response = TextResponse(url="https://example.com", body=html.encode("utf-8"))
        item = spider_instance.parse(response)
        return [dict(item)]

    items: list[dict[str, str]] = []
    process = CrawlerProcess(settings={"LOG_ENABLED": False})

    def _collect(item: dict) -> None:
        items.append(dict(item))

    process.crawl(spider_cls)
    for crawler in process.crawlers:
        crawler.signals.connect(_collect, signal="item_scraped")
    process.start(stop_after_crawl=True)

    return items

@celery_app.task
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
