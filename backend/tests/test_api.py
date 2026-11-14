import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.db import get_session
from app.main_api import app
from app.models import SyncRun, Team
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


def test_detalhe_traz_formacao_e_codigo_dos_lances(client):
    jogo = client.get(f"/api/events/{event_id(client)}").json()
    assert [p["formation"] for p in jogo["participants"]] == ["4-2-3-1", "4-2-3-1"]
    assert all(lance["codigo"] for lance in jogo["lances"])
    assert jogo["penaltis"] is None
    assert (jogo["leg"], jogo["decided_in"]) == (None, None)


def test_jogo_decidido_nos_penaltis(client, session):
    ingest.upsert_event_detail(
        session,
        "espn",
        parse_summary(load("espn_summary_copa_penaltis.json"), "soccer/bra.copa_do_brazil"),
        AGORA,
    )
    session.flush()
    (resumo,) = client.get("/api/events", params={"date": "2025-08-06"}).json()
    assert (resumo["leg"], resumo["decided_in"]) == (2, "penalties")
    cam, fla = resumo["participants"]
    assert (cam["score"], cam["is_winner"], cam["advanced"], cam["shootout_score"]) == (0, True, True, 4)
    assert (fla["score"], fla["is_winner"], fla["advanced"], fla["shootout_score"]) == (1, False, False, 3)
    assert cam["aggregate_score"] == fla["aggregate_score"] == 1

    jogo = client.get(f"/api/events/{resumo['id']}").json()
    assert jogo["penaltis"] == {"home": 4, "away": 3}


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


def test_busca_de_times(client):
    assert [t["name"] for t in client.get("/api/teams", params={"q": "flumi"}).json()] == ["Fluminense"]
    # acento e caixa não importam, nos dois sentidos
    assert [t["name"] for t in client.get("/api/teams", params={"q": "GREMIO"}).json()] == ["Grêmio"]
    assert [t["name"] for t in client.get("/api/teams", params={"q": "cruzéiro"}).json()] == ["Cruzeiro"]
    assert client.get("/api/teams", params={"q": "xyz"}).json() == []


def test_busca_de_times_prioriza_quem_comeca_pelo_texto(client, session):
    santos = session.scalars(select(Team).where(Team.name == "Santos")).one()
    session.add(Team(sport_id=santos.sport_id, name="Clube Santista"))
    session.flush()
    nomes = [t["name"] for t in client.get("/api/teams", params={"q": "sant"}).json()]
    assert nomes == ["Santos", "Clube Santista"]
    assert len(client.get("/api/teams", params={"q": "sant", "limit": 1}).json()) == 1


@pytest.mark.parametrize("params", [{}, {"q": "a"}, {"q": "fl", "limit": 0}])
def test_busca_de_times_parametros_invalidos(client, params):
    assert client.get("/api/teams", params=params).status_code == 422


def test_busca_de_times_trata_curingas_como_texto(client):
    assert client.get("/api/teams", params={"q": "%%"}).json() == []
    assert client.get("/api/teams", params={"q": "__"}).json() == []


def test_jogos_do_time_com_filtros(client, session):
    tid = team_id(session, "Fluminense")
    base = f"/api/teams/{tid}/events"
    assert len(client.get(base, params={"status": "final"}).json()) == 1
    assert client.get(base, params={"status": "scheduled"}).json() == []
    assert client.get(base, params={"status": "invalido"}).status_code == 422
    assert client.get(base, params={"limit": 0}).status_code == 422
    assert client.get(base, params={"order": "asc", "limit": 1}).status_code == 200


# --- status --------------------------------------------------------------------------------------


def test_status_sem_coletas(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    status = resp.json()
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    assert status["last_sync_at"] is None
    assert status["jobs"] == {}
    assert status["dates"]["first"] == "2026-10-18"  # o jogo mais antigo do banco
    assert status["dates"]["last"] == (hoje + timedelta(days=7)).isoformat()


def test_status_usa_a_ultima_coleta_que_gravou_dados(client, session):
    def run(job, status, finished):
        session.add(SyncRun(job=job, provider="espn", status=status, finished_at=finished))

    run("calendar", "success", datetime(2026, 10, 27, 8, 0, tzinfo=UTC))
    run("calendar", "failed", datetime(2026, 10, 27, 9, 0, tzinfo=UTC))
    run("postgame", "partial", datetime(2026, 10, 27, 10, 0, tzinfo=UTC))
    run("postgame", "rate_limited", datetime(2026, 10, 27, 11, 0, tzinfo=UTC))
    session.flush()

    status = client.get("/api/status").json()
    assert status["jobs"] == {"calendar": "2026-10-27T08:00:00Z", "postgame": "2026-10-27T10:00:00Z"}
    assert status["last_sync_at"] == "2026-10-27T10:00:00Z"


def test_status_respeita_o_fuso(client):
    # o jogo das 19:00 UTC do dia 18 já é dia 19 em Tóquio
    assert client.get("/api/status", params={"tz": "Asia/Tokyo"}).json()["dates"]["first"] == "2026-10-19"
    assert client.get("/api/status", params={"tz": "Marte/Olimpo"}).status_code == 422
