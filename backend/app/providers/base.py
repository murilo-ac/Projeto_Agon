"""Contrato dos provedores: devolvem dados já no formato interno e não conhecem o banco."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar("T")


class ProviderError(Exception):
    """Falha definitiva ao falar com o provedor (ex.: 4xx, resposta inválida)."""


class TransientError(ProviderError):
    """Falha temporária (5xx, timeout, rede): vale tentar de novo."""


class RateLimitError(ProviderError):
    """Cota estourada (HTTP 429): não insistir, tentar no próximo ciclo."""


@dataclass(frozen=True)
class RawResponse:
    """Resposta original do provedor, guardada em raw_payloads."""

    endpoint: str
    params: dict[str, Any]
    payload: dict[str, Any]


@dataclass(frozen=True)
class Fetch(Generic[T]):
    raw: RawResponse
    data: T


@dataclass(frozen=True)
class CompetitionData:
    external_id: str
    name: str
    sport_slug: str
    type: str = "league"


@dataclass(frozen=True)
class TeamData:
    external_id: str
    name: str
    short_name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None


@dataclass
class ParticipantData:
    team: TeamData
    side: str | None
    score: int | None = None
    is_winner: bool | None = None
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class EventData:
    external_id: str
    competition: CompetitionData
    season_label: str
    start_time: datetime
    status: str
    participants: list[ParticipantData]
    venue_name: str | None = None
    venue_city: str | None = None
    round: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlayerStatData:
    player_external_id: str
    player_name: str
    team_external_id: str
    position: str | None = None
    shirt_number: int | None = None
    photo_url: str | None = None
    stats: dict[str, Any] = field(default_factory=dict)


@dataclass
class EventDetail:
    event: EventData
    player_stats: list[PlayerStatData] = field(default_factory=list)


class Provider(Protocol):
    name: str
    requests_used: int

    def close(self) -> None: ...

    def listar_jogos(self, liga: str, dia: date) -> Fetch[list[EventData]]: ...

    def detalhar_jogo(self, liga: str, event_id: str) -> Fetch[EventDetail]: ...
