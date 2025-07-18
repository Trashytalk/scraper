"""Spider tracking offshore or shell company data."""

from __future__ import annotations

import scrapy


class ShellCompanySpider(scrapy.Spider):
    """Monitor offshore jurisdiction registries."""

    name = "shell_company"

    def parse(self, response: scrapy.http.Response):
        yield {}
