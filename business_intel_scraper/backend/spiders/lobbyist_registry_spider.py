"""Extract records from lobbying registries to map influence networks."""

from __future__ import annotations

import scrapy


class LobbyistRegistrySpider(scrapy.Spider):
    """Extract records from lobbying registries to map influence networks."""

    name = "lobbyist_registry_spider"
