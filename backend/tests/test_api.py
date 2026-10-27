import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.db import get_session
from app.main_api import app
from app.models import Team
from app.providers.espn import parse_scoreboard, parse_summary
from app.repositories import ingest

FIXTURES = Path(__file__).parent / "fixtures"
AGORA = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf8"))


@pytest.fixture
def client(session):
    """API com a sessão de teste e dois jogos: um com detalhe completo e outro só do calendário."""
    for ev in parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer"):
        ingest.upsert_event(session, "espn", ev)
    ingest.upsert_event_detail(
        session, "espn", parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1"), AGORA
    )
    session.flush()
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def event_id(client, external_home: str = "Fluminense") -> int:
    jogos = client.get("/api/events", params={"date": "2026-10-18"}).json()
    return next(j["id"] for j in jogos if j["participants"][0]["team"]["name"] == external_home)


# --- competições ---------------------------------------------------------------------------------


def test_lista_competicoes(client):
    resp = client.get("/api/competitions")
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "id": resp.json()[0]["id"],
            "name": "Brazilian Serie A",
            "country": None,
            "type": "league",
            "sport": "football",
        }
    ]


def test_competicoes_filtradas_por_esporte(client):
    assert len(client.get("/api/competitions", params={"sport": "football"}).json()) == 1
    assert client.get("/api/competitions", params={"sport": "tennis"}).json() == []


# --- agenda --------------------------------------------------------------------------------------


def test_agenda_do_dia_no_fuso_de_sao_paulo(client):
    resp = client.get("/api/events", params={"date": "2026-10-18"})
    assert resp.status_code == 200
    jogos = resp.json()
    assert len(jogos) == 2

    jogo = jogos[0]
    assert jogo["status"] == "final"
    assert jogo["sport"] == "football"
    assert jogo["competition"]["name"] == "Brazilian Serie A"
    assert jogo["season"] == "2026"
    home, away = jogo["participants"]
    assert (home["side"], home["team"]["name"], home["score"]) == ("home", "Fluminense", 1)
    assert away["side"] == "away" and away["team"]["logo_url"]
    assert "stats" not in home  # o resumo não carrega as estatísticas


def test_agenda_respeita_o_fuso(client):
    # 19:00 UTC do dia 18 = 04:00 do dia 19 em Tóquio
    assert len(client.get("/api/events", params={"date": "2026-10-19", "tz": "Asia/Tokyo"}).json()) == 2
    assert client.get("/api/events", params={"date": "2026-10-19"}).json() == []


def test_agenda_filtra_por_competicao_e_esporte(client):
    comp_id = client.get("/api/competitions").json()[0]["id"]
    params = {"date": "2026-10-18"}
    assert len(client.get("/api/events", params={**params, "competition_id": comp_id}).json()) == 2
    assert client.get("/api/events", params={**params, "competition_id": comp_id + 99}).json() == []
    assert len(client.get("/api/events", params={**params, "sport": "football"}).json()) == 2
    assert client.get("/api/events", params={**params, "sport": "tennis"}).json() == []


def test_agenda_sem_data_usa_hoje(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.parametrize("params", [{"date": "18/10/2026"}, {"date": "2026-10-18", "tz": "Marte/Olimpo"}])
def test_agenda_parametros_invalidos(client, params):
    assert client.get("/api/events", params=params).status_code == 422


# --- detalhe do jogo -----------------------------------------------------------------------------


def test_detalhe_do_jogo(client):
    resp = client.get(f"/api/events/{event_id(client)}")
    assert resp.status_code == 200
    jogo = resp.json()

    assert jogo["venue_name"] == "Estadio do Maracana"
    home, away = jogo["participants"]
    assert home["stats"]["foulsCommitted"] == 18
    assert away["stats"]

    assert len(jogo["lances"]) == 28
    gol = next(lance for lance in jogo["lances"] if lance["gol"])
    assert gol["minuto"] == "4'" and gol["lado"] == "home" and gol["jogadores"][0] == "Rodrigo Castillo"

    castillo = next(p for p in jogo["players"] if p["name"] == "Rodrigo Castillo")
    assert castillo["shirt_number"] == 19
    assert castillo["side"] == "home"
    assert castillo["stats"]["totalGoals"] == 1
    assert castillo["stats"]["starter"] is True
    assert home["team"]["id"] == castillo["team_id"]


def test_detalhe_de_jogo_sem_detalhe_coletado(client):
    resp = client.get(f"/api/events/{event_id(client, 'Grêmio')}")
    assert resp.status_code == 200
    jogo = resp.json()
    assert jogo["players"] == []  # o elenco só vem do job pós-jogo
    assert jogo["participants"][0]["team"]["name"] == "Grêmio"
    assert isinstance(jogo["lances"], list)  # os lances do calendário (gols e cartões) já existem


def test_jogo_inexistente_retorna_404(client):
    assert client.get("/api/events/999999").status_code == 404


def test_id_de_jogo_invalido_retorna_422(client):
    assert client.get("/api/events/abc").status_code == 422


# --- times ---------------------------------------------------------------------------------------


def team_id(session, name: str) -> int:
    return session.scalars(select(Team.id).where(Team.name == name)).one()


def test_time(client, session):
    resp = client.get(f"/api/teams/{team_id(session, 'Fluminense')}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Fluminense"
    assert resp.json()["primary_color"] == "7E0202"


def test_time_inexistente(client):
    assert client.get("/api/teams/999999").status_code == 404
    assert client.get("/api/teams/999999/events").status_code == 404


def test_jogos_do_time(client, session):
    resp = client.get(f"/api/teams/{team_id(session, 'Fluminense')}/events")
    assert resp.status_code == 200
    jogos = resp.json()
    assert len(jogos) == 1
    assert "Fluminense" in [p["team"]["name"] for p in jogos[0]["participants"]]


def test_jogos_do_time_com_filtros(client, session):
    tid = team_id(session, "Fluminense")
    base = f"/api/teams/{tid}/events"
    assert len(client.get(base, params={"status": "final"}).json()) == 1
    assert client.get(base, params={"status": "scheduled"}).json() == []
    assert client.get(base, params={"status": "invalido"}).status_code == 422
    assert client.get(base, params={"limit": 0}).status_code == 422
    assert client.get(base, params={"order": "asc", "limit": 1}).status_code == 200
