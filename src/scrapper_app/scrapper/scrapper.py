# src/scrapper_app/scraper/olx/scraper.py
import asyncio
import logging
from pathlib import Path

from scrapper_app.config import settings
from scrapper_app.scrapper.browser import criar_pagina, fechar_popups, get_stealth_playwright
from scrapper_app.scrapper.models import Anuncio
from scrapper_app.scrapper.parser import parse_anuncios

logger = logging.getLogger(__name__)

DEBUG_HTML = Path(__file__).parent.parent.parent.parent.parent / "data" / "debug.html"


async def fetch_anuncios() -> list[Anuncio]:
    logger.info("Iniciando scraping da OLX...")
    html = ""

    try:
        async with get_stealth_playwright() as p:
            browser, page = await criar_pagina(p)

            logger.info(f"Acessando URL: {settings.OLX_URL}")
            await page.goto(settings.OLX_URL, wait_until="domcontentloaded", timeout=60000)
            logger.info("DOM carregado.")

            await fechar_popups(page)

            logger.info("Aguardando anúncios renderizarem...")
            try:
                await page.wait_for_selector("[data-testid='adcard-link']", timeout=20000)
                logger.info("Cards detectados na página.")
            except Exception:
                logger.warning("Cards não detectados — salvando HTML para diagnóstico.")

            html = await page.content()

            DEBUG_HTML.parent.mkdir(parents=True, exist_ok=True)
            DEBUG_HTML.write_text(html, encoding="utf-8")
            logger.info(f"HTML salvo em {DEBUG_HTML}")

            await browser.close()

    except Exception as e:
        logger.error(f"Erro ao acessar a OLX via Playwright: {e}", exc_info=True)
        return []

    anuncios = parse_anuncios(html)
    logger.info(f"{len(anuncios)} anúncio(s) encontrado(s).")
    return anuncios


if __name__ == "__main__":
    anuncios = asyncio.run(fetch_anuncios())
    if anuncios:
        print(anuncios[0])
    print(f"Total: {len(anuncios)}")