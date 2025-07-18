import scrapy


class DubaiLandDepartmentTitleDeedSpider(scrapy.Spider):
    """Scrape real estate transactions from Dubai Land Department."""

    name = "dubai_land_department_title_deed"
    allowed_domains = ["dubailand.gov.ae"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse property transactions."""
        raise NotImplementedError


class GCCTaxAuthoritySpider(scrapy.Spider):
    """Collect VAT and GST registration data across GCC countries."""

    name = "gcc_tax_authority"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse GCC tax authority listings."""
        raise NotImplementedError


class AbuDhabiDubaiFreeZoneCompanyListSpider(scrapy.Spider):
    """Track company registrations in Abu Dhabi and Dubai free zones."""

    name = "abu_dhabi_dubai_free_zone_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse free zone company lists."""
        raise NotImplementedError


class KuwaitSaudiPublicProcurementSpider(scrapy.Spider):
    """Scrape public procurement records from Kuwait and Saudi Arabia."""

    name = "kuwait_saudi_public_procurement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse procurement announcements."""
        raise NotImplementedError


class JordanCompaniesControlDepartmentRegistrySpider(scrapy.Spider):
    """Harvest Jordanian business registration data."""

    name = "jordan_companies_control_department_registry"
    allowed_domains = ["ccd.gov.jo"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse company registry records."""
        raise NotImplementedError


class QatarCentralBankAMLEnforcementSpider(scrapy.Spider):
    """Monitor AML enforcement actions from the Qatar Central Bank."""

    name = "qatar_central_bank_aml_enforcement"
    allowed_domains = ["qcb.gov.qa"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse AML enforcement data."""
        raise NotImplementedError


class IsraelInnovationAuthorityGrantsSpider(scrapy.Spider):
    """Track grants awarded by the Israel Innovation Authority."""

    name = "israel_innovation_authority_grants"
    allowed_domains = ["innovationisrael.org.il"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse innovation grants."""
        raise NotImplementedError


class IranChamberOfCommerceMembershipSpider(scrapy.Spider):
    """Scrape membership information from Iran's Chamber of Commerce."""

    name = "iran_chamber_of_commerce_membership"
    allowed_domains = ["iccima.ir"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse chamber membership records."""
        raise NotImplementedError


class EgyptPublicBusinessSectorCompanyReportsSpider(scrapy.Spider):
    """Scrape reports from Egypt's public business sector companies."""

    name = "egypt_public_business_sector_company_reports"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse company reports."""
        raise NotImplementedError


class SaudiNitaqatComplianceSpider(scrapy.Spider):
    """Monitor Saudization compliance records."""

    name = "saudi_nitaqat_compliance"
    allowed_domains = ["hrsd.gov.sa"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse Nitaqat compliance lists."""
        raise NotImplementedError


class GCCTenderBlacklistAnnouncementsSpider(scrapy.Spider):
    """Track blacklist announcements for tenders across Gulf states."""

    name = "gcc_tender_blacklist_announcements"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse blacklist entries."""
        raise NotImplementedError


class TurkeyKAPPublicDisclosurePlatformSpider(scrapy.Spider):
    """Scrape public disclosures from Turkey's KAP platform."""

    name = "turkey_kap_public_disclosure_platform"
    allowed_domains = ["kap.org.tr"]
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse KAP filings."""
        raise NotImplementedError


class DubaiCourtsLitigationAnnouncementSpider(scrapy.Spider):
    """Monitor litigation announcements from Dubai courts."""

    name = "dubai_courts_litigation_announcement"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse court announcements."""
        raise NotImplementedError
