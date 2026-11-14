import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select

from app.models import (
    Competition,
    Event,
    EventParticipant,
    ExternalRef,
    Player,
    PlayerEventStats,
    Season,
    Team,
    TeamPlayer,
)
from app.providers.espn import parse_scoreboard, parse_summary
from app.repositories import ingest

FIXTURES = Path(__file__).parent / "fixtures"
AGORA = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf8"))


def count(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


def snapshot(session) -> dict[str, int]:
    models = [Competition, Season, Team, Player, TeamPlayer, Event, EventParticipant]
    models += [PlayerEventStats, ExternalRef]
    return {m.__name__: count(session, m) for m in models}


def test_calendario_cria_catalogo_e_jogos(session):
    for ev in parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer"):
        ingest.upsert_event(session, "espn", ev)

    assert count(session, Competition) == 1
    assert count(session, Season) == 1
    assert count(session, Event) == 2
    assert count(session, EventParticipant) == 4

    event = session.scalars(
        select(Event).join(ExternalRef, ExternalRef.entity_id == Event.id).where(
            ExternalRef.entity_type == "event", ExternalRef.external_id == "401841277"
        )
    ).one()
    assert event.status == "final"
    assert event.venue_name == "Estadio do Maracana"
    assert [p.side for p in event.participants] == ["home", "away"]
    assert event.participants[0].team.name == "Fluminense"
    assert event.participants[0].score == 1
    assert event.details_synced_at is None


def test_rodar_a_coleta_duas_vezes_nao_duplica(session):
    eventos = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")
    for ev in eventos:
        ingest.upsert_event(session, "espn", ev)
    antes = snapshot(session)

    for ev in parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer"):
        ingest.upsert_event(session, "espn", ev)

    assert snapshot(session) == antes


def test_detalhe_grava_estatisticas_e_elencos(session):
    detail = parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1")
    event = ingest.upsert_event_detail(session, "espn", detail, AGORA)

    assert event.details_synced_at == AGORA
    assert event.participants[0].stats["foulsCommitted"] == 18
    assert len(event.extra["lances"]) == 28
    assert count(session, PlayerEventStats) == len(detail.player_stats)
    assert count(session, Player) == len(detail.player_stats)
    assert count(session, TeamPlayer) == len(detail.player_stats)

    castillo = session.scalars(select(Player).where(Player.name == "Rodrigo Castillo")).one()
    stats = session.scalars(
        select(PlayerEventStats).where(PlayerEventStats.player_id == castillo.id)
    ).one()
    assert stats.stats["totalGoals"] == 1
    link = session.scalars(select(TeamPlayer).where(TeamPlayer.player_id == castillo.id)).one()
    assert link.shirt_number == 19


def test_detalhe_duas_vezes_nao_duplica(session):
    ingest.upsert_event_detail(
        session, "espn", parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1"), AGORA
    )
    antes = snapshot(session)

    ingest.upsert_event_detail(
        session, "espn", parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1"), AGORA
    )
    assert snapshot(session) == antes


def test_calendario_depois_do_detalhe_preserva_estatisticas_e_lances(session):
    ingest.upsert_event_detail(
        session, "espn", parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1"), AGORA
    )
    # o scoreboard também traz estatísticas (menos completas) e lances próprios
    for ev in parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer"):
        ev.participants[0].stats = {}
        ev.extra = {}
        ingest.upsert_event(session, "espn", ev)

    event = session.scalars(select(Event).where(Event.id.in_(select(ExternalRef.entity_id).where(
        ExternalRef.entity_type == "event", ExternalRef.external_id == "401841277"
    )))).one()
    assert event.participants[0].stats["foulsCommitted"] == 18
    assert len(event.extra["lances"]) == 28
    assert event.details_synced_at == AGORA


def test_mata_mata_grava_penaltis_agregado_e_formacao(session):
    detail = parse_summary(load("espn_summary_copa_penaltis.json"), "soccer/bra.copa_do_brazil")
    event = ingest.upsert_event_detail(session, "espn", detail, AGORA)

    assert (event.leg, event.decided_in) == (2, "penalties")
    cam, fla = event.participants
    assert (cam.score, cam.is_winner, cam.advanced, cam.shootout_score, cam.aggregate_score) == (
        0, True, True, 4, 1,
    )
    assert (fla.score, fla.is_winner, fla.advanced, fla.shootout_score, fla.aggregate_score) == (
        1, False, False, 3, 1,
    )
    assert (cam.formation, fla.formation) == ("4-3-3", "4-2-3-1")
    assert event.extra["penaltis"] == {"home": 4, "away": 3}


def test_calendario_depois_do_detalhe_preserva_penaltis(session):
    ingest.upsert_event_detail(
        session,
        "espn",
        parse_summary(load("espn_summary_copa_penaltis.json"), "soccer/bra.copa_do_brazil"),
        AGORA,
    )
    (ev,) = parse_scoreboard(load("espn_scoreboard_copa_penaltis.json"), "soccer")
    event = ingest.upsert_event(session, "espn", ev)

    assert event.extra["penaltis"] == {"home": 4, "away": 3}
    assert event.participants[0].formation == "4-3-3"  # nem a formação
    assert event.participants[0].shootout_score == 4


def test_detalhe_de_jogo_nao_encerrado_nao_marca_como_sincronizado(session):
    detail = parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1")
    detail.event.status = "live"
    event = ingest.upsert_event_detail(session, "espn", detail, AGORA)
    assert event.details_synced_at is None
