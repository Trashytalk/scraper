"""Spider gathering bank regulator enforcement actions."""

from __future__ import annotations

import scrapy


class BankRegulatorEnforcementSpider(scrapy.Spider):
    """Collect public enforcement actions from regulators."""

    name = "bank_regulator_enforcement"

    def parse(self, response: scrapy.http.Response):
        yield {}
