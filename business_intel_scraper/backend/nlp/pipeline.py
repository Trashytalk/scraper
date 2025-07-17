"""Lightweight NLP pipeline helpers."""

from __future__ import annotations

from typing import Iterable

try:
    from .cleaning import clean_text
except Exception:  # pragma: no cover - fallback for direct execution
    import importlib.util
    import pathlib

    module_path = pathlib.Path(__file__).resolve().parent / "cleaning.py"
    spec = importlib.util.spec_from_file_location("cleaning", module_path)
    cleaning = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(cleaning)  # type: ignore[attr-defined]
    clean_text = cleaning.clean_text  # type: ignore

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
    """Extract named entities from text collection."""

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
    """Clean and normalize raw text strings."""

    return [clean_text(t) for t in texts]
