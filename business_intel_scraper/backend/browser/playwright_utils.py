"""Utilities for launching Playwright browsers with proxies."""

from __future__ import annotations

from playwright.async_api import async_playwright, Browser

from ..proxy.manager import ProxyManager


async def launch_browser(proxy_manager: ProxyManager, headless: bool = True) -> Browser:
    """Launch a Chromium browser using a proxy from the manager."""

    proxy = proxy_manager.get_proxy()
    playwright = await async_playwright().start()
    try:
        browser = await playwright.chromium.launch(
            headless=headless, proxy={"server": proxy}
        )
    except Exception:
        proxy_manager.rotate_proxy()
        raise
    return browser
