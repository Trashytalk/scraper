import scrapy


class UaeNmcSocialMediaPartnershipDisclosureSpider(scrapy.Spider):
    name = "uae_nmc_social_media_partnership_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
