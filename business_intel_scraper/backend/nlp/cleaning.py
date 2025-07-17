"""Text cleaning utilities for NLP preprocessing."""

from __future__ import annotations

import re
import unicodedata
from html import unescape
from html.parser import HTMLParser


class _HTMLStripper(HTMLParser):
    """Helper class to strip HTML tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:  # pragma: no cover - passthrough
        self._chunks.append(data)

    def get_data(self) -> str:
        """Return concatenated text collected from HTML."""
        return "".join(self._chunks)


def strip_html(text: str) -> str:
    """Remove HTML tags from ``text``.

    Parameters
    ----------
    text : str
        HTML content to clean.

    Returns
    -------
    str
        Text with HTML tags removed.
    """
    stripper = _HTMLStripper()
    stripper.feed(text)
    return stripper.get_data()


def normalize_whitespace(text: str) -> str:
    """Collapse and trim whitespace in ``text``."""
    return re.sub(r"\s+", " ", text).strip()


def clean_text(text: str) -> str:
    """Fully normalize ``text`` by stripping HTML and collapsing spaces."""
    no_html = strip_html(unescape(text))
    normalized = normalize_whitespace(no_html)
    return unicodedata.normalize("NFKC", normalized)
