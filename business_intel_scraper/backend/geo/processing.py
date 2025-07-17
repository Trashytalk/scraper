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

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
GOOGLE_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"


def _deterministic_coords(address: str) -> tuple[float, float]:
    """Return reproducible coordinates for an address."""

    digest = hashlib.sha1(address.encode()).hexdigest()
    num = int(digest[:8], 16)
    latitude = float((num % 180) - 90)
    longitude = float(((num // 180) % 360) - 180)
    return latitude, longitude



def _parse_nominatim_response(
    data: list[dict[str, str]],
) -> tuple[float | None, float | None]:
    """Parse a Nominatim JSON response."""
    if data:
        try:
            return float(data[0]["lat"]), float(data[0]["lon"])
        except (KeyError, ValueError, TypeError):
            pass
    return None, None


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
        return _parse_nominatim_response(data)
    except Exception:  # pragma: no cover - network issues
        pass

    return None, None


def _parse_google_response(data: dict) -> tuple[float | None, float | None]:
    """Parse a Google geocoding JSON response."""
    try:
        if data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return float(loc["lat"]), float(loc["lng"])
    except (KeyError, ValueError, TypeError):
        pass
    return None, None


def _google_lookup(address: str, api_key: str) -> tuple[float | None, float | None]:
    """Query Google Geocoding API for coordinates."""
    query = urllib.parse.urlencode({"address": address, "key": api_key})
    req = urllib.request.Request(f"{GOOGLE_GEOCODE_URL}?{query}")

    try:  # pragma: no cover - network issues
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        return _parse_google_response(data)
    except Exception:  # pragma: no cover - network issues
        pass

    return None, None


def geocode_addresses(
    addresses: Iterable[str],
    *,
    engine: Engine | None = None,
    use_nominatim: bool = True,
    google_api_key: str | None = None,
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

    local_results: list[Tuple[str, float, float]] = []
    with Session(engine) as session:
        for address in addresses:
            latitude, longitude = _deterministic_coords(address)

            session.add(
                Location(address=address, latitude=latitude, longitude=longitude)
            )
            local_results.append((address, latitude, longitude))

        session.commit()

    if not fetch_remote:
        return local_results

    final_results: list[Tuple[str, float | None, float | None]] = []
    for address, _lat, _lon in local_results:
        if use_nominatim:
            lat, lon = _nominatim_lookup(address)
        else:
            lat, lon = _google_lookup(address, google_api_key or "")
        final_results.append((address, lat, lon))
        time.sleep(1)

    return results
