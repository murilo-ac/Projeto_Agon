"""Consultas de leitura usadas pela API."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

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


def _event_query():
    return select(Event).options(
        joinedload(Event.season).joinedload(Season.competition).joinedload(Competition.sport),
        selectinload(Event.participants).joinedload(EventParticipant.team),
    )


def list_competitions(session: Session, sport_slug: str | None = None) -> list[Competition]:
    stmt = select(Competition).options(joinedload(Competition.sport)).order_by(Competition.name)
    if sport_slug:
        stmt = stmt.join(Sport).where(Sport.slug == sport_slug)
    return list(session.scalars(stmt))


def list_events_between(
    session: Session,
    start: datetime,
    end: datetime,
    competition_id: int | None = None,
    sport_slug: str | None = None,
) -> list[Event]:
    stmt = _event_query().where(Event.start_time >= start, Event.start_time < end)
    if competition_id is not None:
        stmt = stmt.join(Season, Season.id == Event.season_id).where(
            Season.competition_id == competition_id
        )
    if sport_slug:
        stmt = stmt.where(Event.sport_id == select(Sport.id).where(Sport.slug == sport_slug).scalar_subquery())
    return list(session.scalars(stmt.order_by(Event.start_time, Event.id)).unique())


def get_event(session: Session, event_id: int) -> Event | None:
    return session.scalars(_event_query().where(Event.id == event_id)).unique().first()


def event_players(session: Session, event: Event) -> list[tuple[PlayerEventStats, Player, int | None]]:
    """Estatísticas por jogador no jogo, com o número da camisa na temporada."""
    stmt = (
        select(PlayerEventStats, Player, TeamPlayer.shirt_number)
        .join(Player, Player.id == PlayerEventStats.player_id)
        .outerjoin(
            TeamPlayer,
            (TeamPlayer.team_id == PlayerEventStats.team_id)
            & (TeamPlayer.player_id == PlayerEventStats.player_id)
            & (TeamPlayer.season_id == event.season_id),
        )
        .where(PlayerEventStats.event_id == event.id)
        .order_by(PlayerEventStats.id)
    )
    return [(row[0], row[1], row[2]) for row in session.execute(stmt)]


def get_team(session: Session, team_id: int) -> Team | None:
    return session.get(Team, team_id)


def list_events_by_team(
    session: Session,
    team_id: int,
    status: str | None = None,
    descending: bool = True,
    limit: int = 20,
) -> list[Event]:
    stmt = _event_query().where(
        Event.id.in_(select(EventParticipant.event_id).where(EventParticipant.team_id == team_id))
    )
    if status:
        stmt = stmt.where(Event.status == status)
    order = (Event.start_time.desc(), Event.id.desc()) if descending else (Event.start_time, Event.id)
    return list(session.scalars(stmt.order_by(*order).limit(limit)).unique())
