import json
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.ingestion import calendar, postgame
from app.ingestion.recovery import run_recovery
from app.models import Event, ExternalRef, RawPayload, SyncRun
from app.providers.base import Fetch, ProviderError, RateLimitError, RawResponse
from app.providers.espn import parse_scoreboard, parse_summary
from app.repositories import ingest

FIXTURES = Path(__file__).parent / "fixtures"
LIGA = "soccer/bra.1"
# os dois jogos da fixture começaram em 18/10/2026 19:00 UTC
CLOCK_POS_JOGO = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)
JOGO_COM_DETALHE = "401841277"
JOGO_SEM_DETALHE = "401841276"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf8"))


class FakeProvider:
    name = "espn"

    def __init__(self, falhas: dict | None = None):
        self.requests_used = 0
        self.falhas = falhas or {}  # chave (dia ou id do jogo) -> exceção
        self.chamadas: list = []
        self.closed = False

    def close(self) -> None:
        self.closed = True

    def listar_jogos(self, liga: str, dia: date):
        self.requests_used += 1
        self.chamadas.append(dia)
        if dia in self.falhas:
            raise self.falhas[dia]
        payload = load("espn_scoreboard_bra1.json")
        raw = RawResponse(f"{liga}/scoreboard", {"dates": dia.strftime("%Y%m%d")}, payload)
        return Fetch(raw, parse_scoreboard(payload, "soccer"))

    def detalhar_jogo(self, liga: str, event_id: str):
        self.requests_used += 1
        self.chamadas.append(event_id)
        if event_id in self.falhas:
            raise self.falhas[event_id]
        payload = load("espn_summary_bra1.json")
        return Fetch(RawResponse(f"{liga}/summary", {"event": event_id}, payload), parse_summary(payload, liga))


@pytest.fixture
def factory(session):
    return lambda: session


def runs(session) -> list[SyncRun]:
    return list(session.scalars(select(SyncRun).order_by(SyncRun.id)))


def contar(session, model) -> int:
    return session.scalar(select(func.count()).select_from(model))


def semear_calendario(session, factory):
    calendar.run_calendar(factory, FakeProvider(), [LIGA], date(2026, 10, 18), 0, 0)
    session.query(SyncRun).delete()
    session.query(RawPayload).delete()
    session.commit()


def evento(session, external_id: str) -> Event:
    return session.scalars(
        select(Event).where(
            Event.id.in_(
                select(ExternalRef.entity_id).where(
                    ExternalRef.entity_type == "event", ExternalRef.external_id == external_id
                )
            )
        )
    ).one()


# --- calendário --------------------------------------------------------------------------------


def test_calendario_grava_jogos_payloads_e_sync_run(session, factory):
    provider = FakeProvider()
    run = calendar.run_calendar(factory, provider, [LIGA], date(2026, 10, 18), 0, 1)

    assert run.status == "success"
    assert run.requests_used == 2
    assert run.finished_at is not None and run.error is None
    assert contar(session, Event) == 2
    assert contar(session, RawPayload) == 2


def test_calendario_duas_execucoes_nao_duplicam_jogos(session, factory):
    calendar.run_calendar(factory, FakeProvider(), [LIGA], date(2026, 10, 18), 0, 0)
    calendar.run_calendar(factory, FakeProvider(), [LIGA], date(2026, 10, 18), 0, 0)

    assert contar(session, Event) == 2
    assert [r.status for r in runs(session)] == ["success", "success"]


def test_calendario_erro_numa_unidade_nao_derruba_as_outras(session, factory):
    falhas = {date(2026, 10, 18): ProviderError("HTTP 404")}
    run = calendar.run_calendar(factory, FakeProvider(falhas), [LIGA], date(2026, 10, 18), 0, 1)

    assert run.status == "partial"
    assert "2026-10-18" in run.error and "HTTP 404" in run.error
    assert contar(session, Event) == 2  # o dia seguinte foi gravado


def test_calendario_com_tudo_falhando_fica_failed(session, factory):
    falhas = {date(2026, 10, 18): ProviderError("x")}
    run = calendar.run_calendar(factory, FakeProvider(falhas), [LIGA], date(2026, 10, 18), 0, 0)
    assert run.status == "failed"


def test_calendario_bug_de_parse_desfaz_a_unidade_e_segue(session, factory):
    class QuebraNoPrimeiro(FakeProvider):
        def listar_jogos(self, liga, dia):
            fetch = super().listar_jogos(liga, dia)
            if len(self.chamadas) == 1:
                fetch.data[0].competition = None  # estoura dentro do upsert
            return fetch

    run = calendar.run_calendar(factory, QuebraNoPrimeiro(), [LIGA], date(2026, 10, 18), 0, 1)

    assert run.status == "partial"
    assert contar(session, Event) == 2
    assert contar(session, RawPayload) == 1  # a unidade com erro foi desfeita por inteiro


def test_calendario_429_para_o_job_sem_insistir(session, factory):
    falhas = {date(2026, 10, 18): RateLimitError("HTTP 429")}
    provider = FakeProvider(falhas)
    run = calendar.run_calendar(
        factory, provider, [LIGA, "soccer/uefa.champions"], date(2026, 10, 18), 0, 3
    )

    assert run.status == "rate_limited"
    assert provider.requests_used == 1  # nenhuma outra requisição depois do 429
    assert run.requests_used == 1


# --- pós-jogo ----------------------------------------------------------------------------------


def test_posjogo_busca_detalhe_e_marca_como_sincronizado(session, factory):
    semear_calendario(session, factory)
    falhas = {JOGO_SEM_DETALHE: ProviderError("HTTP 500")}
    provider = FakeProvider(falhas)

    run = postgame.run_postgame(factory, provider, clock=lambda: CLOCK_POS_JOGO)

    assert run.status == "partial"
    assert run.requests_used == 2
    assert evento(session, JOGO_COM_DETALHE).details_synced_at == CLOCK_POS_JOGO
    assert evento(session, JOGO_SEM_DETALHE).details_synced_at is None
    assert contar(session, RawPayload) == 1


def test_posjogo_tenta_de_novo_so_o_que_ficou_pendente(session, factory):
    semear_calendario(session, factory)
    postgame.run_postgame(
        factory, FakeProvider({JOGO_SEM_DETALHE: ProviderError("x")}), clock=lambda: CLOCK_POS_JOGO
    )

    provider = FakeProvider()
    postgame.run_postgame(factory, provider, clock=lambda: CLOCK_POS_JOGO)

    assert provider.chamadas == [JOGO_SEM_DETALHE]


def test_posjogo_sem_pendencias_nao_registra_execucao(session, factory):
    provider = FakeProvider()
    assert postgame.run_postgame(factory, provider, clock=lambda: CLOCK_POS_JOGO) is None
    assert provider.requests_used == 0
    assert runs(session) == []


def test_posjogo_ignora_jogo_que_ainda_nao_deveria_ter_terminado(session, factory):
    semear_calendario(session, factory)
    durante_o_jogo = datetime(2026, 10, 18, 20, 30, tzinfo=UTC)  # 1h30 após o início

    provider = FakeProvider()
    assert postgame.run_postgame(factory, provider, clock=lambda: durante_o_jogo) is None
    assert provider.requests_used == 0


def test_posjogo_ignora_jogo_fora_da_janela_de_recuperacao(session, factory):
    semear_calendario(session, factory)
    muito_depois = CLOCK_POS_JOGO + timedelta(days=30)

    assert postgame.run_postgame(factory, FakeProvider(), clock=lambda: muito_depois) is None


def test_posjogo_ignora_jogo_cancelado_ou_adiado(session, factory):
    semear_calendario(session, factory)
    evento(session, JOGO_COM_DETALHE).status = "postponed"
    evento(session, JOGO_SEM_DETALHE).status = "canceled"
    session.flush()

    assert postgame.run_postgame(factory, FakeProvider(), clock=lambda: CLOCK_POS_JOGO) is None


def test_posjogo_refaz_jogo_com_detalhe_mas_ainda_nao_final(session, factory):
    semear_calendario(session, factory)
    postgame.run_postgame(factory, FakeProvider(), clock=lambda: CLOCK_POS_JOGO)
    ev = evento(session, JOGO_COM_DETALHE)
    ev.status = "live"  # ex.: o calendário viu o jogo em andamento depois
    session.flush()

    provider = FakeProvider()
    postgame.run_postgame(factory, provider, clock=lambda: CLOCK_POS_JOGO)

    assert JOGO_COM_DETALHE in provider.chamadas
    assert evento(session, JOGO_COM_DETALHE).status == "final"


def test_posjogo_429_para_o_job(session, factory):
    semear_calendario(session, factory)
    provider = FakeProvider({JOGO_COM_DETALHE: RateLimitError("429"), JOGO_SEM_DETALHE: RateLimitError("429")})

    run = postgame.run_postgame(factory, provider, clock=lambda: CLOCK_POS_JOGO)

    assert run.status == "rate_limited"
    assert provider.requests_used == 1
    assert evento(session, JOGO_COM_DETALHE).details_synced_at is None


# --- recuperação ---------------------------------------------------------------------------------


def test_recuperacao_sem_historico_roda_calendario_e_posjogo(session, factory):
    criados: list[FakeProvider] = []

    def provider_factory():
        criados.append(FakeProvider())
        return criados[-1]

    run_recovery(
        factory, provider_factory, "espn", [LIGA], lambda: date(2026, 10, 18), 0, 0,
        clock=lambda: CLOCK_POS_JOGO,
    )

    assert [r.job for r in runs(session)] == ["calendar", "postgame"]
    assert all(p.closed for p in criados)
    assert evento(session, JOGO_COM_DETALHE).details_synced_at is not None


def test_recuperacao_com_calendario_recente_so_roda_posjogo(session, factory):
    semear_calendario(session, factory)
    session.add(
        SyncRun(
            job="calendar", provider="espn", status="success", requests_used=99,
            started_at=CLOCK_POS_JOGO - timedelta(hours=3),
            finished_at=CLOCK_POS_JOGO - timedelta(hours=3),
        )
    )
    session.commit()

    run_recovery(
        factory, FakeProvider, "espn", [LIGA], lambda: date(2026, 10, 19), 0, 0,
        clock=lambda: CLOCK_POS_JOGO,
    )

    assert [r.job for r in runs(session)] == ["calendar", "postgame"]  # o calendar é o semeado
    assert runs(session)[0].requests_used == 99  # não houve novo calendário


def test_recuperacao_com_calendario_velho_roda_calendario(session, factory):
    session.add(
        SyncRun(
            job="calendar", provider="espn", status="success", requests_used=1,
            started_at=CLOCK_POS_JOGO - timedelta(days=2),
            finished_at=CLOCK_POS_JOGO - timedelta(days=2),
        )
    )
    session.commit()

    run_recovery(
        factory, FakeProvider, "espn", [LIGA], lambda: date(2026, 10, 19), 0, 0,
        clock=lambda: CLOCK_POS_JOGO,
    )

    assert [r.job for r in runs(session)].count("calendar") == 2


def test_ingest_e_job_compartilham_o_mesmo_banco(session):
    # garante que o fixture de sessão enxerga o que os repositórios gravam
    ev = parse_scoreboard(load("espn_scoreboard_bra1.json"), "soccer")[0]
    ingest.upsert_event(session, "espn", ev)
    assert contar(session, Event) == 1
