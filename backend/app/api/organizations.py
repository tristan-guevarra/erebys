from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrgCreate, OrgUpdate, OrgResponse
from app.api.deps import get_current_user, require_superadmin

router = APIRouter(prefix="/orgs", tags=["Organizations"])


@router.get("", response_model=list[OrgResponse])
async def list_orgs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.is_superadmin:
        result = await db.execute(select(Organization))
    else:
        org_ids = [r.organization_id for r in (user.org_roles or [])]
        result = await db.execute(select(Organization).where(Organization.id.in_(org_ids)))
    return [OrgResponse.model_validate(o) for o in result.scalars().all()]


@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrgResponse.model_validate(org)


@router.post("", response_model=OrgResponse, status_code=201)
async def create_org(
    body: OrgCreate,
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    org = Organization(**body.model_dump())
    db.add(org)
    await db.flush()
    return OrgResponse.model_validate(org)


@router.patch("/{org_id}", response_model=OrgResponse)
async def update_org(
    org_id: str,
    body: OrgUpdate,
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    await db.flush()
    return OrgResponse.model_validate(org)
