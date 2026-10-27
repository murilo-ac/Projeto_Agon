from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None


class CompetitionRef(BaseModel):
    id: int
    name: str


class CompetitionOut(BaseModel):
    id: int
    name: str
    country: str | None = None
    type: str
    sport: str  # slug do esporte
