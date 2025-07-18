"""Collection of specialized Scrapy spiders used for business intelligence."""

from __future__ import annotations

import scrapy


class CompanyRegistrySpider(scrapy.Spider):
    """Crawl official company registries for basic company details."""

    name = "company_registry"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/registry"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class SocialMediaProfileSpider(scrapy.Spider):
    """Gather public info from social profiles."""

    name = "social_media_profile"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/profile"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class NewsArticleSpider(scrapy.Spider):
    """Scrape news sites for articles about target companies."""

    name = "news_article"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/news"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class JobListingsSpider(scrapy.Spider):
    """Extract job listings to gauge hiring trends."""

    name = "job_listings"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/jobs"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class IndustryReportsSpider(scrapy.Spider):
    """Fetch industry whitepapers or reports."""

    name = "industry_reports"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/reports"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class FinancialFilingsSpider(scrapy.Spider):
    """Collect regulatory financial filings."""

    name = "financial_filings"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/filings"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class GovernmentContractPortalSpider(scrapy.Spider):
    """Harvest contract awards and procurement notices."""

    name = "government_contract_portal"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/contracts"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class CompanyBlogSpider(scrapy.Spider):
    """Monitor official company blogs for announcements."""

    name = "company_blog"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/blog"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class ConferenceEventsSpider(scrapy.Spider):
    """Extract schedules or attendee lists from conference sites."""

    name = "conference_events"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/events"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class GeographicDirectorySpider(scrapy.Spider):
    """Scrape business directories for a specific region."""

    name = "geographic_directory"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/directory"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class ProductReviewSpider(scrapy.Spider):
    """Gather product reviews from e-commerce sites."""

    name = "product_review"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/reviews"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class RealEstateListingSpider(scrapy.Spider):
    """Track commercial real estate listings."""

    name = "real_estate_listing"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/realestate"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class GrantFundingDatabaseSpider(scrapy.Spider):
    """Collect information on grants or venture funding."""

    name = "grant_funding_database"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/grants"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class SecurityAdvisorySpider(scrapy.Spider):
    """Monitor vendor security advisories."""

    name = "security_advisory"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/advisories"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class CorporateOfficerSpider(scrapy.Spider):
    """Extract executive details from About pages."""

    name = "corporate_officer"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/about"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class PatentTrademarkSpider(scrapy.Spider):
    """Gather patent or trademark filings."""

    name = "patent_trademark"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/patents"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class FinancialNewsSpider(scrapy.Spider):
    """Monitor financial news for market insights."""

    name = "financial_news"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/finance-news"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class PublicRecordSpider(scrapy.Spider):
    """Collect public legal records."""

    name = "public_record"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/records"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class SupplyChainSpider(scrapy.Spider):
    """Harvest supplier information for supply chain mapping."""

    name = "supply_chain"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/suppliers"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}


class CompetitorPriceSpider(scrapy.Spider):
    """Track competitor pricing from online retailers."""

    name = "competitor_price"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/pricing"]

    def parse(self, response: scrapy.http.Response):
        yield {"url": response.url}
