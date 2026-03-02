from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.coach import Coach
from app.models.user import User
from app.api.deps import get_org_id, get_current_user

router = APIRouter(prefix="/coaches", tags=["Coaches"])


class CoachResponse(BaseModel):
    id: str
    organization_id: str
    full_name: str
    email: str | None
    specialty: str
    hourly_rate: float
    avg_rating: float
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[CoachResponse])
async def list_coaches(
    org_id: str = Depends(get_org_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Coach)
        .where(Coach.organization_id == org_id)
        .order_by(Coach.avg_rating.desc())
    )
    return [CoachResponse.model_validate(c) for c in result.scalars().all()]
