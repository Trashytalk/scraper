"""
Data Enrichment Engine

Enriches entities with external data sources:
- Sanctions lists (OFAC, EU, UN)
- Government contracts and procurement data
- Patent databases (USPTO, EPO)
- Social media profiles (LinkedIn, Twitter)
- Financial data (SEC filings, market data)
- News and media mentions
- Credit ratings and risk scores
"""

import asyncio
import aiohttp
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class EnrichmentSource:
    """Configuration for an enrichment data source"""

    name: str
    source_type: str  # sanctions, contracts, patents, social, financial, news
    api_endpoint: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    confidence_weight: float = 1.0
    cost_per_request: float = 0.0
    enabled: bool = True


@dataclass
class EnrichmentResult:
    """Container for enrichment results"""

    entity_id: str
    source_name: str
    enrichment_type: str
    data: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any]
    cost: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


class DataEnrichmentEngine:
    """Comprehensive data enrichment system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sources = self._load_enrichment_sources()
        self.session: Optional[aiohttp.ClientSession] = None

        # Rate limiting
        self.rate_limiters = {}

        # Caching
        self.cache = {}
        self.cache_ttl = config.get("cache_ttl_hours", 24) * 3600

        # Metrics
        self.enrichment_metrics = {
            "total_requests": 0,
            "successful_enrichments": 0,
            "failed_requests": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
        }

    def _load_enrichment_sources(self) -> Dict[str, EnrichmentSource]:
        """Load enrichment source configurations"""
        sources = {}

        # Sanctions databases
        sources["ofac_sdn"] = EnrichmentSource(
            name="OFAC SDN List",
            source_type="sanctions",
            api_endpoint="https://api.ofac.treasury.gov/sdn",
            rate_limit=60,
            confidence_weight=1.0,
        )

        sources["eu_sanctions"] = EnrichmentSource(
            name="EU Sanctions List",
            source_type="sanctions",
            api_endpoint="https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content",
            rate_limit=30,
            confidence_weight=0.9,
        )

        sources["un_sanctions"] = EnrichmentSource(
            name="UN Sanctions List",
            source_type="sanctions",
            api_endpoint="https://scsanctions.un.org/resources/xml/en/consolidated.xml",
            rate_limit=20,
            confidence_weight=0.9,
        )

        # Government contracts (example endpoints)
        sources["usaspending"] = EnrichmentSource(
            name="USAspending.gov",
            source_type="contracts",
            api_endpoint="https://api.usaspending.gov/api/v2/",
            rate_limit=120,
            confidence_weight=0.8,
        )

        sources["sam_gov"] = EnrichmentSource(
            name="SAM.gov",
            source_type="contracts",
            api_endpoint="https://api.sam.gov/entity-information/v3/",
            api_key=self.config.get("sam_api_key"),
            rate_limit=100,
            confidence_weight=0.9,
        )

        # Patent databases
        sources["uspto"] = EnrichmentSource(
            name="USPTO Patents",
            source_type="patents",
            api_endpoint="https://developer.uspto.gov/ds-api/",
            rate_limit=240,
            confidence_weight=0.8,
        )

        # Social media (would need API keys)
        sources["linkedin"] = EnrichmentSource(
            name="LinkedIn",
            source_type="social",
            api_endpoint="https://api.linkedin.com/v2/",
            api_key=self.config.get("linkedin_api_key"),
            rate_limit=100,
            confidence_weight=0.7,
            cost_per_request=0.01,
            enabled=bool(self.config.get("linkedin_api_key")),
        )

        # Financial data
        sources["sec_edgar"] = EnrichmentSource(
            name="SEC EDGAR",
            source_type="financial",
            api_endpoint="https://data.sec.gov/api/xbrl/",
            rate_limit=600,
            confidence_weight=0.9,
        )

        # News and media
        sources["news_api"] = EnrichmentSource(
            name="News API",
            source_type="news",
            api_endpoint="https://newsapi.org/v2/",
            api_key=self.config.get("news_api_key"),
            rate_limit=1000,
            confidence_weight=0.6,
            cost_per_request=0.001,
            enabled=bool(self.config.get("news_api_key")),
        )

        return sources

    async def enrich_entities(
        self,
        entities: List[Dict[str, Any]],
        enrichment_types: Optional[List[str]] = None,
    ) -> List[EnrichmentResult]:
        """Main enrichment pipeline for multiple entities"""
        if not enrichment_types:
            enrichment_types = ["sanctions", "contracts", "patents", "financial"]

        logger.info(
            f"Starting enrichment for {len(entities)} entities with types: {enrichment_types}"
        )

        all_results = []

        # Initialize HTTP session
        async with aiohttp.ClientSession() as session:
            self.session = session

            # Process entities in batches to manage rate limits
            batch_size = 10
            for i in range(0, len(entities), batch_size):
                batch = entities[i : i + batch_size]

                batch_results = await self._enrich_entity_batch(batch, enrichment_types)
                all_results.extend(batch_results)

                # Rate limiting pause between batches
                await asyncio.sleep(1)

        logger.info(f"Enrichment completed. Total results: {len(all_results)}")
        return all_results

    async def _enrich_entity_batch(
        self, entities: List[Dict], enrichment_types: List[str]
    ) -> List[EnrichmentResult]:
        """Enrich a batch of entities"""
        tasks = []

        for entity in entities:
            for enrichment_type in enrichment_types:
                if enrichment_type in ["sanctions"]:
                    tasks.append(self._enrich_sanctions(entity))
                elif enrichment_type in ["contracts"]:
                    tasks.append(self._enrich_contracts(entity))
                elif enrichment_type in ["patents"]:
                    tasks.append(self._enrich_patents(entity))
                elif enrichment_type in ["social"]:
                    tasks.append(self._enrich_social(entity))
                elif enrichment_type in ["financial"]:
                    tasks.append(self._enrich_financial(entity))
                elif enrichment_type in ["news"]:
                    tasks.append(self._enrich_news(entity))

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and flatten results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Enrichment task failed: {result}")
                self.enrichment_metrics["failed_requests"] += 1
            elif isinstance(result, list):
                valid_results.extend(result)
            elif result:
                valid_results.append(result)

        return valid_results

    async def _enrich_sanctions(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Check entity against sanctions lists"""
        results = []
        entity_id = entity.get("entity_id", "")
        entity_name = entity.get("name", "")

        if not entity_name:
            return results

        # Check OFAC SDN List
        ofac_result = await self._check_ofac_sanctions(entity_id, entity_name)
        if ofac_result:
            results.append(ofac_result)

        # Check EU sanctions
        eu_result = await self._check_eu_sanctions(entity_id, entity_name)
        if eu_result:
            results.append(eu_result)

        # Check UN sanctions
        un_result = await self._check_un_sanctions(entity_id, entity_name)
        if un_result:
            results.append(un_result)

        return results

    async def _check_ofac_sanctions(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check OFAC SDN list"""
        cache_key = f"ofac_{hashlib.md5(entity_name.encode()).hexdigest()}"

        # Check cache
        if self._is_cached(cache_key):
            self.enrichment_metrics["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            if cached_data:
                return EnrichmentResult(
                    entity_id=entity_id,
                    source_name="OFAC SDN List",
                    enrichment_type="sanctions",
                    data=cached_data,
                    confidence_score=1.0,
                    metadata={"cached": True},
                )
            return None

        try:
            # In a real implementation, this would call the OFAC API
            # For demonstration, we'll simulate a response
            is_sanctioned = await self._simulate_sanctions_check(entity_name)

            data = None
            if is_sanctioned:
                data = {
                    "sanctioned": True,
                    "list_name": "OFAC SDN",
                    "match_type": "name_match",
                    "entity_type": "individual",  # or 'entity'
                    "sanction_type": "blocking",
                    "effective_date": "2024-01-01",
                    "programs": ["SYRIA", "IRAN"],
                    "match_quality": 0.9,
                }

                result = EnrichmentResult(
                    entity_id=entity_id,
                    source_name="OFAC SDN List",
                    enrichment_type="sanctions",
                    data=data,
                    confidence_score=0.9,
                    metadata={"source_url": "https://ofac.treasury.gov/sdn-list"},
                )

                # Cache result
                self._cache_result(cache_key, data)
                self.enrichment_metrics["successful_enrichments"] += 1
                return result
            else:
                # Cache negative result
                self._cache_result(cache_key, None)
                return None

        except Exception as e:
            logger.error(f"OFAC sanctions check failed for {entity_name}: {e}")
            return None

    async def _check_eu_sanctions(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check EU sanctions list"""
        # Similar implementation to OFAC
        # For brevity, returning None (no match)
        return None

    async def _check_un_sanctions(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check UN sanctions list"""
        # Similar implementation to OFAC
        # For brevity, returning None (no match)
        return None

    async def _enrich_contracts(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Enrich with government contracts data"""
        results = []
        entity_id = entity.get("entity_id", "")
        entity_name = entity.get("name", "")

        if not entity_name:
            return results

        # Check USAspending.gov
        usa_result = await self._check_usa_spending(entity_id, entity_name)
        if usa_result:
            results.append(usa_result)

        return results

    async def _check_usa_spending(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check USAspending.gov for contracts"""
        cache_key = f"usaspending_{hashlib.md5(entity_name.encode()).hexdigest()}"

        if self._is_cached(cache_key):
            self.enrichment_metrics["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            if cached_data:
                return EnrichmentResult(
                    entity_id=entity_id,
                    source_name="USAspending.gov",
                    enrichment_type="contracts",
                    data=cached_data,
                    confidence_score=0.8,
                    metadata={"cached": True},
                )
            return None

        try:
            # Simulate contract data
            contracts_found = await self._simulate_contracts_check(entity_name)

            if contracts_found:
                data = {
                    "total_contracts": contracts_found["total"],
                    "total_value": contracts_found["total_value"],
                    "active_contracts": contracts_found["active"],
                    "agencies": contracts_found["agencies"],
                    "latest_contract_date": contracts_found["latest_date"],
                    "top_contract_types": contracts_found["types"],
                }

                result = EnrichmentResult(
                    entity_id=entity_id,
                    source_name="USAspending.gov",
                    enrichment_type="contracts",
                    data=data,
                    confidence_score=0.8,
                    metadata={"source_url": "https://usaspending.gov"},
                )

                self._cache_result(cache_key, data)
                self.enrichment_metrics["successful_enrichments"] += 1
                return result
            else:
                self._cache_result(cache_key, None)
                return None

        except Exception as e:
            logger.error(f"USAspending check failed for {entity_name}: {e}")
            return None

    async def _enrich_patents(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Enrich with patent data"""
        results = []
        entity_id = entity.get("entity_id", "")
        entity_name = entity.get("name", "")

        if not entity_name:
            return results

        # Check USPTO patents
        uspto_result = await self._check_uspto_patents(entity_id, entity_name)
        if uspto_result:
            results.append(uspto_result)

        return results

    async def _check_uspto_patents(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check USPTO for patents"""
        cache_key = f"uspto_{hashlib.md5(entity_name.encode()).hexdigest()}"

        if self._is_cached(cache_key):
            self.enrichment_metrics["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            if cached_data:
                return EnrichmentResult(
                    entity_id=entity_id,
                    source_name="USPTO Patents",
                    enrichment_type="patents",
                    data=cached_data,
                    confidence_score=0.8,
                    metadata={"cached": True},
                )
            return None

        try:
            # Simulate patent data
            patents_found = await self._simulate_patents_check(entity_name)

            if patents_found:
                data = {
                    "total_patents": patents_found["total"],
                    "active_patents": patents_found["active"],
                    "patent_categories": patents_found["categories"],
                    "latest_patent_date": patents_found["latest_date"],
                    "top_inventors": patents_found["inventors"],
                }

                result = EnrichmentResult(
                    entity_id=entity_id,
                    source_name="USPTO Patents",
                    enrichment_type="patents",
                    data=data,
                    confidence_score=0.8,
                    metadata={"source_url": "https://developer.uspto.gov"},
                )

                self._cache_result(cache_key, data)
                self.enrichment_metrics["successful_enrichments"] += 1
                return result
            else:
                self._cache_result(cache_key, None)
                return None

        except Exception as e:
            logger.error(f"USPTO patents check failed for {entity_name}: {e}")
            return None

    async def _enrich_social(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Enrich with social media profiles"""
        results = []

        # LinkedIn enrichment (if API key available)
        if self.sources["linkedin"].enabled:
            linkedin_result = await self._check_linkedin(entity)
            if linkedin_result:
                results.append(linkedin_result)

        return results

    async def _check_linkedin(
        self, entity: Dict[str, Any]
    ) -> Optional[EnrichmentResult]:
        """Check LinkedIn for company profiles"""
        # Implementation would use LinkedIn API
        # For demonstration purposes, returning None
        return None

    async def _enrich_financial(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Enrich with financial data"""
        results = []
        entity_id = entity.get("entity_id", "")
        entity_name = entity.get("name", "")

        if not entity_name:
            return results

        # Check SEC EDGAR
        sec_result = await self._check_sec_edgar(entity_id, entity_name)
        if sec_result:
            results.append(sec_result)

        return results

    async def _check_sec_edgar(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check SEC EDGAR for filings"""
        cache_key = f"sec_{hashlib.md5(entity_name.encode()).hexdigest()}"

        if self._is_cached(cache_key):
            self.enrichment_metrics["cache_hits"] += 1
            cached_data = self.cache[cache_key]["data"]
            if cached_data:
                return EnrichmentResult(
                    entity_id=entity_id,
                    source_name="SEC EDGAR",
                    enrichment_type="financial",
                    data=cached_data,
                    confidence_score=0.9,
                    metadata={"cached": True},
                )
            return None

        try:
            # Simulate SEC filing data
            filings_found = await self._simulate_sec_check(entity_name)

            if filings_found:
                data = {
                    "cik": filings_found["cik"],
                    "ticker": filings_found["ticker"],
                    "total_filings": filings_found["total_filings"],
                    "latest_10k": filings_found["latest_10k"],
                    "latest_10q": filings_found["latest_10q"],
                    "market_cap": filings_found["market_cap"],
                    "exchange": filings_found["exchange"],
                }

                result = EnrichmentResult(
                    entity_id=entity_id,
                    source_name="SEC EDGAR",
                    enrichment_type="financial",
                    data=data,
                    confidence_score=0.9,
                    metadata={"source_url": "https://data.sec.gov"},
                )

                self._cache_result(cache_key, data)
                self.enrichment_metrics["successful_enrichments"] += 1
                return result
            else:
                self._cache_result(cache_key, None)
                return None

        except Exception as e:
            logger.error(f"SEC EDGAR check failed for {entity_name}: {e}")
            return None

    async def _enrich_news(self, entity: Dict[str, Any]) -> List[EnrichmentResult]:
        """Enrich with news and media mentions"""
        if not self.sources["news_api"].enabled:
            return []

        results = []
        entity_id = entity.get("entity_id", "")
        entity_name = entity.get("name", "")

        if not entity_name:
            return results

        news_result = await self._check_news_mentions(entity_id, entity_name)
        if news_result:
            results.append(news_result)

        return results

    async def _check_news_mentions(
        self, entity_id: str, entity_name: str
    ) -> Optional[EnrichmentResult]:
        """Check for news mentions"""
        # Implementation would use News API or similar
        # For demonstration purposes, returning None
        return None

    # Simulation methods for demonstration
    async def _simulate_sanctions_check(self, entity_name: str) -> bool:
        """Simulate sanctions list check"""
        # Simulate some entities being on sanctions lists
        suspicious_names = ["sanctioned corp", "blocked entity", "restricted company"]
        return any(name.lower() in entity_name.lower() for name in suspicious_names)

    async def _simulate_contracts_check(self, entity_name: str) -> Optional[Dict]:
        """Simulate contracts check"""
        # Simulate finding contracts for some entities
        if "corp" in entity_name.lower() or "inc" in entity_name.lower():
            return {
                "total": 15,
                "total_value": 2500000,
                "active": 3,
                "agencies": ["DOD", "GSA", "NASA"],
                "latest_date": "2024-06-15",
                "types": ["IT Services", "Consulting", "Equipment"],
            }
        return None

    async def _simulate_patents_check(self, entity_name: str) -> Optional[Dict]:
        """Simulate patents check"""
        # Simulate finding patents for technology companies
        if any(
            word in entity_name.lower()
            for word in ["tech", "software", "systems", "solutions"]
        ):
            return {
                "total": 8,
                "active": 6,
                "categories": ["Computer Technology", "Software", "Telecommunications"],
                "latest_date": "2024-03-22",
                "inventors": ["John Smith", "Jane Doe", "Bob Johnson"],
            }
        return None

    async def _simulate_sec_check(self, entity_name: str) -> Optional[Dict]:
        """Simulate SEC filings check"""
        # Simulate finding SEC filings for public companies
        if any(word in entity_name.lower() for word in ["corporation", "inc.", "corp"]):
            return {
                "cik": "0001234567",
                "ticker": "ABCD",
                "total_filings": 45,
                "latest_10k": "2024-03-31",
                "latest_10q": "2024-06-30",
                "market_cap": 1500000000,
                "exchange": "NASDAQ",
            }
        return None

    # Utility methods
    def _is_cached(self, cache_key: str) -> bool:
        """Check if result is cached and still valid"""
        if cache_key not in self.cache:
            return False

        cache_entry = self.cache[cache_key]
        age = (datetime.utcnow() - cache_entry["timestamp"]).total_seconds()

        return age < self.cache_ttl

    def _cache_result(self, cache_key: str, data: Any):
        """Cache enrichment result"""
        self.cache[cache_key] = {"data": data, "timestamp": datetime.utcnow()}

    def get_enrichment_metrics(self) -> Dict[str, Any]:
        """Get enrichment performance metrics"""
        return self.enrichment_metrics.copy()

    def clear_cache(self):
        """Clear enrichment cache"""
        self.cache.clear()
        logger.info("Enrichment cache cleared")
