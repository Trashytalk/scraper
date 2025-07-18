"""Placeholder spider for Russia Government-Business Appointment."""

import scrapy


class RussiaGovernmentBusinessAppointmentSpider(scrapy.Spider):
    name = "russia_government_business_appointment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
