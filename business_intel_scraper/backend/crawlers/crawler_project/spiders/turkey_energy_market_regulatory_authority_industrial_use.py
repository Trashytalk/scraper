import scrapy


class TurkeyEnergyMarketRegulatoryAuthorityIndustrialUseSpider(scrapy.Spider):
    name = "turkey_energy_market_regulatory_authority_industrial_use"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
