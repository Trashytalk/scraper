"""Gather Thai anti-corruption case data.

Collect cases, disclosures, and resolved sanctions from the Office of the
National Anti-Corruption Commission (NACC).
"""

from __future__ import annotations

import scrapy


class ThailandAntiCorruptionSpider(scrapy.Spider):
    """Spider for NACC case disclosures."""

    name = "thailandanticorruptionspider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
