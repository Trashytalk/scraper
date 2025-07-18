import scrapy


class SingaporeSgxGreenBondListingSpider(scrapy.Spider):
    name = "singapore_sgx_green_bond_listing"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
