"""Enhanced NLP pipeline with multi-language support."""

from __future__ import annotations

import logging
from typing import Iterable, List, TypedDict, Any, Optional, Dict, Union

from business_intel_scraper.backend.nlp.cleaning import clean_text

# Optional spacy integration
spacy: Optional[Any] = None
try:
    import spacy
except ModuleNotFoundError:  # pragma: no cover
    pass

# Multi-language processor integration
try:
    from business_intel_scraper.backend.nlp.multilang import multilang_processor
    HAS_MULTILANG = True
except ImportError:
    HAS_MULTILANG = False
    multilang_processor = None

logger = logging.getLogger(__name__)

_NLP_MODEL: Any = None


class Entity(TypedDict):
    """Structured representation of a named entity."""

    text: str
    label: str
    start: int
    end: int


def _get_nlp() -> Any:
    """Load and cache the SpaCy language model if available."""
    global _NLP_MODEL
    if spacy is None:
        return None
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("en_core_web_sm")
        except Exception:  # pragma: no cover - model not installed
            _NLP_MODEL = spacy.blank("en")
    return _NLP_MODEL


def extract_entities(texts: Iterable[str]) -> list[str]:
    """Extract named entities from text collection."""

    processed = preprocess(texts)
    nlp = _get_nlp()
    entities: list[str] = []
    if nlp is None:
        for text in processed:
            entities.extend(text.split())
        return entities

    for doc in nlp.pipe(processed):
        found = [ent.text for ent in getattr(doc, "ents", [])]
        if found:
            entities.extend(found)
        else:
            entities.extend(doc.text.split())
    return entities


def extract_entities_structured(text: str) -> List[Entity]:
    """Return SpaCy named entities from ``text`` in structured form."""
    nlp = _get_nlp()
    if nlp is None:
        return []
    doc = nlp(text)
    return [
        {
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        }
        for ent in getattr(doc, "ents", [])
    ]


def preprocess(texts: Iterable[str]) -> list[str]:
    """Clean and normalize raw text strings."""
    return [clean_text(t) for t in texts]


def extract_multilang_entities(text: str, target_language: str = 'en') -> Dict[str, Any]:
    """Extract entities using multi-language NLP processor."""
    if not HAS_MULTILANG or not multilang_processor:
        logger.warning("Multi-language processor not available, falling back to basic extraction")
        return {
            'entities': extract_entities_structured(text),
            'language_info': {'detected_language': 'unknown'}
        }
    
    try:
        # Use the multi-language processor for comprehensive analysis
        intelligence = multilang_processor.extract_business_intelligence(text)
        return intelligence
    
    except Exception as e:
        logger.error(f"Multi-language processing failed: {e}")
        # Fallback to basic extraction
        return {
            'entities': extract_entities_structured(text),
            'language_info': {'detected_language': 'unknown'},
            'error': str(e)
        }


def process_multilang_text(text: str, **kwargs) -> Dict[str, Any]:
    """Complete multi-language text processing pipeline."""
    if not HAS_MULTILANG or not multilang_processor:
        logger.warning("Multi-language processor not available")
        return {'error': 'Multi-language processor not available'}
    
    try:
        result = multilang_processor.process_text(text, **kwargs)
        
        # Convert to serializable dictionary
        return {
            'original_text': result.original_text,
            'detected_language': {
                'name': result.detected_language.language.name,
                'code': result.detected_language.language.code,
                'script': result.detected_language.script.value,
                'confidence': result.detected_language.confidence
            },
            'tokenization': {
                'tokens': result.tokenization.tokens,
                'token_count': len(result.tokenization.tokens)
            } if result.tokenization else None,
            'entities': [
                {
                    'text': entity.text,
                    'type': entity.entity_type.value if hasattr(entity.entity_type, 'value') else str(entity.entity_type),
                    'confidence': entity.confidence,
                    'span': entity.span,
                    'metadata': entity.metadata
                }
                for entity in result.entities
            ],
            'transliteration': {
                'original': result.transliteration.original,
                'transliterated': result.transliteration.transliterated,
                'method': result.transliteration.method,
                'confidence': result.transliteration.confidence
            } if result.transliteration else None,
            'translation': {
                'original': result.translation.original,
                'translated': result.translation.translated,
                'method': result.translation.method,
                'confidence': result.translation.confidence
            } if result.translation else None,
            'normalized_entities': result.normalized_entities,
            'metadata': result.metadata
        }
    
    except Exception as e:
        logger.error(f"Multi-language text processing failed: {e}")
        return {'error': str(e)}


def get_supported_languages() -> List[str]:
    """Get list of supported languages."""
    if HAS_MULTILANG and multilang_processor:
        return list(multilang_processor.get_supported_languages().keys())
    else:
        return ['en']  # Default to English only


def get_processor_capabilities() -> Dict[str, Any]:
    """Get capabilities of the NLP processor."""
    if HAS_MULTILANG and multilang_processor:
        return multilang_processor.get_capabilities()
    else:
        return {
            'languages': ['en'],
            'scripts': ['latin'],
            'basic_ner': bool(spacy),
            'multilang_support': False
        }
