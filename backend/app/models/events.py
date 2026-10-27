from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.catalog import Player, Season, Team

EVENT_STATUSES = ("scheduled", "live", "final", "postponed", "canceled")


class Event(TimestampMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'live', 'final', 'postponed', 'canceled')", name="status"
        ),
        Index("ix_events_start_time", "start_time"),
        Index("ix_events_season_id_start_time", "season_id", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    round: Mapped[str | None] = mapped_column(String(60))
    venue_name: Mapped[str | None] = mapped_column(String(160))
    venue_city: Mapped[str | None] = mapped_column(String(100))
    extra: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    # preenchido quando o detalhe (estatísticas) do jogo encerrado foi coletado
    details_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    season: Mapped[Season] = relationship()
    participants: Mapped[list["EventParticipant"]] = relationship(
        back_populates="event", order_by="EventParticipant.id"
    )


class EventParticipant(Base):
    __tablename__ = "event_participants"
    __table_args__ = (
        Index("ix_event_participants_team_id", "team_id"),
        Index("ix_event_participants_player_id", "player_id"),
        Index(
            "uq_event_participants_event_team",
            "event_id",
            "team_id",
            unique=True,
            postgresql_where=text("player_id IS NULL"),
        ),
        Index(
            "uq_event_participants_event_player",
            "event_id",
            "player_id",
            unique=True,
            postgresql_where=text("player_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    player_id: Mapped[int | None] = mapped_column(ForeignKey("players.id"))
    side: Mapped[str | None] = mapped_column(String(10))  # home, away ou nulo
    position: Mapped[int | None] = mapped_column(Integer)
    score: Mapped[int | None] = mapped_column(Integer)
    is_winner: Mapped[bool | None] = mapped_column(Boolean)
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    event: Mapped[Event] = relationship(back_populates="participants")
    team: Mapped[Team | None] = relationship()
    player: Mapped[Player | None] = relationship()


class PlayerEventStats(Base):
    __tablename__ = "player_event_stats"
    __table_args__ = (UniqueConstraint("event_id", "player_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    stats: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    player: Mapped[Player] = relationship()
