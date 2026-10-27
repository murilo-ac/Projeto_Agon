from fastapi.testclient import TestClient

from app.core.db import get_session
from app.main_api import app


class _SessaoQuebrada:
    def execute(self, *args, **kwargs):
        raise RuntimeError("banco fora do ar")


def test_health_ok(session):
    app.dependency_overrides[get_session] = lambda: session
    try:
        resp = TestClient(app).get("/api/health")
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_health_sem_banco_retorna_503():
    app.dependency_overrides[get_session] = lambda: _SessaoQuebrada()
    try:
        resp = TestClient(app).get("/api/health")
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 503
