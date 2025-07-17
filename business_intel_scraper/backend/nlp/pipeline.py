"""NLP processing pipeline stubs."""

from __future__ import annotations

from typing import Iterable

from .cleaning import clean_text


def extract_entities(texts: Iterable[str]) -> list[str]:
    """Extract named entities from text collection.

    Parameters
    ----------
    texts : Iterable[str]
        List or generator of text strings.

    Returns
    -------
    list[str]
        Extracted entities.
    """
    return []


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
