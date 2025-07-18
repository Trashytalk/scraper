"""Spider for Brazil Receita Federal CNPJ (placeholder)."""

import scrapy


class BrazilReceitaFederalCnpjSpider(scrapy.Spider):
    """Placeholder spider for Brazil Receita Federal CNPJ."""

    name = "brazilreceitafederalcnpj"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
