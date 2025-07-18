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
from typing import Any


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return text.strip()


def run_spiderfoot(domain: str, parse_output: bool = False) -> dict[str, Any]:
    """Run SpiderFoot against a domain.

    The function expects the ``spiderfoot`` (or ``sf.py``) executable to be
    available on the ``PATH``.  If the executable cannot be found the returned
    dictionary contains an ``error`` key describing the problem instead of
    raising an exception.

    Parameters
    ----------
    domain : str
        Domain to investigate.

    Returns
    -------
    dict[str, str]
        ``domain`` plus either ``output`` from the command or an ``error``
        message.
    """

    executable = (
        shutil.which("spiderfoot") or shutil.which("sf.py") or shutil.which("sf")
    )
    if executable is None:
        return {"domain": domain, "error": "SpiderFoot executable not found"}

    cmd = [executable, "-q", domain, "-F", "json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    if parse_output:
        return {"domain": domain, "data": _parse_json(output)}
    return {"domain": domain, "output": output}


def run_sherlock(username: str) -> dict[str, str]:
    """Run Sherlock to check a username across social networks.

    Parameters
    ----------
    username : str
        Username to search for.

    Returns
    -------
    dict[str, str]
        ``username`` plus either ``output`` from the command or an ``error``
        message.
    """

    executable = shutil.which("sherlock")
    if executable is None:
        return {"username": username, "error": "sherlock executable not found"}

    cmd = [executable, username, "--print-found"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    return {"username": username, "output": output}


def run_subfinder(domain: str) -> dict[str, str]:
    """Run subfinder to enumerate subdomains of ``domain``.

    Parameters
    ----------
    domain : str
        Domain to scan.

    Returns
    -------
    dict[str, str]
        ``domain`` plus either ``output`` from the command or an ``error``
        message.
    """

    executable = shutil.which("subfinder")
    if executable is None:
        return {"domain": domain, "error": "subfinder executable not found"}

    cmd = [executable, "-d", domain, "-silent"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    return {"domain": domain, "output": output}


def run_theharvester(domain: str, parse_output: bool = False) -> dict[str, Any]:
    """Run TheHarvester against a domain.

    Similar to :func:`run_spiderfoot`, this wrapper relies on the presence of
    the ``theharvester`` executable.  The function does not attempt to parse the
    output; instead the raw command output is returned.

    Parameters
    ----------
    domain : str
        Domain to investigate.

    Returns
    -------
    dict[str, str]
        ``domain`` plus either ``output`` from the command or an ``error``
        message.
    """

    executable = shutil.which("theharvester")
    if executable is None:
        return {"domain": domain, "error": "theHarvester executable not found"}

    cmd = [executable, "-d", domain, "-b", "all"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    if parse_output:
        return {"domain": domain, "data": _parse_json(output)}
    return {"domain": domain, "output": output}


def run_shodan(target: str) -> dict[str, str]:
    """Run Shodan search against ``target``.

    Parameters
    ----------
    target : str
        IP address or query string.

    Returns
    -------
    dict[str, str]
        ``target`` plus command output or error message.
    """

    executable = shutil.which("shodan")
    if executable is None:
        return {"target": target, "error": "shodan executable not found"}

    cmd = [executable, "host", target]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    return {"target": target, "output": output}


def run_nmap(target: str) -> dict[str, str]:
    """Run Nmap service scan on ``target``."""

    executable = shutil.which("nmap")
    if executable is None:
        return {"target": target, "error": "nmap executable not found"}

    cmd = [executable, "-sV", target]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stdout.strip() or proc.stderr.strip()
    return {"target": target, "output": output}


__all__ = [
    "run_spiderfoot",
    "run_theharvester",
    "run_sherlock",
    "run_subfinder",
    "run_shodan",
    "run_nmap",
]
