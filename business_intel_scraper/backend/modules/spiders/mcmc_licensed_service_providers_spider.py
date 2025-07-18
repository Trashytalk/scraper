"""Placeholder spider for MCMC Licensed Service Providers."""

import scrapy


class McmcLicensedServiceProvidersSpider(scrapy.Spider):
    name = "mcmc_licensed_service_providers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
