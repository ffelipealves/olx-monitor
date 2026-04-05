from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OLX_URL = os.getenv("OLX_URL")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))

# Validação básica na inicialização
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN não definido no .env")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID não definido no .env")
if not OLX_URL:
    raise ValueError("OLX_URL não definida no .env")