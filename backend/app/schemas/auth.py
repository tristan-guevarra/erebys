from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superadmin: bool
    org_roles: list["OrgRoleResponse"] = []

    model_config = {"from_attributes": True}


class OrgRoleResponse(BaseModel):
    organization_id: str
    role: str
    organization_name: str | None = None

    model_config = {"from_attributes": True}


# resolve forward references so pydantic can build the nested models
TokenResponse.model_rebuild()
UserResponse.model_rebuild()
