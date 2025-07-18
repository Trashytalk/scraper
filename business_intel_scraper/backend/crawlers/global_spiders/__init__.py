"""Collection of additional Scrapy spiders."""

from .african_corporate_registry_spider import AfricanCorporateRegistrySpider
from .asia_pacific_business_registry_spider import AsiaPacificBusinessRegistrySpider
from .country_specific_litigation_judiciary_spider import (
    CountrySpecificLitigationJudiciarySpider,
)
from .cross_border_m_a_filing_spider import CrossBorderMAFilingSpider
from .eu_aml_cft_enforcement_spider import EuAmlCftEnforcementSpider
from .eu_company_register_spider import EuCompanyRegisterSpider
from .eu_global_esg_disclosure_spider import EuGlobalEsgDisclosureSpider
from .european_asian_ipo_delisting_spider import EuropeanAsianIpoDelistingSpider
from .european_procurement_tender_spider import EuropeanProcurementTenderSpider
from .foreign_bank_financial_institution_registry_spider import (
    ForeignBankFinancialInstitutionRegistrySpider,
)
from .foreign_exchange_control_compliance_spider import (
    ForeignExchangeControlComplianceSpider,
)
from .foreign_financial_regulatory_filing_spider import (
    ForeignFinancialRegulatoryFilingSpider,
)
from .foreign_lobbyist_registry_spider import ForeignLobbyistRegistrySpider
from .global_customs_port_authority_spider import GlobalCustomsPortAuthoritySpider
from .global_labor_workplace_violation_spider import GlobalLaborWorkplaceViolationSpider
from .global_opencorporates_integration_spider import (
    GlobalOpencorporatesIntegrationSpider,
)
from .global_public_procurement_blacklist_spider import (
    GlobalPublicProcurementBlacklistSpider,
)
from .global_real_estate_ownership_spider import GlobalRealEstateOwnershipSpider
from .global_trade_registry_spider import GlobalTradeRegistrySpider
from .global_ubo_registry_spider import GlobalUboRegistrySpider
from .international_e_commerce_marketplace_spider import (
    InternationalECommerceMarketplaceSpider,
)
from .international_grant_development_aid_spider import (
    InternationalGrantDevelopmentAidSpider,
)
from .international_maritime_registry_spider import InternationalMaritimeRegistrySpider
from .international_ngo_watch_spider import InternationalNgoWatchSpider
from .international_utility_infrastructure_ownership_spider import (
    InternationalUtilityInfrastructureOwnershipSpider,
)
from .latin_america_company_registry_spider import LatinAmericaCompanyRegistrySpider
from .middle_east_company_register_spider import MiddleEastCompanyRegisterSpider
from .non_us_patent_trademark_registry_spider import NonUsPatentTrademarkRegistrySpider
from .non_us_sanctions_list_spider import NonUsSanctionsListSpider
from .vat_taxpayer_registry_spider import VatTaxpayerRegistrySpider

__all__ = [
    "AfricanCorporateRegistrySpider",
    "AsiaPacificBusinessRegistrySpider",
    "CountrySpecificLitigationJudiciarySpider",
    "CrossBorderMAFilingSpider",
    "EuAmlCftEnforcementSpider",
    "EuCompanyRegisterSpider",
    "EuGlobalEsgDisclosureSpider",
    "EuropeanAsianIpoDelistingSpider",
    "EuropeanProcurementTenderSpider",
    "ForeignBankFinancialInstitutionRegistrySpider",
    "ForeignExchangeControlComplianceSpider",
    "ForeignFinancialRegulatoryFilingSpider",
    "ForeignLobbyistRegistrySpider",
    "GlobalCustomsPortAuthoritySpider",
    "GlobalLaborWorkplaceViolationSpider",
    "GlobalOpencorporatesIntegrationSpider",
    "GlobalPublicProcurementBlacklistSpider",
    "GlobalRealEstateOwnershipSpider",
    "GlobalTradeRegistrySpider",
    "GlobalUboRegistrySpider",
    "InternationalECommerceMarketplaceSpider",
    "InternationalGrantDevelopmentAidSpider",
    "InternationalMaritimeRegistrySpider",
    "InternationalNgoWatchSpider",
    "InternationalUtilityInfrastructureOwnershipSpider",
    "LatinAmericaCompanyRegistrySpider",
    "MiddleEastCompanyRegisterSpider",
    "NonUsPatentTrademarkRegistrySpider",
    "NonUsSanctionsListSpider",
    "VatTaxpayerRegistrySpider",
]
