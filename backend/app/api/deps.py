"""
api dependency injection for auth, rbac, and multi-tenancy.
every protected route uses these to enforce access control.
"""

from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth import decode_token, get_user_by_id, get_user_org_role
from app.models.user import User, OrgUserRole, RoleEnum

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """grabs the jwt, checks it's valid, and returns the user — used on every protected route"""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload["sub"]
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_org_id(x_organization_id: str = Header(..., alias="X-Organization-Id")) -> str:
    """pulls the org id from the request header — how we do multi-tenancy"""
    if not x_organization_id:
        raise HTTPException(status_code=400, detail="X-Organization-Id header required")
    return x_organization_id


async def require_admin(
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """blocks anyone who isn't an admin for this org"""
    if user.is_superadmin:
        return user

    role = await get_user_org_role(db, user.id, org_id)
    if not role or role.role not in (RoleEnum.ADMIN, RoleEnum.SUPERADMIN):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def require_manager_or_above(
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """lets through managers and admins, blocks anyone with no org role"""
    if user.is_superadmin:
        return user

    role = await get_user_org_role(db, user.id, org_id)
    if not role:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
    return user


async def require_superadmin(
    user: User = Depends(get_current_user),
) -> User:
    """only for platform-level superadmins — not org admins"""
    if not user.is_superadmin:
        raise HTTPException(status_code=403, detail="Superadmin access required")
    return user
