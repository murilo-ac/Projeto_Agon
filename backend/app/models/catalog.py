from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(30), unique=True)
    name: Mapped[str] = mapped_column(String(60))


class Competition(TimestampMixin, Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str | None] = mapped_column(String(60))
    # league, cup, tournament, race_series
    type: Mapped[str] = mapped_column(String(20), default="league")
    gender: Mapped[str | None] = mapped_column(String(10))

    sport: Mapped[Sport] = relationship()


class Season(TimestampMixin, Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("competition_id", "label"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"))
    label: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)

    competition: Mapped[Competition] = relationship()


class Team(TimestampMixin, Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    name: Mapped[str] = mapped_column(String(120))
    short_name: Mapped[str | None] = mapped_column(String(40))
    country: Mapped[str | None] = mapped_column(String(60))
    is_national_team: Mapped[bool] = mapped_column(Boolean, default=False)
    logo_url: Mapped[str | None] = mapped_column(String(300))
    primary_color: Mapped[str | None] = mapped_column(String(10))


class Player(TimestampMixin, Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"))
    name: Mapped[str] = mapped_column(String(120))
    nationality: Mapped[str | None] = mapped_column(String(60))
    birth_date: Mapped[date | None] = mapped_column(Date)
    position: Mapped[str | None] = mapped_column(String(30))
    photo_url: Mapped[str | None] = mapped_column(String(300))


class TeamPlayer(Base):
    __tablename__ = "team_players"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), primary_key=True)
    shirt_number: Mapped[int | None] = mapped_column(Integer)
