from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from business_intel_scraper.backend.db.models import Base, Location
from business_intel_scraper.backend.geo.processing import geocode_addresses


def test_geocode_addresses_persists_locations() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    addresses = ["123 Main St", "456 Elm St"]
    results = geocode_addresses(addresses, engine=engine)
    assert len(results) == 2

    with Session(engine) as session:
        stored = session.query(Location).order_by(Location.id).all()
        assert [loc.address for loc in stored] == addresses
        for loc, (_, lat, lon) in zip(stored, results):
            assert loc.latitude == lat
            assert loc.longitude == lon
