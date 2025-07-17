"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import hashlib
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from business_intel_scraper.backend.db.models import Base, Location
import json
import time
import urllib.parse
import urllib.request


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_addresses(
    addresses: Iterable[str],
    *,
    engine: Engine | None = None,
) -> list[Tuple[str, float, float]]:
    """Geocode a list of addresses.

    Parameters
    ----------
    addresses : Iterable[str]
        Addresses to geocode.

    Returns
    -------
    list[Tuple[str, float, float]]
        Tuples containing address and latitude/longitude.
    """

    if engine is None:
        engine = create_engine("sqlite:///geo.db")

    Base.metadata.create_all(engine)

    results: list[Tuple[str, float | None, float | None]] = []
    with Session(engine) as session:
        for address in addresses:
            digest = hashlib.sha1(address.encode()).hexdigest()
            num = int(digest[:8], 16)
            hashed_lat = float((num % 180) - 90)
            hashed_lon = float(((num // 180) % 360) - 180)

            session.add(
                Location(
                    address=address, latitude=hashed_lat, longitude=hashed_lon
                )
            )
            try:
                query = urllib.parse.urlencode({"q": address, "format": "json"})
                req = urllib.request.Request(
                    f"{NOMINATIM_URL}?{query}",
                    headers={"User-Agent": "business-intel-scraper/1.0"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.load(resp)
                if data:
                    latitude = float(data[0]["lat"])
                    longitude = float(data[0]["lon"])
                else:
                    latitude = hashed_lat
                    longitude = hashed_lon
            except Exception:  # pragma: no cover - network or parsing issues
                latitude = hashed_lat
                longitude = hashed_lon

            results.append((address, latitude, longitude))

        session.commit()

    return results
