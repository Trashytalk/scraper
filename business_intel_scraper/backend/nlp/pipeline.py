"""Lightweight NLP pipeline helpers."""

from __future__ import annotations

from typing import Iterable, List, TypedDict

from business_intel_scraper.backend.nlp.cleaning import clean_text

try:  # pragma: no cover - optional dependency
    import spacy
    from spacy.language import Language
except ModuleNotFoundError:  # pragma: no cover
    spacy = None  # type: ignore

    class Language:  # type: ignore[override]
        """Fallback type used when SpaCy is unavailable."""

        pass


_NLP_MODEL: Language | None = None


class Entity(TypedDict):
    """Structured representation of a named entity."""

    text: str
    label: str
    start: int
    end: int


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
