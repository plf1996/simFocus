from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class PersonalityConfig(BaseModel):
    openness: int = Field(..., ge=1, le=10)
    rigor: int = Field(..., ge=1, le=10)
    critical_thinking: int = Field(..., ge=1, le=10)
    optimism: int = Field(..., ge=1, le=10)


class KnowledgeConfig(BaseModel):
    fields: List[str] = Field(default_factory=list)
    experience_years: int = Field(default=0, ge=0)
    representative_views: List[str] = Field(default_factory=list)


class CharacterConfig(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    profession: Optional[str] = None
    personality: PersonalityConfig
    knowledge: KnowledgeConfig
    stance: str = Field(..., description="'support', 'oppose', 'neutral', 'critical_exploration'")
    expression_style: str = Field(..., description="'formal', 'casual', 'technical', 'storytelling'")
    behavior_pattern: str = Field(..., description="'active', 'passive', 'balanced'")


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    config: CharacterConfig


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    config: Optional[CharacterConfig] = None


class CharacterResponse(CharacterBase):
    id: UUID
    user_id: Optional[UUID] = None
    is_template: bool
    is_public: bool
    usage_count: int
    rating_avg: float
    rating_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CharacterTemplateResponse(CharacterResponse):
    """System template character (user_id is None)"""
    pass


class CharacterListItem(BaseModel):
    id: UUID
    name: str
    avatar_url: Optional[str] = None
    is_template: bool
    is_public: bool = True
    config: Optional[CharacterConfig] = None
    usage_count: int
    rating_avg: float
    rating_count: int = 0
    similarity_score: Optional[float] = Field(default=None, description="Semantic similarity score (0-1)")
    weighted_score: Optional[float] = Field(default=None, description="Weighted recommendation score (0-1)")

    model_config = ConfigDict(from_attributes=True)
