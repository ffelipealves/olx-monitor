import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    print("=== DEBUG TELEGRAM ===")
    print(f"TOKEN carregado? {'SIM' if TOKEN else 'NÃO'}")
    print(f"CHAT_ID carregado? {'SIM' if CHAT_ID else 'NÃO'}")

    if not TOKEN or not CHAT_ID:
        print("❌ ERRO: Variáveis de ambiente não carregadas")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    print(f"➡️ URL: {url}")
    print(f"➡️ Payload: {payload}")

    try:
        response = requests.post(url, json=payload)

        print(f"⬅️ Status Code: {response.status_code}")
        print(f"⬅️ Response Text: {response.text}")

        data = response.json()

        if data.get("ok"):
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Erro retornado pela API do Telegram:")
            print(data)

    except Exception as e:
        print("💥 Exceção ao enviar mensagem:")
        print(str(e))


send_message("Scraper rodou com sucesso 🚀")