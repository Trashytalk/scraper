from __future__ import annotations

import types

from business_intel_scraper.backend.nlp import pipeline


def test_extract_entities_without_spacy(monkeypatch) -> None:
    monkeypatch.setattr(pipeline, "_get_nlp", lambda: None)
    pipeline._NLP_MODEL = None
    result = pipeline.extract_entities(["hello world"])
    assert result == ["hello", "world"]


def test_extract_entities_with_stub_nlp(monkeypatch) -> None:
    class DummyDoc:
        def __init__(self, text: str, ents: list[str] | None = None) -> None:
            self.text = text
            self.ents = [types.SimpleNamespace(text=e) for e in ents or []]

    class DummyNLP:
        def pipe(self, texts):
            for text in texts:
                if "Apple" in text:
                    yield DummyDoc(text, ["Apple"])
                else:
                    yield DummyDoc(text)

    monkeypatch.setattr(pipeline, "_get_nlp", lambda: DummyNLP())
    pipeline._NLP_MODEL = None
    result = pipeline.extract_entities(["Apple was founded", "No entity here"])
    assert result == ["Apple", "No", "entity", "here"]


def test_extract_entities_cleans_html(monkeypatch) -> None:
    """HTML content is stripped before tokenization."""
    monkeypatch.setattr(pipeline, "_get_nlp", lambda: None)
    pipeline._NLP_MODEL = None
    result = pipeline.extract_entities(["<p>Hello <b>World</b></p>"])
    assert result == ["Hello", "World"]
