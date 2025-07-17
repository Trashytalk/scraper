"""Tests for text cleaning utilities."""

from __future__ import annotations

import pytest

cleaning = pytest.importorskip("business_intel_scraper.backend.nlp.cleaning")
clean_text = cleaning.clean_text
normalize_whitespace = cleaning.normalize_whitespace
strip_html = cleaning.strip_html


def test_strip_html() -> None:
    """HTML tags are removed."""
    assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_normalize_whitespace() -> None:
    """Whitespace is collapsed and trimmed."""
    assert normalize_whitespace(" a \n  b\t c  ") == "a b c"


def test_clean_text() -> None:
    """Full cleaning removes HTML and normalizes."""
    assert clean_text(" <p>Hello&nbsp; <b>world</b>\n</p>") == "Hello world"
