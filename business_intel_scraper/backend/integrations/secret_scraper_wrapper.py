"""Wrapper for the optional `secretscraper` package."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from subprocess import CompletedProcess


def run_secret_scraper(target: str) -> CompletedProcess[str]:
    """Run SecretScraper against ``target`` if available."""
    if (
        importlib.util.find_spec("secretscraper") is None
        and shutil.which("secretscraper") is None
    ):
        raise NotImplementedError("SecretScraper is not installed")
    if shutil.which("secretscraper"):
        return subprocess.run(
            ["secretscraper", target],
            check=True,
            text=True,
            capture_output=True,
        )
    return subprocess.run(
        ["python", "-m", "secretscraper", target],
        check=True,
        text=True,
        capture_output=True,
    )
