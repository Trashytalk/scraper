"""Tests for third-party integration wrappers."""

# ruff: noqa: E402

from __future__ import annotations

import os
import sys
import types

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, BASE_DIR)  # noqa: E402

import pytest

from business_intel_scraper.backend.integrations import (
    run_crawl4ai,
    run_secret_scraper,
    run_colly,
    run_proxy_pool,
    run_spiderfoot,
    run_katana,
)


@pytest.mark.parametrize(
    "func",
    [
        run_crawl4ai,
        run_secret_scraper,
        run_colly,
        run_proxy_pool,
        run_spiderfoot,
        run_katana,
    ],
)
def test_missing_tools_raise(func: types.FunctionType) -> None:
    """Ensure wrappers error when tools are not installed."""
    with pytest.raises(NotImplementedError):
        func("--help")
