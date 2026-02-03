from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.api_key import UserAPIKey
from app.models.user import User
from app.core.security import api_key_encryption
from app.schemas.api_key import APIKeyCreate, APIKeyUpdate, APIKeyResponse, APIKeyWithDecrypted


class APIKeyService:
    """Service for API key management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_api_keys(self, user_id: UUID) -> List[UserAPIKey]:
        """Get all API keys for a user"""
        result = await self.db.execute(
            select(UserAPIKey)
            .where(UserAPIKey.user_id == user_id)
            .order_by(desc(UserAPIKey.created_at))
        )
        return list(result.scalars().all())

    async def get_api_key_by_id(self, api_key_id: UUID, user_id: UUID) -> Optional[UserAPIKey]:
        """Get API key by ID (ensuring user owns it)"""
        result = await self.db.execute(
            select(UserAPIKey).where(
                and_(UserAPIKey.id == api_key_id, UserAPIKey.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_active_api_key(self, user_id: UUID, provider: str) -> Optional[APIKeyWithDecrypted]:
        """Get active API key for a specific provider"""
        result = await self.db.execute(
            select(UserAPIKey).where(
                and_(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.provider == provider,
                    UserAPIKey.is_active == True
                )
            ).order_by(desc(UserAPIKey.last_used_at))
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        # Decrypt and return
        try:
            decrypted_key = api_key_encryption.decrypt(api_key.encrypted_key)
            return APIKeyWithDecrypted(
                id=api_key.id,
                user_id=api_key.user_id,
                provider=api_key.provider,
                key_name=api_key.key_name,
                api_base_url=api_key.api_base_url,
                default_model=api_key.default_model,
                is_active=api_key.is_active,
                api_key=decrypted_key,
                created_at=api_key.created_at,
                last_used_at=api_key.last_used_at
            )
        except Exception:
            return None

    async def create_api_key(self, user_id: UUID, api_key_data: APIKeyCreate) -> UserAPIKey:
        """Create new API key"""
        # Encrypt the API key
        encrypted_key = api_key_encryption.encrypt(api_key_data.api_key)

        api_key = UserAPIKey(
            user_id=user_id,
            provider=api_key_data.provider,
            key_name=api_key_data.key_name,
            encrypted_key=encrypted_key,
            api_base_url=api_key_data.api_base_url,
            default_model=api_key_data.default_model,
            is_active=True
        )
        self.db.add(api_key)
        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def update_api_key(
        self,
        api_key_id: UUID,
        user_id: UUID,
        api_key_data: APIKeyUpdate
    ) -> Optional[UserAPIKey]:
        """Update API key (cannot change the actual key, only metadata)"""
        api_key = await self.get_api_key_by_id(api_key_id, user_id)
        if not api_key:
            return None

        update_data = api_key_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field != "api_key":  # Cannot update the actual key
                setattr(api_key, field, value)

        await self.db.commit()
        await self.db.refresh(api_key)
        return api_key

    async def delete_api_key(self, api_key_id: UUID, user_id: UUID) -> bool:
        """Delete API key"""
        api_key = await self.get_api_key_by_id(api_key_id, user_id)
        if not api_key:
            return False

        await self.db.delete(api_key)
        await self.db.commit()
        return True

    async def update_last_used(self, api_key_id: UUID) -> bool:
        """Update last_used_at timestamp"""
        api_key = await self.db.execute(
            select(UserAPIKey).where(UserAPIKey.id == api_key_id)
        )
        api_key = api_key.scalar_one_or_none()
        if not api_key:
            return False

        api_key.last_used_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def verify_user_has_api_key(self, user_id: UUID) -> bool:
        """Check if user has any active API keys configured"""
        result = await self.db.execute(
            select(UserAPIKey).where(
                and_(
                    UserAPIKey.user_id == user_id,
                    UserAPIKey.is_active == True
                )
            ).limit(1)
        )
        return result.scalar_one_or_none() is not None
