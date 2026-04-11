# src/scrapper_app/notifier/notifier.py
import asyncio
import logging

from telegram import Bot
from telegram.error import TelegramError

from scrapper_app.config import settings
from scrapper_app.scrapper.models import Anuncio

logger = logging.getLogger(__name__)


def _formatar_mensagem(anuncio: Anuncio) -> str:
    """Formata um anúncio para envio no Telegram com Markdown."""
    badges = " · ".join(anuncio.badges) if anuncio.badges else None

    linhas = [
        f"🎮 *{anuncio.titulo}*",
        f"💰 {anuncio.preco}",
    ]

    if anuncio.parcela:
        linhas.append(f"💳 {anuncio.parcela}")

    linhas.append(f"📍 {anuncio.local}")

    if anuncio.data_anuncio:
        linhas.append(f"🕐 {anuncio.data_anuncio}")

    if badges:
        linhas.append(f"🏷️ {badges}")

    linhas.append(f"🔗 [Ver anúncio]({anuncio.url})")

    return "\n".join(linhas)


async def notificar_novos(anuncios: list[Anuncio]) -> None:
    """Envia uma mensagem no Telegram para cada anúncio novo."""
    if not anuncios:
        logger.info("Nenhum anúncio novo para notificar.")
        return

    bot = Bot(token=settings.TELEGRAM_TOKEN)

    try:
        await bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"🔔 *{len(anuncios)} anúncio(s) novo(s) de RTX!*",
            parse_mode="Markdown",
        )
    except TelegramError as e:
        logger.error(f"Erro ao enviar cabeçalho: {e}")
        return

    for anuncio in anuncios:
        try:
            await bot.send_message(
                chat_id=settings.TELEGRAM_CHAT_ID,
                text=_formatar_mensagem(anuncio),
                parse_mode="Markdown",
                disable_web_page_preview=False,
            )
            logger.info(f"Notificação enviada: {anuncio.titulo}")
        except TelegramError as e:
            logger.error(f"Erro ao notificar anúncio {anuncio.id}: {e}")
            continue


if __name__ == "__main__":
    falso = Anuncio(
        id="999",
        titulo="Nintendo 3DS XL teste",
        preco="R$ 500",
        parcela="em até 3x de R$ 166,67 sem juros",
        local="Fortaleza - CE",
        badges=["Frete grátis", "Pague Online"],
        url="https://www.olx.com.br",
    )
    asyncio.run(notificar_novos([falso]))