import scrapy


class EgyptStateAssetSaleAnnouncementSpider(scrapy.Spider):
    name = "egypt_state_asset_sale_announcement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
