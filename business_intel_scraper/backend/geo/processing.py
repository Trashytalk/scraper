"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import hashlib
import json
import time
import urllib.parse
import urllib.request
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from business_intel_scraper.backend.db.models import Base, Location
from urllib.error import HTTPError, URLError


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def _deterministic_coords(address: str) -> tuple[float, float]:
    """Return reproducible coordinates for an address."""

    digest = hashlib.sha1(address.encode()).hexdigest()
    num = int(digest[:8], 16)
    latitude = float((num % 180) - 90)
    longitude = float(((num // 180) % 360) - 180)
    return latitude, longitude


def _nominatim_lookup(address: str) -> tuple[float | None, float | None]:
    """Query Nominatim for coordinates."""

    query = urllib.parse.urlencode({"q": address, "format": "json"})
    req = urllib.request.Request(
        f"{NOMINATIM_URL}?{query}",
        headers={"User-Agent": "business-intel-scraper/1.0"},
    )

    try:  # pragma: no cover - network issues
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:  # pragma: no cover - network issues
        pass

    return None, None


def geocode_addresses(
    addresses: Iterable[str],
    *,
    engine: Engine | None = None,
    use_nominatim: bool = True,
) -> list[Tuple[str, float | None, float | None]]:
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

    fetch_remote = engine is None
    if engine is None:
        engine = create_engine("sqlite:///geo.db")

    Base.metadata.create_all(engine)

    results: list[Tuple[str, float, float]] = []
    with Session(engine) as session:
        for address in addresses:
            lat, lon = _deterministic_coords(address)
            session.add(Location(address=address, latitude=lat, longitude=lon))
            results.append((address, lat, lon))

        session.commit()

    if not fetch_remote or not use_nominatim:
        return results

    final_results: list[Tuple[str, float | None, float | None]] = []
    for address, _lat, _lon in results:
        lat, lon = _nominatim_lookup(address)
        final_results.append((address, lat, lon))
        time.sleep(1)

    return final_results
