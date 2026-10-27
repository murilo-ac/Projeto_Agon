from datetime import datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models import Event, ExternalRef, RawPayload, Season, SyncRun
from app.providers.base import RawResponse


def save_raw_payload(session: Session, provider: str, raw: RawResponse) -> RawPayload:
    row = RawPayload(
        provider=provider, endpoint=raw.endpoint, params=raw.params, payload=raw.payload
    )
    session.add(row)
    session.flush()
    return row


def start_run(session: Session, job: str, provider: str) -> SyncRun:
    run = SyncRun(job=job, provider=provider, status="running", requests_used=0)
    session.add(run)
    session.commit()
    return run


def finish_run(
    session: Session,
    run: SyncRun,
    status: str,
    requests_used: int,
    finished_at: datetime,
    error: str | None = None,
) -> None:
    run.status = status
    run.requests_used = requests_used
    run.finished_at = finished_at
    run.error = error
    session.commit()


def last_success_at(session: Session, job: str, provider: str) -> datetime | None:
    return session.scalars(
        select(SyncRun.finished_at)
        .where(SyncRun.job == job, SyncRun.provider == provider, SyncRun.status == "success")
        .order_by(SyncRun.finished_at.desc())
    ).first()


def requests_used_on(session: Session, provider: str, since: datetime) -> int:
    return (
        session.scalar(
            select(func.coalesce(func.sum(SyncRun.requests_used), 0)).where(
                SyncRun.provider == provider, SyncRun.started_at >= since
            )
        )
        or 0
    )


def pending_details(
    session: Session, provider: str, started_before: datetime, started_after: datetime
) -> list[tuple[int, str, str]]:
    """Jogos que já deveriam ter terminado e ainda precisam do detalhe.

    São os sem detalhe coletado ou ainda não marcados como `final`. Devolve
    (id interno, id externo do jogo, "liga" externa da competição).
    """
    event_ref = aliased(ExternalRef)
    comp_ref = aliased(ExternalRef)
    stmt = (
        select(Event.id, event_ref.external_id, comp_ref.external_id)
        .join(
            event_ref,
            and_(
                event_ref.provider == provider,
                event_ref.entity_type == "event",
                event_ref.entity_id == Event.id,
            ),
        )
        .join(Season, Season.id == Event.season_id)
        .join(
            comp_ref,
            and_(
                comp_ref.provider == provider,
                comp_ref.entity_type == "competition",
                comp_ref.entity_id == Season.competition_id,
            ),
        )
        .where(
            Event.start_time <= started_before,
            Event.start_time >= started_after,
            Event.status.not_in(("canceled", "postponed")),
            or_(Event.details_synced_at.is_(None), Event.status != "final"),
        )
        .order_by(Event.start_time)
    )
    return [(row[0], row[1], row[2]) for row in session.execute(stmt)]
