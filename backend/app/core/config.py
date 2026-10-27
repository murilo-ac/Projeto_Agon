from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_ESPN_LEAGUES = ",".join(
    [
        "soccer/bra.1",
        "soccer/bra.copa_do_brazil",
        "soccer/conmebol.libertadores",
        "soccer/conmebol.sudamericana",
        "soccer/uefa.champions",
        "soccer/fifa.friendly",
    ]
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    log_level: str = "INFO"
    api_sports_key: str = ""

    # coleta
    espn_leagues: str = DEFAULT_ESPN_LEAGUES  # "esporte/liga" separados por vírgula
    worker_timezone: str = "America/Sao_Paulo"
    calendar_hour: int = 5
    calendar_days_back: int = 1
    calendar_days_ahead: int = 7
    postgame_interval_minutes: int = 20
    postgame_min_age_minutes: int = 120  # tempo após o início até o jogo "dever" ter terminado
    postgame_lookback_days: int = 7

    @property
    def espn_league_list(self) -> list[str]:
        return [item.strip() for item in self.espn_leagues.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
