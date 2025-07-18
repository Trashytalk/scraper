"""Placeholder spider for Russia Rosfinmonitoring AML Action."""

import scrapy


class RussiaRosfinmonitoringAmlActionSpider(scrapy.Spider):
    name = "russia_rosfinmonitoring_aml_action"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
