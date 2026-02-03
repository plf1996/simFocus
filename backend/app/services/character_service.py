from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_, update
from typing import Optional, List
from uuid import UUID
import random

from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse


class CharacterService:
    """Service for character management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_character_by_id(self, character_id: UUID) -> Optional[Character]:
        """Get character by ID"""
        result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        return result.scalar_one_or_none()

    async def get_user_characters(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[Character]:
        """Get custom characters for a user"""
        result = await self.db.execute(
            select(Character)
            .where(Character.user_id == user_id)
            .order_by(desc(Character.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_template_characters(
        self,
        skip: int = 0,
        limit: int = 20
    ) -> List[Character]:
        """Get system template characters (user_id is None)"""
        result = await self.db.execute(
            select(Character)
            .where(
                and_(
                    Character.is_template == True,
                    Character.user_id.is_(None)
                )
            )
            .order_by(desc(Character.usage_count), Character.rating_avg.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_character(
        self,
        user_id: UUID,
        character_data: CharacterCreate
    ) -> Character:
        """Create custom character"""
        character = Character(
            user_id=user_id,
            name=character_data.name,
            avatar_url=character_data.avatar_url,
            is_template=False,
            is_public=False,
            config=character_data.config.model_dump(),
            usage_count=0,
            rating_avg=0.0,
            rating_count=0
        )
        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def update_character(
        self,
        character_id: UUID,
        user_id: UUID,
        character_data: CharacterUpdate
    ) -> Optional[Character]:
        """Update custom character (only user's own characters)"""
        character = await self.db.execute(
            select(Character).where(
                and_(
                    Character.id == character_id,
                    Character.user_id == user_id
                )
            )
        )
        character = character.scalar_one_or_none()

        if not character:
            return None

        # Cannot update system templates
        if character.is_template:
            raise ValueError("Cannot update system template characters")

        update_data = character_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "config" and value:
                setattr(character, field, value)
            elif field != "config":
                setattr(character, field, value)

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def delete_character(
        self,
        character_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete custom character"""
        character = await self.db.execute(
            select(Character).where(
                and_(
                    Character.id == character_id,
                    Character.user_id == user_id
                )
            )
        )
        character = character.scalar_one_or_none()

        if not character:
            return False

        if character.is_template:
            raise ValueError("Cannot delete system template characters")

        await self.db.delete(character)
        await self.db.commit()
        return True

    async def rate_character(
        self,
        character_id: UUID,
        user_id: UUID,
        rating: int
    ) -> Optional[Character]:
        """Rate a character (1-5 stars)"""
        character = await self.get_character_by_id(character_id)
        if not character:
            return None

        # Simple rating logic (in production, track per-user ratings to prevent duplicates)
        current_avg = character.rating_avg or 0
        current_count = character.rating_count or 0

        new_avg = ((current_avg * current_count) + rating) / (current_count + 1)

        character.rating_avg = round(new_avg, 2)
        character.rating_count = current_count + 1
        character.usage_count += 1

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def increment_usage(self, character_id: UUID) -> bool:
        """Increment usage count for a character"""
        character = await self.get_character_by_id(character_id)
        if not character:
            return False

        character.usage_count += 1
        await self.db.commit()
        return True

    async def search_characters(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Character]:
        """Search template characters by name or profession"""
        search_pattern = f"%{query}%"

        result = await self.db.execute(
            select(Character)
            .where(
                and_(
                    Character.is_template == True,
                    Character.user_id.is_(None),
                    or_(
                        Character.name.ilike(search_pattern),
                        Character.config['profession'].astext.ilike(search_pattern)
                    )
                )
            )
            .order_by(desc(Character.usage_count))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_random_templates(
        self,
        count: int = 5
    ) -> List[Character]:
        """Get random template characters for recommendations"""
        # Get all templates
        result = await self.db.execute(
            select(Character)
            .where(
                and_(
                    Character.is_template == True,
                    Character.user_id.is_(None)
                )
            )
        )
        templates = list(result.scalars().all())

        # Return random selection
        if len(templates) <= count:
            return templates
        return random.sample(templates, count)
