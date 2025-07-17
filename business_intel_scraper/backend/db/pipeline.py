"""Data normalization pipeline for database inputs."""

from __future__ import annotations

from typing import Iterable, List


def normalize_names(names: Iterable[str]) -> List[str]:
    """Strip whitespace and deduplicate company names.

    Parameters
    ----------
    names : Iterable[str]
        Raw company name strings.

    Returns
    -------
    list[str]
        Cleaned list of unique names preserving input order.
    """
    seen: set[str] = set()
    cleaned: List[str] = []
    for name in names:
        if not name:
            continue
        normalized = name.strip()
        if not normalized:
            continue
        if normalized not in seen:
            seen.add(normalized)
            cleaned.append(normalized)
    return cleaned
