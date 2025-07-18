import scrapy


class PolandMinistryOfStateAssetsAuctionSpider(scrapy.Spider):
    name = "poland_ministry_of_state_assets_auction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
