from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models import UserRole


# ── Auth request / response ──────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ─────────────────────────────────────────────────────────────

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    restaurant_id: int | None = None
    created_at: datetime
    updated_at: datetime


# ── Restaurant ───────────────────────────────────────────────────────

class RestaurantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    timezone: str
    currency: str
    settings_json: dict | None = None
    created_at: datetime
    updated_at: datetime
