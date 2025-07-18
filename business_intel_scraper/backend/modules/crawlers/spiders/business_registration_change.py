"""Spider detecting changes in business registrations."""

from __future__ import annotations

import scrapy


class BusinessRegistrationChangeSpider(scrapy.Spider):
    """Detect updates to company registrations."""

    name = "business_registration_change"

    def parse(self, response: scrapy.http.Response):
        yield {}
