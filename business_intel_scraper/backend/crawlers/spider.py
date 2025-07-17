"""Example Scrapy spider."""

from __future__ import annotations

import scrapy


class ExampleSpider(scrapy.Spider):
    """Simple spider that scrapes example.com."""

    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    def parse(
        self,
        response: scrapy.http.Response,
    ) -> scrapy.Item | dict[str, str]:
        """Parse the response.

        Parameters
        ----------
        response : scrapy.http.Response
            The HTTP response to parse.

        Returns
        -------
        scrapy.Item | dict[str, str]
            Parsed item from the page.
        """
        return {"url": response.url}
