from pathlib import Path
from dotenv import load_dotenv
import os

# Garante que o .env é encontrado independente de onde o processo é iniciado
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")


class Settings:
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    OLX_URL: str = os.getenv("OLX_URL", "")
    CHECK_INTERVAL_MINUTES: int = int(os.getenv("CHECK_INTERVAL_MINUTES", "10"))
    DB_RETENTION_DAYS: int = int(os.getenv("DB_RETENTION_DAYS", "60"))

    # Caminho centralizado do banco — sempre em data/ na raiz do projeto
    DB_PATH: Path = Path(__file__).parent.parent.parent / "data" / "anuncios.db"

    def validate(self) -> None:
        errors = []
        if not self.TELEGRAM_TOKEN:
            errors.append("TELEGRAM_TOKEN não definido no .env")
        if not self.TELEGRAM_CHAT_ID:
            errors.append("TELEGRAM_CHAT_ID não definido no .env")
        if not self.OLX_URL:
            errors.append("OLX_URL não definida no .env")
        if errors:
            raise ValueError("\n".join(errors))


settings = Settings()