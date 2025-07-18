"""Placeholder spider for Israel Vertex Ventures Portfolio."""

import scrapy


class IsraelVertexVenturesPortfolioSpider(scrapy.Spider):
    name = "israel_vertex_ventures_portfolio"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
