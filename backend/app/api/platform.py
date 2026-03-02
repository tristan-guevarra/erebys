from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.api.deps import require_superadmin
import app.services.platform as svc

router = APIRouter(prefix="/platform", tags=["Platform"])


@router.get("/overview")
async def platform_overview(
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_platform_overview(db)


@router.get("/academies")
async def list_academies(
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_all_academies_with_metrics(db)


@router.get("/academies/{org_id}")
async def get_academy(
    org_id: str,
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.organization import Organization
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Academy not found")
    academies = await svc.get_all_academies_with_metrics(db)
    match = next((a for a in academies if a["id"] == org_id), None)
    return match or {"id": org_id, "name": org.name}


@router.get("/revenue")
async def platform_revenue(
    days: int = 90,
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_platform_revenue(db, days)


@router.get("/users")
async def list_users(
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_platform_users(db)


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    body: dict,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    from app.models.user import User as UserModel
    target = await db.get(UserModel, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if "is_active" in body:
        target.is_active = body["is_active"]
    await db.flush()
    return {"id": target.id, "email": target.email, "is_active": target.is_active}


@router.get("/health")
async def system_health(
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    return await svc.get_system_health(db)


@router.post("/academies", status_code=201)
async def create_academy(
    body: dict,
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    import uuid
    from app.models.organization import Organization
    org = Organization(
        id=str(uuid.uuid4()),
        name=body["name"],
        slug=body["slug"],
        sport_type=body.get("sport_type", "multi"),
        region=body.get("region", "US-East"),
        competition_proxy=body.get("competition_proxy", 5.0),
    )
    db.add(org)
    await db.flush()
    return {"id": org.id, "name": org.name, "slug": org.slug}
