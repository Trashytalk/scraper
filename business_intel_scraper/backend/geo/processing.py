"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import hashlib
import json
import time
import urllib.parse
import urllib.request

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from business_intel_scraper.backend.db.models import Base, Location
import urllib.parse
import urllib.request



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
    """Geocode a list of addresses."""

    final_results: list[Tuple[str, float | None, float | None]] = []
    for address, lat, lon in results:
        query = urllib.parse.urlencode({"q": address, "format": "json"})
        req = urllib.request.Request(
            f"{NOMINATIM_URL}?{query}",
            headers={"User-Agent": "business-intel-scraper/1.0"},
        )


    for address in addresses:
        lat, lon = (
            _nominatim_lookup(address)
            if use_nominatim
            else _deterministic_coords(address)
        )
        results.append((address, lat, lon))

        time.sleep(1)

    return results
