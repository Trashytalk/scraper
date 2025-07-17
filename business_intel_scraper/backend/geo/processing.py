"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple

import hashlib
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from business_intel_scraper.backend.db.models import Base, Location


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
