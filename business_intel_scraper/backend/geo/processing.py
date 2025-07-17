"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import json
import time
import urllib.parse
import urllib.request


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_addresses(
    addresses: Iterable[str],
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
    results: list[Tuple[str, float | None, float | None]] = []

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
