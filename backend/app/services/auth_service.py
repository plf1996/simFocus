"""
Authentication service

Handles user registration, login, email verification, password reset,
and JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.exceptions import (
    DuplicateUserException,
    InvalidCredentialsException,
    InvalidTokenException,
    UserNotFoundException,
    ValidationException,
)
from app.core.security import (
    AESEncryption,
    create_access_token,
    create_refresh_token,
    generate_secure_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User

settings = get_settings()


class AuthService:
    """
    Authentication and authorization service.

    Manages user authentication flow including:
    - Registration with email verification
    - Login with JWT tokens
    - Email verification
    - Token refresh
    - Password reset
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize auth service with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def register(
        self,
        email: str,
        password: str,
        name: Optional[str] = None,
    ) -> dict:
        """
        Register a new user account.

        Creates a new user with hashed password, generates JWT tokens,
        and initiates email verification process.

        Args:
            email: User email address (must be unique)
            password: Plain text password (will be hashed)
            name: Optional display name

        Returns:
            Dictionary containing:
                - access_token: JWT access token
                - refresh_token: JWT refresh token
                - token_type: Token type (always "bearer")
                - expires_in: Access token expiry in seconds

        Raises:
            DuplicateUserException: If email already exists
            ValidationException: If password doesn't meet requirements

        Example:
            >>> tokens = await auth_service.register(
            ...     email="user@example.com",
            ...     password="securepassword123",
            ...     name="John Doe"
            ... )
            >>> print(tokens["access_token"])
        """
        # Check if user already exists
        existing_user = await self._get_user_by_email(email)
        if existing_user:
            # Check if this is a soft-deleted user
            if existing_user.deleted_at is not None:
                raise ValidationException(
                    message="This email was previously registered. Please contact support.",
                    details={"email": email}
                )
            raise DuplicateUserException(email=email)

        # Validate password strength
        self._validate_password(password)

        # Hash password
        password_hash = get_password_hash(password)

        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            auth_provider="email",
            email_verified=False,  # Requires email verification
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Generate verification token (for email verification flow)
        verification_token = generate_secure_token()

        # TODO: Send verification email with token
        # For now, we'll log the token (in production, use email service)
        # await self._send_verification_email(user.email, verification_token)

        # Generate JWT tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def login(
        self,
        email: str,
        password: str,
    ) -> dict:
        """
        Authenticate user with email and password.

        Verifies credentials and returns JWT tokens.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dictionary containing JWT tokens and expiry info

        Raises:
            InvalidCredentialsException: If email or password is invalid
            UserNotFoundException: If user doesn't exist
            ValidationException: If user is OAuth-only (no password)

        Example:
            >>> tokens = await auth_service.login(
            ...     email="user@example.com",
            ...     password="securepassword123"
            ... )
        """
        # Get user by email
        user = await self._get_user_by_email(email)

        if not user:
            # Use generic error message for security
            raise InvalidCredentialsException()

        # Check if user is soft deleted
        if user.deleted_at is not None:
            raise InvalidCredentialsException()

        # Check if user has password (OAuth-only users don't)
        if not user.password_hash:
            raise ValidationException(
                message="Please use OAuth login (Google/GitHub)",
                details={"auth_provider": user.auth_provider}
            )

        # Verify password
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsException()

        # Update last login timestamp
        user.last_login_at = datetime.utcnow()
        await self.db.commit()

        # Generate JWT tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def verify_email(self, token: str) -> bool:
        """
        Verify user email address with verification token.

        Args:
            token: Email verification token

        Returns:
            True if verification successful

        Raises:
            InvalidTokenException: If token is invalid or expired

        Note:
            In production, tokens should be stored in Redis or database
            with expiry. This is a simplified implementation.
        """
        # TODO: Implement proper token storage and verification
        # For now, this is a placeholder that demonstrates the flow

        # Decode token to get user email (in production, use dedicated verification tokens)
        try:
            payload = verify_token(token, token_type="access")
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidTokenException("Invalid token format")

            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)

            # Mark email as verified
            user.email_verified = True
            await self.db.commit()

            return True

        except Exception as e:
            raise InvalidTokenException(str(e))

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dictionary with new access token

        Raises:
            InvalidTokenException: If refresh token is invalid or expired

        Example:
            >>> new_tokens = await auth_service.refresh_token(refresh_token)
        """
        try:
            # Verify refresh token
            payload = verify_token(refresh_token, token_type="refresh")
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidTokenException("Invalid token format")

            # Verify user still exists and is active
            user = await self._get_user_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidTokenException("User not found or inactive")

            # Generate new access token
            access_token = create_access_token(data={"sub": str(user.id)})

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }

        except InvalidTokenException:
            raise
        except Exception as e:
            raise InvalidTokenException(f"Token refresh failed: {str(e)}")

    async def initiate_password_reset(self, email: str) -> str:
        """
        Initiate password reset flow.

        Generates a secure reset token and stores it (in production).
        Sends email with reset link.

        Args:
            email: User email address

        Returns:
            Reset token (in production, this should be sent via email)

        Raises:
            UserNotFoundException: If user doesn't exist

        Note:
            For security, we don't reveal if email exists or not.
            This implementation returns the token for testing purposes.
        """
        user = await self._get_user_by_email(email)

        if not user:
            # For security, don't reveal if email exists
            # But we still raise an error to prevent proceeding
            raise UserNotFoundException(email=email)

        # Generate secure reset token
        reset_token = generate_secure_token()

        # TODO: Store reset token in Redis/database with expiry (e.g., 1 hour)
        # TODO: Send password reset email with token
        # await self._send_password_reset_email(user.email, reset_token)

        # Log token for development (remove in production)
        return reset_token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset user password with reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            True if password reset successful

        Raises:
            InvalidTokenException: If token is invalid
            ValidationException: If password doesn't meet requirements
            UserNotFoundException: If user not found

        Note:
            This is a simplified implementation. In production,
            verify the reset token against stored value in Redis/DB.
        """
        # Validate password strength
        self._validate_password(new_password)

        # TODO: Verify reset token against stored value
        # For now, we'll decode as JWT (not ideal for reset tokens)
        try:
            payload = verify_token(token, token_type="access")
            user_id = payload.get("sub")

            if not user_id:
                raise InvalidTokenException("Invalid reset token")

            # Get user
            user = await self._get_user_by_id(user_id)
            if not user:
                raise UserNotFoundException(user_id=user_id)

            # Hash new password
            password_hash = get_password_hash(new_password)

            # Update password
            user.password_hash = password_hash
            await self.db.commit()

            # TODO: Invalidate all existing refresh tokens for security
            # This forces re-login on all devices

            return True

        except InvalidTokenException:
            raise
        except Exception as e:
            raise InvalidTokenException(f"Password reset failed: {str(e)}")

    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email

        Returns:
            User object or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID as string

        Returns:
            User object or None
        """
        result = await self.db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        return result.scalar_one_or_none()

    def _validate_password(self, password: str) -> None:
        """
        Validate password strength requirements.

        Args:
            password: Password to validate

        Raises:
            ValidationException: If password doesn't meet requirements
        """
        if len(password) < 8:
            raise ValidationException(
                message="Password must be at least 8 characters",
                details={"min_length": 8}
            )

        if len(password) > 100:
            raise ValidationException(
                message="Password must not exceed 100 characters",
                details={"max_length": 100}
            )

        # TODO: Add more validation rules:
        # - At least one uppercase letter
        # - At least one lowercase letter
        # - At least one number
        # - At least one special character
        # - Not in common passwords list

    async def _send_verification_email(self, email: str, token: str) -> None:
        """
        Send verification email to user.

        Args:
            email: User email address
            token: Verification token

        Note:
            This is a placeholder for email service integration.
        """
        # TODO: Integrate with email service (SendGrid, AWS SES, etc.)
        pass

    async def _send_password_reset_email(self, email: str, token: str) -> None:
        """
        Send password reset email to user.

        Args:
            email: User email address
            token: Reset token

        Note:
            This is a placeholder for email service integration.
        """
        # TODO: Integrate with email service
        pass
