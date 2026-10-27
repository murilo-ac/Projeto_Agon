import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError

from app.models import Base, Event, ExternalRef, Sport


def test_migracao_semeia_esportes(session):
    slugs = set(session.scalars(select(Sport.slug)))
    assert slugs == {"football", "basketball", "nfl", "tennis", "f1", "volleyball"}


def test_modelos_e_migracao_estao_sincronizados(test_db_url):
    engine = create_engine(test_db_url)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    engine.dispose()
    assert diff == []


def test_external_ref_unica_por_provedor(session):
    session.add(ExternalRef(entity_type="team", entity_id=1, provider="espn", external_id="3445"))
    session.flush()
    session.add(ExternalRef(entity_type="team", entity_id=2, provider="espn", external_id="3445"))
    with pytest.raises(IntegrityError):
        session.flush()


def test_status_de_evento_invalido_e_rejeitado(session):
    from datetime import UTC, datetime

    from app.models import Competition, Season

    sport = session.scalars(select(Sport).where(Sport.slug == "football")).one()
    comp = Competition(sport_id=sport.id, name="Teste")
    session.add(comp)
    session.flush()
    season = Season(competition_id=comp.id, label="2026")
    session.add(season)
    session.flush()
    session.add(
        Event(sport_id=sport.id, season_id=season.id, start_time=datetime.now(UTC), status="xyz")
    )
    with pytest.raises(IntegrityError):
        session.flush()
