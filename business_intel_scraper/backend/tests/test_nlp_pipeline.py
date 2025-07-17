import importlib.util
import pathlib

pipeline_path = pathlib.Path(__file__).resolve().parents[1] / "nlp" / "pipeline.py"
spec = importlib.util.spec_from_file_location("pipeline", pipeline_path)
pipeline = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(pipeline)  # type: ignore[attr-defined]
extract_entities = pipeline.extract_entities


def test_extract_entities_smoke() -> None:
    texts = ["Apple is based in Cupertino"]
    entities = extract_entities(texts)
    assert isinstance(entities, list)
    assert all(isinstance(e, str) for e in entities)
    assert len(entities) > 0
