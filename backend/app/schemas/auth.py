"""
Authentication and authorization schemas

Provides request/response schemas for user authentication operations.
"""
from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import MessageResponse


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)"
    )
    name: str | None = Field(
        None,
        max_length=100,
        description="Display name (optional)"
    )


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    password: str = Field(
        ...,
        description="User password"
    )


class TokenResponse(BaseModel):
    """JWT token response for successful authentication."""

    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token for obtaining new access tokens"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        ...,
        ge=1,
        description="Access token expiration time in seconds"
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(
        ...,
        description="Valid refresh token"
    )


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""

    email: EmailStr = Field(
        ...,
        description="User email address"
    )


class ResetPasswordRequest(BaseModel):
    """Password reset confirmation."""

    token: str = Field(
        ...,
        description="Password reset token from email"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 characters)"
    )


class VerifyEmailRequest(BaseModel):
    """Email verification request."""

    token: str = Field(
        ...,
        description="Email verification token"
    )


class ChangePasswordRequest(BaseModel):
    """Password change request for authenticated users."""

    current_password: str = Field(
        ...,
        description="Current password"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 characters)"
    )
