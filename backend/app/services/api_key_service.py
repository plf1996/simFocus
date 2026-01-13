"""
API Key service

Manages encrypted storage and retrieval of user's LLM API keys.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    APIKeyNotFoundException,
    EncryptionException,
    NotFoundException,
    ValidationException,
)
from app.core.security import AESEncryption
from app.models.api_key import UserApiKey
from app.models.user import User


class ApiKeyService:
    """
    API key management service.

    Handles:
    - Secure storage of API keys with AES-256-GCM encryption
    - Listing user's API keys
    - Deleting API keys
    - Retrieving active API key for LLM calls
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize API key service with database session.

        Args:
            db: Async database session
        """
        self.db = db
        self.encryption = AESEncryption()

    async def create_api_key(
        self,
        user_id: str,
        provider: str,
        key_name: str,
        api_key: str,
        api_base_url: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> UserApiKey:
        """
        Create and store encrypted API key for user.

        Args:
            user_id: User UUID as string
            provider: API provider (openai, anthropic, custom)
            key_name: User-defined name for the key
            api_key: Plain text API key (will be encrypted)
            api_base_url: Optional custom API endpoint URL
            default_model: Optional default model name

        Returns:
            Created UserApiKey object (without actual key)

        Raises:
            ValidationException: If validation fails
            EncryptionException: If encryption fails

        Example:
            >>> api_key = await api_key_service.create_api_key(
            ...     user_id="123",
            ...     provider="openai",
            ...     key_name="My OpenAI Key",
            ...     api_key="sk-...",
            ...     default_model="gpt-4"
            ... )
        """
        # Validate provider
        valid_providers = ["openai", "anthropic", "custom"]
        if provider not in valid_providers:
            raise ValidationException(
                message=f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
                details={"provider": provider, "valid_providers": valid_providers}
            )

        # Validate key name
        if not key_name or len(key_name) > 100:
            raise ValidationException(
                message="Key name must be 1-100 characters",
                details={"min_length": 1, "max_length": 100}
            )

        # Validate API key format
        if not api_key or len(api_key) < 10:
            raise ValidationException(
                message="API key must be at least 10 characters",
                details={"min_length": 10}
            )

        # Validate custom endpoint URL if provided
        if api_base_url and not self._is_valid_url(api_base_url):
            raise ValidationException(
                message="Invalid API base URL",
                details={"api_base_url": api_base_url}
            )

        # Validate default model if provided
        if default_model and len(default_model) > 100:
            raise ValidationException(
                message="Model name must not exceed 100 characters",
                details={"max_length": 100, "provided_length": len(default_model)}
            )

        # Check if user has too many API keys (limit to 10 per user)
        existing_count = await self._count_user_api_keys(user_id)
        if existing_count >= 10:
            raise ValidationException(
                message="Maximum API key limit reached (10 keys per user)",
                details={"current_count": existing_count, "max_keys": 10}
            )

        # Encrypt API key
        try:
            encrypted_key = self.encryption.encrypt(api_key)
        except Exception as e:
            raise EncryptionException(
                message=f"Failed to encrypt API key: {str(e)}"
            )

        # Create API key record
        user_api_key = UserApiKey(
            user_id=UUID(user_id),
            provider=provider,
            key_name=key_name,
            encrypted_key=encrypted_key,
            api_base_url=api_base_url,
            default_model=default_model,
            is_active=True,
        )

        self.db.add(user_api_key)
        await self.db.commit()
        await self.db.refresh(user_api_key)

        return user_api_key

    async def list_api_keys(self, user_id: str) -> list[UserApiKey]:
        """
        Get all API keys for user.

        Returns API key metadata without actual key values.

        Args:
            user_id: User UUID as string

        Returns:
            List of UserApiKey objects (without decrypted keys)

        Example:
            >>> keys = await api_key_service.list_api_keys(user_id="123")
            >>> for key in keys:
            ...     print(f"{key.provider}: {key.key_name}")
        """
        result = await self.db.execute(
            select(UserApiKey).where(
                UserApiKey.user_id == UUID(user_id)
            ).order_by(UserApiKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_api_key(self, user_id: str, api_key_id: str) -> bool:
        """
        Delete an API key.

        Args:
            user_id: User UUID as string (for authorization)
            api_key_id: API key UUID as string to delete

        Returns:
            True if deleted successfully

        Raises:
            NotFoundException: If API key not found
            ValidationException: If API key belongs to different user

        Example:
            >>> success = await api_key_service.delete_api_key(
            ...     user_id="123",
            ...     api_key_id="456"
            ... )
        """
        # Get API key
        api_key = await self._get_api_key_by_id(api_key_id)

        if not api_key:
            raise NotFoundException(
                message="API key not found",
                details={"api_key_id": api_key_id}
            )

        # Verify ownership
        if str(api_key.user_id) != user_id:
            raise ValidationException(
                message="API key does not belong to this user",
                details={
                    "api_key_id": api_key_id,
                    "expected_user_id": user_id,
                    "actual_user_id": str(api_key.user_id)
                }
            )

        # Delete API key
        await self.db.delete(api_key)
        await self.db.commit()

        return True

    async def get_active_api_key(
        self,
        user_id: str,
        provider: Optional[str] = None,
    ) -> tuple[str, Optional[str], Optional[str]]:
        """
        Get decrypted active API key for LLM calls.

        This is the primary method used by the discussion engine
        to get API keys for making LLM API calls.

        Args:
            user_id: User UUID as string
            provider: Optional provider filter (openai, anthropic, custom)

        Returns:
            Tuple of (decrypted_api_key, api_base_url, default_model)

        Raises:
            APIKeyNotFoundException: If no active API key found
            EncryptionException: If decryption fails

        Example:
            >>> api_key, base_url, model = await api_key_service.get_active_api_key(
            ...     user_id="123",
            ...     provider="openai"
            ... )
            >>> print(f"Using model: {model}")
        """
        # Build query
        query = select(UserApiKey).where(
            UserApiKey.user_id == UUID(user_id),
            UserApiKey.is_active == True
        )

        if provider:
            query = query.where(UserApiKey.provider == provider)

        # Get most recently updated API key
        query = query.order_by(UserApiKey.updated_at.desc())

        result = await self.db.execute(query)
        api_key_record = result.scalar_one_or_none()

        if not api_key_record:
            if provider:
                raise APIKeyNotFoundException(
                    provider=provider,
                    user_id=user_id
                )
            else:
                raise ValidationException(
                    message="No active API key found",
                    details={"user_id": user_id}
                )

        # Decrypt API key
        try:
            decrypted_key = self.encryption.decrypt(api_key_record.encrypted_key)
        except Exception as e:
            raise EncryptionException(
                message=f"Failed to decrypt API key: {str(e)}"
            )

        # Update last_used_at timestamp
        api_key_record.last_used_at = datetime.utcnow()
        await self.db.commit()

        return (
            decrypted_key,
            api_key_record.api_base_url,
            api_key_record.default_model,
        )

    async def update_api_key(
        self,
        user_id: str,
        api_key_id: str,
        key_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        default_model: Optional[str] = None,
    ) -> UserApiKey:
        """
        Update API key metadata.

        Note: This does not update the actual key value.
        To change the key, delete and recreate.

        Args:
            user_id: User UUID as string
            api_key_id: API key UUID as string
            key_name: New key name (optional)
            is_active: New active status (optional)
            default_model: New default model (optional)

        Returns:
            Updated UserApiKey object

        Raises:
            NotFoundException: If API key not found
            ValidationException: If validation fails or ownership mismatch

        Example:
            >>> updated = await api_key_service.update_api_key(
            ...     user_id="123",
            ...     api_key_id="456",
            ...     key_name="Updated Name",
            ...     is_active=False
            ... )
        """
        # Get API key
        api_key = await self._get_api_key_by_id(api_key_id)

        if not api_key:
            raise NotFoundException(
                message="API key not found",
                details={"api_key_id": api_key_id}
            )

        # Verify ownership
        if str(api_key.user_id) != user_id:
            raise ValidationException(
                message="API key does not belong to this user",
                details={"api_key_id": api_key_id}
            )

        # Update fields
        if key_name is not None:
            if not key_name or len(key_name) > 100:
                raise ValidationException(
                    message="Key name must be 1-100 characters",
                    details={"min_length": 1, "max_length": 100}
                )
            api_key.key_name = key_name

        if is_active is not None:
            api_key.is_active = is_active

        if default_model is not None:
            if default_model and len(default_model) > 100:
                raise ValidationException(
                    message="Model name must not exceed 100 characters",
                    details={"max_length": 100, "provided_length": len(default_model)}
                )
            api_key.default_model = default_model

        await self.db.commit()
        await self.db.refresh(api_key)

        return api_key

    async def _get_api_key_by_id(self, api_key_id: str) -> Optional[UserApiKey]:
        """
        Get API key by ID.

        Args:
            api_key_id: API key UUID as string

        Returns:
            UserApiKey object or None
        """
        result = await self.db.execute(
            select(UserApiKey).where(UserApiKey.id == UUID(api_key_id))
        )
        return result.scalar_one_or_none()

    async def _count_user_api_keys(self, user_id: str) -> int:
        """
        Count number of API keys for user.

        Args:
            user_id: User UUID as string

        Returns:
            Number of API keys
        """
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.count(UserApiKey.id)).where(
                UserApiKey.user_id == UUID(user_id)
            )
        )
        return result.scalar() or 0

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
        return url.startswith(("http://", "https://"))
