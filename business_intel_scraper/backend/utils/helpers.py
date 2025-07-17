"""Utility functions for the backend."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure basic logging.

    Parameters
    ----------
    level : int, optional
        Logging level, by default ``logging.INFO``.
    """
    logging.basicConfig(level=level)
    logger.debug("Logging configured")
