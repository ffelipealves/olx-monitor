# src/scrapper_app/scraper/olx/parser.py
import logging
from bs4 import BeautifulSoup

from scrapper_app.scrapper.models import Anuncio
from scrapper_app.scrapper.utils import normalizar

logger = logging.getLogger(__name__)


def parse_anuncios(html: str) -> list[Anuncio]:
    """Recebe HTML da OLX e devolve lista de Anuncio."""
    soup = BeautifulSoup(html, "html.parser")
    anuncios = []

    cards = soup.select("section.olx-adcard")
    logger.debug(f"Cards encontrados no HTML: {len(cards)}")

    if not cards:
        logger.warning("Nenhum card encontrado. Verifique o debug.html.")

    for card in cards:
        try:
            link_tag = card.select_one("[data-testid='adcard-link']")
            if not link_tag:
                logger.debug("Card sem link, pulando.")
                continue

            url = link_tag.get("href", "")
            anuncio_id = url.rstrip("/").split("-")[-1]
            titulo_tag = link_tag.select_one("h2")
            preco_tag = card.select_one(".olx-adcard__mediumbody h3.olx-adcard__price")
            parcela_tag = card.select_one("[data-testid='adcard-price-info'] span")
            local_tag = card.select_one(".olx-adcard__location")
            data_tag = card.select_one(".olx-adcard__date")
            badges = [
                normalizar(b.get_text(strip=True))
                for b in card.select(".olx-core-badge")
            ]

            parcela = (
                parcela_tag.get_text(separator=" ", strip=True)
                .replace("\xa0", " ")
                .replace("  ", " ")
                if parcela_tag else None
            )

            anuncios.append(Anuncio(
                id=anuncio_id,
                titulo=normalizar(titulo_tag.get_text(strip=True)) if titulo_tag else "Sem título",
                preco=normalizar(preco_tag.get_text(strip=True)) if preco_tag else "Sem preço",
                parcela=parcela,
                local=normalizar(local_tag.get_text(strip=True)) if local_tag else "Sem local",
                data_anuncio=normalizar(data_tag.get_text(strip=True)) if data_tag else None,
                badges=badges,
                url=url,
            ))

        except Exception as e:
            logger.warning(f"Erro ao parsear card: {e}", exc_info=True)
            continue

    return anuncios