"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple, Any

import os

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


def _parse_google_response(data: dict[str, Any]) -> tuple[float | None, float | None]:
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

    if engine is None:
        engine = create_engine("sqlite:///geo.db")

    Base.metadata.create_all(engine)

    results: list[Tuple[str, float | None, float | None]] = []
    
    # Ensure we have a valid Google API key if not using Nominatim
    effective_google_key = google_api_key or os.getenv("GOOGLE_API_KEY", "")
    
    lookup = (
        _nominatim_lookup
        if use_nominatim or not effective_google_key
        else (
            lambda addr: _google_lookup(addr, effective_google_key)
        )
    )

    with Session(engine) as session:
        for address in addresses:
            lat, lon = lookup(address)
            if lat is not None and lon is not None:
                session.add(Location(address=address, latitude=lat, longitude=lon))
            results.append((address, lat, lon))
            time.sleep(1)

        session.commit()

    return results
