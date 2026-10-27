from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.catalog import CompetitionRef, TeamOut


class ParticipantOut(BaseModel):
    side: str | None = None
    team: TeamOut | None = None
    score: int | None = None
    is_winner: bool | None = None


class EventSummary(BaseModel):
    id: int
    start_time: datetime
    status: str
    round: str | None = None
    venue_name: str | None = None
    venue_city: str | None = None
    sport: str
    competition: CompetitionRef
    season: str
    participants: list[ParticipantOut]


class ParticipantDetail(ParticipantOut):
    stats: dict[str, Any] = {}


class Lance(BaseModel):
    tipo: str | None = None
    minuto: str | None = None
    lado: str | None = None  # home, away ou nulo (lance sem time, ex.: apito inicial)
    jogadores: list[str] = []
    gol: bool = False


class PlayerStatsOut(BaseModel):
    player_id: int
    name: str
    position: str | None = None
    shirt_number: int | None = None
    side: str | None = None
    team_id: int | None = None
    stats: dict[str, Any] = {}


class EventDetailOut(EventSummary):
    participants: list[ParticipantDetail]  # type: ignore[assignment]
    lances: list[Lance]
    players: list[PlayerStatsOut]
