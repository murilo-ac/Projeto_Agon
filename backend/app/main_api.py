from fastapi import FastAPI

from app.api import competitions, events, health, status, teams
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging(get_settings().log_level)

app = FastAPI(title="Ágon API")
for module in (health, status, competitions, events, teams):
    app.include_router(module.router, prefix="/api")
