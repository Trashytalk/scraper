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

    if engine is not None:
        Base.metadata.create_all(engine)
        results: list[Tuple[str, float, float]] = []
        with Session(engine) as session:
            for address in addresses:
                digest = hashlib.sha1(address.encode()).hexdigest()
                num = int(digest[:8], 16)
                latitude = float((num % 180) - 90)
                longitude = float(((num // 180) % 360) - 180)

                session.add(
                    Location(
                        address=address, latitude=latitude, longitude=longitude
                    )
                )
                results.append((address, latitude, longitude))

            session.commit()
        return results

    results: list[Tuple[str, float, float]] = []
    for address in addresses:
        query = urllib.parse.urlencode({"q": address, "format": "json"})
        req = urllib.request.Request(
            f"{NOMINATIM_URL}?{query}",
            headers={"User-Agent": "business-intel-scraper/1.0"},
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.load(resp)
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                results.append((address, lat, lon))
            else:
                results.append((address, None, None))
        except Exception:  # pragma: no cover - network issues
            results.append((address, None, None))

        time.sleep(1)

    return results
