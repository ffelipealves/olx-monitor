# src/scrapper_app/core/models.py
import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Anuncio:
    id: str
    titulo: str
    preco: str
    url: str
    local: str = "Sem local"
    parcela: str | None = None
    data_anuncio: str | None = None
    badges: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Converte para dict pronto para o INSERT no SQLite."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "preco": self.preco,
            "parcela": self.parcela,
            "local": self.local,
            "data_anuncio": self.data_anuncio,
            "badges": json.dumps(self.badges, ensure_ascii=False),
            "url": self.url,
            "visto_em": datetime.now(),
        }