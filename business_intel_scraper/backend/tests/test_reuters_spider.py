from __future__ import annotations

# ruff: noqa: E402

import sys
from pathlib import Path
from scrapy.http import TextResponse

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from business_intel_scraper.backend.modules.spiders.reuters_news_spider import (
    ReutersNewsSpider,
)


def test_reuters_news_spider_parse() -> None:
    html = """
    <html><body>
    <article class='story'>
    <h3><a href='/article/1'>Title 1</a></h3>
    <time datetime='2025-07-18T12:00:00Z'></time>
    </article>
    <article class='story'>
    <h3><a href='/article/2'>Title 2</a></h3>
    <time datetime='2025-07-18T13:00:00Z'></time>
    </article>
    </body></html>
    """
    response = TextResponse(
        url="https://www.reuters.com/world/", body=html, encoding="utf-8"
    )
    spider = ReutersNewsSpider()
    items = list(spider.parse(response))
    assert len(items) == 2
    assert items[0]["title"] == "Title 1"
    assert items[0]["url"].endswith("/article/1")
