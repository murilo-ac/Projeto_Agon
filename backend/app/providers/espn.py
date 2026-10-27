"""Adapter da API não-oficial da ESPN (site.api.espn.com).

`liga` é sempre "esporte/slug", como na URL da ESPN (ex.: "soccer/bra.1").
"""

import logging
import time
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import httpx
from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.providers.base import (
    CompetitionData,
    EventData,
    EventDetail,
    Fetch,
    ParticipantData,
    PlayerStatData,
    ProviderError,
    RateLimitError,
    RawResponse,
    TeamData,
    TransientError,
)

log = logging.getLogger(__name__)

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

# esporte da ESPN -> slug interno
SPORT_SLUGS = {"soccer": "football"}
COMPETITION_TYPES = {
    "bra.copa_do_brazil": "cup",
    "conmebol.libertadores": "tournament",
    "conmebol.sudamericana": "tournament",
    "uefa.champions": "tournament",
    "fifa.friendly": "tournament",
}


def _to_number(value: Any) -> Any:
    """Converte "49.9" em 49.9 e "3" em 3; mantém o que não for numérico."""
    if isinstance(value, (int, float)):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return value
    return int(number) if number.is_integer() and "." not in str(value) else number


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_status(status: dict[str, Any]) -> str:
    type_ = status.get("type", {})
    name = type_.get("name", "")
    if "POSTPONED" in name:
        return "postponed"
    if any(word in name for word in ("CANCELED", "CANCELLED", "ABANDONED")):
        return "canceled"
    return {"pre": "scheduled", "in": "live", "post": "final"}.get(type_.get("state"), "scheduled")


def _team(team: dict[str, Any]) -> TeamData:
    logo = team.get("logo")
    if not logo and team.get("logos"):
        logo = team["logos"][0].get("href")
    return TeamData(
        external_id=str(team["id"]),
        name=team.get("displayName") or team.get("name") or str(team["id"]),
        short_name=team.get("shortDisplayName") or team.get("abbreviation"),
        logo_url=logo,
        primary_color=team.get("color"),
    )


def _stats(items: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Achata a lista [{name, displayValue}] em {name: valor}."""
    return {item["name"]: _to_number(item.get("displayValue")) for item in items or [] if "name" in item}


def _lance(item: dict[str, Any]) -> dict[str, Any]:
    """Lance da partida (gol, cartão, substituição...) em formato compacto."""
    players = [
        a.get("displayName")
        for a in (item.get("athletesInvolved") or [p.get("athlete", {}) for p in item.get("participants", [])])
        if a.get("displayName")
    ]
    return {
        "tipo": item.get("type", {}).get("text"),
        "minuto": item.get("clock", {}).get("displayValue") or None,
        "time_id": (item.get("team") or {}).get("id"),
        "jogadores": players,
        "gol": bool(item.get("scoringPlay")),
    }


def _competition(league: dict[str, Any], sport_path: str) -> CompetitionData:
    slug = league["slug"]
    return CompetitionData(
        external_id=f"{sport_path}/{slug}",
        name=league.get("name") or slug,
        sport_slug=SPORT_SLUGS[sport_path],
        type=COMPETITION_TYPES.get(slug, "league"),
    )


def _participants(competitors: list[dict[str, Any]], final: bool, with_stats: bool) -> list[ParticipantData]:
    result = []
    for comp in sorted(competitors, key=lambda c: c.get("order", 0)):
        score = comp.get("score")
        result.append(
            ParticipantData(
                team=_team(comp["team"]),
                side=comp.get("homeAway"),
                score=int(score) if score not in (None, "") else None,
                is_winner=bool(comp.get("winner")) if final else None,
                stats=_stats(comp.get("statistics")) if with_stats else {},
            )
        )
    return result


def parse_scoreboard(payload: dict[str, Any], sport_path: str) -> list[EventData]:
    leagues = payload.get("leagues") or []
    if not leagues:
        return []
    league = leagues[0]
    competition = _competition(league, sport_path)
    league_year = (league.get("season") or {}).get("year")

    events = []
    for ev in payload.get("events", []):
        comp = ev["competitions"][0]
        status = map_status(ev.get("status") or comp.get("status") or {})
        year = (ev.get("season") or {}).get("year") or league_year
        venue = comp.get("venue") or ev.get("venue") or {}
        extra: dict[str, Any] = {}
        if comp.get("details"):
            extra["lances"] = [_lance(d) for d in comp["details"]]
        events.append(
            EventData(
                external_id=str(ev["id"]),
                competition=competition,
                season_label=str(year),
                start_time=_parse_datetime(ev["date"]),
                status=status,
                participants=_participants(comp.get("competitors", []), status == "final", True),
                venue_name=venue.get("fullName"),
                venue_city=(venue.get("address") or {}).get("city"),
                extra=extra,
            )
        )
    return events


def parse_summary(payload: dict[str, Any], liga: str) -> EventDetail:
    sport_path, slug = liga.split("/", 1)
    header = payload["header"]
    comp = header["competitions"][0]
    status = map_status(comp.get("status") or {})
    league = {**header.get("league", {}), "slug": slug}
    competition = _competition(league, sport_path)
    year = (header.get("season") or {}).get("year")

    participants = _participants(comp.get("competitors", []), status == "final", False)
    box_stats = {
        t["team"]["id"]: _stats(t.get("statistics")) for t in payload.get("boxscore", {}).get("teams", [])
    }
    for part in participants:
        part.stats = box_stats.get(part.team.external_id, {})

    venue = payload.get("gameInfo", {}).get("venue") or {}
    extra: dict[str, Any] = {}
    if payload.get("keyEvents"):
        extra["lances"] = [_lance(k) for k in payload["keyEvents"]]
    event = EventData(
        external_id=str(header["id"]),
        competition=competition,
        season_label=str(year),
        start_time=_parse_datetime(comp["date"]),
        status=status,
        participants=participants,
        venue_name=venue.get("fullName"),
        venue_city=(venue.get("address") or {}).get("city"),
        extra=extra,
    )

    player_stats = []
    for roster in payload.get("rosters", []):
        team_id = str(roster["team"]["id"])
        for entry in roster.get("roster", []):
            athlete = entry["athlete"]
            jersey = entry.get("jersey")
            stats = _stats(entry.get("stats"))
            stats.update(
                starter=bool(entry.get("starter")),
                subbedIn=bool(entry.get("subbedIn")),
                subbedOut=bool(entry.get("subbedOut")),
            )
            player_stats.append(
                PlayerStatData(
                    player_external_id=str(athlete["id"]),
                    player_name=athlete.get("fullName") or athlete.get("displayName"),
                    team_external_id=team_id,
                    position=(entry.get("position") or {}).get("abbreviation"),
                    shirt_number=int(jersey) if str(jersey).isdigit() else None,
                    photo_url=(athlete.get("headshot") or {}).get("href"),
                    stats=stats,
                )
            )
    return EventDetail(event=event, player_stats=player_stats)


class EspnProvider:
    name = "espn"

    def __init__(
        self,
        client: httpx.Client | None = None,
        max_attempts: int = 4,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or httpx.Client(timeout=20, headers={"User-Agent": "agon/0.1"})
        self._max_attempts = max_attempts
        self._sleep = sleep
        self.requests_used = 0

    def _request(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        self.requests_used += 1
        try:
            resp = self._client.get(url, params=params)
        except httpx.TransportError as exc:  # inclui timeouts
            raise TransientError(f"falha de rede em {url}: {exc}") from exc
        if resp.status_code == 429:
            raise RateLimitError(f"HTTP 429 em {url}")
        if resp.status_code >= 500:
            raise TransientError(f"HTTP {resp.status_code} em {url}")
        if resp.status_code >= 400:
            raise ProviderError(f"HTTP {resp.status_code} em {url}")
        try:
            return resp.json()
        except ValueError as exc:
            raise ProviderError(f"resposta não é JSON em {url}") from exc

    def _get(self, path: str, params: dict[str, Any]) -> RawResponse:
        retrying = Retrying(
            retry=retry_if_exception_type(TransientError),
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=30),
            sleep=self._sleep,
            before_sleep=lambda state: log.warning(
                "tentativa %s falhou em %s: %s", state.attempt_number, path, state.outcome.exception()
            ),
        )
        try:
            payload = retrying(self._request, f"{BASE_URL}/{path}", params)
        except RetryError as exc:  # esgotou as tentativas
            raise exc.last_attempt.exception() from None
        return RawResponse(endpoint=path, params=params, payload=payload)

    def listar_jogos(self, liga: str, dia: date) -> Fetch[list[EventData]]:
        raw = self._get(f"{liga}/scoreboard", {"dates": dia.strftime("%Y%m%d")})
        return Fetch(raw=raw, data=parse_scoreboard(raw.payload, liga.split("/", 1)[0]))

    def detalhar_jogo(self, liga: str, event_id: str) -> Fetch[EventDetail]:
        raw = self._get(f"{liga}/summary", {"event": event_id})
        return Fetch(raw=raw, data=parse_summary(raw.payload, liga))
