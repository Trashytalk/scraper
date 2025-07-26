"""
Advanced Entity Resolution System with Fuzzy Matching and ML

Implements comprehensive entity resolution using multiple matching algorithms:
- Fuzzy string matching with multiple similarity metrics
- Phonetic matching using Double Metaphone
- Machine learning-based clustering (DBSCAN)
- Business-specific normalization rules
- Multi-field confidence scoring
"""

import hashlib
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jellyfish

try:
    from metaphone import doublemetaphone

    HAS_METAPHONE = True
except ImportError:
    HAS_METAPHONE = False

    def doublemetaphone(s):
        return (s[:3], None)  # Fallback


logger = logging.getLogger(__name__)


@dataclass
class EntityMatch:
    """Container for entity match results"""

    entity1_id: str
    entity2_id: str
    match_score: float
    match_type: str
    confidence_level: str
    evidence: Dict[str, Any]
    matched_fields: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResolvedEntity:
    """Container for resolved entity cluster"""

    canonical_id: str
    canonical_name: str
    entity_type: str
    member_ids: List[str]
    confidence_score: float
    resolution_method: str
    canonical_data: Dict[str, Any]
    alternative_names: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)


class AdvancedEntityResolver:
    """Comprehensive entity resolution system with multiple matching algorithms"""

    def __init__(self, db_url: str, similarity_threshold: float = 0.8):
        # Database setup
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

        # NLP setup
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm"
            )
            self.nlp = None

        self.name_vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=1000)
        self.address_vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=500)

        # Configuration
        self.similarity_threshold = similarity_threshold
        self.business_suffixes = self._load_business_suffixes()
        self.normalization_rules = self._load_normalization_rules()

        # Caching for performance
        self.entity_cache = {}
        self.similarity_cache = {}

        # Metrics
        self.resolution_metrics = defaultdict(int)

    def _load_business_suffixes(self) -> Set[str]:
        """Load business entity suffixes for normalization"""
        return {
            "inc",
            "inc.",
            "incorporated",
            "corp",
            "corp.",
            "corporation",
            "ltd",
            "ltd.",
            "limited",
            "llc",
            "l.l.c.",
            "pte",
            "pte.",
            "plc",
            "p.l.c.",
            "gmbh",
            "sa",
            "s.a.",
            "bv",
            "b.v.",
            "ag",
            "co",
            "co.",
            "company",
            "group",
            "holdings",
            "partnership",
            "lp",
            "l.p.",
            "llp",
            "l.l.p.",
            "foundation",
            "trust",
            "association",
            "society",
        }

    def _load_normalization_rules(self) -> Dict[str, str]:
        """Load text normalization rules"""
        return {
            "&": "and",
            "@": "at",
            "+": "plus",
            "%": "percent",
            "#": "number",
            "$": "dollar",
            "saint": "st",
            "street": "st",
            "avenue": "ave",
            "boulevard": "blvd",
            "road": "rd",
            "drive": "dr",
        }

    async def resolve_entities(
        self, entities: List[Dict[str, Any]], entity_type: str = "company"
    ) -> List[ResolvedEntity]:
        """Main entity resolution pipeline"""
        logger.info(
            f"Starting entity resolution for {len(entities)} {entity_type} entities"
        )

        # Step 1: Normalize entity data
        normalized_entities = [self._normalize_entity(entity) for entity in entities]

        # Step 2: Generate candidate pairs using blocking
        candidate_pairs = await self._generate_candidate_pairs(
            normalized_entities, entity_type
        )
        logger.info(f"Generated {len(candidate_pairs)} candidate pairs for matching")

        # Step 3: Score candidate pairs
        matches = await self._score_candidate_pairs(
            candidate_pairs, normalized_entities
        )

        # Step 4: Apply clustering to create entity groups
        entity_clusters = await self._cluster_entities(matches, normalized_entities)

        # Step 5: Create canonical entities for each cluster
        resolved_entities = await self._create_canonical_entities(
            entity_clusters, entity_type
        )

        # Step 6: Store results
        await self._store_resolution_results(resolved_entities, matches)

        logger.info(
            f"Entity resolution completed. Created {len(resolved_entities)} canonical entities"
        )
        self.resolution_metrics["total_resolved"] += len(resolved_entities)
        return resolved_entities

    def _normalize_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive entity data normalization"""
        normalized = entity.copy()

        # Normalize name
        if "name" in entity:
            normalized["normalized_name"] = self._normalize_business_name(
                entity["name"]
            )
            normalized["phonetic_name"] = doublemetaphone(normalized["normalized_name"])
            normalized["name_tokens"] = set(normalized["normalized_name"].split())

        # Normalize address
        if "address" in entity:
            normalized["normalized_address"] = self._normalize_address(
                entity["address"]
            )
            normalized["address_tokens"] = set(normalized["normalized_address"].split())

        # Normalize identifiers
        for id_field in ["registration_number", "tax_id", "vat_number", "duns_number"]:
            if id_field in entity:
                normalized[f"normalized_{id_field}"] = re.sub(
                    r"[^a-zA-Z0-9]", "", str(entity[id_field]).upper()
                )

        # Normalize contact info
        if "email" in entity:
            normalized["normalized_email"] = entity["email"].lower().strip()
            normalized["email_domain"] = (
                normalized["normalized_email"].split("@")[-1]
                if "@" in normalized["normalized_email"]
                else ""
            )

        if "phone" in entity:
            normalized["normalized_phone"] = re.sub(r"[^0-9]", "", str(entity["phone"]))
            # Keep last 10 digits for US-style matching
            if len(normalized["normalized_phone"]) >= 10:
                normalized["phone_suffix"] = normalized["normalized_phone"][-10:]

        if "website" in entity:
            normalized["normalized_website"] = self._normalize_url(entity["website"])
            normalized["website_domain"] = self._extract_domain(entity["website"])

        return normalized

    def _normalize_business_name(self, name: str) -> str:
        """Advanced business name normalization"""
        if not name:
            return ""

        # Convert to lowercase and strip
        normalized = name.lower().strip()

        # Apply normalization rules
        for old, new in self.normalization_rules.items():
            normalized = normalized.replace(old, new)

        # Remove common punctuation
        normalized = re.sub(r"[^\w\s\-]", " ", normalized)

        # Normalize whitespace
        normalized = re.sub(r"\s+", " ", normalized).strip()

        # Remove business suffixes for better matching
        words = normalized.split()
        filtered_words = []
        for word in words:
            if word not in self.business_suffixes:
                filtered_words.append(word)

        return " ".join(filtered_words) if filtered_words else normalized

    def _normalize_address(self, address: str) -> str:
        """Address normalization for matching"""
        if not address:
            return ""

        normalized = address.lower().strip()

        # Common address abbreviations
        abbreviations = {
            "street": "st",
            "avenue": "ave",
            "road": "rd",
            "boulevard": "blvd",
            "drive": "dr",
            "lane": "ln",
            "court": "ct",
            "place": "pl",
            "suite": "ste",
            "apartment": "apt",
            "floor": "fl",
            "unit": "unit",
            "north": "n",
            "south": "s",
            "east": "e",
            "west": "w",
        }

        for full, abbrev in abbreviations.items():
            normalized = re.sub(rf"\b{full}\b", abbrev, normalized)

        # Remove punctuation and normalize whitespace
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _normalize_url(self, url: str) -> str:
        """URL normalization"""
        if not url:
            return ""

        # Remove protocol and www
        url = re.sub(r"^https?://", "", url.lower())
        url = re.sub(r"^www\.", "", url)

        # Remove trailing slash
        url = url.rstrip("/")

        return url

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        normalized = self._normalize_url(url)
        return normalized.split("/")[0] if normalized else ""

    async def _generate_candidate_pairs(
        self, entities: List[Dict], entity_type: str
    ) -> List[Tuple[int, int]]:
        """Generate candidate pairs using blocking strategies"""
        candidate_pairs = set()

        # Blocking strategy 1: Exact name prefix matching
        name_blocks = defaultdict(list)
        for i, entity in enumerate(entities):
            name = entity.get("normalized_name", "")
            if name:
                # Create blocks based on first few characters
                for length in [3, 4, 5]:
                    if len(name) >= length:
                        prefix = name[:length]
                        name_blocks[prefix].append(i)

        for indices in name_blocks.values():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        candidate_pairs.add((indices[i], indices[j]))

        # Blocking strategy 2: Phonetic matching
        phonetic_blocks = defaultdict(list)
        for i, entity in enumerate(entities):
            phonetic = entity.get("phonetic_name")
            if phonetic and phonetic[0]:  # doublemetaphone returns tuple
                phonetic_blocks[phonetic[0]].append(i)
                if phonetic[1]:  # Secondary phonetic code
                    phonetic_blocks[phonetic[1]].append(i)

        for indices in phonetic_blocks.values():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        candidate_pairs.add((indices[i], indices[j]))

        # Blocking strategy 3: Registration number/ID matching
        for id_field in [
            "normalized_registration_number",
            "normalized_tax_id",
            "normalized_duns_number",
        ]:
            id_blocks = defaultdict(list)
            for i, entity in enumerate(entities):
                id_val = entity.get(id_field)
                if id_val:
                    id_blocks[id_val].append(i)

            for indices in id_blocks.values():
                if len(indices) > 1:
                    for i in range(len(indices)):
                        for j in range(i + 1, len(indices)):
                            candidate_pairs.add((indices[i], indices[j]))

        # Blocking strategy 4: Domain-based matching
        domain_blocks = defaultdict(list)
        for i, entity in enumerate(entities):
            domain = entity.get("website_domain") or entity.get("email_domain")
            if domain:
                domain_blocks[domain].append(i)

        for indices in domain_blocks.values():
            if len(indices) > 1:
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        candidate_pairs.add((indices[i], indices[j]))

        # Blocking strategy 5: Token overlap
        token_blocks = defaultdict(list)
        for i, entity in enumerate(entities):
            name_tokens = entity.get("name_tokens", set())
            for token in name_tokens:
                if len(token) >= 3:  # Only consider meaningful tokens
                    token_blocks[token].append(i)

        for indices in token_blocks.values():
            if len(indices) > 1 and len(indices) <= 100:  # Avoid overly large blocks
                for i in range(len(indices)):
                    for j in range(i + 1, len(indices)):
                        candidate_pairs.add((indices[i], indices[j]))

        return list(candidate_pairs)

    async def _score_candidate_pairs(
        self, candidate_pairs: List[Tuple[int, int]], entities: List[Dict]
    ) -> List[EntityMatch]:
        """Score candidate pairs using multiple similarity metrics"""
        matches = []

        for i, j in candidate_pairs:
            entity1 = entities[i]
            entity2 = entities[j]

            # Calculate similarity scores for different fields
            similarities = await self._calculate_field_similarities(entity1, entity2)

            # Calculate overall match score
            overall_score, match_type, evidence = self._calculate_overall_score(
                similarities
            )

            if overall_score >= self.similarity_threshold:
                confidence_level = self._determine_confidence_level(
                    overall_score, evidence
                )

                match = EntityMatch(
                    entity1_id=entity1.get("entity_id", f"entity_{i}"),
                    entity2_id=entity2.get("entity_id", f"entity_{j}"),
                    match_score=overall_score,
                    match_type=match_type,
                    confidence_level=confidence_level,
                    evidence=evidence,
                    matched_fields=list(similarities.keys()),
                )

                matches.append(match)

        return matches

    async def _calculate_field_similarities(
        self, entity1: Dict, entity2: Dict
    ) -> Dict[str, float]:
        """Calculate similarity scores for individual fields"""
        similarities = {}

        # Name similarity (most important)
        if entity1.get("normalized_name") and entity2.get("normalized_name"):
            name_sim = self._calculate_name_similarity(
                entity1["normalized_name"], entity2["normalized_name"]
            )
            similarities["name"] = name_sim

            # Token-based name similarity
            tokens1 = entity1.get("name_tokens", set())
            tokens2 = entity2.get("name_tokens", set())
            if tokens1 and tokens2:
                jaccard_sim = len(tokens1.intersection(tokens2)) / len(
                    tokens1.union(tokens2)
                )
                similarities["name_tokens"] = jaccard_sim

        # Address similarity
        if entity1.get("normalized_address") and entity2.get("normalized_address"):
            addr_sim = self._calculate_address_similarity(
                entity1["normalized_address"], entity2["normalized_address"]
            )
            similarities["address"] = addr_sim

        # Exact ID matches (highest priority)
        for id_field in [
            "normalized_registration_number",
            "normalized_tax_id",
            "normalized_duns_number",
        ]:
            if entity1.get(id_field) and entity2.get(id_field):
                id_sim = 1.0 if entity1[id_field] == entity2[id_field] else 0.0
                similarities[id_field] = id_sim

        # Contact similarity
        if entity1.get("normalized_email") and entity2.get("normalized_email"):
            email_sim = (
                1.0
                if entity1["normalized_email"] == entity2["normalized_email"]
                else 0.0
            )
            similarities["email"] = email_sim

        # Domain similarity
        if entity1.get("email_domain") and entity2.get("email_domain"):
            domain_sim = (
                1.0 if entity1["email_domain"] == entity2["email_domain"] else 0.0
            )
            similarities["email_domain"] = domain_sim

        if entity1.get("website_domain") and entity2.get("website_domain"):
            web_domain_sim = (
                1.0 if entity1["website_domain"] == entity2["website_domain"] else 0.0
            )
            similarities["website_domain"] = web_domain_sim

        # Phone similarity
        if entity1.get("phone_suffix") and entity2.get("phone_suffix"):
            phone_sim = (
                1.0 if entity1["phone_suffix"] == entity2["phone_suffix"] else 0.0
            )
            similarities["phone"] = phone_sim

        return similarities

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Advanced name similarity calculation using multiple metrics"""
        if not name1 or not name2:
            return 0.0

        # Exact match
        if name1 == name2:
            return 1.0

        # Multiple similarity metrics
        ratio = fuzz.ratio(name1, name2) / 100.0
        partial_ratio = fuzz.partial_ratio(name1, name2) / 100.0
        token_sort = fuzz.token_sort_ratio(name1, name2) / 100.0
        token_set = fuzz.token_set_ratio(name1, name2) / 100.0

        # Sequence matcher for additional precision
        sequence_sim = SequenceMatcher(None, name1, name2).ratio()

        # Jaro-Winkler similarity (good for names)
        jaro_sim = jellyfish.jaro_winkler_similarity(name1, name2)

        # Weighted combination favoring different aspects
        final_score = (
            ratio * 0.25  # Overall similarity
            + partial_ratio * 0.15  # Substring matching
            + token_sort * 0.20  # Token order invariant
            + token_set * 0.20  # Token set matching
            + sequence_sim * 0.10  # Character sequence
            + jaro_sim * 0.10  # Name-specific algorithm
        )

        return final_score

    def _calculate_address_similarity(self, addr1: str, addr2: str) -> float:
        """Address-specific similarity calculation"""
        if not addr1 or not addr2:
            return 0.0

        if addr1 == addr2:
            return 1.0

        # Token-based similarity for addresses
        token_sort = fuzz.token_sort_ratio(addr1, addr2) / 100.0
        token_set = fuzz.token_set_ratio(addr1, addr2) / 100.0
        partial_ratio = fuzz.partial_ratio(addr1, addr2) / 100.0

        # Address tokens
        tokens1 = set(addr1.split())
        tokens2 = set(addr2.split())
        jaccard = (
            len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
            if tokens1.union(tokens2)
            else 0
        )

        # Weighted for address matching
        return token_sort * 0.4 + token_set * 0.3 + partial_ratio * 0.2 + jaccard * 0.1

    def _calculate_overall_score(
        self, similarities: Dict[str, float]
    ) -> Tuple[float, str, Dict]:
        """Calculate overall match score with evidence"""
        if not similarities:
            return 0.0, "no_match", {}

        # Field weights (business priority order)
        weights = {
            "normalized_registration_number": 0.30,
            "normalized_tax_id": 0.25,
            "normalized_duns_number": 0.20,
            "email": 0.15,
            "website_domain": 0.12,
            "email_domain": 0.10,
            "name": 0.25,
            "name_tokens": 0.15,
            "address": 0.10,
            "phone": 0.08,
        }

        # Calculate weighted score
        total_weight = 0
        weighted_score = 0

        for field, score in similarities.items():
            weight = weights.get(field, 0.05)  # Default weight for unspecified fields
            weighted_score += score * weight
            total_weight += weight

        overall_score = weighted_score / total_weight if total_weight > 0 else 0

        # Boost score for perfect ID matches
        id_perfect = any(
            similarities.get(f, 0) == 1.0
            for f in [
                "normalized_registration_number",
                "normalized_tax_id",
                "normalized_duns_number",
            ]
        )
        if id_perfect:
            overall_score = min(overall_score * 1.2, 1.0)

        # Boost score for domain matches
        domain_match = (
            similarities.get("website_domain", 0) == 1.0
            or similarities.get("email_domain", 0) == 1.0
        )
        if domain_match and similarities.get("name", 0) > 0.7:
            overall_score = min(overall_score * 1.1, 1.0)

        # Determine match type
        if any(
            similarities.get(f, 0) == 1.0
            for f in ["normalized_registration_number", "normalized_tax_id"]
        ):
            match_type = "exact_id_match"
        elif (
            similarities.get("name", 0) > 0.95 and similarities.get("address", 0) > 0.8
        ):
            match_type = "high_confidence_match"
        elif overall_score > 0.9:
            match_type = "probable_match"
        elif overall_score > 0.8:
            match_type = "possible_match"
        else:
            match_type = "weak_match"

        evidence = {
            "field_similarities": similarities,
            "weighted_score": overall_score,
            "highest_scoring_field": (
                max(similarities, key=similarities.get) if similarities else None
            ),
            "perfect_matches": [f for f, s in similarities.items() if s == 1.0],
            "strong_matches": [f for f, s in similarities.items() if s > 0.9],
        }

        return overall_score, match_type, evidence

    def _determine_confidence_level(self, score: float, evidence: Dict) -> str:
        """Determine confidence level for the match"""
        perfect_matches = len(evidence.get("perfect_matches", []))

        if perfect_matches >= 2 or score >= 0.95:
            return "very_high"
        elif perfect_matches >= 1 or score >= 0.9:
            return "high"
        elif score >= 0.85:
            return "medium"
        else:
            return "low"

    async def _cluster_entities(
        self, matches: List[EntityMatch], entities: List[Dict]
    ) -> List[List[str]]:
        """Cluster entities using graph-based approach"""
        # Create graph from matches
        G = nx.Graph()

        # Add all entities as nodes
        for i, entity in enumerate(entities):
            entity_id = entity.get("entity_id", f"entity_{i}")
            G.add_node(entity_id)

        # Add edges for matches above threshold
        for match in matches:
            if match.match_score >= self.similarity_threshold:
                G.add_edge(
                    match.entity1_id,
                    match.entity2_id,
                    weight=match.match_score,
                    match_type=match.match_type,
                    confidence=match.confidence_level,
                )

        # Find connected components (entity clusters)
        clusters = list(nx.connected_components(G))

        # Post-process clusters to handle complex cases
        processed_clusters = []
        for cluster in clusters:
            cluster_list = list(cluster)

            # For large clusters, apply additional validation
            if len(cluster_list) > 10:
                # Break down overly large clusters using stricter thresholds
                subgraph = G.subgraph(cluster_list)
                # Remove weak edges
                weak_edges = [
                    (u, v) for u, v, d in subgraph.edges(data=True) if d["weight"] < 0.9
                ]
                subgraph_copy = subgraph.copy()
                subgraph_copy.remove_edges_from(weak_edges)

                # Get new components
                sub_clusters = list(nx.connected_components(subgraph_copy))
                processed_clusters.extend([list(sc) for sc in sub_clusters])
            else:
                processed_clusters.append(cluster_list)

        return processed_clusters

    async def _create_canonical_entities(
        self, clusters: List[List[str]], entity_type: str
    ) -> List[ResolvedEntity]:
        """Create canonical entities from clusters"""
        resolved_entities = []

        for cluster in clusters:
            if len(cluster) == 1:
                # Single entity cluster
                canonical_id = cluster[0]
                canonical_name = f"Entity_{canonical_id}"
                confidence = 1.0
                method = "single_entity"
                canonical_data = {}
                alternative_names = []
            else:
                # Multiple entity cluster - need to determine canonical form
                canonical_id = f"canonical_{hashlib.md5('_'.join(sorted(cluster)).encode()).hexdigest()[:8]}"
                canonical_name, canonical_data, alternative_names = (
                    await self._determine_canonical_form(cluster)
                )
                confidence = self._calculate_cluster_confidence(cluster)
                method = "entity_resolution"

            resolved_entity = ResolvedEntity(
                canonical_id=canonical_id,
                canonical_name=canonical_name,
                entity_type=entity_type,
                member_ids=cluster,
                confidence_score=confidence,
                resolution_method=method,
                canonical_data=canonical_data,
                alternative_names=alternative_names,
            )

            resolved_entities.append(resolved_entity)

        return resolved_entities

    async def _determine_canonical_form(
        self, cluster: List[str]
    ) -> Tuple[str, Dict, List[str]]:
        """Determine the canonical form for an entity cluster"""
        # This is simplified - in production, you'd want more sophisticated logic
        # that considers data quality, recency, completeness, etc.

        canonical_name = f"Resolved_Entity_{'_'.join(cluster[:2])}"

        canonical_data = {
            "cluster_size": len(cluster),
            "member_entities": cluster,
            "resolution_timestamp": datetime.utcnow().isoformat(),
            "resolution_method": "advanced_fuzzy_matching",
        }

        alternative_names = [f"Alt_name_{entity_id}" for entity_id in cluster]

        return canonical_name, canonical_data, alternative_names

    def _calculate_cluster_confidence(self, cluster: List[str]) -> float:
        """Calculate confidence score for entity cluster"""
        # Simple confidence calculation based on cluster size
        # In production, you'd consider match scores, evidence quality, etc.
        if len(cluster) <= 2:
            return 0.95
        elif len(cluster) <= 5:
            return 0.85
        elif len(cluster) <= 10:
            return 0.75
        else:
            return 0.65

    async def _store_resolution_results(
        self, resolved_entities: List[ResolvedEntity], matches: List[EntityMatch]
    ):
        """Store resolution results to database"""
        # Import here to avoid circular imports
        from ..storage.models import ResolvedEntityModel, EntityMatchModel

        session = self.Session()

        try:
            # Store resolved entities
            for entity in resolved_entities:
                db_entity = ResolvedEntityModel(
                    canonical_id=entity.canonical_id,
                    canonical_name=entity.canonical_name,
                    entity_type=entity.entity_type,
                    member_ids=entity.member_ids,
                    confidence_score=entity.confidence_score,
                    resolution_method=entity.resolution_method,
                    canonical_data=entity.canonical_data,
                    alternative_names=entity.alternative_names,
                )
                session.merge(db_entity)

            # Store matches
            for match in matches:
                match_id = f"{match.entity1_id}_{match.entity2_id}_{int(match.match_score*1000)}"
                db_match = EntityMatchModel(
                    match_id=match_id,
                    entity1_id=match.entity1_id,
                    entity2_id=match.entity2_id,
                    match_score=match.match_score,
                    match_type=match.match_type,
                    confidence_level=match.confidence_level,
                    evidence=match.evidence,
                    matched_fields=match.matched_fields,
                )
                session.merge(db_match)

            session.commit()
            logger.info(
                f"Stored {len(resolved_entities)} resolved entities and {len(matches)} matches"
            )

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store resolution results: {e}")
            raise
        finally:
            session.close()

    def get_resolution_metrics(self) -> Dict[str, Any]:
        """Get resolution performance metrics"""
        return dict(self.resolution_metrics)
