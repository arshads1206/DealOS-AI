"""
DealOS AI — User Schemas.

Pydantic models for user CRUD operations.

Key separation:
- UserCreate: Admin-only, allows setting role
- UserUpdate: Partial updates (admin or self)
- UserResponse: Public-facing, NEVER includes password hash
- UserListResponse: Paginated list with metadata
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class UserResponse(BaseModel):
    """
    User data returned to clients.

    Explicitly excludes hashed_password — this field must NEVER
    appear in API responses. The allowlist approach (listing fields
    to include) is safer than a denylist (listing fields to exclude).
    """

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    """
    Admin-only user creation schema.

    Differs from RegisterRequest:
    - Admin can assign any role (register always creates ANALYST)
    - Admin can set initial status
    - Used for bulk user provisioning
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: str = Field(default=UserRole.ANALYST)


class UserUpdate(BaseModel):
    """
    Partial user update schema.

    All fields optional — only provided fields are updated.
    Password changes require the current password for verification
    (handled in the service layer, not here).
    """

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    role: str | None = None
    status: str | None = None


class UserProfile(BaseModel):
    """
    Extended user profile with computed fields.

    Used for the /me endpoint — includes permissions for frontend RBAC.
    """

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    status: str
    permissions: list[str]
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}
