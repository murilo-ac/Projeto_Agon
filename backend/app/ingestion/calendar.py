"""Job de calendário: atualiza datas, horários, placares e status dos jogos de uma janela de dias."""

import logging
from collections.abc import Callable, Sequence
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.ingestion.runner import Clock, JobRun, utcnow
from app.models import SyncRun
from app.providers.base import Provider
from app.repositories import ingest, ops

log = logging.getLogger(__name__)

JOB = "calendar"


def run_calendar(
    session_factory: Callable[[], Session],
    provider: Provider,
    ligas: Sequence[str],
    hoje: date,
    dias_antes: int = 1,
    dias_depois: int = 7,
    clock: Clock = utcnow,
) -> SyncRun:
    dias = [hoje + timedelta(days=i) for i in range(-dias_antes, dias_depois + 1)]
    with session_factory() as session:
        run = JobRun(session, provider, JOB, clock)
        for liga in ligas:
            for dia in dias:
                if run.rate_limited:
                    break
                with run.unit(f"{liga} {dia:%Y-%m-%d}"):
                    fetch = provider.listar_jogos(liga, dia)
                    ops.save_raw_payload(session, provider.name, fetch.raw)
                    for event in fetch.data:
                        ingest.upsert_event(session, provider.name, event)
        return run.finish()
