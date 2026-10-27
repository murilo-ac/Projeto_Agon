from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.db import engine

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="banco indisponível") from exc
    return {"status": "ok"}
