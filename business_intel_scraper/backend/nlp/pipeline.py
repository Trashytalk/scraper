"""Lightweight NLP pipeline helpers."""

from __future__ import annotations

from typing import Iterable

try:
    from .cleaning import clean_text
except ImportError:  # pragma: no cover - fallback when executed as script
    from business_intel_scraper.backend.nlp.cleaning import clean_text


try:
    import spacy
    from spacy.language import Language
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    spacy = None  # type: ignore

    class Language:  # type: ignore
        """Fallback type used when SpaCy is unavailable."""

        pass


_NLP_MODEL: Language | None = None


def _get_nlp() -> Language | None:
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
    """Extract named entities from a sequence of texts.

    When SpaCy is unavailable or no model is installed the text is simply
    tokeni=======
sed on whitespace.
    """
    nlp = _get_nlp()
    entities: list[str] = []

    if nlp is None:
        for text in texts:
            entities.extend(text.split())
        return entities

    for doc in nlp.pipe(texts):
        found = [ent.text for ent in getattr(doc, "ents", [])]
        if found:
            entities.extend(found)
        else:
            entities.extend(doc.text.split())

    return entities


def preprocess(texts: Iterable[str]) -> list[str]:
    """Clean and normalise raw text strings."""
    
    return [clean_text(t) for t in texts]
