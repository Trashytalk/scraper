"""Scrape latest Reuters news articles."""

from __future__ import annotations

from datetime import datetime
import scrapy


class ReutersNewsSpider(scrapy.Spider):
    """Spider that extracts article headlines from Reuters."""

    name = "reuters_news_spider"
    allowed_domains = ["www.reuters.com"]
    start_urls = ["https://www.reuters.com/world/"]

    def parse(self, response: scrapy.http.Response):
        for article in response.css("article.story"):
            title = article.css("h3 a::text").get()
            url = response.urljoin(article.css("h3 a::attr(href)").get(""))
            published_str = article.css("time::attr(datetime)").get()
            published = None
            if published_str:
                published = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            yield {
                "title": title,
                "url": url,
                "published": published,
            }
