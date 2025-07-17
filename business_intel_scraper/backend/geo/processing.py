"""Geospatial processing utilities."""

from __future__ import annotations

from typing import Iterable, Tuple


def geocode_addresses(
    addresses: Iterable[str],
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
    return []
