from __future__ import annotations

import pytest

spiders = pytest.importorskip("business_intel_scraper.backend.modules.spiders")


def test_spider_modules_exist() -> None:
    for name in spiders.__all__:
        assert hasattr(spiders, name)
