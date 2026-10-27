"""Gravação idempotente dos dados normalizados pelos providers.

Cada entidade é localizada pela referência externa (provider + tipo + id do provedor):
rodar a mesma coleta duas vezes atualiza as linhas existentes em vez de duplicá-las.
"""

from datetime import datetime
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Competition,
    Event,
    EventParticipant,
    Player,
    PlayerEventStats,
    Season,
    Sport,
    Team,
    TeamPlayer,
)
from app.models.base import Base
from app.providers.base import (
    CompetitionData,
    EventData,
    EventDetail,
    ParticipantData,
    PlayerStatData,
    TeamData,
)
from app.repositories import refs

M = TypeVar("M", bound=Base)


def _get_or_create(
    session: Session,
    provider: str,
    entity_type: str,
    external_id: str,
    model: type[M],
    values: dict[str, Any],
) -> M:
    """Cria a entidade (e sua referência externa) ou atualiza os campos não nulos."""
    entity_id = refs.find_entity_id(session, provider, entity_type, external_id)
    if entity_id is None:
        obj = model(**values)
        session.add(obj)
        session.flush()
        refs.add_ref(session, provider, entity_type, obj.id, external_id)  # type: ignore[attr-defined]
        return obj
    obj = session.get(model, entity_id)
    for key, value in values.items():
        if value is not None:
            setattr(obj, key, value)
    return obj


def get_sport(session: Session, slug: str) -> Sport:
    return session.scalars(select(Sport).where(Sport.slug == slug)).one()


def upsert_competition(session: Session, provider: str, data: CompetitionData) -> Competition:
    sport = get_sport(session, data.sport_slug)
    return _get_or_create(
        session,
        provider,
        "competition",
        data.external_id,
        Competition,
        {"sport_id": sport.id, "name": data.name, "type": data.type},
    )


def upsert_season(
    session: Session, provider: str, competition: CompetitionData, label: str
) -> Season:
    comp = upsert_competition(session, provider, competition)
    return _get_or_create(
        session,
        provider,
        "season",
        f"{competition.external_id}:{label}",
        Season,
        {"competition_id": comp.id, "label": label},
    )


def upsert_team(session: Session, provider: str, sport_id: int, data: TeamData) -> Team:
    return _get_or_create(
        session,
        provider,
        "team",
        data.external_id,
        Team,
        {
            "sport_id": sport_id,
            "name": data.name,
            "short_name": data.short_name,
            "logo_url": data.logo_url,
            "primary_color": data.primary_color,
        },
    )


def _upsert_participant(
    session: Session, provider: str, event: Event, data: ParticipantData
) -> EventParticipant:
    team = upsert_team(session, provider, event.sport_id, data.team)
    part = session.scalars(
        select(EventParticipant).where(
            EventParticipant.event_id == event.id,
            EventParticipant.team_id == team.id,
            EventParticipant.player_id.is_(None),
        )
    ).first()
    if part is None:
        part = EventParticipant(event_id=event.id, team_id=team.id, stats={})
        session.add(part)
    part.side = data.side
    if data.score is not None:
        part.score = data.score
    if data.is_winner is not None:
        part.is_winner = data.is_winner
    if data.stats:
        part.stats = data.stats
    return part


def upsert_event(session: Session, provider: str, data: EventData) -> Event:
    season = upsert_season(session, provider, data.competition, data.season_label)
    competition = session.get(Competition, season.competition_id)
    event = _get_or_create(
        session,
        provider,
        "event",
        data.external_id,
        Event,
        {
            "sport_id": competition.sport_id,
            "season_id": season.id,
            "start_time": data.start_time,
            "status": data.status,
            "round": data.round,
            "venue_name": data.venue_name,
            "venue_city": data.venue_city,
        },
    )
    if data.extra:
        event.extra = {**(event.extra or {}), **data.extra}
    session.flush()
    for part in data.participants:
        _upsert_participant(session, provider, event, part)
    session.flush()
    return event


def _upsert_player_stats(
    session: Session, provider: str, event: Event, data: PlayerStatData
) -> None:
    team_id = refs.find_entity_id(session, provider, "team", data.team_external_id)
    player = _get_or_create(
        session,
        provider,
        "player",
        data.player_external_id,
        Player,
        {
            "sport_id": event.sport_id,
            "name": data.player_name,
            "position": data.position,
            "photo_url": data.photo_url,
        },
    )
    if team_id is not None:
        link = session.get(TeamPlayer, (team_id, player.id, event.season_id))
        if link is None:
            session.add(
                TeamPlayer(
                    team_id=team_id,
                    player_id=player.id,
                    season_id=event.season_id,
                    shirt_number=data.shirt_number,
                )
            )
        elif data.shirt_number is not None:
            link.shirt_number = data.shirt_number

    row = session.scalars(
        select(PlayerEventStats).where(
            PlayerEventStats.event_id == event.id, PlayerEventStats.player_id == player.id
        )
    ).first()
    if row is None:
        session.add(
            PlayerEventStats(
                event_id=event.id, player_id=player.id, team_id=team_id, stats=data.stats
            )
        )
    else:
        row.team_id = team_id
        row.stats = data.stats


def upsert_event_detail(
    session: Session, provider: str, detail: EventDetail, now: datetime
) -> Event:
    """Grava o jogo, as estatísticas dos times e dos jogadores.

    `details_synced_at` só é preenchido quando o jogo está encerrado, para que
    o job pós-jogo continue buscando jogos ainda em andamento.
    """
    event = upsert_event(session, provider, detail.event)
    for stat in detail.player_stats:
        _upsert_player_stats(session, provider, event, stat)
    if event.status == "final":
        event.details_synced_at = now
    session.flush()
    return event
