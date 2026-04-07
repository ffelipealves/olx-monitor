# storage.py
import sqlite3
import json
import logging
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

DB_PATH = "anuncios.db"


def init_db() -> None:
    """Cria o banco e a tabela se não existirem."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS anuncios (
                id          TEXT PRIMARY KEY,
                titulo      TEXT,
                preco       TEXT,
                parcela     TEXT,
                local       TEXT,
                data_anuncio TEXT,
                badges      TEXT,
                url         TEXT,
                visto_em    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    logger.info("Banco de dados inicializado.")


def limpar_anuncios_antigos(dias: int = 7) -> None:
    """Remove anúncios mais antigos que X dias."""
    limite = datetime.now() - timedelta(days=dias)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "DELETE FROM anuncios WHERE visto_em < ?",
            (limite,)
        )
        conn.commit()
    removidos = cursor.rowcount
    if removidos:
        logger.info(f"{removidos} anúncio(s) antigos removidos do banco.")
    else:
        logger.info("Nenhum anúncio antigo para remover.")

def buscar_ids_conhecidos() -> set[str]:
    """Retorna todos os IDs já salvos no banco."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("SELECT id FROM anuncios").fetchall()
    ids = {row[0] for row in rows}
    logger.debug(f"{len(ids)} IDs conhecidos no banco.")
    return ids


def salvar_anuncios(anuncios: list[dict]) -> None:
    """Salva uma lista de anúncios, ignorando duplicatas."""
    if not anuncios:
        logger.info("Nenhum anúncio para salvar.")
        return

    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO anuncios (id, titulo, preco, parcela, local, data_anuncio, badges, url, visto_em)
            VALUES (:id, :titulo, :preco, :parcela, :local, :data_anuncio, :badges, :url, :visto_em)
            """,
            [
                {**a, "badges": json.dumps(a["badges"], ensure_ascii=False), "visto_em": datetime.now()}
                for a in anuncios
            ],
        )
        conn.commit()
    logger.info(f"{len(anuncios)} anúncio(s) salvos no banco.")


def filtrar_novos(anuncios: list[dict]) -> list[dict]:
    """Retorna só os anúncios cujo ID ainda não está no banco."""
    ids_conhecidos = buscar_ids_conhecidos()
    novos = [a for a in anuncios if a["id"] not in ids_conhecidos]
    logger.info(f"{len(novos)} anúncio(s) novo(s) encontrado(s).")
    return novos