from datetime import date, datetime

from pydantic import BaseModel


class DateRange(BaseModel):
    first: date  # primeiro dia com jogo no banco (hoje, se ainda não há jogos)
    last: date  # hoje + a janela do calendário


class StatusOut(BaseModel):
    last_sync_at: datetime | None = None  # última coleta que gravou dados, de qualquer job
    jobs: dict[str, datetime] = {}  # última coleta que gravou dados, por job
    dates: DateRange
