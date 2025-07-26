"""
AI Integration Module
Provides intelligent data processing, entity extraction, and classification
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import asyncio
from pathlib import Path

# Optional AI dependencies
try:
    import openai

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import spacy

    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

logger = logging.getLogger(__name__)


@dataclass
class ExtractedEntity:
    """Represents an extracted entity from text"""

    text: str
    label: str
    confidence: float
    start: int
    end: int
    metadata: Dict[str, Any] = None


@dataclass
class ClassificationResult:
    """Represents text classification result"""

    category: str
    confidence: float
    subcategories: List[Tuple[str, float]] = None


@dataclass
class ProcessedData:
    """Represents processed data with AI enhancements"""

    original_data: Dict[str, Any]
    entities: List[ExtractedEntity]
    classification: ClassificationResult
    summary: Optional[str] = None
    sentiment: Optional[Dict[str, float]] = None
    duplicates: List[str] = None
    quality_score: float = 0.0


class AIProcessor:
    """Main AI processing engine"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.models = {}
        self._initialize_models()

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load AI configuration"""
        default_config = {
            "ai": {
                "enabled": True,
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "models": {
                    "entity_extraction": "en_core_web_sm",
                    "classification": "distilbert-base-uncased-finetuned-sst-2-english",
                    "summarization": "facebook/bart-large-cnn",
                    "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                    "embedding": "all-MiniLM-L6-v2",
                },
                "entity_types": [
                    "PERSON",
                    "ORG",
                    "GPE",
                    "MONEY",
                    "DATE",
                    "PRODUCT",
                    "EVENT",
                    "LAW",
                    "EMAIL",
                    "URL",
                ],
                "classification_categories": [
                    "business",
                    "technology",
                    "finance",
                    "news",
                    "social",
                    "entertainment",
                    "sports",
                    "politics",
                ],
                "similarity_threshold": 0.85,
                "max_text_length": 5000,
            }
        }

        # Load custom config if provided
        if config_path and os.path.exists(config_path):
            try:
                import yaml

                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load AI config: {e}")

        return default_config

    def _initialize_models(self):
        """Initialize AI models based on available libraries"""
        logger.info("Initializing AI models...")

        # Initialize spaCy for entity extraction
        if HAS_SPACY:
            try:
                model_name = self.config["ai"]["models"]["entity_extraction"]
                self.models["nlp"] = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")
                self.models["nlp"] = None

        # Initialize transformers for classification and sentiment
        if HAS_TRANSFORMERS:
            try:
                # Classification model
                self.models["classifier"] = pipeline(
                    "text-classification",
                    model=self.config["ai"]["models"]["classification"],
                )

                # Sentiment model
                self.models["sentiment"] = pipeline(
                    "sentiment-analysis", model=self.config["ai"]["models"]["sentiment"]
                )

                # Summarization model
                self.models["summarizer"] = pipeline(
                    "summarization", model=self.config["ai"]["models"]["summarization"]
                )

                logger.info(
                    "Loaded transformer models for classification, sentiment, and summarization"
                )
            except Exception as e:
                logger.warning(f"Failed to load transformer models: {e}")

        # Initialize sentence transformers for embeddings
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.models["embedder"] = SentenceTransformer(
                    self.config["ai"]["models"]["embedding"]
                )
                logger.info("Loaded sentence transformer for embeddings")
            except Exception as e:
                logger.warning(f"Failed to load sentence transformer: {e}")

        # Initialize OpenAI client
        if HAS_OPENAI and self.config["ai"]["openai_api_key"]:
            try:
                openai.api_key = self.config["ai"]["openai_api_key"]
                self.models["openai"] = True
                logger.info("OpenAI API initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract named entities from text"""
        if not text or not self.models.get("nlp"):
            return []

        try:
            # Truncate text if too long
            max_length = self.config["ai"]["max_text_length"]
            if len(text) > max_length:
                text = text[:max_length]

            doc = self.models["nlp"](text)
            entities = []

            for ent in doc.ents:
                if ent.label_ in self.config["ai"]["entity_types"]:
                    entity = ExtractedEntity(
                        text=ent.text,
                        label=ent.label_,
                        confidence=0.9,  # Default confidence since spaCy doesn't provide this directly
                        start=ent.start_char,
                        end=ent.end_char,
                        metadata={
                            "spacy_kb_id": (
                                ent.kb_id_ if hasattr(ent, "kb_id_") else None
                            )
                        },
                    )
                    entities.append(entity)

            # Add custom entity extraction for emails and URLs
            entities.extend(self._extract_custom_entities(text))

            return entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

    def _extract_custom_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract custom entities like emails and URLs"""
        entities = []

        # Email regex
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        for match in re.finditer(email_pattern, text):
            entities.append(
                ExtractedEntity(
                    text=match.group(),
                    label="EMAIL",
                    confidence=0.95,
                    start=match.start(),
                    end=match.end(),
                )
            )

        # URL regex
        url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        for match in re.finditer(url_pattern, text):
            entities.append(
                ExtractedEntity(
                    text=match.group(),
                    label="URL",
                    confidence=0.95,
                    start=match.start(),
                    end=match.end(),
                )
            )

        return entities

    def classify_text(self, text: str) -> ClassificationResult:
        """Classify text into categories"""
        if not text or not self.models.get("classifier"):
            return ClassificationResult("unknown", 0.0)

        try:
            # Truncate text if too long
            max_length = self.config["ai"]["max_text_length"]
            if len(text) > max_length:
                text = text[:max_length]

            result = self.models["classifier"](text)

            # Map result to our categories
            category_mapping = {
                "POSITIVE": "business",
                "NEGATIVE": "news",
                "NEUTRAL": "general",
            }

            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                category = category_mapping.get(
                    prediction["label"], prediction["label"].lower()
                )
                confidence = prediction["score"]
            else:
                category = "unknown"
                confidence = 0.0

            return ClassificationResult(category, confidence)

        except Exception as e:
            logger.error(f"Text classification failed: {e}")
            return ClassificationResult("unknown", 0.0)

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        if not text or not self.models.get("sentiment"):
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

        try:
            # Truncate text if too long
            max_length = self.config["ai"]["max_text_length"]
            if len(text) > max_length:
                text = text[:max_length]

            result = self.models["sentiment"](text)

            if isinstance(result, list) and len(result) > 0:
                prediction = result[0]
                label = prediction["label"].lower()
                score = prediction["score"]

                sentiment = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
                sentiment[label] = score

                return sentiment

            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

    def summarize_text(self, text: str, max_length: int = 150) -> Optional[str]:
        """Generate text summary"""
        if not text or not self.models.get("summarizer"):
            return None

        try:
            # Text must be long enough for summarization
            if len(text.split()) < 30:
                return text[:max_length] + "..." if len(text) > max_length else text

            result = self.models["summarizer"](
                text, max_length=max_length, min_length=30, do_sample=False
            )

            if isinstance(result, list) and len(result) > 0:
                return result[0]["summary_text"]

            return None

        except Exception as e:
            logger.error(f"Text summarization failed: {e}")
            return None

    def detect_duplicates(
        self, texts: List[str], threshold: float = None
    ) -> List[List[int]]:
        """Detect duplicate or near-duplicate texts using embeddings"""
        if not texts or len(texts) < 2 or not self.models.get("embedder"):
            return []

        threshold = threshold or self.config["ai"]["similarity_threshold"]

        try:
            # Generate embeddings
            embeddings = self.models["embedder"].encode(texts)

            # Calculate similarity matrix
            from sklearn.metrics.pairwise import cosine_similarity

            similarity_matrix = cosine_similarity(embeddings)

            # Find duplicates
            duplicates = []
            processed = set()

            for i in range(len(texts)):
                if i in processed:
                    continue

                duplicate_group = [i]
                for j in range(i + 1, len(texts)):
                    if j not in processed and similarity_matrix[i][j] >= threshold:
                        duplicate_group.append(j)
                        processed.add(j)

                if len(duplicate_group) > 1:
                    duplicates.append(duplicate_group)
                    processed.update(duplicate_group)

            return duplicates

        except Exception as e:
            logger.error(f"Duplicate detection failed: {e}")
            return []

    def calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score based on completeness and content"""
        try:
            score = 0.0
            max_score = 100.0

            # Check data completeness (40 points)
            required_fields = ["title", "content", "url"]
            present_fields = sum(1 for field in required_fields if data.get(field))
            score += (present_fields / len(required_fields)) * 40

            # Check content length (20 points)
            content = data.get("content", "")
            if content:
                if len(content) > 1000:
                    score += 20
                elif len(content) > 500:
                    score += 15
                elif len(content) > 100:
                    score += 10
                else:
                    score += 5

            # Check for structured data (20 points)
            structured_fields = ["date", "author", "category", "tags"]
            present_structured = sum(
                1 for field in structured_fields if data.get(field)
            )
            score += (present_structured / len(structured_fields)) * 20

            # Check for unique identifiers (20 points)
            if data.get("url"):
                score += 10
            if data.get("id") or data.get("title"):
                score += 10

            return min(score / max_score, 1.0)

        except Exception as e:
            logger.error(f"Quality score calculation failed: {e}")
            return 0.0

    async def process_data(self, data: Dict[str, Any]) -> ProcessedData:
        """Process data with all AI enhancements"""
        try:
            # Extract text content for processing
            text_content = self._extract_text_content(data)

            # Run AI processing tasks
            entities = self.extract_entities(text_content)
            classification = self.classify_text(text_content)
            sentiment = self.analyze_sentiment(text_content)
            summary = self.summarize_text(text_content)
            quality_score = self.calculate_quality_score(data)

            return ProcessedData(
                original_data=data,
                entities=entities,
                classification=classification,
                summary=summary,
                sentiment=sentiment,
                quality_score=quality_score,
            )

        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return ProcessedData(
                original_data=data,
                entities=[],
                classification=ClassificationResult("unknown", 0.0),
                quality_score=0.0,
            )

    def _extract_text_content(self, data: Dict[str, Any]) -> str:
        """Extract text content from structured data"""
        text_parts = []

        # Common text fields
        text_fields = ["title", "content", "description", "text", "body", "summary"]

        for field in text_fields:
            if field in data and data[field]:
                text_parts.append(str(data[field]))

        return " ".join(text_parts)

    async def enhance_scraped_data(
        self, scraped_items: List[Dict[str, Any]]
    ) -> List[ProcessedData]:
        """Enhance a batch of scraped data with AI processing"""
        logger.info(f"Processing {len(scraped_items)} items with AI enhancement")

        # Process items concurrently
        tasks = [self.process_data(item) for item in scraped_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        processed_data = []
        for result in results:
            if isinstance(result, ProcessedData):
                processed_data.append(result)
            else:
                logger.error(f"Processing failed: {result}")

        # Detect duplicates across all processed items
        if len(processed_data) > 1:
            texts = [
                self._extract_text_content(item.original_data)
                for item in processed_data
            ]
            duplicate_groups = self.detect_duplicates(texts)

            # Mark duplicates
            for group in duplicate_groups:
                for idx in group[1:]:  # Skip first item in each group
                    if idx < len(processed_data):
                        processed_data[idx].duplicates = [
                            processed_data[group[0]].original_data.get("url", "")
                        ]

        logger.info(f"AI processing completed. Enhanced {len(processed_data)} items")
        return processed_data

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of loaded AI models"""
        status = {
            "ai_enabled": self.config["ai"]["enabled"],
            "models": {
                "spacy": bool(self.models.get("nlp")),
                "transformers": bool(self.models.get("classifier")),
                "sentence_transformers": bool(self.models.get("embedder")),
                "openai": bool(self.models.get("openai")),
            },
            "capabilities": {
                "entity_extraction": bool(self.models.get("nlp")),
                "text_classification": bool(self.models.get("classifier")),
                "sentiment_analysis": bool(self.models.get("sentiment")),
                "summarization": bool(self.models.get("summarizer")),
                "duplicate_detection": bool(self.models.get("embedder")),
                "quality_scoring": True,
            },
        }

        return status


# Convenience functions for easy integration
def create_ai_processor(config_path: str = None) -> AIProcessor:
    """Create an AI processor instance"""
    return AIProcessor(config_path)


async def process_scraped_data(
    data: List[Dict[str, Any]], config_path: str = None
) -> List[ProcessedData]:
    """Process scraped data with AI enhancements"""
    processor = create_ai_processor(config_path)
    return await processor.enhance_scraped_data(data)
