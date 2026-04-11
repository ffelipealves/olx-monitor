# src/scrapper_app/storage/storage.py
import sqlite3
import logging
from datetime import datetime, timedelta

from scrapper_app.config import settings
from scrapper_app.scrapper.models import Anuncio

logger = logging.getLogger(__name__)


def init_db() -> None:
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(settings.DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS anuncios (
                id            TEXT PRIMARY KEY,
                titulo        TEXT,
                preco         TEXT,
                parcela       TEXT,
                local         TEXT,
                data_anuncio  TEXT,
                badges        TEXT,
                url           TEXT,
                visto_em      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("Banco de dados inicializado.")


def limpar_anuncios_antigos() -> None:
    limite = datetime.now() - timedelta(days=settings.DB_RETENTION_DAYS)
    with sqlite3.connect(settings.DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM anuncios WHERE visto_em < ?", (limite,)
        )
        conn.commit()
    if cursor.rowcount:
        logger.info(f"{cursor.rowcount} anúncio(s) antigos removidos.")
    else:
        logger.info("Nenhum anúncio antigo para remover.")


def buscar_ids_conhecidos() -> set[str]:
    with sqlite3.connect(settings.DB_PATH) as conn:
        rows = conn.execute("SELECT id FROM anuncios").fetchall()
    ids = {row[0] for row in rows}
    logger.debug(f"{len(ids)} IDs conhecidos no banco.")
    return ids


def salvar_anuncios(anuncios: list[Anuncio]) -> None:
    if not anuncios:
        logger.info("Nenhum anúncio para salvar.")
        return

    with sqlite3.connect(settings.DB_PATH) as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO anuncios
                (id, titulo, preco, parcela, local, data_anuncio, badges, url, visto_em)
            VALUES
                (:id, :titulo, :preco, :parcela, :local, :data_anuncio, :badges, :url, :visto_em)
            """,
            [a.to_dict() for a in anuncios],
        )
        conn.commit()
    logger.info(f"{len(anuncios)} anúncio(s) salvos no banco.")


def filtrar_novos(anuncios: list[Anuncio]) -> list[Anuncio]:
    ids_conhecidos = buscar_ids_conhecidos()
    novos = [a for a in anuncios if a.id not in ids_conhecidos]
    logger.info(f"{len(novos)} anúncio(s) novo(s) encontrado(s).")
    return novos