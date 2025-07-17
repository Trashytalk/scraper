"""Lightweight NLP pipeline helpers."""

from __future__ import annotations

from typing import Iterable

try:
    from .cleaning import clean_text
except ImportError:  # pragma: no cover - direct execution
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "cleaning", Path(__file__).parent / "cleaning.py"
    )
    cleaning = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(cleaning)  # type: ignore[attr-defined]
    clean_text = cleaning.clean_text  # type: ignore[attr-defined]


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

    Returns
    -------
    list[str]
        Extracted entities. When SpaCy or its English model is not
        available, the returned entities will simply be whitespace
        separated tokens from the input text.
        
    cleaned = [clean_text(t) for t in texts]


    
    nlp = _get_nlp()
    cleaned = preprocess(texts)
    if nlp is None:
        for text in cleaned:
            entities.extend(text.split())
        return entities


    for doc in nlp.pipe(cleaned):
        if getattr(doc, "ents", None):
            found = [ent.text for ent in doc.ents if ent.text]
            if found:
                entities.extend(found)
                continue
        entities.extend(doc.text.split())
    return entities


def preprocess(texts: Iterable[str]) -> list[str]:
    """Clean and normalize raw text strings.

    Parameters
    ----------
    texts : Iterable[str]
        Text strings to preprocess.

    Returns
    -------
    list[str]
        Cleaned text strings.
    """
    return [clean_text(t) for t in texts]
