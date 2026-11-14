from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.catalog import CompetitionRef, TeamOut


class ParticipantOut(BaseModel):
    side: str | None = None
    team: TeamOut | None = None
    score: int | None = None
    is_winner: bool | None = None  # pelo placar da partida; empate = os dois False
    shootout_score: int | None = None
    aggregate_score: int | None = None
    advanced: bool | None = None  # avançou no mata-mata


class EventSummary(BaseModel):
    id: int
    start_time: datetime
    status: str
    round: str | None = None
    leg: int | None = None  # ida (1) ou volta (2)
    decided_in: str | None = None  # extra_time, penalties ou nulo
    venue_name: str | None = None
    venue_city: str | None = None
    sport: str
    competition: CompetitionRef
    season: str
    participants: list[ParticipantOut]


class ParticipantDetail(ParticipantOut):
    formation: str | None = None
    stats: dict[str, Any] = {}


class Lance(BaseModel):
    tipo: str | None = None
    codigo: str | None = None  # ex.: "yellow-card", "penalty---scored"
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
    penaltis: dict[str, int] | None = None  # placar da disputa: {"home": 5, "away": 3}
    players: list[PlayerStatsOut]
