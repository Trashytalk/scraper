import io
import json
import urllib.request
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from business_intel_scraper.backend.geo.processing import geocode_addresses


def fake_urlopen_factory(response_json: str):
    class FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.close()

    def fake_urlopen(_req: urllib.request.Request, timeout: int = 10):
        return FakeResponse(response_json.encode())

    return fake_urlopen


def test_geocode_addresses(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_response = json.dumps([
        {"lat": "51.5074", "lon": "-0.1278"}
    ])
    monkeypatch.setattr(
        urllib.request, "urlopen", fake_urlopen_factory(mock_response)
    )
    monkeypatch.setattr("time.sleep", lambda _x: None)

    results = geocode_addresses(["London"])
    assert results == [("London", 51.5074, -0.1278)]


def test_geocode_addresses_google(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_response = json.dumps(
        {
            "results": [
                {"geometry": {"location": {"lat": 40.0, "lng": -75.0}}}
            ],
            "status": "OK",
        }
    )
    monkeypatch.setattr(
        urllib.request, "urlopen", fake_urlopen_factory(mock_response)
    )
    monkeypatch.setattr("time.sleep", lambda _x: None)

    results = geocode_addresses(
        ["Philly"], use_nominatim=False, google_api_key="dummy"
    )
    assert results == [("Philly", 40.0, -75.0)]
