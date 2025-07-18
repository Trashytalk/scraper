"""Placeholder spider for Malaysian Assoc. of Convention & Exhibition Organisers."""

import scrapy


class MalaysianAssociationOfConventionExhibitionOrganisersSuppliersSpider(
    scrapy.Spider
):
    name = "malaysian_association_of_convention_exhibition_organisers_suppliers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
