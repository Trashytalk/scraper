"""Crawler module providing Scrapy spiders and browser-based crawlers."""

try:
    from .spider import ExampleSpider
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ExampleSpider = None  # type: ignore

from .browser import BrowserCrawler
from .playwright_utils import fetch_with_playwright
from .spiders.southeast_asia import (
    AseanPepCorruptionCaseSpider,
    CambodiaMinistryOfCommerceFilingsSpider,
    IndonesiaOJKEnforcementSpider,
    MalaysiaSCDisclosureSpider,
    PhilippinesPhilgepsProcurementSpider,
    RegionalTaxTribunalJudgmentSpider,
    SeAsiaRenewableEnergyCarbonCreditRegistrySpider,
    SingaporeMASEnforcementActionsSpider,
    SingaporeStraitsTimesMalaysianStarCorporateNewsSpider,
    ThailandBoardOfInvestmentSpider,
    VietnamExportProcessingZoneRegistrySpider,
    VietnamStateSecuritiesCommissionPenaltySpider,
)
from .spiders.middle_east import (
    AbuDhabiDubaiFreeZoneCompanyListSpider,
    DubaiCourtsLitigationAnnouncementSpider,
    DubaiLandDepartmentTitleDeedSpider,
    EgyptPublicBusinessSectorCompanyReportsSpider,
    GCCTaxAuthoritySpider,
    GCCTenderBlacklistAnnouncementsSpider,
    IranChamberOfCommerceMembershipSpider,
    IsraelInnovationAuthorityGrantsSpider,
    JordanCompaniesControlDepartmentRegistrySpider,
    KuwaitSaudiPublicProcurementSpider,
    QatarCentralBankAMLEnforcementSpider,
    SaudiNitaqatComplianceSpider,
    TurkeyKAPPublicDisclosurePlatformSpider,
)

# Regional spider modules
from .spiders.asean_customs_trade import AseanCustomsTradeSpider
from .spiders.asean_financial_filings import AseanFinancialFilingsSpider
from .spiders.asean_pep import AseanPEPSanctionsSpider
from .spiders.central_bank_filings import CentralBankFilingsSpider
from .spiders.dfm_tadawul import DFMTadawulListingSpider
from .spiders.ecommerce_marketplace import SEAEcommerceMarketplaceSpider
from .spiders.egypt_gafi import EgyptGAFIRegistrySpider
from .spiders.free_zone_registry import FreeZoneRegistrySpider
from .spiders.gcc_customs_trade import GCCCustomsTradeSpider
from .spiders.gcc_ip_registry import GCCIPTrademarkRegistrySpider
from .spiders.indonesia_ahu_oss import IndonesiaAHUOSSRegistrySpider
from .spiders.israel_companies import IsraelCompaniesSpider
from .spiders.malaysia_ssm import MalaysiaSSMCompanyRegistrySpider
from .spiders.me_pep_sanctions import MiddleEastPEPSanctionsSpider
from .spiders.me_procurement import MiddleEastProcurementSpider
from .spiders.philippines_sec import PhilippinesSECCompanySpider
from .spiders.qatar_moctrade import QatarMinistryCommerceSpider
from .spiders.real_estate_registry import RealEstateRegistrySpider
from .spiders.regional_ngo_registry import RegionalNGORegistrySpider
from .spiders.regional_procurement import RegionalProcurementSpider
from .spiders.saudi_cr import SaudiCRCompanyRegistrySpider
from .spiders.saudi_mol import SaudiMOLSpider
from .spiders.sea_ip_registry import SEAsiaPatentTrademarkSpider
from .spiders.sgx_bursa_listings import SGXBursaListingSpider
from .spiders.singapore_acra import SingaporeACRABusinessRegistrySpider
from .spiders.thailand_dbd import ThailandDBDCompanyRegistrySpider
from .spiders.trade_permit import TradePermitSpider
from .spiders.turkey_mersis import TurkeyMERSISRegistrySpider
from .spiders.uae_ded import UAEDedCompanyRegistrySpider
from .spiders.vietnam_nbr import VietnamNationalBusinessRegistrySpider

__all__ = [
    "BrowserCrawler",
    "fetch_with_playwright",
    "AseanCustomsTradeSpider",
    "AseanFinancialFilingsSpider",
    "AseanPEPSanctionsSpider",
    "CentralBankFilingsSpider",
    "DFMTadawulListingSpider",
    "SEAEcommerceMarketplaceSpider",
    "EgyptGAFIRegistrySpider",
    "FreeZoneRegistrySpider",
    "GCCCustomsTradeSpider",
    "GCCIPTrademarkRegistrySpider",
    "IndonesiaAHUOSSRegistrySpider",
    "IsraelCompaniesSpider",
    "MalaysiaSSMCompanyRegistrySpider",
    "MiddleEastPEPSanctionsSpider",
    "MiddleEastProcurementSpider",
    "PhilippinesSECCompanySpider",
    "QatarMinistryCommerceSpider",
    "RealEstateRegistrySpider",
    "RegionalNGORegistrySpider",
    "RegionalProcurementSpider",
    "SaudiCRCompanyRegistrySpider",
    "SaudiMOLSpider",
    "SEAsiaPatentTrademarkSpider",
    "SGXBursaListingSpider",
    "SingaporeACRABusinessRegistrySpider",
    "ThailandDBDCompanyRegistrySpider",
    "TradePermitSpider",
    "TurkeyMERSISRegistrySpider",
    "UAEDedCompanyRegistrySpider",
    "VietnamNationalBusinessRegistrySpider",
]

if ExampleSpider is not None:
    __all__.insert(0, "ExampleSpider")

__all__ += [
    "SingaporeStraitsTimesMalaysianStarCorporateNewsSpider",
    "SingaporeMASEnforcementActionsSpider",
    "ThailandBoardOfInvestmentSpider",
    "VietnamExportProcessingZoneRegistrySpider",
    "IndonesiaOJKEnforcementSpider",
    "MalaysiaSCDisclosureSpider",
    "CambodiaMinistryOfCommerceFilingsSpider",
    "AseanPepCorruptionCaseSpider",
    "RegionalTaxTribunalJudgmentSpider",
    "SeAsiaRenewableEnergyCarbonCreditRegistrySpider",
    "PhilippinesPhilgepsProcurementSpider",
    "VietnamStateSecuritiesCommissionPenaltySpider",
    "DubaiLandDepartmentTitleDeedSpider",
    "GCCTaxAuthoritySpider",
    "AbuDhabiDubaiFreeZoneCompanyListSpider",
    "KuwaitSaudiPublicProcurementSpider",
    "JordanCompaniesControlDepartmentRegistrySpider",
    "QatarCentralBankAMLEnforcementSpider",
    "IsraelInnovationAuthorityGrantsSpider",
    "IranChamberOfCommerceMembershipSpider",
    "EgyptPublicBusinessSectorCompanyReportsSpider",
    "SaudiNitaqatComplianceSpider",
    "GCCTenderBlacklistAnnouncementsSpider",
    "TurkeyKAPPublicDisclosurePlatformSpider",
    "DubaiCourtsLitigationAnnouncementSpider",
]
