# src/scrapper_app/core/utils.py
import unicodedata


def normalizar(texto: str) -> str:
    """Remove caracteres problemáticos e normaliza unicode."""
    return unicodedata.normalize("NFC", texto).replace("\xa0", " ").strip()