from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, RefreshRequest, UserResponse, OrgRoleResponse
from app.services.auth import (
    authenticate_user,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_user_by_id,
)
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    # build the org roles list to include in the token response
    org_roles = [
        OrgRoleResponse(
            organization_id=r.organization_id,
            role=r.role.value if hasattr(r.role, "value") else r.role,
            organization_name=r.organization.name if r.organization else None,
        )
        for r in (user.org_roles or [])
    ]

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            org_roles=org_roles,
        ),
    )


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    await db.flush()

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            org_roles=[],
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    org_roles = [
        OrgRoleResponse(
            organization_id=r.organization_id,
            role=r.role.value if hasattr(r.role, "value") else r.role,
        )
        for r in (user.org_roles or [])
    ]

    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superadmin=user.is_superadmin,
            org_roles=org_roles,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    org_roles = [
        OrgRoleResponse(
            organization_id=r.organization_id,
            role=r.role.value if hasattr(r.role, "value") else r.role,
            organization_name=r.organization.name if r.organization else None,
        )
        for r in (user.org_roles or [])
    ]
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superadmin=user.is_superadmin,
        org_roles=org_roles,
    )
