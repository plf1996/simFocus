"""
Authentication API routes

Provides endpoints for user registration, login, token management,
and password operations.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import get_auth_service, get_user_service, get_current_user
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
)
async def register(
    data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: At least 8 characters
    - **name**: Optional display name

    Returns JWT access and refresh tokens on successful registration.
    """
    tokens = await auth_service.register(
        email=data.email,
        password=data.password,
        name=data.name,
    )
    return tokens


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
)
async def login(
    data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Authenticate user with email and password.

    Returns JWT access and refresh tokens on successful authentication.
    """
    tokens = await auth_service.login(
        email=data.email,
        password=data.password,
    )
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
async def refresh_token(
    data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Obtain new access token using refresh token.

    Validates the refresh token and returns a new access token.
    """
    tokens = await auth_service.refresh_token(
        refresh_token=data.refresh_token
    )
    return tokens


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email address",
)
async def verify_email(
    data: VerifyEmailRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Verify user email with verification token.

    Typically sent via email after registration.
    """
    await auth_service.verify_email(token=data.token)
    return MessageResponse(message="Email verified successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Send password reset email.

    Initiates password reset flow by sending reset token to user's email.
    """
    # For security, always return success even if email doesn't exist
    try:
        await auth_service.initiate_password_reset(email=data.email)
    except Exception:
        # Log error but don't reveal to user
        pass

    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
)
async def reset_password(
    data: ResetPasswordRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    """
    Reset password with reset token.

    Completes password reset flow initiated by forgot-password endpoint.
    """
    await auth_service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
    return MessageResponse(message="Password reset successfully")


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends(get_user_service)],
):
    """
    Change password for authenticated user.

    Requires current password for verification.
    """
    await user_service.change_password(
        user_id=str(current_user.id),
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return MessageResponse(message="Password changed successfully")
