from __future__ import annotations

import pytest

from business_intel_scraper.backend.security import solve_captcha


def test_solve_captcha_not_implemented() -> None:
    """Ensure solve_captcha raises NotImplementedError by default."""
    with pytest.raises(NotImplementedError):
        solve_captcha(b"dummy")
