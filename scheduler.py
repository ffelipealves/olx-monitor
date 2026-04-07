# scheduler.py
import asyncio
import logging
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import CHECK_INTERVAL_MINUTES
from scrapper import fetch_anuncios
from storage import init_db, filtrar_novos, limpar_anuncios_antigos, salvar_anuncios
from notifier import notificar_novos

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def verificar_anuncios() -> None:
    """Pipeline completo: scrape → filtra novos → salva → notifica."""
    logger.info("=== Iniciando verificação ===")
    delay = random.randint(0, 60)
    logger.info(f"Aguardando {delay}s antes de iniciar...")
    await asyncio.sleep(delay)

    try:
        limpar_anuncios_antigos(dias=15)
        anuncios = await fetch_anuncios()
        if not anuncios:
            logger.warning("Nenhum anúncio retornado pelo scraper.")
            return

        novos = filtrar_novos(anuncios)

        if novos:
            salvar_anuncios(novos)
            await notificar_novos(novos)
        else:
            logger.info("Nenhum anúncio novo desta vez.")

    except Exception as e:
        logger.error(f"Erro durante a verificação: {e}", exc_info=True)

    logger.info("=== Verificação concluída ===")


async def main() -> None:
    init_db()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        verificar_anuncios,
        trigger=IntervalTrigger(minutes=CHECK_INTERVAL_MINUTES),
        id="verificar_olx",
        name="Verifica anúncios OLX",
        replace_existing=True,
        misfire_grace_time=120,   # tolera até 120s de atraso antes de considerar perdido
        max_instances=1, 
    )
    scheduler.start()
    logger.info(
        f"Scheduler iniciado — verificando a cada {CHECK_INTERVAL_MINUTES} minutos."
    )

    # Primeira execução: só salva, sem notificar
    logger.info("Executando carga inicial (sem notificações)...")
    try:
        anuncios = await fetch_anuncios()
        if anuncios:
            salvar_anuncios(anuncios)  # salva todos como "conhecidos"
            logger.info(f"{len(anuncios)} anúncio(s) salvos como base. Próximas verificações notificarão apenas os novos.")
        else:
            logger.warning("Nenhum anúncio retornado na carga inicial.")
    except Exception as e:
        logger.error(f"Erro na carga inicial: {e}", exc_info=True)

    # Mantém o loop rodando
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Encerrando scheduler...")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())