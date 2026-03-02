from pydantic import BaseModel
from datetime import datetime


class OrgCreate(BaseModel):
    name: str
    slug: str
    sport_type: str = "multi"
    region: str = "US-East"
    competition_proxy: float = 5.0


class OrgUpdate(BaseModel):
    name: str | None = None
    sport_type: str | None = None
    region: str | None = None
    competition_proxy: float | None = None


class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    sport_type: str
    region: str
    competition_proxy: float
    created_at: datetime

    model_config = {"from_attributes": True}
