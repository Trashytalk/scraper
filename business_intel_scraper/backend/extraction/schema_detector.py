"""
Schema Detection System with Confidence Scoring

This module automatically detects structured data patterns in web pages
and generates extraction schemas with confidence scores for reliable data extraction.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from collections import defaultdict, Counter

try:
    import numpy as np
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import lxml.html
    from lxml import etree

    ANALYSIS_AVAILABLE = True
except ImportError:
    ANALYSIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Data types for schema fields"""

    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    BOOLEAN = "boolean"
    LIST = "list"
    NESTED = "nested"


class FieldImportance(Enum):
    """Importance levels for detected fields"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    OPTIONAL = 5


@dataclass
class SchemaField:
    """Represents a field in the detected schema"""

    name: str
    data_type: DataType
    selector: str  # CSS or XPath selector
    importance: FieldImportance = FieldImportance.MEDIUM
    confidence: float = 0.0
    examples: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    optional: bool = False
    multiple: bool = False
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetectedSchema:
    """Complete schema for a page type"""

    schema_id: str
    name: str
    confidence: float
    fields: List[SchemaField]
    selectors: Dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    sample_urls: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    last_updated: float = field(default_factory=time.time)


class SchemaDetector:
    """
    Adaptive schema detector for business intelligence data extraction.

    Features:
    - Automatic schema detection from HTML structure
    - Machine learning-based field classification
    - Confidence scoring for extraction reliability
    - Template generation for consistent extraction
    - Schema evolution and refinement
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.detected_schemas: Dict[str, DetectedSchema] = {}
        self.field_patterns = self._compile_field_patterns()

        # ML components
        self.text_vectorizer: Optional[Any] = None
        self.schema_classifier: Optional[Any] = None

        # Configuration
        self.min_confidence = self.config.get("min_confidence", 0.6)
        self.min_examples = self.config.get("min_examples", 3)
        self.max_schemas = self.config.get("max_schemas", 100)

        logger.info(
            f"SchemaDetector initialized with analysis support: {ANALYSIS_AVAILABLE}"
        )

        if ANALYSIS_AVAILABLE:
            self._initialize_ml_components()

    def _initialize_ml_components(self) -> None:
        """Initialize ML components for schema analysis"""
        if not ANALYSIS_AVAILABLE:
            return

        self.text_vectorizer = TfidfVectorizer(
            max_features=500, stop_words="english", ngram_range=(1, 2), lowercase=True
        )

    def _compile_field_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile patterns for field type detection"""
        patterns = {
            DataType.EMAIL: [
                re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            ],
            DataType.PHONE: [
                re.compile(
                    r"\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b"
                ),
                re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
            ],
            DataType.URL: [
                re.compile(r'https?://[^\s<>"]{2,}', re.I),
                re.compile(r'www\.[^\s<>"]{2,}', re.I),
            ],
            DataType.DATE: [
                re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
                re.compile(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"),
                re.compile(
                    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b",
                    re.I,
                ),
            ],
            DataType.CURRENCY: [
                re.compile(r"\$[\d,]+\.?\d*"),
                re.compile(r"[\d,]+\.?\d*\s*(USD|EUR|GBP|JPY|CAD)", re.I),
            ],
            DataType.PERCENTAGE: [
                re.compile(r"\d+\.?\d*%"),
                re.compile(r"\d+\.?\d*\s*percent", re.I),
            ],
            DataType.NUMBER: [
                re.compile(r"\b\d+\.?\d*\b"),
            ],
        }
        return patterns

    def detect_schema(
        self,
        html_content: str,
        url: str,
        existing_schema: Optional[DetectedSchema] = None,
    ) -> Optional[DetectedSchema]:
        """Detect or refine schema from HTML content"""
        try:
            if not ANALYSIS_AVAILABLE:
                logger.warning("lxml not available, using simplified schema detection")
                return self._simple_schema_detection(html_content, url)

            # Parse HTML
            doc = lxml.html.fromstring(html_content)

            # Extract structural information
            structure = self._analyze_page_structure(doc)

            # Detect potential data fields
            fields = self._detect_data_fields(doc, url)

            if not fields:
                logger.debug(f"No data fields detected for {url}")
                return None

            # Generate schema
            schema = self._generate_schema(fields, structure, url, existing_schema)

            # Validate and score confidence
            schema.confidence = self._calculate_schema_confidence(schema, doc)

            if schema.confidence >= self.min_confidence:
                return schema
            else:
                logger.debug(f"Schema confidence too low: {schema.confidence}")
                return None

        except Exception as e:
            logger.error(f"Schema detection failed for {url}: {e}")
            return None

    def _simple_schema_detection(
        self, html_content: str, url: str
    ) -> Optional[DetectedSchema]:
        """Simplified schema detection without lxml"""
        try:
            # Basic regex-based detection for common business data
            fields = []

            # Company name detection
            name_patterns = [
                r"<h1[^>]*>([^<]+)</h1>",
                r"<title>([^<]+)</title>",
                r'<meta[^>]*name="company"[^>]*content="([^"]+)"',
            ]

            for pattern in name_patterns:
                matches = re.findall(pattern, html_content, re.I)
                if matches:
                    fields.append(
                        SchemaField(
                            name="company_name",
                            data_type=DataType.TEXT,
                            selector=pattern,
                            confidence=0.7,
                            examples=matches[:3],
                            importance=FieldImportance.CRITICAL,
                        )
                    )
                    break

            # Email detection
            email_matches = re.findall(
                self.field_patterns[DataType.EMAIL][0], html_content
            )
            if email_matches:
                fields.append(
                    SchemaField(
                        name="email",
                        data_type=DataType.EMAIL,
                        selector="email_pattern",
                        confidence=0.8,
                        examples=email_matches[:3],
                        importance=FieldImportance.HIGH,
                    )
                )

            # Phone detection
            for phone_pattern in self.field_patterns[DataType.PHONE]:
                phone_matches = re.findall(phone_pattern, html_content)
                if phone_matches:
                    fields.append(
                        SchemaField(
                            name="phone",
                            data_type=DataType.PHONE,
                            selector="phone_pattern",
                            confidence=0.8,
                            examples=phone_matches[:3],
                            importance=FieldImportance.HIGH,
                        )
                    )
                    break

            if fields:
                schema = DetectedSchema(
                    schema_id=f"simple_{hash(url) % 10000}",
                    name=f"Simple Schema for {self._extract_domain(url)}",
                    confidence=0.6,
                    fields=fields,
                    sample_urls=[url],
                )
                return schema

            return None

        except Exception as e:
            logger.error(f"Simple schema detection failed: {e}")
            return None

    def _analyze_page_structure(self, doc: Any) -> Dict[str, Any]:
        """Analyze the structural patterns of the page"""
        structure = {
            "has_tables": len(doc.xpath("//table")) > 0,
            "has_lists": len(doc.xpath("//ul | //ol")) > 0,
            "has_forms": len(doc.xpath("//form")) > 0,
            "heading_levels": len(doc.xpath("//h1 | //h2 | //h3 | //h4 | //h5 | //h6")),
            "div_count": len(doc.xpath("//div")),
            "span_count": len(doc.xpath("//span")),
            "p_count": len(doc.xpath("//p")),
            "script_count": len(doc.xpath("//script")),
        }

        # Detect common business page patterns
        structure.update(
            {
                "likely_contact_page": self._is_contact_page(doc),
                "likely_about_page": self._is_about_page(doc),
                "likely_product_page": self._is_product_page(doc),
                "likely_news_page": self._is_news_page(doc),
                "has_structured_data": self._has_structured_data(doc),
            }
        )

        return structure

    def _detect_data_fields(self, doc: Any, url: str) -> List[SchemaField]:
        """Detect potential data fields in the document"""
        fields = []

        # Text content analysis
        text_elements = doc.xpath("//p | //span | //div[not(*)] | //td | //th | //li")

        for element in text_elements:
            text = element.text_content().strip()
            if not text or len(text) < 3:
                continue

            # Classify text content
            field = self._classify_text_field(text, element)
            if field:
                fields.append(field)

        # Attribute analysis (meta tags, etc.)
        meta_fields = self._extract_meta_fields(doc)
        fields.extend(meta_fields)

        # Structured data analysis
        structured_fields = self._extract_structured_data(doc)
        fields.extend(structured_fields)

        # Deduplicate and merge similar fields
        fields = self._merge_similar_fields(fields)

        return fields

    def _classify_text_field(self, text: str, element: Any) -> Optional[SchemaField]:
        """Classify a text field based on content and context"""
        # Get element context
        tag_name = element.tag.lower()
        class_attr = element.get("class", "").lower()
        id_attr = element.get("id", "").lower()
        context = f"{tag_name} {class_attr} {id_attr}".strip()

        # Pattern matching for data types
        for data_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    field_name = self._infer_field_name(data_type, context, text)
                    selector = self._generate_selector(element)

                    return SchemaField(
                        name=field_name,
                        data_type=data_type,
                        selector=selector,
                        confidence=0.7,
                        examples=[text],
                        importance=self._determine_importance(data_type, context),
                    )

        # Business-specific field detection
        business_field = self._detect_business_field(text, context, element)
        if business_field:
            return business_field

        return None

    def _detect_business_field(
        self, text: str, context: str, element: Any
    ) -> Optional[SchemaField]:
        """Detect business-specific fields"""
        text_lower = text.lower()
        context_lower = context.lower()

        # Company name detection
        if (
            any(
                keyword in context_lower
                for keyword in ["company", "name", "title", "brand"]
            )
            and len(text.split()) <= 5
            and len(text) > 3
        ):
            return SchemaField(
                name="company_name",
                data_type=DataType.TEXT,
                selector=self._generate_selector(element),
                confidence=0.8,
                examples=[text],
                importance=FieldImportance.CRITICAL,
            )

        # Address detection
        if any(
            keyword in text_lower
            for keyword in ["street", "ave", "road", "blvd", "suite"]
        ) or any(keyword in context_lower for keyword in ["address", "location"]):
            return SchemaField(
                name="address",
                data_type=DataType.ADDRESS,
                selector=self._generate_selector(element),
                confidence=0.7,
                examples=[text],
                importance=FieldImportance.HIGH,
            )

        # Industry/business type
        if any(
            keyword in context_lower
            for keyword in ["industry", "sector", "business", "category"]
        ):
            return SchemaField(
                name="industry",
                data_type=DataType.TEXT,
                selector=self._generate_selector(element),
                confidence=0.6,
                examples=[text],
                importance=FieldImportance.MEDIUM,
            )

        # Description/about text
        if len(text) > 50 and any(
            keyword in context_lower
            for keyword in ["description", "about", "overview", "summary"]
        ):
            return SchemaField(
                name="description",
                data_type=DataType.TEXT,
                selector=self._generate_selector(element),
                confidence=0.6,
                examples=[text[:100] + "..." if len(text) > 100 else text],
                importance=FieldImportance.MEDIUM,
            )

        return None

    def _generate_selector(self, element: Any) -> str:
        """Generate CSS selector for element"""
        try:
            # Build selector path
            path = []
            current = element

            while current is not None and current.tag != "html":
                tag = current.tag.lower()

                # Add class if available
                class_attr = current.get("class")
                if class_attr:
                    classes = class_attr.split()
                    if classes:
                        tag += f".{classes[0]}"

                # Add ID if available
                id_attr = current.get("id")
                if id_attr:
                    tag += f"#{id_attr}"

                path.insert(0, tag)
                current = current.getparent()

                # Limit depth
                if len(path) >= 5:
                    break

            return " > ".join(path) if path else "unknown"

        except Exception as e:
            logger.error(f"Selector generation failed: {e}")
            return "unknown"

    def _extract_meta_fields(self, doc: Any) -> List[SchemaField]:
        """Extract fields from meta tags and structured attributes"""
        fields = []

        try:
            # Meta tags
            meta_tags = doc.xpath("//meta[@name or @property]")
            for meta in meta_tags:
                name = meta.get("name") or meta.get("property", "")
                content = meta.get("content", "")

                if content and any(
                    keyword in name.lower()
                    for keyword in [
                        "company",
                        "organization",
                        "business",
                        "title",
                        "description",
                    ]
                ):
                    field_name = name.lower().replace(":", "_")
                    fields.append(
                        SchemaField(
                            name=field_name,
                            data_type=DataType.TEXT,
                            selector=f'meta[name="{name}"]',
                            confidence=0.8,
                            examples=[content],
                            importance=FieldImportance.HIGH,
                        )
                    )

            # Microdata
            microdata = doc.xpath("//*[@itemtype or @itemscope]")
            for item in microdata:
                itemtype = item.get("itemtype", "")
                if "organization" in itemtype.lower() or "business" in itemtype.lower():
                    props = item.xpath(".//*[@itemprop]")
                    for prop in props:
                        prop_name = prop.get("itemprop", "")
                        prop_text = prop.text_content().strip()
                        if prop_text and prop_name:
                            fields.append(
                                SchemaField(
                                    name=prop_name,
                                    data_type=self._infer_data_type(prop_text),
                                    selector=f'[itemprop="{prop_name}"]',
                                    confidence=0.9,
                                    examples=[prop_text],
                                    importance=FieldImportance.HIGH,
                                )
                            )

        except Exception as e:
            logger.error(f"Meta field extraction failed: {e}")

        return fields

    def _extract_structured_data(self, doc: Any) -> List[SchemaField]:
        """Extract structured data (JSON-LD, RDFa)"""
        fields = []

        try:
            # JSON-LD scripts
            json_scripts = doc.xpath('//script[@type="application/ld+json"]')
            for script in json_scripts:
                try:
                    data = json.loads(script.text_content())
                    if isinstance(data, dict):
                        fields.extend(self._parse_json_ld(data))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                fields.extend(self._parse_json_ld(item))
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            logger.error(f"Structured data extraction failed: {e}")

        return fields

    def _parse_json_ld(self, data: Dict[str, Any]) -> List[SchemaField]:
        """Parse JSON-LD structured data"""
        fields = []

        # Common schema.org types for business data
        business_fields = {
            "name": ("company_name", DataType.TEXT, FieldImportance.CRITICAL),
            "description": ("description", DataType.TEXT, FieldImportance.MEDIUM),
            "email": ("email", DataType.EMAIL, FieldImportance.HIGH),
            "telephone": ("phone", DataType.PHONE, FieldImportance.HIGH),
            "address": ("address", DataType.ADDRESS, FieldImportance.HIGH),
            "url": ("website", DataType.URL, FieldImportance.MEDIUM),
            "industry": ("industry", DataType.TEXT, FieldImportance.MEDIUM),
        }

        for key, value in data.items():
            if key.startswith("@"):
                continue

            if key in business_fields and value:
                field_name, data_type, importance = business_fields[key]

                # Handle nested objects
                if isinstance(value, dict):
                    if "name" in value:
                        value = value["name"]
                    else:
                        continue
                elif isinstance(value, list):
                    value = value[0] if value else None

                if value:
                    fields.append(
                        SchemaField(
                            name=field_name,
                            data_type=data_type,
                            selector=f"json-ld:{key}",
                            confidence=0.95,
                            examples=[str(value)],
                            importance=importance,
                        )
                    )

        return fields

    def _merge_similar_fields(self, fields: List[SchemaField]) -> List[SchemaField]:
        """Merge similar fields to avoid duplicates"""
        if not fields:
            return fields

        merged = []
        field_groups = defaultdict(list)

        # Group fields by name and type
        for field in fields:
            key = (field.name, field.data_type)
            field_groups[key].append(field)

        # Merge each group
        for (name, data_type), group in field_groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Merge multiple fields of same type
                best_field = max(group, key=lambda f: f.confidence)
                best_field.examples = list(set(sum([f.examples for f in group], [])))[
                    :5
                ]
                best_field.confidence = max(f.confidence for f in group)
                merged.append(best_field)

        return merged

    def _generate_schema(
        self,
        fields: List[SchemaField],
        structure: Dict[str, Any],
        url: str,
        existing_schema: Optional[DetectedSchema] = None,
    ) -> DetectedSchema:
        """Generate complete schema from detected fields"""

        if existing_schema:
            # Update existing schema
            schema_id = existing_schema.schema_id
            schema_name = existing_schema.name
            sample_urls = existing_schema.sample_urls + [url]
        else:
            # Create new schema
            domain = self._extract_domain(url)
            schema_id = f"schema_{hash(url) % 10000}_{int(time.time())}"

            # Infer schema name from structure and fields
            if structure.get("likely_contact_page"):
                schema_name = f"Contact Page - {domain}"
            elif structure.get("likely_about_page"):
                schema_name = f"About Page - {domain}"
            elif structure.get("likely_product_page"):
                schema_name = f"Product Page - {domain}"
            elif structure.get("likely_news_page"):
                schema_name = f"News Page - {domain}"
            else:
                schema_name = f"Business Page - {domain}"

            sample_urls = [url]

        # Sort fields by importance
        fields.sort(key=lambda f: f.importance.value)

        return DetectedSchema(
            schema_id=schema_id,
            name=schema_name,
            confidence=0.0,  # Will be calculated separately
            fields=fields,
            sample_urls=sample_urls,
        )

    def _calculate_schema_confidence(self, schema: DetectedSchema, doc: Any) -> float:
        """Calculate confidence score for the schema"""
        if not schema.fields:
            return 0.0

        # Base confidence from field confidences
        field_confidences = [f.confidence for f in schema.fields]
        base_confidence = np.mean(field_confidences)

        # Bonus for critical fields
        critical_fields = sum(
            1 for f in schema.fields if f.importance == FieldImportance.CRITICAL
        )
        critical_bonus = min(critical_fields * 0.1, 0.3)

        # Bonus for structured data
        structured_fields = sum(1 for f in schema.fields if "json-ld" in f.selector)
        structured_bonus = min(structured_fields * 0.05, 0.2)

        # Penalty for too few fields
        field_count_penalty = 0.0
        if len(schema.fields) < 3:
            field_count_penalty = 0.2

        final_confidence = (
            base_confidence + critical_bonus + structured_bonus - field_count_penalty
        )
        return max(0.0, min(1.0, final_confidence))

    def _is_contact_page(self, doc: Any) -> bool:
        """Check if page appears to be a contact page"""
        text = doc.text_content().lower()
        title = doc.xpath("//title/text()")
        title_text = title[0].lower() if title else ""

        contact_indicators = [
            "contact",
            "phone",
            "email",
            "address",
            "location",
            "reach us",
        ]
        return any(
            indicator in text or indicator in title_text
            for indicator in contact_indicators
        )

    def _is_about_page(self, doc: Any) -> bool:
        """Check if page appears to be an about page"""
        text = doc.text_content().lower()
        title = doc.xpath("//title/text()")
        title_text = title[0].lower() if title else ""

        about_indicators = [
            "about",
            "company",
            "history",
            "mission",
            "vision",
            "team",
            "leadership",
        ]
        return any(indicator in title_text for indicator in about_indicators)

    def _is_product_page(self, doc: Any) -> bool:
        """Check if page appears to be a product page"""
        text = doc.text_content().lower()
        return any(
            indicator in text
            for indicator in ["product", "service", "solution", "offering"]
        )

    def _is_news_page(self, doc: Any) -> bool:
        """Check if page appears to be a news page"""
        text = doc.text_content().lower()
        title = doc.xpath("//title/text()")
        title_text = title[0].lower() if title else ""

        news_indicators = ["news", "press", "announcement", "media", "blog"]
        return any(indicator in title_text for indicator in news_indicators)

    def _has_structured_data(self, doc: Any) -> bool:
        """Check if page has structured data markup"""
        return (
            len(doc.xpath('//script[@type="application/ld+json"]')) > 0
            or len(doc.xpath("//*[@itemtype or @itemscope]")) > 0
            or len(doc.xpath("//*[@typeof]")) > 0
        )

    def _infer_field_name(self, data_type: DataType, context: str, text: str) -> str:
        """Infer appropriate field name based on type and context"""
        context_lower = context.lower()

        if data_type == DataType.EMAIL:
            return "email"
        elif data_type == DataType.PHONE:
            return "phone"
        elif data_type == DataType.URL:
            if "social" in context_lower:
                return "social_media_url"
            else:
                return "website_url"
        elif data_type == DataType.DATE:
            if "founded" in context_lower or "established" in context_lower:
                return "founded_date"
            else:
                return "date"
        elif data_type == DataType.CURRENCY:
            if "revenue" in context_lower:
                return "revenue"
            elif "price" in context_lower:
                return "price"
            else:
                return "amount"
        else:
            return data_type.value

    def _infer_data_type(self, text: str) -> DataType:
        """Infer data type from text content"""
        for data_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return data_type
        return DataType.TEXT

    def _determine_importance(
        self, data_type: DataType, context: str
    ) -> FieldImportance:
        """Determine field importance based on type and context"""
        context_lower = context.lower()

        # Critical business fields
        if data_type == DataType.TEXT and any(
            keyword in context_lower for keyword in ["name", "title", "company"]
        ):
            return FieldImportance.CRITICAL

        # High importance fields
        if data_type in [DataType.EMAIL, DataType.PHONE, DataType.ADDRESS]:
            return FieldImportance.HIGH

        # Medium importance fields
        if data_type in [DataType.URL, DataType.DATE, DataType.CURRENCY]:
            return FieldImportance.MEDIUM

        return FieldImportance.LOW

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse

            return urlparse(url).netloc
        except:
            return "unknown"

    def save_schema(
        self, schema: DetectedSchema, filepath: Optional[str] = None
    ) -> bool:
        """Save schema to file"""
        try:
            if not filepath:
                schema_dir = Path(self.config.get("schema_dir", "data/schemas"))
                schema_dir.mkdir(parents=True, exist_ok=True)
                filepath = schema_dir / f"{schema.schema_id}.json"

            schema_data = {
                "schema_id": schema.schema_id,
                "name": schema.name,
                "confidence": schema.confidence,
                "created_at": schema.created_at,
                "last_updated": schema.last_updated,
                "sample_urls": schema.sample_urls,
                "success_rate": schema.success_rate,
                "fields": [
                    {
                        "name": field.name,
                        "data_type": field.data_type.value,
                        "selector": field.selector,
                        "importance": field.importance.value,
                        "confidence": field.confidence,
                        "examples": field.examples,
                        "patterns": field.patterns,
                        "optional": field.optional,
                        "multiple": field.multiple,
                        "validation_rules": field.validation_rules,
                    }
                    for field in schema.fields
                ],
            }

            with open(filepath, "w") as f:
                json.dump(schema_data, f, indent=2)

            # Store in memory
            self.detected_schemas[schema.schema_id] = schema

            logger.info(f"Saved schema {schema.schema_id} to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save schema: {e}")
            return False

    def load_schema(self, filepath: str) -> Optional[DetectedSchema]:
        """Load schema from file"""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            fields = []
            for field_data in data.get("fields", []):
                field = SchemaField(
                    name=field_data["name"],
                    data_type=DataType(field_data["data_type"]),
                    selector=field_data["selector"],
                    importance=FieldImportance(field_data["importance"]),
                    confidence=field_data["confidence"],
                    examples=field_data.get("examples", []),
                    patterns=field_data.get("patterns", []),
                    optional=field_data.get("optional", False),
                    multiple=field_data.get("multiple", False),
                    validation_rules=field_data.get("validation_rules", {}),
                )
                fields.append(field)

            schema = DetectedSchema(
                schema_id=data["schema_id"],
                name=data["name"],
                confidence=data["confidence"],
                fields=fields,
                created_at=data.get("created_at", time.time()),
                last_updated=data.get("last_updated", time.time()),
                sample_urls=data.get("sample_urls", []),
                success_rate=data.get("success_rate", 0.0),
            )

            self.detected_schemas[schema.schema_id] = schema
            logger.info(f"Loaded schema {schema.schema_id}")
            return schema

        except Exception as e:
            logger.error(f"Failed to load schema from {filepath}: {e}")
            return None

    def get_detector_stats(self) -> Dict[str, Any]:
        """Get detector statistics"""
        return {
            "analysis_available": ANALYSIS_AVAILABLE,
            "total_schemas": len(self.detected_schemas),
            "min_confidence": self.min_confidence,
            "schemas_by_confidence": {
                "high": sum(
                    1 for s in self.detected_schemas.values() if s.confidence >= 0.8
                ),
                "medium": sum(
                    1
                    for s in self.detected_schemas.values()
                    if 0.6 <= s.confidence < 0.8
                ),
                "low": sum(
                    1 for s in self.detected_schemas.values() if s.confidence < 0.6
                ),
            },
            "field_types": dict(
                Counter(
                    field.data_type.value
                    for schema in self.detected_schemas.values()
                    for field in schema.fields
                )
            ),
            "avg_fields_per_schema": (
                np.mean(
                    [len(schema.fields) for schema in self.detected_schemas.values()]
                )
                if self.detected_schemas
                else 0.0
            ),
        }
