from __future__ import annotations

import io
import json
import os
import sys
import urllib.request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, relationship
import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

from business_intel_scraper.backend.db.models import Base, Location
from business_intel_scraper.backend.geo.processing import geocode_addresses

Location.companies = relationship("Company", back_populates="location")


def fake_urlopen_factory(response_json: str):
    class FakeResponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            self.close()

    def fake_urlopen(_req: urllib.request.Request, timeout: int = 10):
        return FakeResponse(response_json.encode())

    return fake_urlopen


def test_geocode_addresses_persists_locations(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    addresses = ["123 Main St", "456 Elm St"]
    mock_response = json.dumps([{"lat": "40.0", "lon": "-75.0"}])
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen_factory(mock_response))
    monkeypatch.setattr("time.sleep", lambda _x: None)

    results = geocode_addresses(addresses, engine=engine)
    assert len(results) == 2

    with Session(engine) as session:
        stored = session.query(Location).order_by(Location.id).all()
        assert [loc.address for loc in stored] == addresses
        for loc, (_, lat, lon) in zip(stored, results):
            assert loc.latitude == lat
            assert loc.longitude == lon
