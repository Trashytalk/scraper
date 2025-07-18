import scrapy


class SingaporeTemasekAssetRestructuringSpider(scrapy.Spider):
    name = "singapore_temasek_asset_restructuring"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
