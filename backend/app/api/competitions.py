from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.repositories import queries
from app.schemas.catalog import CompetitionOut

router = APIRouter(prefix="/competitions", tags=["competições"])


@router.get("", response_model=list[CompetitionOut])
def list_competitions(sport: str | None = None, session: Session = Depends(get_session)):
    """Competições conhecidas, opcionalmente filtradas pelo slug do esporte (ex.: `football`)."""
    return [
        CompetitionOut(id=c.id, name=c.name, country=c.country, type=c.type, sport=c.sport.slug)
        for c in queries.list_competitions(session, sport)
    ]
