"""Track court decisions related to anti-corruption and business conduct."""

from __future__ import annotations

import scrapy


class UkraineHighAntiCorruptionCourtJudgmentSpider(scrapy.Spider):
    """Track court decisions related to anti-corruption and business conduct."""

    name = "ukrainehighanticorruptioncourtjudgmentspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
