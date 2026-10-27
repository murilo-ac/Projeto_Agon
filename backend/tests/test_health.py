import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://x:x@localhost:5432/x")

from fastapi.testclient import TestClient  # noqa: E402

from app.main_api import app  # noqa: E402


def test_health_sem_banco_retorna_503():
    client = TestClient(app)
    assert client.get("/api/health").status_code == 503
