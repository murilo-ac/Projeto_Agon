import json
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import pytest

from app.providers.base import ProviderError, RateLimitError, TransientError
from app.providers.espn import (
    EspnProvider,
    map_decided_in,
    map_status,
    parse_scoreboard,
    parse_summary,
)

FIXTURES = Path(__file__).parent / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf8"))


def make_provider(handler, max_attempts: int = 3) -> tuple[EspnProvider, list[float]]:
    sleeps: list[float] = []
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return EspnProvider(client=client, max_attempts=max_attempts, sleep=sleeps.append), sleeps


# --- normalização ---------------------------------------------------------------------------


def test_parse_scoreboard():
    events = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")
    assert len(events) == 2

    ev = events[0]
    assert ev.external_id == "401841277"
    assert ev.start_time == datetime(2026, 10, 18, 19, 0, tzinfo=UTC)
    assert ev.status == "final"
    assert ev.season_label == "2026"
    assert ev.competition.external_id == "soccer/bra.1"
    assert ev.competition.sport_slug == "football"
    assert ev.venue_name == "Estadio do Maracana"
    assert ev.venue_city == "Rio de Janeiro"

    home, away = ev.participants
    assert (home.side, home.team.name, home.score) == ("home", "Fluminense", 1)
    assert away.side == "away" and isinstance(away.score, int)
    assert home.team.external_id == "3445"
    assert home.team.logo_url.endswith("/3445.png")
    assert home.team.primary_color == "7E0202"
    assert home.is_winner is not None

    gols = [lance for lance in ev.extra["lances"] if lance["gol"]]
    assert len(gols) == 3
    assert gols[0]["minuto"] == "4'"
    assert gols[0]["jogadores"] == ["Rodrigo Castillo"]
    assert gols[0]["lado"] == "home"
    assert [g["lado"] for g in gols] == ["home", "away", "away"]


def test_jogo_agendado_nao_tem_placar():
    payload = load("espn_scoreboard_bra1.json")
    ev = payload["events"][0]
    ev["status"]["type"] = {"name": "STATUS_SCHEDULED", "state": "pre"}
    for comp in ev["competitions"][0]["competitors"]:
        comp["score"] = "0"
        comp["winner"] = False

    jogo = parse_scoreboard(payload, "soccer")[0]
    assert jogo.status == "scheduled"
    assert [p.score for p in jogo.participants] == [None, None]
    assert [p.is_winner for p in jogo.participants] == [None, None]


def test_parse_scoreboard_sem_jogos():
    payload = {"leagues": [{"slug": "bra.1", "name": "X", "season": {"year": 2026}}], "events": []}
    assert parse_scoreboard(payload, "soccer") == []
    assert parse_scoreboard({"events": []}, "soccer") == []


def test_parse_summary():
    detail = parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1")
    ev = detail.event
    assert ev.external_id == "401841277"
    assert ev.status == "final"
    assert ev.competition.name == "Brazilian Serie A"

    home, away = ev.participants
    assert home.team.external_id == "3445"
    # estatísticas do boxscore achatadas em {nome: valor numérico}
    assert home.stats["foulsCommitted"] == 18
    assert isinstance(home.stats["possessionPct"], float)
    assert set(home.stats) != set()
    assert away.stats

    assert len(ev.extra["lances"]) == 28
    assert {lance["lado"] for lance in ev.extra["lances"]} == {"home", "away", None}
    assert len(detail.player_stats) > 20

    castillo = next(p for p in detail.player_stats if p.player_name == "Rodrigo Castillo")
    assert castillo.team_external_id == "3445"
    assert castillo.shirt_number == 19
    assert castillo.stats["starter"] is True
    assert castillo.stats["subbedOut"] is True
    assert castillo.stats["totalGoals"] == 1
    assert castillo.stats["formationPlace"] == 9


def test_parse_summary_escalacao():
    detail = parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1")
    assert [p.formation for p in detail.event.participants] == ["4-2-3-1", "4-2-3-1"]

    titulares = [p for p in detail.player_stats if p.stats["starter"]]
    assert len(titulares) == 22
    assert sorted(p.stats["formationPlace"] for p in titulares if p.team_external_id == "3445") == list(
        range(1, 12)
    )
    # reservas vêm com formationPlace "0" da ESPN
    assert all(p.stats["formationPlace"] is None for p in detail.player_stats if not p.stats["starter"])


def test_jogo_de_liga_sem_mata_mata():
    santos = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")[0]
    assert [(p.team.name, p.is_winner) for p in santos.participants] == [
        ("Fluminense", False),
        ("Santos", True),
    ]
    assert [p.advanced for p in santos.participants] == [None, None]  # liga não tem mata-mata
    assert santos.decided_in is None and santos.leg is None


def test_lances_tem_codigo():
    scoreboard = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")
    codigos = {lance["codigo"] for ev in scoreboard for lance in ev.extra["lances"]}
    # o scoreboard não traz o código; ele deriva do texto e bate com o do summary
    assert {"goal", "goal---header", "goal---volley", "penalty---scored", "yellow-card"} <= codigos

    summary = parse_summary(load("espn_summary_bra1.json"), "soccer/bra.1")
    codigos = {lance["codigo"] for lance in summary.event.extra["lances"]}
    assert {"kickoff", "goal", "goal---header", "substitution", "yellow-card"} <= codigos


# --- mata-mata com pênaltis (Copa do Brasil 2025, volta das oitavas: Flamengo 1x0, Atlético nos pênaltis)


def test_parse_scoreboard_com_penaltis():
    (jogo,) = parse_scoreboard(load("espn_scoreboard_copa_penaltis.json"), "soccer")
    assert jogo.status == "final"
    assert jogo.decided_in == "penalties"
    assert jogo.leg == 2
    assert jogo.competition.type == "cup"

    cam, fla = jogo.participants
    assert (cam.team.name, cam.side, cam.score) == ("Atlético-MG", "home", 0)
    assert (fla.team.name, fla.side, fla.score) == ("Flamengo", "away", 1)
    # o Flamengo ganhou no tempo normal, mas o vencedor do jogo é quem venceu nos pênaltis
    assert (cam.is_winner, fla.is_winner) == (True, False)
    assert (cam.advanced, fla.advanced) == (True, False)
    assert (cam.shootout_score, fla.shootout_score) == (4, 3)
    assert (cam.aggregate_score, fla.aggregate_score) == (1, 1)


def test_parse_summary_com_penaltis():
    detail = parse_summary(load("espn_summary_copa_penaltis.json"), "soccer/bra.copa_do_brazil")
    ev = detail.event
    assert ev.decided_in == "penalties"
    assert ev.leg == 2

    cam, fla = ev.participants
    assert (cam.is_winner, cam.advanced, cam.shootout_score) == (True, True, 4)
    assert (fla.is_winner, fla.advanced, fla.shootout_score) == (False, False, 3)
    assert (cam.formation, fla.formation) == ("4-3-3", "4-2-3-1")

    assert ev.extra["penaltis"] == {"home": 4, "away": 3}


@pytest.mark.parametrize(
    ("type_", "esperado"),
    [
        ({"name": "STATUS_FULL_TIME", "state": "post"}, None),
        ({"name": "STATUS_FINAL_PEN", "state": "post"}, "penalties"),
        ({"name": "STATUS_FINAL_AET", "state": "post"}, "extra_time"),
        ({"name": "STATUS_SCHEDULED", "state": "pre"}, None),
        ({"name": "STATUS_POSTPONED", "state": "post"}, None),
    ],
)
def test_map_decided_in(type_, esperado):
    assert map_decided_in({"type": type_}) == esperado


# --- pênaltis ----------------------------------------------------------------------------------
# Palmeiras 0x1 Fluminense, semifinal da Libertadores (21/10/2026): 2x2 no agregado e PAL 5-3
# nos pênaltis. Por horas a ESPN marcou `winner` no Fluminense, que venceu o tempo normal.
PAL, FLU = "2029", "3445"


def _flag_errada(competitors: list[dict]) -> None:
    """Reproduz a flag `winner` como a ESPN mostrou por horas depois do jogo."""
    for c in competitors:
        c["winner"] = c["team"]["id"] == FLU


def _scoreboard_penaltis() -> dict:
    payload = load("espn_scoreboard_libertadores_penaltis.json")
    _flag_errada(payload["events"][0]["competitions"][0]["competitors"])
    return payload


def _summary_penaltis() -> dict:
    payload = load("espn_summary_libertadores_penaltis.json")
    _flag_errada(payload["header"]["competitions"][0]["competitors"])
    return payload


def _vencedores(participants) -> dict[str, bool]:
    return {p.team.external_id: p.is_winner for p in participants}


def test_penaltis_decidem_o_vencedor_no_scoreboard():
    (ev,) = parse_scoreboard(_scoreboard_penaltis(), "soccer")
    home, away = ev.participants
    assert (home.team.external_id, home.score) == (PAL, 0)  # perdeu o jogo, passou nos pênaltis
    assert (away.team.external_id, away.score) == (FLU, 1)
    assert _vencedores(ev.participants) == {PAL: True, FLU: False}
    assert ev.extra["penaltis"] == {"home": 5, "away": 3}


def test_penaltis_decidem_o_vencedor_no_summary():
    ev = parse_summary(_summary_penaltis(), "soccer/conmebol.libertadores").event
    assert _vencedores(ev.participants) == {PAL: True, FLU: False}
    assert ev.extra["penaltis"] == {"home": 5, "away": 3}  # a ESPN manda 5.0 no summary


@pytest.mark.parametrize(
    "nota",
    [
        "2nd Leg - Tied on aggregate - PAL win 5-3 on penalties",
        "Palmeiras advance 5-3 on penalties",
    ],
)
def test_sem_placar_dos_penaltis_a_nota_decide(nota):
    payload = _scoreboard_penaltis()
    comp = payload["events"][0]["competitions"][0]
    for c in comp["competitors"]:
        c.pop("shootoutScore")
    comp["notes"] = [{"type": "event", "headline": nota}]
    (ev,) = parse_scoreboard(payload, "soccer")
    assert _vencedores(ev.participants) == {PAL: True, FLU: False}
    assert "penaltis" not in ev.extra


def test_sem_penaltis_vale_a_flag():
    events = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")
    for ev in events:
        comp = next(
            e for e in load("espn_scoreboard_bra1.json")["events"] if e["id"] == ev.external_id
        )["competitions"][0]
        flags = {c["team"]["id"]: bool(c.get("winner")) for c in comp["competitors"]}
        assert _vencedores(ev.participants) == flags
        assert "penaltis" not in ev.extra


@pytest.mark.parametrize(
    ("type_", "esperado"),
    [
        ({"name": "STATUS_SCHEDULED", "state": "pre"}, "scheduled"),
        ({"name": "STATUS_FIRST_HALF", "state": "in"}, "live"),
        ({"name": "STATUS_FULL_TIME", "state": "post"}, "final"),
        ({"name": "STATUS_POSTPONED", "state": "post"}, "postponed"),
        ({"name": "STATUS_CANCELED", "state": "post"}, "canceled"),
        ({"name": "STATUS_ABANDONED", "state": "post"}, "canceled"),
    ],
)
def test_map_status(type_, esperado):
    assert map_status({"type": type_}) == esperado


# --- HTTP, retry e limites -------------------------------------------------------------------


def test_listar_jogos_monta_a_url_e_devolve_o_bruto():
    visto = {}

    def handler(request: httpx.Request) -> httpx.Response:
        visto["url"] = str(request.url)
        return httpx.Response(200, json=load("espn_scoreboard_bra1.json"))

    provider, _ = make_provider(handler)
    result = provider.listar_jogos("soccer/bra.1", date(2026, 10, 18))

    assert visto["url"].endswith("/soccer/bra.1/scoreboard?dates=20261018")
    assert result.raw.endpoint == "soccer/bra.1/scoreboard"
    assert result.raw.params == {"dates": "20261018"}
    assert len(result.data) == 2
    assert provider.requests_used == 1


def test_retry_em_5xx_com_backoff_e_sucesso():
    respostas = [httpx.Response(503), httpx.Response(500), httpx.Response(200, json={"events": []})]

    provider, sleeps = make_provider(lambda request: respostas.pop(0))
    result = provider.listar_jogos("soccer/bra.1", date(2026, 10, 18))

    assert result.data == []
    assert provider.requests_used == 3
    assert len(sleeps) == 2 and sleeps[1] >= sleeps[0]


def test_retry_em_timeout_esgota_as_tentativas():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timeout")

    provider, sleeps = make_provider(handler, max_attempts=3)
    with pytest.raises(TransientError):
        provider.listar_jogos("soccer/bra.1", date(2026, 10, 18))
    assert provider.requests_used == 3
    assert len(sleeps) == 2


def test_429_nao_e_repetido():
    provider, sleeps = make_provider(lambda request: httpx.Response(429))
    with pytest.raises(RateLimitError):
        provider.listar_jogos("soccer/bra.1", date(2026, 10, 18))
    assert provider.requests_used == 1
    assert sleeps == []


def test_4xx_nao_e_repetido():
    provider, _ = make_provider(lambda request: httpx.Response(404))
    with pytest.raises(ProviderError) as exc:
        provider.detalhar_jogo("soccer/bra.1", "1")
    assert not isinstance(exc.value, (TransientError, RateLimitError))
    assert provider.requests_used == 1


def test_resposta_que_nao_e_json_vira_erro():
    provider, _ = make_provider(lambda request: httpx.Response(200, content=b"<html>"))
    with pytest.raises(ProviderError):
        provider.listar_jogos("soccer/bra.1", date(2026, 10, 18))
