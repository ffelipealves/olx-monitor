import asyncio
import logging
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
from config import OLX_URL


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


import unicodedata

def _normalizar(texto: str) -> str:
    """Remove caracteres problemáticos e normaliza unicode."""
    return unicodedata.normalize("NFC", texto).replace("\xa0", " ").strip()

async def _fechar_popups(page) -> None:
    """Tenta fechar popup de cookies e tradução do Google."""

    # Popup de cookies da OLX
    seletores_cookies = [
        "button[id*='accept']",
        "button[id*='cookie']",
        "button[data-testid*='cookie']",
        "button:has-text('Aceitar')",
        "button:has-text('Aceitar todos')",
        "button:has-text('OK')",
    ]
    for seletor in seletores_cookies:
        try:
            btn = page.locator(seletor).first
            if await btn.is_visible(timeout=2000):
                await btn.click()
                logger.info(f"Popup de cookies fechado via: {seletor}")
                await page.wait_for_timeout(500)
                break
        except Exception:
            continue

    # Popup de tradução do Google (barra no topo do Chrome)
    try:
        await page.evaluate("window.onbeforeunload = null")
        # Rejeita a oferta de tradução via JS caso esteja exposta no DOM
        dismiss = page.locator("cr-dialog, #translate-infobar-options, [id*='translate']").first
        if await dismiss.is_visible(timeout=1000):
            await dismiss.locator("button:has-text('Não')").click()
            logger.info("Popup de tradução dispensado.")
    except Exception:
        pass  # Não é crítico, segue em frente


async def fetch_anuncios() -> list[dict]:
    logger.info("Iniciando scraping da OLX...")
    html = ""

    try:
        async with Stealth().use_async(async_playwright()) as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                locale="pt-BR",
                extra_http_headers={"Accept-Language": "pt-BR,pt;q=0.9"},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()

            logger.info(f"Acessando URL: {OLX_URL}")
            await page.goto(OLX_URL, wait_until="domcontentloaded", timeout=60000)
            logger.info("DOM carregado.")

            # 1. Fecha popup de cookies logo que aparecer
            await _fechar_popups(page)

            # 2. Só depois espera os cards renderizarem
            logger.info("Aguardando anúncios renderizarem...")
            try:
                await page.wait_for_selector(
                    "[data-testid='adcard-link']",
                    timeout=20000,
                )
                logger.info("Cards detectados na página.")
            except Exception:
                logger.warning("Cards não detectados — salvando HTML para diagnóstico.")
            
            #await _scroll_pagina(page, max_scrolls=10)

            html = await page.content()
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("HTML salvo em debug.html")

            await browser.close()

    except Exception as e:
        logger.error(f"Erro ao acessar a OLX via Playwright: {e}", exc_info=True)
        return []

    anuncios = _parse_anuncios(html)
    logger.info(f"{len(anuncios)} anúncio(s) encontrado(s).")
    return anuncios
def _parse_anuncios(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    anuncios = []

    # Card raiz é a <section class="olx-adcard...">
    cards = soup.select("section.olx-adcard")
    logger.debug(f"Cards encontrados no HTML: {len(cards)}")

    if not cards:
        logger.warning("Nenhum card encontrado. Verifique o debug.html.")

    for card in cards:
        try:
            # Link e título — dentro de topbody
            link_tag = card.select_one("[data-testid='adcard-link']")
            if not link_tag:
                logger.debug("Card sem link, pulando.")
                continue

            url = link_tag.get("href", "")
            anuncio_id = url.rstrip("/").split("-")[-1]
            titulo_tag = link_tag.select_one("h2")

            # Preço — dentro de mediumbody
            preco_tag = card.select_one(".olx-adcard__mediumbody h3.olx-adcard__price")

            # Parcelamento — opcional, dentro de mediumbody
            parcela_tag = card.select_one("[data-testid='adcard-price-info'] span")

            # Local — dentro de bottombody
            local_tag = card.select_one(".olx-adcard__location")

            # Badges (Frete grátis, Pague Online, etc) — opcional
            badges = [
                b.get_text(strip=True)
                for b in card.select(".olx-core-badge")
            ]

            # Parcelamento — opcional, dentro de mediumbody
            parcela_tag = card.select_one("[data-testid='adcard-price-info'] span")
            parcela = (
                parcela_tag.get_text(separator=" ", strip=True)
                .replace("\xa0", " ")
                .replace("  ", " ")
                if parcela_tag else None
            )

            anuncios.append({
                "id": anuncio_id,
                "titulo": _normalizar(titulo_tag.get_text(strip=True)) if titulo_tag else "Sem título",
                "preco": _normalizar(preco_tag.get_text(strip=True)) if preco_tag else "Sem preço",
                "parcela": parcela,
                "local": _normalizar(local_tag.get_text(strip=True)) if local_tag else "Sem local",
                "badges": [_normalizar(b) for b in badges],
                "url": url,
            })

        except Exception as e:
            logger.warning(f"Erro ao parsear card: {e}", exc_info=True)
            continue

    return anuncios
if __name__ == "__main__":
    anuncios = asyncio.run(fetch_anuncios())
    if anuncios:
        for a in anuncios[:1]:
            print(a)
            
        print(len(anuncios))