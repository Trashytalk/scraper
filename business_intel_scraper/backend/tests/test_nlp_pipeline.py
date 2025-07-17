import importlib
import os
import sys
from types import ModuleType
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_pipeline(monkeypatch: pytest.MonkeyPatch, use_spacy: bool) -> ModuleType:
    """Reload the pipeline module with or without a spaCy dependency."""
    if use_spacy:
        spacy_mod = ModuleType("spacy")

        class DummyLanguage:
            pass

        class DummyDoc:
            def __init__(self, text: str) -> None:
                self.text = text
                self.ents = [type("Ent", (), {"text": w}) for w in text.split() if w.istitle()]

        class DummyNLP:
            def pipe(self, texts):
                for t in texts:
                    yield DummyDoc(t)

        def load(_name: str) -> DummyNLP:  # pragma: no cover - simple stub
            return DummyNLP()

        def blank(_name: str) -> DummyNLP:  # pragma: no cover - simple stub
            return DummyNLP()

        spacy_mod.load = load
        spacy_mod.blank = blank
        spacy_mod.Language = DummyLanguage
        language_mod = ModuleType("spacy.language")
        language_mod.Language = DummyLanguage
        monkeypatch.setitem(sys.modules, "spacy", spacy_mod)
        monkeypatch.setitem(sys.modules, "spacy.language", language_mod)
    else:
        monkeypatch.delitem(sys.modules, "spacy", raising=False)
        monkeypatch.delitem(sys.modules, "spacy.language", raising=False)

    monkeypatch.syspath_prepend(str(ROOT))
    module_name = "business_intel_scraper.backend.nlp.pipeline"
    if module_name in sys.modules:
        del sys.modules[module_name]
    module = importlib.import_module(module_name)
    return module


def test_extract_entities_without_spacy(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _load_pipeline(monkeypatch, use_spacy=False)
    texts = ["A B", "C D"]
    assert pipeline.extract_entities(texts) == ["A", "B", "C", "D"]


def test_extract_entities_with_spacy(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _load_pipeline(monkeypatch, use_spacy=True)
    texts = ["Apple is in Cupertino", "I like oranges"]
    assert pipeline.extract_entities(texts) == ["Apple", "Cupertino", "I"]
