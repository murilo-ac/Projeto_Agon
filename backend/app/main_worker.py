import logging

from apscheduler.schedulers.blocking import BlockingScheduler

from app.core.config import get_settings
from app.core.logging import setup_logging

log = logging.getLogger("agon.worker")


def heartbeat() -> None:
    log.info("worker ativo")


def main() -> None:
    setup_logging(get_settings().log_level)
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(heartbeat, "interval", minutes=1, id="heartbeat")
    log.info("worker iniciado")
    heartbeat()
    scheduler.start()


if __name__ == "__main__":
    main()
