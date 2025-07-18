"""Placeholder spider for Dubai Land Department Foreclosure List."""

import scrapy


class DubaiLandDepartmentForeclosureListSpider(scrapy.Spider):
    name = "dubai_land_department_foreclosure_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
