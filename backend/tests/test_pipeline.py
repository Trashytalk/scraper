from types import SimpleNamespace
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_extract_entities_without_spacy(monkeypatch):
    pipeline = importlib.import_module("backend.nlp.pipeline")
    monkeypatch.setattr(pipeline, "_get_nlp", lambda: None)
    pipeline._NLP_MODEL = None
    assert pipeline.extract_entities("no entities") == []


def test_extract_entities_with_stub(monkeypatch):
    class DummyEnt(SimpleNamespace):
        text: str
        label_: str
        start_char: int
        end_char: int

    class DummyDoc:
        def __init__(self, text):
            self.ents = [DummyEnt(text="ACME", label_="ORG", start_char=0, end_char=4)]

    class DummyNLP:
        def __call__(self, text):
            return DummyDoc(text)

    pipeline = importlib.import_module("backend.nlp.pipeline")
    monkeypatch.setattr(pipeline, "_get_nlp", lambda: DummyNLP())
    pipeline._NLP_MODEL = None
    result = pipeline.extract_entities("ACME launched")
    assert result == [{"text": "ACME", "label": "ORG", "start": 0, "end": 4}]
