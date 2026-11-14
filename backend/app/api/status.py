from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.events import resolve_zone
from app.core.config import get_settings
from app.core.db import get_session
from app.repositories import queries
from app.schemas.status import DateRange, StatusOut

router = APIRouter(tags=["status"])


@router.get("/status", response_model=StatusOut)
def status(
    tz: str | None = Query(None, description="Fuso que define os dias (ex.: America/Sao_Paulo)."),
    session: Session = Depends(get_session),
):
    """Quando os dados foram atualizados e quais dias a agenda cobre.

    O pós-jogo só registra execução quando há jogos pendentes, então `jobs.postgame`
    é a última vez em que algum resultado chegou, não a última verificação.
    """
    zone = resolve_zone(tz)
    today = datetime.now(zone).date()
    jobs = queries.last_sync_by_job(session)
    first = queries.first_event_time(session)
    return StatusOut(
        last_sync_at=max(jobs.values(), default=None),
        jobs=jobs,
        dates=DateRange(
            first=min(first.astimezone(zone).date(), today) if first else today,
            last=today + timedelta(days=get_settings().calendar_days_ahead),
        ),
    )
