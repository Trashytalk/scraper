from __future__ import annotations

"""Utilities for using Playwright within Scrapy spiders."""

from typing import Optional

from playwright.async_api import async_playwright

from ..proxy.manager import ProxyManager


async def fetch_with_playwright(
    url: str,
    proxy_manager: Optional[ProxyManager] = None,
    headless: bool = True,
) -> str:
    """Return page HTML using Playwright.

    Parameters
    ----------
    url : str
        Page URL to fetch.
    proxy_manager : ProxyManager | None, optional
        Use this proxy manager for the request.
    headless : bool, optional
        Launch the browser in headless mode, by default ``True``.
    """
    proxy = None
    if proxy_manager is not None:
        proxy = {"server": proxy_manager.get_proxy()}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless, proxy=proxy)
        page = await browser.new_page()
        await page.goto(url)
        html = await page.content()
        await browser.close()
    return html
