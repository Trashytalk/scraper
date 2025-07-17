import importlib
import sys
from types import ModuleType, SimpleNamespace
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
                self.ents = [
                    type("Ent", (), {"text": w}) for w in text.split() if w.istitle()
                ]

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


def test_extract_entities_structured(monkeypatch: pytest.MonkeyPatch) -> None:
    pipeline = _load_pipeline(monkeypatch, use_spacy=False)
    result = pipeline.extract_entities_structured("ACME launched")
    assert result == []

    class DummyEnt(SimpleNamespace):
        text: str
        label_: str
        start_char: int
        end_char: int

    class DummyDoc:
        def __init__(self, text: str) -> None:
            self.ents = [DummyEnt(text="ACME", label_="ORG", start_char=0, end_char=4)]

    class DummyNLP:
        def __call__(self, text: str) -> DummyDoc:  # pragma: no cover - simple stub
            return DummyDoc(text)

    pipeline = _load_pipeline(monkeypatch, use_spacy=True)
    monkeypatch.setattr(pipeline, "_get_nlp", lambda: DummyNLP())
    pipeline._NLP_MODEL = None
    result = pipeline.extract_entities_structured("ACME launched")
    assert result == [{"text": "ACME", "label": "ORG", "start": 0, "end": 4}]
