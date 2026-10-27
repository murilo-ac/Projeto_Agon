import os
from collections.abc import Iterator
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://agon:agon@localhost:5432/agon")

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.exc import OperationalError  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import get_settings  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parent.parent
TEST_DB_NAME = "agon_test"


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Cria (se preciso) o banco agon_test e aplica as migrações nele."""
    base = make_url(get_settings().database_url)
    admin = create_engine(base.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": TEST_DB_NAME}
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL indisponível (rode os testes no container api): {exc.orig}")
    finally:
        admin.dispose()

    url = base.set(database=TEST_DB_NAME).render_as_string(hide_password=False)
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    cfg.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(cfg, "head")
    return url


@pytest.fixture
def session(test_db_url: str) -> Iterator[Session]:
    """Sessão isolada: tudo o que o teste gravar é desfeito ao final."""
    engine = create_engine(test_db_url)
    conn = engine.connect()
    outer = conn.begin()
    sess = Session(bind=conn, join_transaction_mode="create_savepoint", autoflush=False)
    try:
        yield sess
    finally:
        sess.close()
        outer.rollback()
        conn.close()
        engine.dispose()
