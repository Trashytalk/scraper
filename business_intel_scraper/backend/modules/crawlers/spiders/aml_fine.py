"""Spider gathering AML fine information."""

from __future__ import annotations

import scrapy


class AMLFineSpider(scrapy.Spider):
    """Collect penalties or settlements related to AML."""

    name = "aml_fine"

    def parse(self, response: scrapy.http.Response):
        yield {}
