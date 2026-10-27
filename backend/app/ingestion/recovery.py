"""Recuperação ao iniciar o worker: garante que nada ficou pendente enquanto ele esteve desligado."""

import logging
from collections.abc import Callable, Sequence
from contextlib import closing
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.ingestion import calendar, postgame
from app.ingestion.runner import Clock, utcnow
from app.providers.base import Provider
from app.repositories import ops

log = logging.getLogger(__name__)

MAX_IDADE_CALENDARIO = timedelta(hours=24)


def run_recovery(
    session_factory: Callable[[], Session],
    provider_factory: Callable[[], Provider],
    provider_name: str,
    ligas: Sequence[str],
    hoje: Callable[[], date],
    dias_antes: int = 1,
    dias_depois: int = 7,
    idade_minima: timedelta = timedelta(minutes=120),
    janela: timedelta = timedelta(days=7),
    clock: Clock = utcnow,
) -> None:
    with session_factory() as session:
        ultimo = ops.last_success_at(session, calendar.JOB, provider_name)

    if ultimo is None or clock() - ultimo > MAX_IDADE_CALENDARIO:
        log.info("recuperação: calendário desatualizado (último sucesso: %s)", ultimo)
        with closing(provider_factory()) as provider:
            calendar.run_calendar(
                session_factory, provider, ligas, hoje(), dias_antes, dias_depois, clock
            )
    with closing(provider_factory()) as provider:
        postgame.run_postgame(session_factory, provider, idade_minima, janela, clock)
