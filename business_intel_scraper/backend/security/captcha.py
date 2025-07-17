"""CAPTCHA solving service placeholder."""

from __future__ import annotations

from typing import Any


class CaptchaSolver:
    """Abstract interface for CAPTCHA solving services."""

    def solve(self, image: bytes, **kwargs: Any) -> str:
        """Solve a CAPTCHA challenge.

        Parameters
        ----------
        image : bytes
            Binary image data representing the CAPTCHA challenge.
        **kwargs : Any
            Additional parameters for the solver implementation.

        Returns
        -------
        str
            The solved CAPTCHA text.
        """
        raise NotImplementedError("Captcha solving not implemented")


def solve_captcha(image: bytes, **kwargs: Any) -> str:
    """Convenience function using a default solver instance.

    Parameters
    ----------
    image : bytes
        Binary image data representing the CAPTCHA challenge.
    **kwargs : Any
        Additional parameters for the solver implementation.

    Returns
    -------
    str
        The solved CAPTCHA text.
    """
    solver = CaptchaSolver()
    return solver.solve(image, **kwargs)
