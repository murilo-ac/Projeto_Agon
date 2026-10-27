"""Job pós-jogo: busca o detalhe (estatísticas) de jogos que já deveriam ter terminado.

O que buscar vem do estado do banco (jogo sem detalhe, ou ainda não `final`), então o job
se recupera sozinho depois de o servidor ficar desligado. Sem pendências, não registra execução.
"""

import logging
from collections.abc import Callable
from datetime import timedelta

from sqlalchemy.orm import Session

from app.ingestion.runner import Clock, JobRun, utcnow
from app.models import SyncRun
from app.providers.base import Provider
from app.repositories import ingest, ops

log = logging.getLogger(__name__)

JOB = "postgame"


def run_postgame(
    session_factory: Callable[[], Session],
    provider: Provider,
    idade_minima: timedelta = timedelta(minutes=120),
    janela: timedelta = timedelta(days=7),
    clock: Clock = utcnow,
) -> SyncRun | None:
    with session_factory() as session:
        agora = clock()
        pendentes = ops.pending_details(session, provider.name, agora - idade_minima, agora - janela)
        if not pendentes:
            log.debug("pós-jogo: nada pendente")
            return None

        run = JobRun(session, provider, JOB, clock)
        for _event_id, external_id, liga in pendentes:
            if run.rate_limited:
                break
            with run.unit(f"{liga} jogo {external_id}"):
                fetch = provider.detalhar_jogo(liga, external_id)
                ops.save_raw_payload(session, provider.name, fetch.raw)
                ingest.upsert_event_detail(session, provider.name, fetch.data, clock())
        return run.finish()
