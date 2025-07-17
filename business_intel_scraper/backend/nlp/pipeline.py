"""Lightweight NLP pipeline helpers."""

from __future__ import annotations

from typing import Iterable

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


def preprocess(texts: Iterable[str]) -> list[str]:
    """Clean and normalize raw text strings."""

    return [clean_text(t) for t in texts]


def extract_entities(texts: Iterable[str]) -> list[str]:
    """Extract named entities or fallback to tokenized text."""

    nlp = _get_nlp()
    cleaned = preprocess(texts)
    if nlp is None:
        return [token for text in cleaned for token in text.split()]

    entities: list[str] = []
    for doc in nlp.pipe(cleaned):
        if getattr(doc, "ents", None):
            found = [ent.text for ent in doc.ents if ent.text]
            if found:
                entities.extend(found)
                continue
        entities.extend(doc.text.split())
    return entities
