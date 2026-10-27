from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.mappers import to_summary
from app.core.db import get_session
from app.repositories import queries
from app.schemas.catalog import TeamOut
from app.schemas.events import EventSummary

router = APIRouter(prefix="/teams", tags=["times"])


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, session: Session = Depends(get_session)):
    team = queries.get_team(session, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="time não encontrado")
    return team


@router.get("/{team_id}/events", response_model=list[EventSummary])
def list_team_events(
    team_id: int,
    status: Literal["scheduled", "live", "final", "postponed", "canceled"] | None = None,
    order: Literal["asc", "desc"] = "desc",
    limit: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Jogos do time. Use `status=final&order=desc` para os resultados recentes e
    `status=scheduled&order=asc` para os próximos jogos."""
    if queries.get_team(session, team_id) is None:
        raise HTTPException(status_code=404, detail="time não encontrado")
    events = queries.list_events_by_team(session, team_id, status, order == "desc", limit)
    return [to_summary(e) for e in events]
