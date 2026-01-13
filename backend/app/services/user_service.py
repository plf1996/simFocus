"""
User service

Manages user profile operations, password changes, and account deletion.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    ValidationException,
)
from app.core.security import get_password_hash, verify_password
from app.models.api_key import UserApiKey
from app.models.character import Character
from app.models.discussion import Discussion
from app.models.topic import Topic
from app.models.user import User


class UserService:
    """
    User profile and account management service.

    Handles:
    - Profile retrieval and updates
    - Password changes
    - Account deletion (soft delete)
    - User statistics
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize user service with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_profile(self, user_id: str) -> User:
        """
        Get user profile by ID.

        Args:
            user_id: User UUID as string

        Returns:
            User object with profile data

        Raises:
            UserNotFoundException: If user doesn't exist

        Example:
            >>> user = await user_service.get_profile(user_id="123e4567-e89b-12d3-a456-426614174000")
            >>> print(user.email, user.name)
        """
        result = await self.db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFoundException(user_id=user_id)

        if not user.is_active:
            raise ValidationException(
                message="User account has been deleted",
                details={"user_id": user_id, "deleted_at": str(user.deleted_at)}
            )

        return user

    async def update_profile(
        self,
        user_id: str,
        name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> User:
        """
        Update user profile information.

        Args:
            user_id: User UUID as string
            name: New display name (optional)
            avatar_url: New avatar URL (optional)
            bio: New biography (optional)

        Returns:
            Updated user object

        Raises:
            UserNotFoundException: If user doesn't exist
            ValidationException: If validation fails

        Example:
            >>> user = await user_service.update_profile(
            ...     user_id="123",
            ...     name="John Doe",
            ...     bio="Product Manager"
            ... )
        """
        user = await self.get_profile(user_id)

        # Update fields if provided
        if name is not None:
            if len(name) > 100:
                raise ValidationException(
                    message="Name must not exceed 100 characters",
                    details={"max_length": 100, "provided_length": len(name)}
                )
            user.name = name

        if avatar_url is not None:
            # Basic URL validation
            if avatar_url and not self._is_valid_url(avatar_url):
                raise ValidationException(
                    message="Invalid avatar URL",
                    details={"avatar_url": avatar_url}
                )
            user.avatar_url = avatar_url

        if bio is not None:
            if len(bio) > 500:
                raise ValidationException(
                    message="Bio must not exceed 500 characters",
                    details={"max_length": 500, "provided_length": len(bio)}
                )
            user.bio = bio

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> bool:
        """
        Change user password.

        Args:
            user_id: User UUID as string
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if password changed successfully

        Raises:
            UserNotFoundException: If user doesn't exist
            InvalidCredentialsException: If current password is incorrect
            ValidationException: If new password doesn't meet requirements

        Example:
            >>> success = await user_service.change_password(
            ...     user_id="123",
            ...     current_password="oldpassword",
            ...     new_password="newpassword"
            ... )
        """
        user = await self.get_profile(user_id)

        # Check if user has password (OAuth-only users don't)
        if not user.password_hash:
            raise ValidationException(
                message="Password change not available for OAuth users",
                details={"auth_provider": user.auth_provider}
            )

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsException()

        # Validate new password
        self._validate_password(new_password)

        # Hash and update password
        user.password_hash = get_password_hash(new_password)

        await self.db.commit()

        # TODO: Invalidate all refresh tokens for security
        # This forces re-login on all devices

        return True

    async def delete_account(
        self,
        user_id: str,
        password: Optional[str] = None,
    ) -> bool:
        """
        Soft delete user account.

        Marks account as deleted but preserves data for potential recovery.
        All user data remains in database but account is inaccessible.

        Args:
            user_id: User UUID as string
            password: Current password (required for email/password users)

        Returns:
            True if account deleted successfully

        Raises:
            UserNotFoundException: If user doesn't exist
            InvalidCredentialsException: If password verification fails
            ValidationException: If account cannot be deleted

        Note:
            - OAuth users can delete without password
            - Email/password users must verify password first
            - Data is preserved (soft delete)
            - Hard delete should be done separately with data retention policies
        """
        user = await self.get_profile(user_id)

        # Verify password for email/password users
        if user.auth_provider == "email":
            if not password:
                raise ValidationException(
                    message="Password required to delete account",
                    details={"auth_provider": "email"}
                )

            if not user.password_hash:
                raise InvalidCredentialsException()

            if not verify_password(password, user.password_hash):
                raise InvalidCredentialsException()

        # Check if user has running discussions
        running_discussions = await self.db.execute(
            select(Discussion).where(
                Discussion.user_id == UUID(user_id),
                Discussion.status == "running"
            )
        )
        running_count = len(running_discussions.scalars().all())

        if running_count > 0:
            raise ValidationException(
                message="Cannot delete account with active discussions",
                details={"running_discussions": running_count}
            )

        # Soft delete by setting deleted_at timestamp
        user.deleted_at = datetime.utcnow()

        # Anonymize email for privacy
        user.email = f"deleted_{user_id}@deleted.local"

        # Clear sensitive data
        user.password_hash = None
        user.name = "Deleted User"
        user.avatar_url = None
        user.bio = None

        await self.db.commit()

        # TODO: Send account deletion confirmation email
        # TODO: Schedule data for permanent deletion after retention period (e.g., 30 days)

        return True

    async def get_statistics(self, user_id: str) -> dict:
        """
        Get user usage statistics.

        Args:
            user_id: User UUID as string

        Returns:
            Dictionary with usage statistics:
                - total_discussions: Total number of discussions
                - total_topics: Total number of topics
                - total_characters: Total number of custom characters
                - total_tokens_used: Total LLM tokens consumed
                - estimated_cost_usd: Estimated API cost in USD

        Raises:
            UserNotFoundException: If user doesn't exist

        Example:
            >>> stats = await user_service.get_statistics(user_id="123")
            >>> print(stats["total_discussions"])
        """
        # Verify user exists
        await self.get_profile(user_id)

        # Get counts
        discussions_result = await self.db.execute(
            select(func.count(Discussion.id)).where(
                Discussion.user_id == UUID(user_id)
            )
        )
        total_discussions = discussions_result.scalar() or 0

        topics_result = await self.db.execute(
            select(func.count(Topic.id)).where(
                Topic.user_id == UUID(user_id)
            )
        )
        total_topics = topics_result.scalar() or 0

        characters_result = await self.db.execute(
            select(func.count(Character.id)).where(
                Character.user_id == UUID(user_id),
                Character.is_template == False
            )
        )
        total_characters = characters_result.scalar() or 0

        # Get token usage and cost from discussions
        stats_result = await self.db.execute(
            select(
                func.sum(Discussion.total_tokens_used),
                func.sum(Discussion.estimated_cost_usd)
            ).where(Discussion.user_id == UUID(user_id))
        )
        total_tokens, total_cost = stats_result.one()

        total_tokens_used = total_tokens or 0
        estimated_cost_usd = float(total_cost or 0)

        return {
            "total_discussions": total_discussions,
            "total_topics": total_topics,
            "total_characters": total_characters,
            "total_tokens_used": total_tokens_used,
            "estimated_cost_usd": estimated_cost_usd,
        }

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

        # TODO: Add more validation:
        # - At least one uppercase
        # - At least one lowercase
        # - At least one number
        # - At least one special character

    def _is_valid_url(self, url: str) -> bool:
        """
        Basic URL validation.

        Args:
            url: URL string to validate

        Returns:
            True if URL appears valid
        """
        if not url:
            return False

        # Basic check for http/https URLs
        return url.startswith(("http://", "https://"))

    async def get_api_keys(self, user_id: str) -> list[UserApiKey]:
        """
        Get all API keys for user.

        Args:
            user_id: User UUID as string

        Returns:
            List of user's API keys

        Raises:
            UserNotFoundException: If user doesn't exist

        Note:
            This method is here for convenience. The actual API key
            operations should use api_key_service.
        """
        # Verify user exists
        await self.get_profile(user_id)

        result = await self.db.execute(
            select(UserApiKey).where(
                UserApiKey.user_id == UUID(user_id)
            ).order_by(UserApiKey.created_at.desc())
        )
        return list(result.scalars().all())
