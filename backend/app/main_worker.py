import logging
import threading
from contextlib import closing
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.core.logging import setup_logging
from app.ingestion import calendar, postgame
from app.ingestion.recovery import run_recovery
from app.providers.espn import EspnProvider

log = logging.getLogger("agon.worker")

# os jobs gravam as mesmas tabelas: rodam um por vez
_job_lock = threading.Lock()


def _hoje():
    return datetime.now(ZoneInfo(get_settings().worker_timezone)).date()


def job_calendar() -> None:
    cfg = get_settings()
    with _job_lock, closing(EspnProvider()) as provider:
        calendar.run_calendar(
            SessionLocal,
            provider,
            cfg.espn_league_list,
            _hoje(),
            cfg.calendar_days_back,
            cfg.calendar_days_ahead,
        )


def job_postgame() -> None:
    cfg = get_settings()
    with _job_lock, closing(EspnProvider()) as provider:
        postgame.run_postgame(
            SessionLocal,
            provider,
            timedelta(minutes=cfg.postgame_min_age_minutes),
            timedelta(days=cfg.postgame_lookback_days),
        )


def main() -> None:
    cfg = get_settings()
    setup_logging(cfg.log_level)
    log.info("worker iniciado; ligas: %s", ", ".join(cfg.espn_league_list))

    with _job_lock:
        run_recovery(
            SessionLocal,
            EspnProvider,
            EspnProvider.name,
            cfg.espn_league_list,
            _hoje,
            cfg.calendar_days_back,
            cfg.calendar_days_ahead,
            timedelta(minutes=cfg.postgame_min_age_minutes),
            timedelta(days=cfg.postgame_lookback_days),
        )

    scheduler = BlockingScheduler(timezone=cfg.worker_timezone)
    scheduler.add_job(
        job_calendar,
        CronTrigger(hour=cfg.calendar_hour, minute=0, timezone=cfg.worker_timezone),
        id="calendar",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    scheduler.add_job(
        job_postgame,
        "interval",
        minutes=cfg.postgame_interval_minutes,
        id="postgame",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


if __name__ == "__main__":
    main()
