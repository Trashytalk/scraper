"""Placeholder spider for Israel Former Official Business Appointment."""

import scrapy


class IsraelFormerOfficialBusinessAppointmentSpider(scrapy.Spider):
    name = "israel_former_official_business_appointment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
