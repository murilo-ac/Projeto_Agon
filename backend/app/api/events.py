from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.mappers import event_summary_fields, to_summary
from app.core.config import get_settings
from app.core.db import get_session
from app.repositories import queries
from app.schemas.events import EventDetailOut, EventSummary, Lance, ParticipantDetail, PlayerStatsOut

router = APIRouter(prefix="/events", tags=["jogos"])


def _zone(name: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(name or get_settings().worker_timezone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"fuso horário inválido: {name}") from exc


@router.get("", response_model=list[EventSummary])
def list_events(
    day: date | None = Query(None, alias="date", description="Dia (AAAA-MM-DD). Padrão: hoje."),
    tz: str | None = Query(None, description="Fuso que define o dia (ex.: America/Sao_Paulo)."),
    competition_id: int | None = None,
    sport: str | None = Query(None, description="Slug do esporte (ex.: football)."),
    session: Session = Depends(get_session),
):
    """Agenda do dia: jogos que começam entre 00:00 e 24:00 no fuso informado."""
    zone = _zone(tz)
    day = day or datetime.now(zone).date()
    start = datetime.combine(day, time.min, tzinfo=zone)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=zone)
    events = queries.list_events_between(session, start, end, competition_id, sport)
    return [to_summary(e) for e in events]


@router.get("/{event_id}", response_model=EventDetailOut)
def get_event(event_id: int, session: Session = Depends(get_session)):
    """Detalhe do jogo: placar, estatísticas dos times, lances e estatísticas por jogador."""
    event = queries.get_event(session, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="jogo não encontrado")

    side_by_team = {p.team_id: p.side for p in event.participants}
    players = [
        PlayerStatsOut(
            player_id=player.id,
            name=player.name,
            position=player.position,
            shirt_number=shirt,
            side=side_by_team.get(row.team_id),
            team_id=row.team_id,
            stats=row.stats,
        )
        for row, player, shirt in queries.event_players(session, event)
    ]
    return EventDetailOut(
        **event_summary_fields(event),
        participants=[
            ParticipantDetail.model_validate(p, from_attributes=True) for p in event.participants
        ],
        lances=[Lance(**lance) for lance in (event.extra or {}).get("lances", [])],
        players=players,
    )
