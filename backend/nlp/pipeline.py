"""Simple NLP pipeline using SpaCy for entity extraction."""

from __future__ import annotations

from typing import List, TypedDict

try:  # pragma: no cover - optional dependency
    import spacy
    from spacy.language import Language
except ModuleNotFoundError:  # pragma: no cover - spaCy unavailable
    spacy = None  # type: ignore

    class Language:  # type: ignore[override]
        pass


_NLP_MODEL: Language | None = None


def _get_nlp() -> Language | None:
    """Load and cache the spaCy language model if available."""
    global _NLP_MODEL
    if spacy is None:
        return None
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("en_core_web_sm")
        except Exception:  # pragma: no cover - model not installed
            _NLP_MODEL = spacy.blank("en")
    return _NLP_MODEL


class Entity(TypedDict):
    """Structured representation of a named entity."""

    text: str
    label: str
    start: int
    end: int


def extract_entities(text: str) -> List[Entity]:
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
