import scrapy


class MaltaGamingAuthorityLicenseeSpider(scrapy.Spider):
    name = "malta_gaming_authority_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
