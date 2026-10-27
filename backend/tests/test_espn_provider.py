import json
from datetime import UTC, date, datetime
from pathlib import Path

import httpx
import pytest

from app.providers.base import ProviderError, RateLimitError, TransientError
from app.providers.espn import EspnProvider, map_status, parse_scoreboard, parse_summary

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
    assert len(detail.player_stats) > 20

    castillo = next(p for p in detail.player_stats if p.player_name == "Rodrigo Castillo")
    assert castillo.team_external_id == "3445"
    assert castillo.shirt_number == 19
    assert castillo.stats["starter"] is True
    assert castillo.stats["subbedOut"] is True
    assert castillo.stats["totalGoals"] == 1


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
