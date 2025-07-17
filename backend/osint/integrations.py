"""Wrappers for common OSINT tools.

This module provides thin wrappers around command line utilities used for
open-source intelligence (OSINT) gathering.  The functions are intentionally
light-weight and only execute the tools if they are installed on the system.
The output of each command is captured and returned as a simple dictionary so
that higher level code does not have to deal with subprocess management.

The wrappers degrade gracefully when the underlying command line tools are not
available, returning an error string in the result instead of raising
exceptions.  This makes it easier to run unit tests or to operate in minimal
environments where SpiderFoot or TheHarvester are not installed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any, Dict


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return text.strip()


def run_spiderfoot(domain: str) -> Dict[str, Any]:
    """Run SpiderFoot against a domain and return parsed output."""

    executable = (
        shutil.which("spiderfoot") or shutil.which("sf.py") or shutil.which("sf")
    )
    if executable is None:
        return {"domain": domain, "error": "SpiderFoot executable not found"}

    cmd = [executable, "-q", domain, "-F", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout or proc.stderr
    return {"domain": domain, "data": _parse_json(output)}


def run_theharvester(domain: str) -> Dict[str, Any]:
    """Run TheHarvester against a domain and return parsed output."""

    executable = shutil.which("theharvester")
    if executable is None:
        return {"domain": domain, "error": "theHarvester executable not found"}

    cmd = [executable, "-d", domain, "-b", "all", "-f", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout or proc.stderr
    return {"domain": domain, "data": _parse_json(output)}
