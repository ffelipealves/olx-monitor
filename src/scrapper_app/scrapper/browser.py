# src/scrapper_app/core/browser.py
import logging
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

SELETORES_COOKIES = [
    "button[id*='accept']",
    "button[id*='cookie']",
    "button[data-testid*='cookie']",
    "button:has-text('Aceitar')",
    "button:has-text('Aceitar todos')",
    "button:has-text('OK')",
]


async def fechar_popups(page: Page) -> None:
    """Tenta fechar popup de cookies e tradução do Google."""
    for seletor in SELETORES_COOKIES:
        try:
            btn = page.locator(seletor).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                logger.info(f"Popup de cookies fechado via: {seletor}")
                await page.wait_for_timeout(500)
                break
        except Exception:
            continue

    try:
        await page.evaluate("window.onbeforeunload = null")
        dismiss = page.locator(
            "cr-dialog, #translate-infobar-options, [id*='translate']"
        ).first
        if await dismiss.is_visible(timeout=1000):
            await dismiss.locator("button:has-text('Não')").click()
            logger.info("Popup de tradução dispensado.")
    except Exception:
        pass


async def criar_pagina(playwright):
    """Cria browser, context e page com stealth aplicado."""
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        locale="pt-BR",
        extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
        user_agent=USER_AGENT,
    )
    page = await context.new_page()
    return browser, page


def get_stealth_playwright():
    """Retorna o context manager do Playwright com stealth."""
    return Stealth().use_async(async_playwright())