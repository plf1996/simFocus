"""
Character schemas

Provides request/response schemas for character management operations.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class PersonalityTraits(BaseModel):
    """Character personality traits (1-10 scale)."""

    openness: int = Field(
        ...,
        ge=1,
        le=10,
        description="Openness to new ideas (1-10)"
    )
    rigor: int = Field(
        ...,
        ge=1,
        le=10,
        description="Logical rigor and precision (1-10)"
    )
    critical_thinking: int = Field(
        ...,
        ge=1,
        le=10,
        description="Critical thinking ability (1-10)"
    )
    optimism: int = Field(
        ...,
        ge=1,
        le=10,
        description="Optimism level (1-10)"
    )


class KnowledgeBackground(BaseModel):
    """Character knowledge and expertise background."""

    fields: list[str] = Field(
        ...,
        min_length=1,
        description="Fields of expertise"
    )
    experience_years: int = Field(
        ...,
        ge=0,
        description="Years of experience"
    )
    representative_views: list[str] = Field(
        ...,
        description="Representative viewpoints or beliefs"
    )


class CharacterConfig(BaseModel):
    """Complete character configuration."""

    age: int = Field(
        ...,
        ge=18,
        le=100,
        description="Character age"
    )
    gender: str = Field(
        ...,
        pattern='^(male|female|other|prefer_not_to_say)$',
        description="Character gender"
    )
    profession: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Character profession or role"
    )
    personality: PersonalityTraits = Field(
        ...,
        description="Personality traits"
    )
    knowledge: KnowledgeBackground = Field(
        ...,
        description="Knowledge background"
    )
    stance: str = Field(
        ...,
        pattern='^(support|oppose|neutral|critical_exploration)$',
        description="Default discussion stance"
    )
    expression_style: str = Field(
        ...,
        pattern='^(formal|casual|technical|storytelling)$',
        description="Communication style"
    )
    behavior_pattern: str = Field(
        ...,
        pattern='^(active|passive|balanced)$',
        description="Participation behavior pattern"
    )


class CharacterCreateRequest(BaseModel):
    """Character creation request."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Character display name"
    )
    avatar_url: str | None = Field(
        None,
        description="Character avatar URL"
    )
    config: CharacterConfig = Field(
        ...,
        description="Character configuration"
    )
    is_public: bool = Field(
        default=False,
        description="Whether character is publicly visible"
    )


class CharacterUpdateRequest(BaseModel):
    """Character update request."""

    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="Updated character name"
    )
    avatar_url: str | None = Field(
        None,
        description="Updated avatar URL"
    )
    config: CharacterConfig | None = Field(
        None,
        description="Updated character configuration"
    )
    is_public: bool | None = Field(
        None,
        description="Updated public visibility"
    )


class CharacterResponse(BaseModel):
    """Full character response."""

    id: str = Field(
        ...,
        description="Character ID"
    )
    user_id: str | None = Field(
        None,
        description="Owner user ID (NULL for system templates)"
    )
    name: str = Field(
        ...,
        description="Character name"
    )
    avatar_url: str | None = Field(
        None,
        description="Character avatar URL"
    )
    is_template: bool = Field(
        ...,
        description="Whether this is a system template"
    )
    is_public: bool = Field(
        ...,
        description="Public visibility flag"
    )
    config: CharacterConfig = Field(
        ...,
        description="Character configuration"
    )
    usage_count: int = Field(
        ...,
        ge=0,
        description="Number of times used in discussions"
    )
    rating_avg: float | None = Field(
        None,
        ge=1.0,
        le=5.0,
        description="Average user rating"
    )
    rating_count: int = Field(
        ...,
        ge=0,
        description="Number of ratings"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )

    model_config = {
        "from_attributes": True
    }


class CharacterTemplateResponse(BaseModel):
    """Character template list item (for browse view)."""

    id: str = Field(
        ...,
        description="Character ID"
    )
    name: str = Field(
        ...,
        description="Character name"
    )
    avatar_url: str | None = Field(
        None,
        description="Character avatar URL"
    )
    config: CharacterConfig = Field(
        ...,
        description="Character configuration"
    )
    usage_count: int = Field(
        ...,
        ge=0,
        description="Usage count"
    )
    rating_avg: float | None = Field(
        None,
        description="Average rating"
    )

    model_config = {
        "from_attributes": True
    }
