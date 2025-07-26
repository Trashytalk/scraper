"""
Multi-Language Named Entity Recognition Module

Provides language-specific NER capabilities for extracting business entities
from text in various languages and scripts.
"""

from __future__ import annotations

import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .core import LanguageInfo, DetectedText, language_detector

# NLP Libraries
try:
    import spacy

    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    import stanza

    HAS_STANZA = True
except ImportError:
    HAS_STANZA = False

try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from flair.data import Sentence
    from flair.models import SequenceTagger

    HAS_FLAIR = True
except ImportError:
    HAS_FLAIR = False

logger = logging.getLogger(__name__)


@dataclass
class MultiLangEntity:
    """Multi-language entity with additional metadata"""

    text: str
    label: str
    start: int
    end: int
    confidence: float
    language: LanguageInfo
    original_text: Optional[str] = None  # Original before transliteration
    transliteration: Optional[str] = None  # Transliterated version
    translation: Optional[str] = None  # Translated version
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseNERExtractor:
    """Base class for language-specific NER extractors"""

    def __init__(self, language: LanguageInfo):
        self.language = language
        self.business_entity_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for business entities"""
        patterns = {}

        # Email patterns (universal)
        patterns["email"] = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
        )

        # URL patterns (universal)
        patterns["url"] = re.compile(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            re.IGNORECASE,
        )

        # Phone patterns (international)
        patterns["phone"] = re.compile(
            r"(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})|\+\d{1,3}[-.\s]?\d{1,14}",
            re.IGNORECASE,
        )

        return patterns

    def extract_pattern_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract entities using regex patterns"""
        entities = []

        for label, pattern in self.business_entity_patterns.items():
            for match in pattern.finditer(text):
                entity = MultiLangEntity(
                    text=match.group(),
                    label=label.upper(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,  # High confidence for pattern matches
                    language=self.language,
                    metadata={"extraction_method": "pattern"},
                )
                entities.append(entity)

        return entities

    def extract_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract entities from text - to be overridden by subclasses"""
        return self.extract_pattern_entities(text)


class SpacyNERExtractor(BaseNERExtractor):
    """spaCy-based NER extractor"""

    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.nlp_model = None
        self.business_labels = {
            "ORG",
            "PERSON",
            "GPE",
            "MONEY",
            "PERCENT",
            "DATE",
            "FAC",
            "PRODUCT",
        }
        self._initialize_model()

    def _initialize_model(self):
        """Initialize spaCy model"""
        if not HAS_SPACY:
            return

        if self.language.spacy_model:
            try:
                self.nlp_model = spacy.load(self.language.spacy_model)
                logger.info(f"Initialized spaCy NER for {self.language.name}")
            except Exception as e:
                logger.warning(
                    f"Failed to load spaCy model {self.language.spacy_model}: {e}"
                )
                try:
                    # Try multilingual model
                    self.nlp_model = spacy.load("xx_ent_wiki_sm")
                except Exception:
                    logger.warning(f"No spaCy model available for {self.language.name}")

    def extract_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract entities using spaCy"""
        entities = []

        # Pattern-based entities first
        entities.extend(self.extract_pattern_entities(text))

        if not self.nlp_model or not text:
            return entities

        try:
            doc = self.nlp_model(text)

            for ent in doc.ents:
                # Filter for business-relevant entities
                if ent.label_ in self.business_labels:
                    entity = MultiLangEntity(
                        text=ent.text,
                        label=ent.label_,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=0.8,  # spaCy doesn't provide confidence scores directly
                        language=self.language,
                        metadata={
                            "extraction_method": "spacy",
                            "spacy_kb_id": (
                                ent.kb_id_ if hasattr(ent, "kb_id_") else None
                            ),
                        },
                    )
                    entities.append(entity)

        except Exception as e:
            logger.error(f"spaCy NER extraction failed for {self.language.name}: {e}")

        return entities


class StanzaNERExtractor(BaseNERExtractor):
    """Stanza-based NER extractor"""

    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.nlp_pipeline = None
        self.business_labels = {"ORG", "PER", "LOC", "MISC"}
        self._initialize_pipeline()

    def _initialize_pipeline(self):
        """Initialize Stanza pipeline"""
        if not HAS_STANZA or not self.language.stanza_model:
            return

        try:
            self.nlp_pipeline = stanza.Pipeline(
                self.language.stanza_model,
                processors="tokenize,ner",
                verbose=False,
                download_method=None,
            )
            logger.info(f"Initialized Stanza NER for {self.language.name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Stanza for {self.language.name}: {e}")

    def extract_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract entities using Stanza"""
        entities = []

        # Pattern-based entities first
        entities.extend(self.extract_pattern_entities(text))

        if not self.nlp_pipeline or not text:
            return entities

        try:
            doc = self.nlp_pipeline(text)

            for sentence in doc.sentences:
                for entity in sentence.ents:
                    if entity.type in self.business_labels:
                        # Calculate character positions
                        start_char = sentence.tokens[entity.start_token].start_char
                        end_char = sentence.tokens[entity.end_token - 1].end_char

                        multilang_entity = MultiLangEntity(
                            text=entity.text,
                            label=entity.type,
                            start=start_char,
                            end=end_char,
                            confidence=0.8,  # Stanza doesn't provide confidence directly
                            language=self.language,
                            metadata={"extraction_method": "stanza"},
                        )
                        entities.append(multilang_entity)

        except Exception as e:
            logger.error(f"Stanza NER extraction failed for {self.language.name}: {e}")

        return entities


class TransformersNERExtractor(BaseNERExtractor):
    """Transformers-based NER extractor using multilingual BERT models"""

    def __init__(self, language: LanguageInfo):
        super().__init__(language)
        self.ner_pipeline = None
        self.model_name = self._get_model_name()
        self._initialize_pipeline()

    def _get_model_name(self) -> str:
        """Get appropriate model name for language"""
        # Language-specific models
        model_mapping = {
            "zh": "ckiplab/bert-base-chinese-ner",
            "ja": "cl-tohoku/bert-base-japanese-whole-word-masking",
            "ar": "CAMeL-Lab/bert-base-arabic-camelbert-da-ner",
            "ru": "DeepPavlov/rubert-base-cased-sentence",
            "de": "dbmdz/bert-base-german-cased",
            "fr": "dbmdz/bert-base-french-europeana-cased",
            "es": "dccuchile/bert-base-spanish-wwm-cased",
        }

        if self.language.code in model_mapping:
            return model_mapping[self.language.code]
        else:
            # Fallback to multilingual BERT
            return "bert-base-multilingual-cased"

    def _initialize_pipeline(self):
        """Initialize Transformers NER pipeline"""
        if not HAS_TRANSFORMERS:
            return

        try:
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model_name,
                tokenizer=self.model_name,
                aggregation_strategy="simple",
                device=-1,  # Use CPU
            )
            logger.info(
                f"Initialized Transformers NER for {self.language.name} using {self.model_name}"
            )
        except Exception as e:
            logger.warning(
                f"Failed to initialize Transformers NER for {self.language.name}: {e}"
            )

    def extract_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract entities using Transformers"""
        entities = []

        # Pattern-based entities first
        entities.extend(self.extract_pattern_entities(text))

        if not self.ner_pipeline or not text:
            return entities

        try:
            # Truncate text if too long for model
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]

            ner_results = self.ner_pipeline(text)

            for result in ner_results:
                entity = MultiLangEntity(
                    text=result["word"],
                    label=result["entity_group"],
                    start=result["start"],
                    end=result["end"],
                    confidence=float(result["score"]),
                    language=self.language,
                    metadata={
                        "extraction_method": "transformers",
                        "model": self.model_name,
                    },
                )
                entities.append(entity)

        except Exception as e:
            logger.error(
                f"Transformers NER extraction failed for {self.language.name}: {e}"
            )

        return entities


class BusinessEntityExtractor:
    """Specialized extractor for business-specific entities"""

    def __init__(self, language: LanguageInfo):
        self.language = language
        self.patterns = self._initialize_business_patterns()

    def _initialize_business_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize business-specific patterns by language"""
        patterns = {}

        # Universal patterns
        patterns["universal"] = {
            "company_suffix": {
                "en": re.compile(
                    r"\b(?:Inc|Corp|LLC|Ltd|Limited|Company|Co|Group|Holdings|International|Intl|Industries|Solutions|Services|Technologies|Systems|Enterprises|Associates)\b\.?",
                    re.IGNORECASE,
                ),
                "es": re.compile(
                    r"\b(?:S\.A\.|S\.L\.|S\.R\.L\.|Sociedad|Empresa|Compañía|Corporación|Grupo)\b\.?",
                    re.IGNORECASE,
                ),
                "fr": re.compile(
                    r"\b(?:S\.A\.|S\.A\.R\.L\.|S\.A\.S\.|Société|Entreprise|Compagnie|Corporation|Groupe)\b\.?",
                    re.IGNORECASE,
                ),
                "de": re.compile(
                    r"\b(?:GmbH|AG|KG|OHG|Gesellschaft|Unternehmen|Firma|Konzern|Gruppe)\b\.?",
                    re.IGNORECASE,
                ),
                "zh": re.compile(
                    r"(?:公司|企业|集团|有限公司|股份有限公司|责任有限公司)",
                    re.IGNORECASE,
                ),
                "ja": re.compile(
                    r"(?:株式会社|有限会社|合同会社|合名会社|合資会社|企業|会社)",
                    re.IGNORECASE,
                ),
                "ar": re.compile(
                    r"(?:شركة|مؤسسة|مجموعة|القابضة|محدودة|مساهمة)", re.IGNORECASE
                ),
                "ru": re.compile(
                    r"\b(?:ООО|ЗАО|ОАО|ИП|Общество|Компания|Корпорация|Группа|Холдинг)\b\.?",
                    re.IGNORECASE,
                ),
            }
        }

        # Registration number patterns
        patterns["registration"] = {
            "en": re.compile(
                r"\b(?:Tax ID|EIN|SSN|Registration|Reg|ID)[\s:]*([A-Z0-9-]{5,20})\b",
                re.IGNORECASE,
            ),
            "zh": re.compile(
                r"(?:统一社会信用代码|营业执照号码|组织机构代码)[\s:：]*([A-Z0-9]{10,20})"
            ),
            "ja": re.compile(r"(?:法人番号|会社番号|登記番号)[\s:：]*([0-9-]{10,15})"),
            "ar": re.compile(r"(?:رقم التسجيل|رقم الترخيص)[\s:]*([A-Z0-9-]{5,20})"),
        }

        # Address patterns
        patterns["address"] = {
            "en": re.compile(
                r"\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Place|Pl)(?:\s+[A-Za-z\s]+)?",
                re.IGNORECASE,
            ),
            "zh": re.compile(
                r"(?:[北上广深杭]?[市区县])?[^市区县]*?[市区县][^路街道]*?[路街道][^号]*?号?"
            ),
            "ja": re.compile(r"[都道府県市区町村][^都道府県市区町村]*?[町丁目番地号]"),
            "ar": re.compile(r"[شارع|طريق|شارع|منطقة|حي]\s+[^،。]+"),
        }

        return patterns

    def extract_business_entities(self, text: str) -> List[MultiLangEntity]:
        """Extract business-specific entities"""
        entities = []
        lang_code = self.language.code

        # Company suffixes
        if "company_suffix" in self.patterns.get("universal", {}):
            suffix_pattern = self.patterns["universal"]["company_suffix"].get(lang_code)
            if suffix_pattern:
                for match in suffix_pattern.finditer(text):
                    # Look for company name before suffix
                    start = max(0, match.start() - 50)
                    company_text = text[start : match.end()]

                    entity = MultiLangEntity(
                        text=company_text.strip(),
                        label="COMPANY_SUFFIX",
                        start=start,
                        end=match.end(),
                        confidence=0.9,
                        language=self.language,
                        metadata={"extraction_method": "business_pattern"},
                    )
                    entities.append(entity)

        # Registration numbers
        if lang_code in self.patterns.get("registration", {}):
            reg_pattern = self.patterns["registration"][lang_code]
            for match in reg_pattern.finditer(text):
                entity = MultiLangEntity(
                    text=match.group(),
                    label="REGISTRATION_NUMBER",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                    language=self.language,
                    metadata={"extraction_method": "business_pattern"},
                )
                entities.append(entity)

        # Addresses
        if lang_code in self.patterns.get("address", {}):
            addr_pattern = self.patterns["address"][lang_code]
            for match in addr_pattern.finditer(text):
                entity = MultiLangEntity(
                    text=match.group(),
                    label="ADDRESS",
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    language=self.language,
                    metadata={"extraction_method": "business_pattern"},
                )
                entities.append(entity)

        return entities


class MultiLanguageNER:
    """Main multi-language NER system"""

    def __init__(self):
        self.extractor_cache: Dict[str, List[BaseNERExtractor]] = {}
        self.confidence_threshold = 0.5

    def get_extractors(self, language: LanguageInfo) -> List[BaseNERExtractor]:
        """Get appropriate NER extractors for language"""
        cache_key = language.code

        if cache_key not in self.extractor_cache:
            extractors = []

            # Always add business entity extractor
            extractors.append(BusinessEntityExtractor(language))

            # Add spaCy extractor if available
            if HAS_SPACY and language.spacy_model:
                extractors.append(SpacyNERExtractor(language))

            # Add Stanza extractor if available
            if HAS_STANZA and language.stanza_model:
                extractors.append(StanzaNERExtractor(language))

            # Add Transformers extractor as fallback
            if HAS_TRANSFORMERS:
                extractors.append(TransformersNERExtractor(language))

            self.extractor_cache[cache_key] = extractors

        return self.extractor_cache[cache_key]

    def extract_entities(
        self, text: str, language: Optional[LanguageInfo] = None
    ) -> List[MultiLangEntity]:
        """Extract entities with automatic language detection"""
        if not text:
            return []

        if language is None:
            detected_text = language_detector.create_detected_text(text)
            language = detected_text.language

        all_entities = []
        extractors = self.get_extractors(language)

        for extractor in extractors:
            try:
                entities = extractor.extract_entities(text)
                all_entities.extend(entities)
            except Exception as e:
                logger.error(
                    f"Entity extraction failed with {type(extractor).__name__}: {e}"
                )

        # Filter by confidence and remove duplicates
        filtered_entities = self._filter_and_deduplicate(all_entities)

        return filtered_entities

    def extract_entities_mixed_language(
        self, detected_text: DetectedText
    ) -> Dict[str, List[MultiLangEntity]]:
        """Extract entities from mixed-language text"""
        results = {}

        if detected_text.segments:
            # Process each segment with its detected language
            for segment_text, segment_language in detected_text.segments:
                entities = self.extract_entities(segment_text, segment_language)
                if entities:
                    if segment_language.code not in results:
                        results[segment_language.code] = []
                    results[segment_language.code].extend(entities)
        else:
            # Process as single language
            entities = self.extract_entities(detected_text.text, detected_text.language)
            if entities:
                results[detected_text.language.code] = entities

        return results

    def _filter_and_deduplicate(
        self, entities: List[MultiLangEntity]
    ) -> List[MultiLangEntity]:
        """Filter entities by confidence and remove duplicates"""
        # Filter by confidence
        filtered = [e for e in entities if e.confidence >= self.confidence_threshold]

        # Remove duplicates (same text and label)
        seen = set()
        deduplicated = []

        for entity in filtered:
            key = (entity.text.lower(), entity.label)
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)

        # Sort by confidence (highest first)
        deduplicated.sort(key=lambda x: x.confidence, reverse=True)

        return deduplicated

    def extract_structured_entities(
        self, text: str, language: Optional[LanguageInfo] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract entities and return in structured format"""
        entities = self.extract_entities(text, language)

        structured = {}
        for entity in entities:
            if entity.label not in structured:
                structured[entity.label] = []

            structured[entity.label].append(
                {
                    "text": entity.text,
                    "start": entity.start,
                    "end": entity.end,
                    "confidence": entity.confidence,
                    "language": entity.language.code,
                    "original_text": entity.original_text,
                    "transliteration": entity.transliteration,
                    "translation": entity.translation,
                    "metadata": entity.metadata,
                }
            )

        return structured


# Global NER instance
multilang_ner = MultiLanguageNER()
