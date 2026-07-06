"""
DealOS AI — Authentication Schemas.

Pydantic models for auth request/response validation.

Why separate from User schemas?
- Auth concerns (tokens, credentials) are distinct from user management
- Login request needs email+password, not the full user model
- Token response shape differs from user CRUD responses
- Security: auth schemas explicitly exclude sensitive fields
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class LoginRequest(BaseModel):
    """Login credentials."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=1, description="User password")


class RegisterRequest(BaseModel):
    """New user registration data."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="Password (min 8 chars)")
    full_name: str = Field(min_length=2, max_length=255, description="Full name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Enforce password complexity.

        Requirements:
        - At least 8 characters (enforced by min_length)
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

        Why these rules?
        NIST 800-63B recommends minimum 8 characters. We add basic complexity
        to prevent trivially guessable passwords. We do NOT require special
        characters (NIST explicitly advises against it — it reduces usability
        without significantly improving security).
        """
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Strip whitespace and validate name is not empty."""
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be empty")
        return v


class TokenResponse(BaseModel):
    """JWT token pair returned after successful authentication."""

    access_token: str = Field(description="Short-lived JWT access token")
    refresh_token: str = Field(description="Long-lived JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token using a refresh token."""

    refresh_token: str = Field(description="Valid refresh token")


class TokenPayload(BaseModel):
    """Decoded JWT token payload (internal use)."""

    sub: str = Field(description="User ID")
    email: str | None = Field(default=None, description="User email")
    role: str | None = Field(default=None, description="User role")
    type: str = Field(description="Token type (access/refresh)")
    exp: int = Field(description="Expiration timestamp")
    iat: int = Field(description="Issued-at timestamp")
