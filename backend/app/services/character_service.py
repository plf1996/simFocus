"""
Character service

Manages AI character configurations including templates and custom characters.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    CharacterNotFoundException,
    NotFoundException,
    ValidationException,
)
from app.models.character import Character
from app.models.discussion import DiscussionParticipant


class CharacterService:
    """
    Character management service.

    Handles:
    - Creating custom characters
    - Retrieving characters (templates + user's custom)
    - Updating character configurations
    - Deleting characters
    - Rating characters
    """

    # Valid character config values
    VALID_GENDERS = ["male", "female", "other", "prefer_not_to_say"]
    VALID_STANCES = ["support", "oppose", "neutral", "critical_exploration"]
    VALID_EXPRESSION_STYLES = ["formal", "casual", "technical", "storytelling"]
    VALID_BEHAVIOR_PATTERNS = ["active", "passive", "balanced"]

    def __init__(self, db: AsyncSession):
        """
        Initialize character service with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_character(
        self,
        user_id: str,
        name: str,
        config: dict,
        avatar_url: Optional[str] = None,
        is_public: bool = False,
    ) -> Character:
        """
        Create a new custom character.

        Args:
            user_id: User UUID as string
            name: Character display name (2-100 characters)
            config: Character configuration dict
            avatar_url: Optional avatar image URL
            is_public: Whether character is publicly visible

        Returns:
            Created Character object

        Raises:
            ValidationException: If validation fails

        Example:
            >>> config = {
            ...     "age": 35,
            ...     "gender": "male",
            ...     "profession": "Software Engineer",
            ...     "personality": {"openness": 8, "rigor": 7, "critical_thinking": 9, "optimism": 6},
            ...     "knowledge": {
            ...         "fields": ["Computer Science", "AI"],
            ...         "experience_years": 10,
            ...         "representative_views": ["Code quality matters", "Testing is essential"]
            ...     },
            ...     "stance": "support",
            ...     "expression_style": "technical",
            ...     "behavior_pattern": "balanced"
            ... }
            >>> character = await character_service.create_character(
            ...     user_id="123",
            ...     name="Tech Lead Tom",
            ...     config=config
            ... )
        """
        # Validate name
        if not name or len(name) < 2 or len(name) > 100:
            raise ValidationException(
                message="Name must be 2-100 characters",
                details={"min_length": 2, "max_length": 100, "provided_length": len(name or "")}
            )

        # Validate config structure
        self._validate_character_config(config)

        # Validate avatar URL if provided
        if avatar_url and not self._is_valid_url(avatar_url):
            raise ValidationException(
                message="Invalid avatar URL",
                details={"avatar_url": avatar_url}
            )

        # Create character
        character = Character(
            user_id=UUID(user_id),
            name=name,
            avatar_url=avatar_url,
            is_template=False,  # User-created characters are not templates
            is_public=is_public,
            config=config,
            usage_count=0,
            rating_avg=None,
            rating_count=0,
        )

        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)

        return character

    async def get_character(self, character_id: str) -> Character:
        """
        Get character by ID.

        Args:
            character_id: Character UUID as string

        Returns:
            Character object

        Raises:
            CharacterNotFoundException: If character doesn't exist

        Example:
            >>> character = await character_service.get_character(character_id="123")
            >>> print(character.name)
        """
        character = await self._get_character_by_id(character_id)

        if not character:
            raise CharacterNotFoundException(character_id=character_id)

        return character

    async def list_characters(
        self,
        user_id: str,
        include_templates: bool = True,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> list[Character]:
        """
        List available characters for user.

        Includes user's custom characters and optionally system templates.

        Args:
            user_id: User UUID as string
            include_templates: Whether to include system templates
            category: Optional category filter for templates
            limit: Maximum number of characters to return

        Returns:
            List of Character objects

        Example:
            >>> characters = await character_service.list_characters(
            ...     user_id="123",
            ...     include_templates=True
            ... )
            >>> for char in characters:
            ...     print(f"{char.name} ({'Template' if char.is_template else 'Custom'})")
        """
        # Build query for user's custom characters
        query = select(Character).where(
            Character.user_id == UUID(user_id),
            Character.is_template == False
        )

        # Add templates if requested
        if include_templates:
            # Get templates (no user_id or user_id is NULL)
            template_query = select(Character).where(
                Character.is_template == True
            )

            # Apply category filter if specified
            if category:
                # Filter by profession field in config
                template_query = template_query.where(
                    Character.config["profession"].astext == category
                )

            # Combine queries using union
            query = query.union(template_query)

        # Order by template first (templates before custom), then by usage
        query = query.order_by(
            Character.is_template.desc(),
            Character.usage_count.desc(),
            Character.name.asc()
        )

        # Apply limit
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_templates(
        self,
        category: Optional[str] = None,
        limit: int = 50,
    ) -> list[Character]:
        """
        List system character templates.

        Args:
            category: Optional category/profession filter
            limit: Maximum number of templates to return

        Returns:
            List of template Character objects

        Example:
            >>> templates = await character_service.list_templates(
            ...     category="Product Manager",
            ...     limit=10
            ... )
        """
        query = select(Character).where(
            Character.is_template == True
        )

        # Apply category filter if specified
        if category:
            query = query.where(
                Character.config["profession"].astext == category
            )

        # Order by usage count and name
        query = query.order_by(
            Character.usage_count.desc(),
            Character.name.asc()
        )

        # Apply limit
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_character(
        self,
        character_id: str,
        user_id: str,
        name: Optional[str] = None,
        config: Optional[dict] = None,
        avatar_url: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Character:
        """
        Update character details.

        Only custom characters (non-templates) can be updated by users.

        Args:
            character_id: Character UUID as string
            user_id: User UUID as string (for authorization)
            name: New name (optional)
            config: New config (optional)
            avatar_url: New avatar URL (optional)
            is_public: New public visibility (optional)

        Returns:
            Updated Character object

        Raises:
            CharacterNotFoundException: If character doesn't exist
            ValidationException: If validation fails or authorization denied

        Example:
            >>> updated = await character_service.update_character(
            ...     character_id="123",
            ...     user_id="456",
            ...     name="Updated Name",
            ...     is_public=True
            ... )
        """
        # Get character
        character = await self._get_character_by_id(character_id)

        if not character:
            raise CharacterNotFoundException(character_id=character_id)

        # Verify ownership (only owner can update their custom characters)
        if character.is_template:
            raise ValidationException(
                message="Cannot update system templates",
                details={"character_id": character_id}
            )

        if str(character.user_id) != user_id:
            raise ValidationException(
                message="Character does not belong to this user",
                details={"character_id": character_id, "user_id": user_id}
            )

        # Update name
        if name is not None:
            if len(name) < 2 or len(name) > 100:
                raise ValidationException(
                    message="Name must be 2-100 characters",
                    details={"min_length": 2, "max_length": 100, "provided_length": len(name)}
                )
            character.name = name

        # Update config
        if config is not None:
            self._validate_character_config(config)
            character.config = config

        # Update avatar
        if avatar_url is not None:
            if avatar_url and not self._is_valid_url(avatar_url):
                raise ValidationException(
                    message="Invalid avatar URL",
                    details={"avatar_url": avatar_url}
                )
            character.avatar_url = avatar_url

        # Update visibility
        if is_public is not None:
            character.is_public = is_public

        await self.db.commit()
        await self.db.refresh(character)

        return character

    async def delete_character(self, character_id: str, user_id: str) -> bool:
        """
        Delete a custom character.

        Characters can only be deleted if they're not used in active discussions.

        Args:
            character_id: Character UUID as string
            user_id: User UUID as string (for authorization)

        Returns:
            True if deleted successfully

        Raises:
            CharacterNotFoundException: If character doesn't exist
            ValidationException: If character is in use or authorization denied

        Example:
            >>> success = await character_service.delete_character(
            ...     character_id="123",
            ...     user_id="456"
            ... )
        """
        # Get character
        character = await self._get_character_by_id(character_id)

        if not character:
            raise CharacterNotFoundException(character_id=character_id)

        # Cannot delete templates
        if character.is_template:
            raise ValidationException(
                message="Cannot delete system templates",
                details={"character_id": character_id}
            )

        # Verify ownership
        if str(character.user_id) != user_id:
            raise ValidationException(
                message="Character does not belong to this user",
                details={"character_id": character_id, "user_id": user_id}
            )

        # Check for usage in active discussions
        active_usage = await self.db.execute(
            select(func.count(DiscussionParticipant.id)).where(
                DiscussionParticipant.character_id == UUID(character_id)
            )
        )
        usage_count = active_usage.scalar() or 0

        if usage_count > 0:
            raise ValidationException(
                message="Cannot delete character used in discussions",
                details={"usage_count": usage_count}
            )

        # Delete character
        await self.db.delete(character)
        await self.db.commit()

        return True

    async def rate_character(
        self,
        character_id: str,
        user_id: str,
        rating: int,
    ) -> Character:
        """
        Rate a character (1-5 stars).

        Updates the character's average rating.

        Args:
            character_id: Character UUID as string
            user_id: User UUID as string (for authorization - must have used character)
            rating: Rating value (1-5)

        Returns:
            Updated Character object with new rating

        Raises:
            CharacterNotFoundException: If character doesn't exist
            ValidationException: If rating is invalid

        Example:
            >>> character = await character_service.rate_character(
            ...     character_id="123",
            ...     user_id="456",
            ...     rating=5
            ... )
        """
        # Validate rating
        if not 1 <= rating <= 5:
            raise ValidationException(
                message="Rating must be between 1 and 5",
                details={"rating": rating, "min": 1, "max": 5}
            )

        # Get character
        character = await self._get_character_by_id(character_id)

        if not character:
            raise CharacterNotFoundException(character_id=character_id)

        # TODO: Verify user has used this character in a discussion
        # This prevents rating abuse

        # Update rating using model method
        character.update_rating(rating)

        await self.db.commit()
        await self.db.refresh(character)

        return character

    async def _get_character_by_id(self, character_id: str) -> Optional[Character]:
        """
        Get character by ID.

        Args:
            character_id: Character UUID as string

        Returns:
            Character object or None
        """
        result = await self.db.execute(
            select(Character).where(Character.id == UUID(character_id))
        )
        return result.scalar_one_or_none()

    def _validate_character_config(self, config: dict) -> None:
        """
        Validate character configuration structure.

        Args:
            config: Configuration dict to validate

        Raises:
            ValidationException: If config is invalid
        """
        if not isinstance(config, dict):
            raise ValidationException(
                message="Character config must be a dictionary",
                details={"type": type(config).__name__}
            )

        # Required fields
        required_fields = [
            "age", "gender", "profession",
            "personality", "knowledge", "stance",
            "expression_style", "behavior_pattern"
        ]

        missing_fields = [f for f in required_fields if f not in config]
        if missing_fields:
            raise ValidationException(
                message=f"Missing required config fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields}
            )

        # Validate age
        age = config["age"]
        if not isinstance(age, int) or not (18 <= age <= 100):
            raise ValidationException(
                message="Age must be an integer between 18 and 100",
                details={"age": age}
            )

        # Validate gender
        gender = config["gender"]
        if gender not in self.VALID_GENDERS:
            raise ValidationException(
                message=f"Invalid gender. Must be one of: {', '.join(self.VALID_GENDERS)}",
                details={"gender": gender, "valid_genders": self.VALID_GENDERS}
            )

        # Validate profession
        profession = config["profession"]
        if not isinstance(profession, str) or len(profession) < 2 or len(profession) > 100:
            raise ValidationException(
                message="Profession must be 2-100 characters",
                details={"profession": profession}
            )

        # Validate personality
        personality = config["personality"]
        if not isinstance(personality, dict):
            raise ValidationException(
                message="Personality must be a dictionary",
                details={"personality_type": type(personality).__name__}
            )

        personality_traits = ["openness", "rigor", "critical_thinking", "optimism"]
        for trait in personality_traits:
            if trait not in personality:
                raise ValidationException(
                    message=f"Missing personality trait: {trait}",
                    details={"missing_trait": trait}
                )
            value = personality[trait]
            if not isinstance(value, int) or not (1 <= value <= 10):
                raise ValidationException(
                    message=f"{trait} must be an integer between 1 and 10",
                    details={"trait": trait, "value": value}
                )

        # Validate knowledge
        knowledge = config["knowledge"]
        if not isinstance(knowledge, dict):
            raise ValidationException(
                message="Knowledge must be a dictionary",
                details={"knowledge_type": type(knowledge).__name__}
            )

        if "fields" not in knowledge or not isinstance(knowledge["fields"], list):
            raise ValidationException(
                message="Knowledge must contain a 'fields' list",
                details={"knowledge": knowledge}
            )

        if len(knowledge["fields"]) == 0:
            raise ValidationException(
                message="Knowledge fields cannot be empty",
                details={}
            )

        if "experience_years" not in knowledge:
            raise ValidationException(
                message="Knowledge must contain 'experience_years'",
                details={"knowledge": knowledge}
            )

        exp_years = knowledge["experience_years"]
        if not isinstance(exp_years, int) or exp_years < 0:
            raise ValidationException(
                message="experience_years must be a non-negative integer",
                details={"experience_years": exp_years}
            )

        # Validate stance
        stance = config["stance"]
        if stance not in self.VALID_STANCES:
            raise ValidationException(
                message=f"Invalid stance. Must be one of: {', '.join(self.VALID_STANCES)}",
                details={"stance": stance, "valid_stances": self.VALID_STANCES}
            )

        # Validate expression style
        expression_style = config["expression_style"]
        if expression_style not in self.VALID_EXPRESSION_STYLES:
            raise ValidationException(
                message=f"Invalid expression_style. Must be one of: {', '.join(self.VALID_EXPRESSION_STYLES)}",
                details={"expression_style": expression_style, "valid_styles": self.VALID_EXPRESSION_STYLES}
            )

        # Validate behavior pattern
        behavior_pattern = config["behavior_pattern"]
        if behavior_pattern not in self.VALID_BEHAVIOR_PATTERNS:
            raise ValidationException(
                message=f"Invalid behavior_pattern. Must be one of: {', '.join(self.VALID_BEHAVIOR_PATTERNS)}",
                details={"behavior_pattern": behavior_pattern, "valid_patterns": self.VALID_BEHAVIOR_PATTERNS}
            )

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
