from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging(get_settings().log_level)

app = FastAPI(title="Ágon API")
app.include_router(health.router, prefix="/api")
