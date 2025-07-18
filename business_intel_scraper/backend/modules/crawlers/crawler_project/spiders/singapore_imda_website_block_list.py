import scrapy


class SingaporeImdaWebsiteBlockListSpider(scrapy.Spider):
    name = "singapore_imda_website_block_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
