"""
Adaptive Link Classifier using RandomForest for Business Intelligence Scraping

This module implements intelligent link classification and prioritization using
machine learning to identify high-value targets for business intelligence gathering.
"""

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse
import pickle
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class LinkCategory(Enum):
    """Categories for link classification"""

    BUSINESS_PROFILE = "business_profile"
    FINANCIAL_DATA = "financial_data"
    COMPANY_NEWS = "company_news"
    REGULATORY_FILING = "regulatory_filing"
    CONTACT_INFO = "contact_info"
    PRODUCT_SERVICE = "product_service"
    PARTNERSHIP = "partnership"
    LEGAL_DOCUMENT = "legal_document"
    SOCIAL_MEDIA = "social_media"
    IRRELEVANT = "irrelevant"
    UNKNOWN = "unknown"


class LinkPriority(Enum):
    """Priority levels for link processing"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    IGNORE = 5


@dataclass
class LinkInfo:
    """Information about a discovered link"""

    url: str
    anchor_text: str
    category: LinkCategory = LinkCategory.UNKNOWN
    priority: LinkPriority = LinkPriority.MEDIUM
    confidence: float = 0.0
    features: Dict[str, Any] = None
    parent_url: str = ""
    depth: int = 0
    discovered_at: float = None

    def __post_init__(self):
        if self.features is None:
            self.features = {}
        if self.discovered_at is None:
            self.discovered_at = time.time()


class AdaptiveLinkClassifier:
    """
    ML-powered link classifier for intelligent business intelligence crawling.

    Features:
    - RandomForest classification for link categorization
    - TF-IDF vectorization of link text and context
    - Adaptive learning from crawl results
    - Priority scoring based on business intelligence value
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_trained = False

        # ML Components
        self.classifier: Optional[Any] = None
        self.text_vectorizer: Optional[Any] = None
        self.feature_scaler: Optional[Any] = None
        self.label_encoder: Optional[Any] = None

        # Training data
        self.training_links: List[LinkInfo] = []
        self.feedback_links: List[Tuple[LinkInfo, bool, float]] = (
            []
        )  # link, success, value

        # Feature extraction patterns
        self.business_patterns = self._compile_business_patterns()

        # Configuration
        self.min_training_samples = self.config.get("min_training_samples", 100)
        self.retrain_threshold = self.config.get("retrain_threshold", 500)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)

        logger.info(
            f"AdaptiveLinkClassifier initialized with ML support: {SKLEARN_AVAILABLE}"
        )

        if SKLEARN_AVAILABLE:
            self._initialize_ml_components()
            self._load_initial_training_data()

    def _initialize_ml_components(self) -> None:
        """Initialize machine learning components"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, disabling ML features")
            return

        self.classifier = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )

        self.text_vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 3), lowercase=True
        )

        self.feature_scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

        # Try to load existing model
        model_path = Path(
            self.config.get("model_path", "data/models/link_classifier.pkl")
        )
        if model_path.exists():
            self._load_model(model_path)

    def _compile_business_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for business intelligence content detection"""
        patterns = {
            "business_profile": [
                re.compile(r"\b(about|company|profile|overview|history)\b", re.I),
                re.compile(r"\b(leadership|management|team|board)\b", re.I),
                re.compile(r"\b(mission|vision|values)\b", re.I),
            ],
            "financial_data": [
                re.compile(r"\b(financial|earnings|revenue|profit|loss)\b", re.I),
                re.compile(r"\b(investor|shareholder|annual.report)\b", re.I),
                re.compile(r"\b(sec.filing|10-k|10-q|8-k)\b", re.I),
            ],
            "company_news": [
                re.compile(r"\b(news|press|announcement|media)\b", re.I),
                re.compile(r"\b(acquisition|merger|partnership)\b", re.I),
                re.compile(r"\b(expansion|launch|product)\b", re.I),
            ],
            "regulatory_filing": [
                re.compile(r"\b(filing|regulatory|compliance|sec)\b", re.I),
                re.compile(r"\b(form|document|submission)\b", re.I),
                re.compile(r"\b(license|permit|registration)\b", re.I),
            ],
            "contact_info": [
                re.compile(r"\b(contact|phone|email|address)\b", re.I),
                re.compile(r"\b(location|office|headquarters)\b", re.I),
                re.compile(r"\b(support|sales|inquiry)\b", re.I),
            ],
            "product_service": [
                re.compile(r"\b(product|service|solution|offering)\b", re.I),
                re.compile(r"\b(catalog|portfolio|suite)\b", re.I),
                re.compile(r"\b(feature|specification|detail)\b", re.I),
            ],
            "legal_document": [
                re.compile(r"\b(legal|terms|privacy|policy)\b", re.I),
                re.compile(r"\b(agreement|contract|license)\b", re.I),
                re.compile(r"\b(disclaimer|copyright|trademark)\b", re.I),
            ],
            "social_media": [
                re.compile(r"\b(facebook|twitter|linkedin|instagram)\b", re.I),
                re.compile(r"\b(social|follow|connect)\b", re.I),
            ],
        }
        return patterns

    def classify_link(
        self, url: str, anchor_text: str, parent_url: str = "", context: str = ""
    ) -> LinkInfo:
        """Classify a link and assign priority for business intelligence value"""
        link_info = LinkInfo(url=url, anchor_text=anchor_text, parent_url=parent_url)

        # Extract features
        features = self._extract_link_features(link_info, context)
        link_info.features = features

        if self.is_trained and SKLEARN_AVAILABLE:
            # Use ML classification
            category, confidence = self._ml_classify(features, anchor_text, url)
            link_info.category = category
            link_info.confidence = confidence
        else:
            # Use rule-based classification
            category, confidence = self._rule_based_classify(features, anchor_text, url)
            link_info.category = category
            link_info.confidence = confidence

        # Assign priority based on category and confidence
        link_info.priority = self._assign_priority(link_info.category, confidence)

        return link_info

    def classify_links_batch(self, links: List[Tuple[str, str, str]]) -> List[LinkInfo]:
        """Classify multiple links efficiently"""
        link_infos = []

        for url, anchor_text, parent_url in links:
            link_info = self.classify_link(url, anchor_text, parent_url)
            link_infos.append(link_info)

        # Sort by priority for efficient processing
        link_infos.sort(key=lambda x: x.priority.value)

        return link_infos

    def _extract_link_features(
        self, link_info: LinkInfo, context: str = ""
    ) -> Dict[str, Any]:
        """Extract features for link classification"""
        features = {}

        try:
            parsed_url = urlparse(link_info.url)

            # URL-based features
            features.update(
                {
                    "url_length": len(link_info.url),
                    "path_segments": len(parsed_url.path.split("/")),
                    "has_query": bool(parsed_url.query),
                    "has_fragment": bool(parsed_url.fragment),
                    "is_https": parsed_url.scheme == "https",
                    "subdomain_count": len(parsed_url.netloc.split(".")) - 2,
                }
            )

            # File extension features
            path_lower = parsed_url.path.lower()
            features.update(
                {
                    "is_pdf": path_lower.endswith(".pdf"),
                    "is_doc": path_lower.endswith((".doc", ".docx")),
                    "is_excel": path_lower.endswith((".xls", ".xlsx")),
                    "is_image": path_lower.endswith((".jpg", ".jpeg", ".png", ".gif")),
                    "is_html": path_lower.endswith((".html", ".htm"))
                    or not any(
                        path_lower.endswith(ext)
                        for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx"]
                    ),
                }
            )

            # Text-based features
            combined_text = (
                f"{link_info.anchor_text} {parsed_url.path} {context}".lower()
            )

            # Pattern matching scores
            for category, patterns in self.business_patterns.items():
                score = sum(1 for pattern in patterns if pattern.search(combined_text))
                features[f"{category}_score"] = (
                    score / len(patterns) if patterns else 0.0
                )

            # Anchor text features
            features.update(
                {
                    "anchor_length": len(link_info.anchor_text),
                    "anchor_words": len(link_info.anchor_text.split()),
                    "anchor_has_numbers": bool(re.search(r"\d", link_info.anchor_text)),
                    "anchor_all_caps": link_info.anchor_text.isupper(),
                }
            )

            # Domain-based features
            domain = parsed_url.netloc.lower()
            features.update(
                {
                    "is_gov_domain": domain.endswith(".gov"),
                    "is_edu_domain": domain.endswith(".edu"),
                    "is_org_domain": domain.endswith(".org"),
                    "is_com_domain": domain.endswith(".com"),
                    "domain_length": len(domain),
                }
            )

            return features

        except Exception as e:
            logger.error(f"Feature extraction failed for {link_info.url}: {e}")
            return {}

    def _ml_classify(
        self, features: Dict[str, Any], anchor_text: str, url: str
    ) -> Tuple[LinkCategory, float]:
        """Classify link using trained ML model"""
        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)
            text_features = self.text_vectorizer.transform([f"{anchor_text} {url}"])

            # Combine features
            if feature_vector is not None:
                combined_features = np.hstack(
                    [
                        self.feature_scaler.transform([feature_vector]),
                        text_features.toarray(),
                    ]
                )
            else:
                combined_features = text_features.toarray()

            # Predict
            prediction = self.classifier.predict(combined_features)[0]
            probabilities = self.classifier.predict_proba(combined_features)[0]
            confidence = max(probabilities)

            # Convert back to category
            category_str = self.label_encoder.inverse_transform([prediction])[0]
            category = LinkCategory(category_str)

            return category, confidence

        except Exception as e:
            logger.error(f"ML classification failed: {e}")
            return self._rule_based_classify(features, anchor_text, url)

    def _rule_based_classify(
        self, features: Dict[str, Any], anchor_text: str, url: str
    ) -> Tuple[LinkCategory, float]:
        """Classify link using rule-based approach"""
        scores = {}

        # Calculate category scores based on features
        for category in LinkCategory:
            if category == LinkCategory.UNKNOWN:
                continue

            score = features.get(f"{category.value}_score", 0.0)

            # Additional rule-based scoring
            if category == LinkCategory.BUSINESS_PROFILE:
                if features.get("is_html", False):
                    score += 0.2
                if "about" in url.lower() or "company" in url.lower():
                    score += 0.3

            elif category == LinkCategory.FINANCIAL_DATA:
                if features.get("is_pdf", False) or features.get("is_excel", False):
                    score += 0.3
                if "investor" in url.lower() or "financial" in url.lower():
                    score += 0.4

            elif category == LinkCategory.REGULATORY_FILING:
                if features.get("is_pdf", False) or features.get("is_doc", False):
                    score += 0.3
                if features.get("is_gov_domain", False):
                    score += 0.5

            # Add more rule-based logic as needed

            scores[category] = score

        # Find best category
        if not scores or max(scores.values()) < 0.1:
            return LinkCategory.UNKNOWN, 0.0

        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category], 1.0)

        return best_category, confidence

    def _assign_priority(
        self, category: LinkCategory, confidence: float
    ) -> LinkPriority:
        """Assign processing priority based on category and confidence"""
        # High-value categories for business intelligence
        high_value_categories = {
            LinkCategory.FINANCIAL_DATA,
            LinkCategory.REGULATORY_FILING,
            LinkCategory.BUSINESS_PROFILE,
        }

        medium_value_categories = {
            LinkCategory.COMPANY_NEWS,
            LinkCategory.PARTNERSHIP,
            LinkCategory.CONTACT_INFO,
        }

        if category in high_value_categories:
            if confidence >= 0.8:
                return LinkPriority.CRITICAL
            elif confidence >= 0.6:
                return LinkPriority.HIGH
            else:
                return LinkPriority.MEDIUM

        elif category in medium_value_categories:
            if confidence >= 0.8:
                return LinkPriority.HIGH
            elif confidence >= 0.6:
                return LinkPriority.MEDIUM
            else:
                return LinkPriority.LOW

        elif category == LinkCategory.IRRELEVANT:
            return LinkPriority.IGNORE

        else:
            return LinkPriority.LOW

    def add_training_data(
        self, link_info: LinkInfo, actual_category: LinkCategory
    ) -> None:
        """Add labeled training data for model improvement"""
        link_info.category = actual_category
        self.training_links.append(link_info)

        # Retrain if we have enough new samples
        if len(self.training_links) >= self.retrain_threshold:
            self._retrain_model()

    def add_feedback(
        self, link_info: LinkInfo, was_successful: bool, extracted_value: float
    ) -> None:
        """Add feedback about link processing results"""
        self.feedback_links.append((link_info, was_successful, extracted_value))

        # Use feedback to refine classification
        if len(self.feedback_links) >= 50:
            self._incorporate_feedback()

    def _prepare_feature_vector(
        self, features: Dict[str, Any]
    ) -> Optional[List[float]]:
        """Convert feature dictionary to vector for ML"""
        try:
            # Define expected feature order
            expected_features = [
                "url_length",
                "path_segments",
                "has_query",
                "has_fragment",
                "is_https",
                "subdomain_count",
                "is_pdf",
                "is_doc",
                "is_excel",
                "is_image",
                "is_html",
                "business_profile_score",
                "financial_data_score",
                "company_news_score",
                "regulatory_filing_score",
                "contact_info_score",
                "product_service_score",
                "legal_document_score",
                "social_media_score",
                "anchor_length",
                "anchor_words",
                "anchor_has_numbers",
                "anchor_all_caps",
                "is_gov_domain",
                "is_edu_domain",
                "is_org_domain",
                "is_com_domain",
                "domain_length",
            ]

            vector = []
            for feature_name in expected_features:
                value = features.get(feature_name, 0.0)
                # Convert boolean to float
                if isinstance(value, bool):
                    value = float(value)
                vector.append(value)

            return vector

        except Exception as e:
            logger.error(f"Feature vector preparation failed: {e}")
            return None

    def _load_initial_training_data(self) -> None:
        """Load initial training data from configuration or predefined samples"""
        # This would typically load from a file or database
        # For now, we'll use some predefined samples

        initial_samples = [
            ("https://company.com/about", "About Us", LinkCategory.BUSINESS_PROFILE),
            (
                "https://company.com/investors",
                "Investor Relations",
                LinkCategory.FINANCIAL_DATA,
            ),
            (
                "https://company.com/news/press-release",
                "Latest News",
                LinkCategory.COMPANY_NEWS,
            ),
            ("https://company.com/contact", "Contact Us", LinkCategory.CONTACT_INFO),
            (
                "https://company.com/privacy-policy",
                "Privacy Policy",
                LinkCategory.LEGAL_DOCUMENT,
            ),
        ]

        for url, anchor, category in initial_samples:
            link_info = LinkInfo(url=url, anchor_text=anchor, category=category)
            link_info.features = self._extract_link_features(link_info)
            self.training_links.append(link_info)

        # Train initial model if we have enough samples
        if len(self.training_links) >= self.min_training_samples:
            self._retrain_model()

    def _retrain_model(self) -> None:
        """Retrain the ML model with accumulated training data"""
        if (
            not SKLEARN_AVAILABLE
            or len(self.training_links) < self.min_training_samples
        ):
            return

        try:
            # Prepare training data
            feature_vectors = []
            text_data = []
            labels = []

            for link_info in self.training_links:
                if link_info.features and link_info.category != LinkCategory.UNKNOWN:
                    feature_vector = self._prepare_feature_vector(link_info.features)
                    if feature_vector is not None:
                        feature_vectors.append(feature_vector)
                        text_data.append(f"{link_info.anchor_text} {link_info.url}")
                        labels.append(link_info.category.value)

            if len(feature_vectors) < self.min_training_samples:
                logger.warning("Insufficient training data for model retraining")
                return

            # Prepare features
            X_features = self.feature_scaler.fit_transform(feature_vectors)
            X_text = self.text_vectorizer.fit_transform(text_data)
            X_combined = np.hstack([X_features, X_text.toarray()])
            y = self.label_encoder.fit_transform(labels)

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X_combined, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train model
            self.classifier.fit(X_train, y_train)

            # Evaluate
            y_pred = self.classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            self.is_trained = True
            logger.info(f"Retrained link classifier - Accuracy: {accuracy:.3f}")

            # Save model
            self._save_model()

        except Exception as e:
            logger.error(f"Model retraining failed: {e}")

    def _incorporate_feedback(self) -> None:
        """Incorporate feedback into training data"""
        for link_info, was_successful, extracted_value in self.feedback_links:
            if was_successful and extracted_value > 0.5:
                # Positive feedback - confirm current classification or upgrade
                if link_info.category in [
                    LinkCategory.UNKNOWN,
                    LinkCategory.IRRELEVANT,
                ]:
                    # Upgrade unknown/irrelevant to medium value category
                    link_info.category = LinkCategory.BUSINESS_PROFILE
                    self.training_links.append(link_info)
            elif not was_successful or extracted_value < 0.2:
                # Negative feedback - downgrade or mark as irrelevant
                link_info.category = LinkCategory.IRRELEVANT
                self.training_links.append(link_info)

        # Clear feedback buffer
        self.feedback_links.clear()

    def _save_model(self) -> None:
        """Save the trained model to disk"""
        try:
            model_path = Path(
                self.config.get("model_path", "data/models/link_classifier.pkl")
            )
            model_path.parent.mkdir(parents=True, exist_ok=True)

            model_data = {
                "classifier": self.classifier,
                "text_vectorizer": self.text_vectorizer,
                "feature_scaler": self.feature_scaler,
                "label_encoder": self.label_encoder,
                "is_trained": self.is_trained,
                "training_samples": len(self.training_links),
                "last_update": time.time(),
            }

            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            logger.info(f"Saved link classifier model to {model_path}")

        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _load_model(self, model_path: Path) -> None:
        """Load a saved model from disk"""
        try:
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)

            self.classifier = model_data["classifier"]
            self.text_vectorizer = model_data["text_vectorizer"]
            self.feature_scaler = model_data["feature_scaler"]
            self.label_encoder = model_data["label_encoder"]
            self.is_trained = model_data.get("is_trained", False)

            logger.info(f"Loaded link classifier model from {model_path}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def get_classifier_stats(self) -> Dict[str, Any]:
        """Get classifier performance statistics"""
        return {
            "is_trained": self.is_trained,
            "training_samples": len(self.training_links),
            "feedback_samples": len(self.feedback_links),
            "ml_available": SKLEARN_AVAILABLE,
            "categories": [cat.value for cat in LinkCategory],
            "confidence_threshold": self.confidence_threshold,
            "category_distribution": (
                {
                    cat.value: sum(
                        1 for link in self.training_links if link.category == cat
                    )
                    for cat in LinkCategory
                }
                if self.training_links
                else {}
            ),
        }
