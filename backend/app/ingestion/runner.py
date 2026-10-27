"""Controle de execução dos jobs: registra o histórico em sync_runs e isola falhas por unidade."""

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import SyncRun
from app.providers.base import Provider, RateLimitError
from app.repositories import ops

log = logging.getLogger(__name__)

Clock = Callable[[], datetime]


def utcnow() -> datetime:
    return datetime.now(UTC)


class JobRun:
    """Uma execução de job. Cada `unit` (ex.: uma liga/dia, um jogo) é confirmada à parte.

    - Falha de uma unidade (erro do provedor ou bug) desfaz só aquela unidade e segue.
    - HTTP 429 marca `rate_limited`; o job deve parar e deixar o resto para o próximo ciclo.
    """

    def __init__(self, session: Session, provider: Provider, job: str, clock: Clock = utcnow):
        self.session = session
        self.provider = provider
        self.clock = clock
        self.run: SyncRun = ops.start_run(session, job, provider.name)
        self._requests_before = provider.requests_used
        self.ok = 0
        self.errors: list[str] = []
        self.rate_limited = False

    @contextmanager
    def unit(self, label: str) -> Iterator[None]:
        try:
            yield
            self.session.commit()
            self.ok += 1
        except RateLimitError as exc:
            self.session.rollback()
            self.rate_limited = True
            self.errors.append(f"{label}: {exc}")
            log.warning("limite de requisições atingido em %s; parando o job", label)
        except Exception as exc:
            self.session.rollback()
            self.errors.append(f"{label}: {exc}")
            log.exception("falha em %s", label)

    def finish(self) -> SyncRun:
        if self.rate_limited:
            status = "rate_limited"
        elif not self.errors:
            status = "success"
        elif self.ok:
            status = "partial"
        else:
            status = "failed"
        error = "\n".join(self.errors[:20]) or None
        ops.finish_run(
            self.session,
            self.run,
            status,
            self.provider.requests_used - self._requests_before,
            self.clock(),
            error,
        )
        log.info(
            "job %s: %s (%s unidades ok, %s erros, %s requisições)",
            self.run.job,
            status,
            self.ok,
            len(self.errors),
            self.run.requests_used,
        )
        return self.run
