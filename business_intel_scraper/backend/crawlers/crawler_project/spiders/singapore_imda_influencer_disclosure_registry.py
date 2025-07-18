import scrapy


class SingaporeImdaInfluencerDisclosureRegistrySpider(scrapy.Spider):
    name = "singapore_imda_influencer_disclosure_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
