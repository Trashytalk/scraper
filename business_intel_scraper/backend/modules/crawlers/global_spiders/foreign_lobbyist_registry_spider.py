"""Foreign Lobbyist Registry Spider implementation."""

import scrapy


class ForeignLobbyistRegistrySpider(scrapy.Spider):
    """Spider for Foreign Lobbyist Registry."""

    name = "foreign_lobbyist_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
