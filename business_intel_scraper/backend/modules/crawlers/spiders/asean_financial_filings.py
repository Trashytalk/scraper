"""Harvest financial filings from ASEAN central banks."""

import scrapy


class AseanFinancialFilingsSpider(scrapy.Spider):
    """Harvest financial filings from ASEAN central banks."""

    name = "aseanfinancialfilingsspider"
    allowed_domains = ["bot.or.th"]
    start_urls = ["https://www.bot.or.th"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
