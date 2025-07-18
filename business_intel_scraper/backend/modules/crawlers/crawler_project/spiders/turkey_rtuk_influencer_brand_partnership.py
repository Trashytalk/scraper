import scrapy


class TurkeyRtukInfluencerBrandPartnershipSpider(scrapy.Spider):
    name = "turkey_rtuk_influencer_brand_partnership"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
